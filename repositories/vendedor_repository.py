from database.db_connection import DatabaseConnection
from models.vendedor import Vendedor


class VendedorRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, vendedor: Vendedor) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO vendedor (nome, cpf, telefone, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id_vendedor
            """, (vendedor.nome, vendedor.cpf, vendedor.telefone, vendedor.email))
            novo_id = cursor.fetchone()[0]
            conexao.commit()
            return novo_id

    def listar_todos(self) -> list[Vendedor]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_vendedor, nome, cpf, telefone, email FROM vendedor ORDER BY nome"
            )
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_vendedor: int) -> Vendedor | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_vendedor, nome, cpf, telefone, email FROM vendedor WHERE id_vendedor = %s",
                (id_vendedor,)
            )
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    @staticmethod
    def __linha_para_objeto(linha) -> Vendedor:
        id_vendedor, nome, cpf, telefone, email = linha
        return Vendedor(nome=nome, cpf=cpf, telefone=telefone or "",
                         email=email or "", id_vendedor=id_vendedor)
