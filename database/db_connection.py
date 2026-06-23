import psycopg2
import os

class DatabaseConnection:
    def __init__(self):
        # Atributos encapsulados com as credenciais do banco.
        # ATENÇÃO: Altere os valores abaixo conforme o seu PostgreSQL local.
        self.__host = "localhost"
        self.__database = "otica_mais"
        self.__user = "postgres"
        self.__password = "sua_senha_aqui"  # Insira a senha que você usa no pgAdmin
        self.__port = "5432"
        self.__conexao = None

    def obter_conexao(self):
        """Estabelece e retorna a conexão ativa com o banco de dados."""
        if self.__conexao is None or self.__conexao.closed != 0:
            try:
                self.__conexao = psycopg2.connect(
                    host=self.__host,
                    database=self.__database,
                    user=self.__user,
                    password=self.__password,
                    port=self.__port
                )
            except psycopg2.Error as erro:
                print(f"Erro fatal: Não foi possível conectar ao PostgreSQL. Detalhes: {erro}")
                raise
        return self.__conexao

    def fechar_conexao(self):
        """Encerra a conexão com o banco de dados de forma segura."""
        if self.__conexao is not None and self.__conexao.closed == 0:
            self.__conexao.close()

    def inicializar_banco(self):
        """
        Lê e executa o arquivo schema.sql automaticamente.
        Útil para criar as tabelas na primeira vez que o sistema rodar.
        """
        conexao = self.obter_conexao()
        # Localiza dinamicamente o arquivo schema.sql na mesma pasta deste script
        caminho_schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        try:
            with conexao.cursor() as cursor:
                with open(caminho_schema, 'r', encoding='utf-8') as arquivo_sql:
                    sql_script = arquivo_sql.read()
                    cursor.execute(sql_script)
            
            # Confirma a transação
            conexao.commit()
            print("Sucesso: Banco de dados inicializado e tabelas criadas!")
        except Exception as erro:
            # Em caso de erro, desfaz qualquer alteração pela metade
            conexao.rollback()
            print(f"Aviso: Erro ao executar o schema.sql (as tabelas já podem existir). Detalhes: {erro}")
        finally:
            self.fechar_conexao()