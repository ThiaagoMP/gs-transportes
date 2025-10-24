import sqlite3
from typing import List, Optional
from app.models.route_extra_payment import RouteExtraPayment
from app.database import create_connection

class RouteExtraPaymentRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route_extra_payment: RouteExtraPayment) -> Optional[int]:
        sql = '''INSERT INTO RouteExtraPayment (RouteID, PaymentDate, Amount, Receipt, Description)
                 VALUES (?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        print(f"Tentando conectar ao banco: {self.db_file}")
        if conn is None:
            print(f"Erro: Falha ao conectar ao banco em {self.db_file}")
            return None
        try:
            cursor = conn.cursor()
            print("Conexão bem-sucedida, criando cursor")
            values = (route_extra_payment.route_id, route_extra_payment.payment_date, route_extra_payment.amount,
                      route_extra_payment.receipt if route_extra_payment.receipt is not None else None,
                      route_extra_payment.description)
            print(f"Tentando inserir: RouteID={values[0]}, PaymentDate={values[1]}, Amount={values[2]}, Receipt={values[3] is None}, Description={values[4]}")
            cursor.execute(sql, values)
            print("Execução da query concluída")
            conn.commit()
            print("Commit realizado")
            last_id = cursor.lastrowid
            print(f"Inserção bem-sucedida, ID: {last_id}")
            return last_id
        except sqlite3.Error as e:
            print(f"Erro ao adicionar pagamento extra: {e} - Valores: {values}")
            return None
        finally:
            print("Fechando conexão")
            conn.close()

    def get_all(self) -> List[RouteExtraPayment]:
        sql = '''SELECT ExtraPaymentID, RouteID, PaymentDate, Amount, Receipt, Description FROM RouteExtraPayment'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [RouteExtraPayment.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar pagamentos extras: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, extra_payment_id: int) -> Optional[RouteExtraPayment]:
        sql = '''SELECT ExtraPaymentID, RouteID, PaymentDate, Amount, Receipt, Description FROM RouteExtraPayment WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (extra_payment_id,))
                row = cursor.fetchone()
                return RouteExtraPayment.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar pagamento extra: {e}")
            finally:
                conn.close()
        return None

    def update(self, route_extra_payment: RouteExtraPayment) -> bool:
        sql = '''UPDATE RouteExtraPayment SET RouteID = ?, PaymentDate = ?, Amount = ?, Receipt = ?, Description = ?
                 WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                values = (route_extra_payment.route_id, route_extra_payment.payment_date, route_extra_payment.amount,
                          route_extra_payment.receipt if route_extra_payment.receipt is not None else None,
                          route_extra_payment.description, route_extra_payment.extra_payment_id)
                cursor.execute(sql, values)
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar pagamento extra: {e}")
            finally:
                conn.close()
        return False

    def delete(self, extra_payment_id: int) -> bool:
        sql = '''DELETE FROM RouteExtraPayment WHERE ExtraPaymentID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (extra_payment_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamento extra: {e}")
            finally:
                conn.close()
        return False

    def delete_by_route_id(self, route_id: int) -> bool:
        sql = '''DELETE FROM RouteExtraPayment WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar pagamentos extras por RouteID: {e}")
            finally:
                conn.close()
        return False