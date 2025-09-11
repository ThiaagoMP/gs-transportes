import sqlite3
from typing import List, Optional
from app.models.student import Student
from app.database import create_connection

class StudentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, student: Student) -> Optional[int]:
        sql = '''INSERT INTO Student (Contact, Address, Name, ExtraInfo, ContractValue, DueDay, RG, CPF)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, student.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar aluno: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Student]:
        sql = '''SELECT * FROM Student'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Student.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar alunos: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, student_id: int) -> Optional[Student]:
        sql = '''SELECT * FROM Student WHERE StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id,))
                row = cursor.fetchone()
                return Student.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar aluno: {e}")
            finally:
                conn.close()
        return None

    def update(self, student: Student) -> bool:
        sql = '''UPDATE Student SET Contact = ?, Address = ?, Name = ?, ExtraInfo = ?, ContractValue = ?, DueDay = ?, RG = ?, CPF = ?
                 WHERE StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*student.to_tuple(), student.student_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar aluno: {e}")
            finally:
                conn.close()
        return False

    def delete(self, student_id: int) -> bool:
        sql = '''DELETE FROM Student WHERE StudentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar aluno: {e}")
            finally:
                conn.close()
        return False