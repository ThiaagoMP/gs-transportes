import sqlite3
from typing import List, Optional
from app.models.student_payment import StudentPayment
from app.database import create_connection

class StudentPaymentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, payment: StudentPayment) -> Optional[int]:
        sql = '''INSERT INTO StudentPayment (StudentID, Receipt, PaymentDate, Amount, Paid, ExtraInfo)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, payment.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar pagamento de aluno: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[StudentPayment]:
        sql = '''SELECT * FROM StudentPayment'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [StudentPayment.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar pagamentos de aluno: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, payment_id: int) -> Optional[StudentPayment]:
        sql = '''SELECT * FROM StudentPayment WHERE StudentPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (payment_id,))
                row = cursor.fetchone()
                return StudentPayment.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar pagamento de aluno: {e}")
            finally:
                conn.close()
        return None

    def update(self, payment: StudentPayment) -> bool:
        sql = '''UPDATE StudentPayment SET StudentID = ?, Receipt = ?, PaymentDate = ?, Amount = ?, Paid = ?, ExtraInfo = ?
                 WHERE StudentPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*payment.to_tuple(), payment.student_payment_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar pagamento de aluno: {e}")
            finally:
                conn.close()
        return False

    def delete(self, payment_id: int) -> bool:
        sql = '''DELETE FROM StudentPayment WHERE StudentPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (payment_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamento de aluno: {e}")
            finally:
                conn.close()
        return False