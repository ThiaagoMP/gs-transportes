import os
import sys
import sqlite3
import tkinter as tk

from app.database import create_connection
from app.interface.interface_principal import InterfacePrincipal


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


def get_database_path(db_name):
    base_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "GS-Transportes"
    )
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, db_name)


def initialize_database(db_file, sql_file):
    db_path = get_database_path(db_file)
    sql_path = resource_path(os.path.join("database", "scripts", sql_file))

    conn = create_connection(db_path)
    if conn:
        try:
            cursor = conn.cursor()
            if not os.path.exists(db_path) or os.stat(db_path).st_size == 0:
                with open(sql_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                cursor.executescript(sql_script)
                conn.commit()
        except sqlite3.Error:
            pass
        except FileNotFoundError:
            pass
        finally:
            conn.close()


def main():
    db_file = "gs_transportes.db"
    sql_file = "create_tables.sql"

    initialize_database(db_file, sql_file)

    root = tk.Tk()

    scale = root.winfo_fpixels("1i") / 72
    root.tk.call("tk", "scaling", scale)
    app = InterfacePrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
