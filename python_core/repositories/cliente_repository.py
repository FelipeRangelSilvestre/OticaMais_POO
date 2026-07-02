import psycopg2
from models.cliente import Cliente

class ClienteRepository:
    def __init__(self):
        # Configuração da ligação ao PostgreSQL
        self.config = {
            "host": "localhost",
            "database": "otica_mais",
            "user": "postgres",
            "password": "SUA_PASSWORD_AQUI", # Substitua pela sua palavra-passe
            "port": "5432"
        }

    def conectar(self):
        return psycopg2.connect(**self.config)

    def inserir(self, cliente: Cliente):
        try:
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    # Inserção na tabela que descobrimos anteriormente
                    query = "INSERT INTO CLIENTE (nome, cpf, endereco) VALUES (%s, %s, %s)"
                    cursor.execute(query, (cliente.nome, cliente.cpf, cliente.endereco))
                    conn.commit()
                    print("\n✅ Registo inserido na base de dados com sucesso!")
        except Exception as e:
            # Tratamento de Exceções exigido na rubrica
            print(f"\n❌ Erro ao inserir cliente: {e}")

    def listar_todos(self) -> list[Cliente]:
        clientes = []
        try:
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id_cliente, nome, cpf, endereco FROM CLIENTE ORDER BY id_cliente DESC")
                    for linha in cursor.fetchall():
                        clientes.append(Cliente(linha[0], linha[1], linha[2], linha[3]))
        except Exception as e:
            print(f"\n❌ Erro ao listar: {e}")
        return clientes

    def atualizar_endereco(self, id_cliente: int, novo_endereco: str):
        try:
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    query = "UPDATE CLIENTE SET endereco = %s WHERE id_cliente = %s"
                    cursor.execute(query, (novo_endereco, id_cliente))
                    conn.commit()
                    print("\n✅ Morada atualizada com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao atualizar: {e}")

    def excluir(self, id_cliente: int):
        try:
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    query = "DELETE FROM CLIENTE WHERE id_cliente = %s"
                    cursor.execute(query, (id_cliente,))
                    conn.commit()
                    print("\n✅ Registo excluído do sistema!")
        except Exception as e:
            print(f"\n❌ Erro ao excluir: {e}")