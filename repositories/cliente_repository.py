from database.db_connection import DatabaseConnection
from models.cliente import Cliente

class ClienteRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, cliente: Cliente) -> int:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            # 1. Inserir na tabela pai (PESSOA)
            cursor.execute("""
                INSERT INTO PESSOA (nome, cpf, telefone, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id_pessoa
            """, (cliente.nome, cliente.cpf, cliente.telefone, cliente.email))
            id_pessoa = cursor.fetchone()[0]

            # 2. Inserir na tabela filha (CLIENTE)
            cursor.execute("""
                INSERT INTO CLIENTE (id_pessoa, endereco)
                VALUES (%s, %s)
                RETURNING id_cliente
            """, (id_pessoa, cliente.endereco))
            novo_id = cursor.fetchone()[0]
            
            conexao.commit()
            return novo_id

    def listar_todos(self) -> list[Cliente]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_cliente, p.nome, p.cpf, p.telefone, p.email, c.endereco 
                FROM CLIENTE c
                JOIN PESSOA p ON c.id_pessoa = p.id_pessoa
                ORDER BY p.nome
            """)
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_cliente: int) -> Cliente | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_cliente, p.nome, p.cpf, p.telefone, p.email, c.endereco 
                FROM CLIENTE c
                JOIN PESSOA p ON c.id_pessoa = p.id_pessoa
                WHERE c.id_cliente = %s
            """, (id_cliente,))
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    def buscar_por_cpf(self, cpf: str) -> Cliente | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_cliente, p.nome, p.cpf, p.telefone, p.email, c.endereco 
                FROM CLIENTE c
                JOIN PESSOA p ON c.id_pessoa = p.id_pessoa
                WHERE p.cpf = %s
            """, (cpf,))
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    def buscar_por_nome(self, termo: str) -> list[Cliente]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_cliente, p.nome, p.cpf, p.telefone, p.email, c.endereco 
                FROM CLIENTE c
                JOIN PESSOA p ON c.id_pessoa = p.id_pessoa
                WHERE p.nome ILIKE %s ORDER BY p.nome
            """, (f"%{termo}%",))
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def atualizar(self, cliente: Cliente):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id_pessoa FROM CLIENTE WHERE id_cliente = %s", (cliente.id_cliente,))
            id_pessoa = cursor.fetchone()[0]

            # Atualiza os dados comuns na tabela PESSOA
            cursor.execute("""
                UPDATE PESSOA
                   SET nome = %s, telefone = %s, email = %s
                 WHERE id_pessoa = %s
            """, (cliente.nome, cliente.telefone, cliente.email, id_pessoa))

            # Atualiza os dados específicos na tabela CLIENTE
            cursor.execute("""
                UPDATE CLIENTE
                   SET endereco = %s
                 WHERE id_cliente = %s
            """, (cliente.endereco, cliente.id_cliente))
            conexao.commit()

    def excluir(self, id_cliente: int):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id_pessoa FROM CLIENTE WHERE id_cliente = %s", (id_cliente,))
            resultado = cursor.fetchone()
            if resultado:
                id_pessoa = resultado[0]
                # Como a restrição estrangeira está com ON DELETE CASCADE, remover a PESSOA limpa o CLIENTE automaticamente
                cursor.execute("DELETE FROM PESSOA WHERE id_pessoa = %s", (id_pessoa,))
            conexao.commit()

    @staticmethod
    def __linha_para_objeto(linha) -> Cliente:
        id_cliente, nome, cpf, telefone, email, endereco = linha
        return Cliente(nome=nome, cpf=cpf, telefone=telefone or "",
                        email=email or "", endereco=endereco or "", id_cliente=id_cliente)