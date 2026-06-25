from database.db_connection import DatabaseConnection
from models.medico import Medico

class MedicoRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, medico: Medico):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            # 1. Inserir dados básicos em PESSOA (Envia um CPF padrão fictício válido pelo CHECK)
            cursor.execute("""
                INSERT INTO PESSOA (nome, cpf, telefone, email)
                VALUES (%s, '00000000000', %s, '')
                RETURNING id_pessoa
            """, (medico.nome, medico.telefone))
            id_pessoa = cursor.fetchone()[0]

            # 2. Inserir dados clínicos na tabela filha MEDICO
            cursor.execute("""
                INSERT INTO MEDICO (id_pessoa, crm, especialidade)
                VALUES (%s, %s, %s)
            """, (id_pessoa, medico.crm, medico.especialidade))
            conexao.commit()

    def listar_todos(self) -> list[Medico]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT m.crm, p.nome, m.especialidade, p.telefone 
                FROM MEDICO m
                JOIN PESSOA p ON m.id_pessoa = p.id_pessoa
                ORDER BY p.nome
            """)
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_crm(self, crm: str) -> Medico | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT m.crm, p.nome, m.especialidade, p.telefone 
                FROM MEDICO m
                JOIN PESSOA p ON m.id_pessoa = p.id_pessoa
                WHERE m.crm = %s
            """, (crm,))
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    @staticmethod
    def __linha_para_objeto(linha) -> Medico:
        crm, nome, especialidade, telefone = linha
        return Medico(crm=crm, nome=nome, especialidade=especialidade, telefone=telefone or "")