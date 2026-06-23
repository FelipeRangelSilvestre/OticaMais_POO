"""
Ponto de entrada do sistema Ótica Mais.

Para executar:
    python main.py

Na primeira execução, o sistema tenta criar as tabelas automaticamente
a partir de database/schema.sql (se ainda não existirem).
"""

from database.db_connection import DatabaseConnection
from ui.menu import menu_principal

if __name__ == "__main__":
    DatabaseConnection().inicializar_banco()
    menu_principal()
