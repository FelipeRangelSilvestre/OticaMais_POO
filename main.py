"""
Ponto de entrada do sistema Ótica Mais — Versão Desktop (GUI).
"""

from database.db_connection import DatabaseConnection
from ui.sistema_gui import OticaMaisGUI

if __name__ == "__main__":
    # Garante a inicialização das tabelas relacionais do schema.sql no PostgreSQL
    DatabaseConnection().inicializar_banco()
    
    # Instancia e roda a interface gráfica Tkinter
    app = OticaMaisGUI()
    app.mainloop()