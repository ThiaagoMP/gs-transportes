import sqlite3
from typing import List
from app.models.route_student import RouteStudent
from app.database import create_connection

class RouteStudentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add_student_to_route(self, route_id: int, student_id: int) -> bool:
        from datetime import datetime
        start_date = datetime.now().strftime('%Y-%m-%d')
        route_student = RouteStudent(route_id, student_id, start_date, None)
        return self.add(route_student)

    def get_by_student_id(self, student_id: int) -> List[RouteStudent]:
        sql = '''SELECT RouteID, StudentID, StartDate, EndDate
                 FROM RouteStudent
                 WHERE StudentID = ? AND EndDate IS NULL'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id,))
                rows = cursor.fetchall()
                return [RouteStudent(row[0], row[1], row[2], row[3] if row[3] else None) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar RouteStudent por StudentID: {e}")
            finally:
                conn.close()
        return []

    def count_students_in_route(self, route_id: int) -> int:
        try:
            conn = create_connection(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM RouteStudent
                           WHERE RouteID = ?
                           """, (route_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Erro ao contar alunos da rota: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def add(self, route_student: RouteStudent) -> bool:
        sql = '''INSERT INTO RouteStudent (RouteID, StudentID, StartDate, EndDate)
                 VALUES (?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                values = (route_student.route_id, route_student.student_id, route_student.start_date,
                          route_student.end_date)
                cursor.execute(sql, values)
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao adicionar RouteStudent: {e}")
            finally:
                conn.close()
        return False

    def delete_by_route_id(self, route_id: int) -> bool:
        sql = '''DELETE
                 FROM RouteStudent
                 WHERE RouteID = ?'''
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

    def delete_by_student_id(self, student_id: int, route_id: int) -> bool:
        sql = '''DELETE
                 FROM RouteStudent
                 WHERE StudentID = ?
                   AND RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id, route_id))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao deletar RouteStudent: {e}")
            finally:
                conn.close()
        return False

    def get_students_by_route_id(self, route_id: int) -> List[RouteStudent]:
        sql = '''SELECT RouteID, StudentID, StartDate, EndDate
                 FROM RouteStudent
                 WHERE RouteID = ? AND EndDate IS NULL'''
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

    def update_end_date(self, route_id: int, student_id: int, end_date) -> bool:
        sql = '''UPDATE RouteStudent
                 SET EndDate = ?
                 WHERE RouteID = ?
                   AND StudentID = ?;'''
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
