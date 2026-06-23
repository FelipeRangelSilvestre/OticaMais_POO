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
            cursor.execute("""
                INSERT INTO venda (data_venda, valor_total, id_cliente, id_vendedor, id_receita)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_venda
            """, (venda.data_venda, venda.valor_total, venda.id_cliente,
                  venda.id_vendedor, venda.id_receita))
            novo_id = cursor.fetchone()[0]

            for item in venda.itens:
                # A trigger trg_item_venda_after já soma valor_total e baixa
                # o estoque automaticamente a cada INSERT em item_venda.
                cursor.execute("""
                    INSERT INTO item_venda (id_venda, id_produto, quantidade, valor_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (novo_id, item.id_produto, item.quantidade, item.valor_unitario))

            conexao.commit()
            venda.id_venda = novo_id
            return novo_id

    # ---------------------------- READ ----------------------------
    def listar_todas(self) -> list[Venda]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT id_venda, data_venda, id_cliente, id_vendedor, id_receita
                  FROM venda ORDER BY data_venda DESC
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
                SELECT id_venda, data_venda, id_cliente, id_vendedor, id_receita
                  FROM venda WHERE id_venda = %s
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
                SELECT id_venda, data_venda, id_cliente, id_vendedor, id_receita
                  FROM venda WHERE id_cliente = %s ORDER BY data_venda DESC
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
                "UPDATE venda SET id_vendedor = %s WHERE id_venda = %s",
                (novo_id_vendedor, id_venda)
            )
            conexao.commit()

    def atualizar_receita(self, id_venda: int, novo_id_receita: int):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE venda SET id_receita = %s WHERE id_venda = %s",
                (novo_id_receita, id_venda)
            )
            conexao.commit()

    # ---------------------------- DELETE ----------------------------
    def excluir(self, id_venda: int):
        # ON DELETE CASCADE em ITEM_VENDA remove os itens automaticamente.
        # Antes, devolve o estoque dos produtos vendidos (a trigger só atua
        # em INSERT, então a devolução no DELETE precisa ser manual).
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_produto, quantidade FROM item_venda WHERE id_venda = %s", (id_venda,)
            )
            itens = cursor.fetchall()
            for id_produto, quantidade in itens:
                cursor.execute(
                    "UPDATE produto SET qtd_estoque = qtd_estoque + %s WHERE id_produto = %s",
                    (quantidade, id_produto)
                )
            cursor.execute("DELETE FROM venda WHERE id_venda = %s", (id_venda,))
            conexao.commit()

    # ---------------------------- auxiliares ----------------------------
    @staticmethod
    def __linha_para_venda(linha) -> Venda:
        id_venda, data_venda, id_cliente, id_vendedor, id_receita = linha
        return Venda(id_cliente=id_cliente, id_vendedor=id_vendedor,
                      id_receita=id_receita, data_venda=data_venda, id_venda=id_venda)

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
