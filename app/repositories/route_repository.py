import sqlite3
from typing import List, Optional
from app.models.route import Route
from app.database import create_connection

class RouteRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route: Route) -> Optional[int]:
        sql = '''INSERT INTO Route (VehicleID, AvgKm, Period, AvgTimeMinutes, Name, Active)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, route.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar rota: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Route]:
        sql = '''SELECT * FROM Route'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Route.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar rotas: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, route_id: int) -> Optional[Route]:
        sql = '''SELECT * FROM Route WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                row = cursor.fetchone()
                return Route.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar rota: {e}")
            finally:
                conn.close()
        return None

    def update(self, route: Route) -> bool:
        sql = '''UPDATE Route SET VehicleID = ?, AvgKm = ?, Period = ?, AvgTimeMinutes = ?, Name = ?, Active = ?
                 WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*route.to_tuple(), route.route_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar rota: {e}")
            finally:
                conn.close()
        return False

    def delete(self, route_id: int) -> bool:
        sql = '''DELETE FROM Route WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar rota: {e}")
            finally:
                conn.close()
        return False