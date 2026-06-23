from database.db_connection import DatabaseConnection
from models.medico import Medico


class MedicoRepository:
    def __init__(self, db: DatabaseConnection = None):
        self.__db = db or DatabaseConnection()

    def inserir(self, medico: Medico):
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO medico (crm, nome, especialidade, telefone)
                VALUES (%s, %s, %s, %s)
            """, (medico.crm, medico.nome, medico.especialidade, medico.telefone))
            conexao.commit()

    def listar_todos(self) -> list[Medico]:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT crm, nome, especialidade, telefone FROM medico ORDER BY nome")
            return [self.__linha_para_objeto(linha) for linha in cursor.fetchall()]

    def buscar_por_crm(self, crm: str) -> Medico | None:
        conexao = self.__db.obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT crm, nome, especialidade, telefone FROM medico WHERE crm = %s", (crm,)
            )
            linha = cursor.fetchone()
            return self.__linha_para_objeto(linha) if linha else None

    @staticmethod
    def __linha_para_objeto(linha) -> Medico:
        crm, nome, especialidade, telefone = linha
        return Medico(crm=crm, nome=nome, especialidade=especialidade, telefone=telefone or "")
