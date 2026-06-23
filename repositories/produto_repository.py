from database.db_connection import DatabaseConnection
from models.produto import Produto, Armacao, Lente


class ProdutoRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir_armacao(self, armacao: Armacao) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO produto (tipo, descricao, preco_venda, qtd_estoque, qtd_minima)
                VALUES ('ARMACAO', %s, %s, %s, %s)
                RETURNING id_produto
            """, (armacao.descricao, armacao.preco_venda, armacao.qtd_estoque, armacao.qtd_minima))
            novo_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO armacao (id_produto, marca, modelo, cor, material)
                VALUES (%s, %s, %s, %s, %s)
            """, (novo_id, armacao.marca, "", armacao.cor, ""))
            conexao.commit()
            return novo_id

    def inserir_lente(self, lente: Lente) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO produto (tipo, descricao, preco_venda, qtd_estoque, qtd_minima)
                VALUES ('LENTE', %s, %s, %s, %s)
                RETURNING id_produto
            """, (lente.descricao, lente.preco_venda, lente.qtd_estoque, lente.qtd_minima))
            novo_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO lente (id_produto, material, tipo_foco, indice)
                VALUES (%s, %s, %s, %s)
            """, (novo_id, "-", lente.tipo_foco, lente.indice))
            conexao.commit()
            return novo_id

    def listar_todos(self) -> list[Produto]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT p.id_produto, p.tipo, p.descricao, p.preco_venda, p.qtd_estoque, p.qtd_minima,
                       a.marca, a.cor,
                       l.tipo_foco, l.indice
                  FROM produto p
                  LEFT JOIN armacao a ON a.id_produto = p.id_produto
                  LEFT JOIN lente   l ON l.id_produto = p.id_produto
                 ORDER BY p.id_produto
            """)
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT p.id_produto, p.tipo, p.descricao, p.preco_venda, p.qtd_estoque, p.qtd_minima,
                       a.marca, a.cor,
                       l.tipo_foco, l.indice
                  FROM produto p
                  LEFT JOIN armacao a ON a.id_produto = p.id_produto
                  LEFT JOIN lente   l ON l.id_produto = p.id_produto
                 WHERE p.id_produto = %s
            """, (id_produto,))
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    def atualizar_estoque(self, id_produto: int, nova_quantidade: int):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE produto SET qtd_estoque = %s WHERE id_produto = %s",
                (nova_quantidade, id_produto)
            )
            conexao.commit()

    def excluir(self, id_produto: int):
        # ON DELETE CASCADE em ARMACAO/LENTE remove a linha filha automaticamente
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
            conexao.commit()

    @staticmethod
    def __linha_para_objeto(linha) -> Produto:
        (id_produto, tipo, descricao, preco, estoque, minimo,
         marca, cor, tipo_foco, indice) = linha

        if tipo == "ARMACAO":
            return Armacao(id_produto=id_produto, descricao=descricao, preco_venda=float(preco),
                            qtd_estoque=estoque, marca=marca, cor=cor or "", qtd_minima=minimo)
        else:  # LENTE
            return Lente(id_produto=id_produto, descricao=descricao, preco_venda=float(preco),
                          qtd_estoque=estoque, tipo_foco=tipo_foco,
                          indice=float(indice) if indice is not None else None, qtd_minima=minimo)
