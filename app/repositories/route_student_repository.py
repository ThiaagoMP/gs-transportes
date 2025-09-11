import sqlite3
from typing import List, Optional
from models.route_student import RouteStudent
from database import create_connection

class RouteStudentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_student: RouteStudent) -> bool:
        sql = '''INSERT INTO RouteStudent (RouteID, StudentID, StartDate, EndDate)
                 VALUES (?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, route_student.to_tuple())
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao adicionar relação rota-aluno: {e}")
            finally:
                conn.close()
        return False

    def get_all(self) -> List[RouteStudent]:
        sql = '''SELECT * FROM RouteStudent'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [RouteStudent.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar relações rota-aluno: {e}")
            finally:
                conn.close()
        return []

    def get_by_ids(self, route_id: int, student_id: int) -> Optional[RouteStudent]:
        sql = '''SELECT * FROM RouteStudent WHERE RouteID = ? AND StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id, student_id))
                row = cursor.fetchone()
                return RouteStudent.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar relação rota-aluno: {e}")
            finally:
                conn.close()
        return None

    def update(self, route_student: RouteStudent) -> bool:
        sql = '''UPDATE RouteStudent SET StartDate = ?, EndDate = ?
                 WHERE RouteID = ? AND StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_student.start_date, route_student.end_date, route_student.route_id, route_student.student_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar relação rota-aluno: {e}")
            finally:
                conn.close()
        return False

    def delete(self, route_id: int, student_id: int) -> bool:
        sql = '''DELETE FROM RouteStudent WHERE RouteID = ? AND StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id, student_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar relação rota-aluno: {e}")
            finally:
                conn.close()
        return False