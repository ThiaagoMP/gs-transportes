import sqlite3
from typing import List, Optional
from app.models.route_expense_payment import RouteExpensePayment
from app.database import create_connection

class RouteExpensePaymentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_expense_payment: RouteExpensePayment) -> Optional[int]:
        sql = '''INSERT INTO RouteExpensePayment (RouteID, PaymentDate, Amount, Receipt, Description)
                 VALUES (?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn is None:
            print(f"Erro: Falha ao conectar ao banco em {self.db_file}")
            return None
        try:
            cursor = conn.cursor()
            values = (route_expense_payment.route_id, route_expense_payment.payment_date, route_expense_payment.amount,
                      route_expense_payment.receipt if route_expense_payment.receipt is not None else None,
                      route_expense_payment.description)
            print(f"Tentando inserir: RouteID={values[0]}, PaymentDate={values[1]}, Amount={values[2]}, Receipt={values[3] is None}, Description={values[4]}")
            cursor.execute(sql, values)
            conn.commit()
            print("Commit realizado")
            last_id = cursor.lastrowid
            print(f"Inserção bem-sucedida, ID: {last_id}")
            return last_id
        except sqlite3.Error as e:
            print(f"Erro ao adicionar pagamento de despesa: {e} - Valores: {values}")
            return None
        finally:
            conn.close()

    def get_all(self) -> List[RouteExpensePayment]:
        sql = '''SELECT ExpensePaymentID, RouteID, PaymentDate, Amount, Receipt, Description FROM RouteExpensePayment'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [RouteExpensePayment.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar pagamentos de despesa: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, expense_payment_id: int) -> Optional[RouteExpensePayment]:
        sql = '''SELECT ExpensePaymentID, RouteID, PaymentDate, Amount, Receipt, Description FROM RouteExpensePayment WHERE ExpensePaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (expense_payment_id,))
                row = cursor.fetchone()
                return RouteExpensePayment.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar pagamento de despesa: {e}")
            finally:
                conn.close()
        return None

    def update(self, route_expense_payment: RouteExpensePayment) -> bool:
        sql = '''UPDATE RouteExpensePayment SET RouteID = ?, PaymentDate = ?, Amount = ?, Receipt = ?, Description = ?
                 WHERE ExpensePaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                values = (route_expense_payment.route_id, route_expense_payment.payment_date, route_expense_payment.amount,
                          route_expense_payment.receipt if route_expense_payment.receipt is not None else None,
                          route_expense_payment.description, route_expense_payment.expense_payment_id)
                cursor.execute(sql, values)
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar pagamento de despesa: {e}")
            finally:
                conn.close()
        return False

    def delete(self, expense_payment_id: int) -> bool:
        sql = '''DELETE FROM RouteExpensePayment WHERE ExpensePaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (expense_payment_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamento de despesa: {e}")
            finally:
                conn.close()
        return False

    def delete_by_route_id(self, route_id: int) -> bool:
        sql = '''DELETE FROM RouteExpensePayment WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamentos de despesa por RouteID: {e}")
            finally:
                conn.close()
        return False