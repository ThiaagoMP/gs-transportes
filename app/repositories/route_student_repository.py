import sqlite3
from typing import List
from app.models.route_student import RouteStudent
from app.database import create_connection

class RouteStudentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_student: RouteStudent) -> bool:
        sql = '''INSERT INTO RouteStudent (RouteID, StudentID, StartDate, EndDate) VALUES (?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                values = (route_student.route_id, route_student.student_id, route_student.start_date, route_student.end_date)
                cursor.execute(sql, values)
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao adicionar RouteStudent: {e}")
            finally:
                conn.close()
        return False

    def delete_by_route_id(self, route_id: int) -> bool:
        sql = '''DELETE FROM RouteStudent WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao deletar RouteStudent: {e}")
            finally:
                conn.close()
        return False

    def get_by_route_id(self, route_id: int) -> List[RouteStudent]:
        sql = '''SELECT RouteID, StudentID, StartDate, EndDate FROM RouteStudent WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                rows = cursor.fetchall()
                return [RouteStudent(row[0], row[1], row[2], row[3] if row[3] else None) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar RouteStudent: {e}")
            finally:
                conn.close()
        return []

    def update_end_date(self, route_id: int, student_id: int, end_date: str) -> bool:
        sql = '''UPDATE RouteStudent SET EndDate = ? WHERE RouteID = ? AND StudentID = ? AND EndDate IS NULL'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (end_date, route_id, student_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar EndDate: {e}")
            finally:
                conn.close()
        return False