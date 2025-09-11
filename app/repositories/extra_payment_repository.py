import sqlite3
from typing import List, Optional
from models.extra_payment import ExtraPayment
from database import create_connection

class ExtraPaymentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, payment: ExtraPayment) -> Optional[int]:
        sql = '''INSERT INTO ExtraPayment (RouteID, PaymentDate, Amount, Receipt, Description)
                 VALUES (?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, payment.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar pagamento extra: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[ExtraPayment]:
        sql = '''SELECT * FROM ExtraPayment'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [ExtraPayment.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar pagamentos extras: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, payment_id: int) -> Optional[ExtraPayment]:
        sql = '''SELECT * FROM ExtraPayment WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (payment_id,))
                row = cursor.fetchone()
                return ExtraPayment.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar pagamento extra: {e}")
            finally:
                conn.close()
        return None

    def update(self, payment: ExtraPayment) -> bool:
        sql = '''UPDATE ExtraPayment SET RouteID = ?, PaymentDate = ?, Amount = ?, Receipt = ?, Description = ?
                 WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*payment.to_tuple(), payment.extra_payment_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar pagamento extra: {e}")
            finally:
                conn.close()
        return False

    def delete(self, payment_id: int) -> bool:
        sql = '''DELETE FROM ExtraPayment WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (payment_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamento extra: {e}")
            finally:
                conn.close()
        return False