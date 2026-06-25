from database.db_connection import DatabaseConnection
from models.vendedor import Vendedor

class VendedorRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, vendedor: Vendedor) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            # 1. Inserir dados de entidade em PESSOA
            cursor.execute("""
                INSERT INTO PESSOA (nome, cpf, telefone, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id_pessoa
            """, (vendedor.nome, vendedor.cpf, vendedor.telefone, vendedor.email))
            id_pessoa = cursor.fetchone()[0]

            # 2. Inserir na tabela filha VENDEDOR
            cursor.execute("""
                INSERT INTO VENDEDOR (id_pessoa)
                VALUES (%s)
                RETURNING id_vendedor
            """, (id_pessoa,))
            novo_id = cursor.fetchone()[0]
            
            conexao.commit()
            return novo_id

    def listar_todos(self) -> list[Vendedor]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_vendedor, p.nome, p.cpf, p.telefone, p.email 
                FROM VENDEDOR v
                JOIN PESSOA p ON v.id_pessoa = p.id_pessoa
                ORDER BY p.nome
            """)
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_vendedor: int) -> Vendedor | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_vendedor, p.nome, p.cpf, p.telefone, p.email 
                FROM VENDEDOR v
                JOIN PESSOA p ON v.id_pessoa = p.id_pessoa
                WHERE v.id_vendedor = %s
            """, (id_vendedor,))
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    @staticmethod
    def __linha_para_objeto(linha) -> Vendedor:
        id_vendedor, nome, cpf, telefone, email = linha
        return Vendedor(nome=nome, cpf=cpf, telefone=telefone or "",
                         email=email or "", id_vendedor=id_vendedor)