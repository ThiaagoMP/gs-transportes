import sqlite3
from typing import Optional, List
from app.database import create_connection
from app.models.route_driver import RouteDriver

class RouteDriverRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_driver: RouteDriver) -> Optional[int]:
        sql = '''INSERT INTO RouteDriver (RouteID, DriverID)
                 VALUES (?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_driver.route_id, route_driver.driver_id))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar motorista à linha: {e}")
            finally:
                conn.close()
        return None

    def get_by_route_id(self, route_id: int) -> List[RouteDriver]:
        sql = '''SELECT RouteID, DriverID FROM RouteDriver WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                rows = cursor.fetchall()
                return [RouteDriver(row[0], row[1]) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao buscar motoristas: {e}")
            finally:
                conn.close()
        return []

    def delete_by_route_id(self, route_id: int) -> bool:
        sql = '''DELETE FROM RouteDriver WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar associações: {e}")
            finally:
                conn.close()
        return False