import sqlite3
from typing import List, Optional
from models.route_driver import RouteDriver
from database import create_connection

class RouteDriverRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_driver: RouteDriver) -> bool:
        sql = '''INSERT INTO RouteDriver (RouteID, DriverID)
                 VALUES (?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, route_driver.to_tuple())
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao adicionar relação rota-motorista: {e}")
            finally:
                conn.close()
        return False

    def get_all(self) -> List[RouteDriver]:
        sql = '''SELECT * FROM RouteDriver'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [RouteDriver.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar relações rota-motorista: {e}")
            finally:
                conn.close()
        return []

    def get_by_ids(self, route_id: int, driver_id: int) -> Optional[RouteDriver]:
        sql = '''SELECT * FROM RouteDriver WHERE RouteID = ? AND DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id, driver_id))
                row = cursor.fetchone()
                return RouteDriver.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar relação rota-motorista: {e}")
            finally:
                conn.close()
        return None

    def update(self, route_driver: RouteDriver) -> bool:
        return False  # Não há campos para atualizar, apenas chaves primárias

    def delete(self, route_id: int, driver_id: int) -> bool:
        sql = '''DELETE FROM RouteDriver WHERE RouteID = ? AND DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id, driver_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar relação rota-motorista: {e}")
            finally:
                conn.close()
        return False