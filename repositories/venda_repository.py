from database.db_connection import DatabaseConnection
from models.venda import Venda
from models.item_venda import ItemVenda


class VendaRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    # ---------------------------- CREATE ----------------------------
    def inserir(self, venda: Venda) -> int:
        venda.validar_para_fechamento()  # regra de negócio: não salva venda sem item
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            # 1. Insere primeiro na Superclasse SERVICO
            cursor.execute("""
                INSERT INTO SERVICO (id_cliente, data_servico, tipo_servico)
                VALUES (%s, %s, 'VENDA')
                RETURNING id_servico
            """, (venda.id_cliente, venda.data_venda))
            id_servico = cursor.fetchone()[0]

            # 2. Insere na Subclasse VENDA usando a chave estrangeira gerada
            cursor.execute("""
                INSERT INTO VENDA (id_servico, id_vendedor, id_receita, valor_total)
                VALUES (%s, %s, %s, %s)
                RETURNING id_venda
            """, (id_servico, venda.id_vendedor, venda.id_receita, venda.valor_total))
            id_venda = cursor.fetchone()[0]

            for item in venda.itens:
                # A trigger trg_item_venda_after já soma valor_total e baixa
                # o estoque automaticamente a cada INSERT em item_venda.
                cursor.execute("""
                    INSERT INTO item_venda (id_venda, id_produto, quantidade, valor_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (id_venda, item.id_produto, item.quantidade, item.valor_unitario))

            conexao.commit()
            venda.id_venda = id_venda
            return id_venda

    # ---------------------------- READ ----------------------------
    def listar_todas(self) -> list[Venda]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_venda, s.data_servico, s.id_cliente, v.id_vendedor, v.id_receita, v.valor_total
                  FROM VENDA v
                  JOIN SERVICO s ON v.id_servico = s.id_servico
                 ORDER BY s.data_servico DESC
            """)
            linhas = cursor.fetchall()
            vendas = [self.__linha_para_venda(linha) for linha in linhas]
            for venda in vendas:
                venda.definir_itens(self.__carregar_itens(cursor, venda.id_venda))
            return vendas

    def buscar_por_id(self, id_venda: int) -> Venda | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_venda, s.data_servico, s.id_cliente, v.id_vendedor, v.id_receita, v.valor_total
                  FROM VENDA v
                  JOIN SERVICO s ON v.id_servico = s.id_servico
                 WHERE v.id_venda = %s
            """, (id_venda,))
            linha = cursor.fetchone()
            if not linha:
                return None
            venda = self.__linha_para_venda(linha)
            venda.definir_itens(self.__carregar_itens(cursor, id_venda))
            return venda

    def buscar_por_cliente(self, id_cliente: int) -> list[Venda]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_venda, s.data_servico, s.id_cliente, v.id_vendedor, v.id_receita, v.valor_total
                  FROM VENDA v
                  JOIN SERVICO s ON v.id_servico = s.id_servico
                 WHERE s.id_cliente = %s 
                 ORDER BY s.data_servico DESC
            """, (id_cliente,))
            linhas = cursor.fetchall()
            vendas = [self.__linha_para_venda(linha) for linha in linhas]
            for venda in vendas:
                venda.definir_itens(self.__carregar_itens(cursor, venda.id_venda))
            return vendas

    # ---------------------------- UPDATE ----------------------------
    def atualizar_vendedor(self, id_venda: int, novo_id_vendedor: int):
        """Permite corrigir qual vendedor está associado à venda."""
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE VENDA SET id_vendedor = %s WHERE id_venda = %s",
                (novo_id_vendedor, id_venda)
            )
            conexao.commit()

    def atualizar_receita(self, id_venda: int, novo_id_receita: int):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE VENDA SET id_receita = %s WHERE id_venda = %s",
                (novo_id_receita, id_venda)
            )
            conexao.commit()

    # ---------------------------- DELETE ----------------------------
    def excluir(self, id_venda: int):
        # ON DELETE CASCADE atuará em cascata. Precisamos excluir o SERVICO 
        # que é o pai da VENDA, e isso limpará a VENDA e o ITEM_VENDA sozinhos.
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            # 1. Recupera os itens para devolver o estoque primeiro
            cursor.execute(
                "SELECT id_produto, quantidade FROM item_venda WHERE id_venda = %s", (id_venda,)
            )
            itens = cursor.fetchall()
            for id_produto, quantidade in itens:
                cursor.execute(
                    "UPDATE produto SET qtd_estoque = qtd_estoque + %s WHERE id_produto = %s",
                    (quantidade, id_produto)
                )
            
            # 2. Descobre o id_servico associado a esta venda
            cursor.execute("SELECT id_servico FROM VENDA WHERE id_venda = %s", (id_venda,))
            resultado = cursor.fetchone()
            
            if resultado:
                id_servico = resultado[0]
                # 3. Exclui a superclasse SERVICO (O PostgreSQL apaga a VENDA em cascata)
                cursor.execute("DELETE FROM SERVICO WHERE id_servico = %s", (id_servico,))
            
            conexao.commit()

    # ---------------------------- auxiliares ----------------------------
    @staticmethod
    def __linha_para_venda(linha) -> Venda:
        # A ordem aqui tem que casar perfeitamente com os SELECTs acima
        id_venda, data_venda, id_cliente, id_vendedor, id_receita, valor_total = linha
        
        v = Venda(id_cliente=id_cliente, id_vendedor=id_vendedor,
                  id_receita=id_receita, data_venda=data_venda, id_venda=id_venda)
        
        # Como o valor total vem do banco (calculado pela trigger), precisamos 
        # injetar no objeto que por padrão nasce zerado no Python.
        v._Venda__valor_total = float(valor_total) if valor_total else 0.0
        return v

    @staticmethod
    def __carregar_itens(cursor, id_venda: int) -> list[ItemVenda]:
        cursor.execute("""
            SELECT iv.id_produto, iv.quantidade, iv.valor_unitario, p.descricao
              FROM item_venda iv
              JOIN produto p ON p.id_produto = iv.id_produto
             WHERE iv.id_venda = %s
        """, (id_venda,))
        return [
            ItemVenda(id_produto=id_produto, quantidade=quantidade,
                      valor_unitario=float(valor_unitario), descricao_produto=descricao)
            for id_produto, quantidade, valor_unitario, descricao in cursor.fetchall()
        ]