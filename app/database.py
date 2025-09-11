import sqlite3
from typing import Optional

def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None