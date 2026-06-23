from database.db_connection import DatabaseConnection
from models.cliente import Cliente


class ClienteRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, cliente: Cliente) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cliente (nome, cpf, telefone, email, endereco)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_cliente
            """, (cliente.nome, cliente.cpf, cliente.telefone, cliente.email, cliente.endereco))
            novo_id = cursor.fetchone()[0]
            conexao.commit()
            return novo_id

    def listar_todos(self) -> list[Cliente]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_cliente, nome, cpf, telefone, email, endereco FROM cliente ORDER BY nome"
            )
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_cliente: int) -> Cliente | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_cliente, nome, cpf, telefone, email, endereco FROM cliente WHERE id_cliente = %s",
                (id_cliente,)
            )
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    def buscar_por_cpf(self, cpf: str) -> Cliente | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_cliente, nome, cpf, telefone, email, endereco FROM cliente WHERE cpf = %s",
                (cpf,)
            )
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    def buscar_por_nome(self, termo: str) -> list[Cliente]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_cliente, nome, cpf, telefone, email, endereco "
                "FROM cliente WHERE nome ILIKE %s ORDER BY nome",
                (f"%{termo}%",)
            )
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def atualizar(self, cliente: Cliente):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE cliente
                   SET nome = %s, telefone = %s, email = %s, endereco = %s
                 WHERE id_cliente = %s
            """, (cliente.nome, cliente.telefone, cliente.email, cliente.endereco, cliente.id_cliente))
            conexao.commit()

    def excluir(self, id_cliente: int):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
            conexao.commit()

    @staticmethod
    def __linha_para_objeto(linha) -> Cliente:
        id_cliente, nome, cpf, telefone, email, endereco = linha
        return Cliente(nome=nome, cpf=cpf, telefone=telefone or "",
                        email=email or "", endereco=endereco or "", id_cliente=id_cliente)
