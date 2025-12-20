import os
import sqlite3
import tkinter as tk

from app.database import create_connection
from app.interface.interface_principal import InterfacePrincipal

def initialize_database(db_file, sql_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    db_path = os.path.join(parent_dir, 'database', 'data', os.path.basename(db_file))
    sql_path = os.path.join(parent_dir, 'database', 'scripts', sql_file)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = create_connection(db_path)
    if conn:
        try:
            cursor = conn.cursor()
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print("Banco de dados inicializado com sucesso em {}".format(db_path))
        except sqlite3.Error as e:
            print("Erro ao inicializar o banco de dados: {}".format(e))
            print("Verifique o conteúdo do arquivo SQL para erros de sintaxe.")
        except FileNotFoundError:
            print("Arquivo SQL {} não encontrado".format(sql_path))
        finally:
            conn.close()
    else:
        print("Falha ao conectar ao banco de dados")


def main():
    db_file = "gs_transportes.db"
    sql_file = "create_tables.sql"

    initialize_database(db_file, sql_file)

    root = tk.Tk()
    app = InterfacePrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()
