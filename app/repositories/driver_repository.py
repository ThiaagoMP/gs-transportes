import sqlite3
from typing import List, Optional
from app.models.driver import Driver
from app.database import create_connection

class DriverRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def create(self, driver: Driver) -> Optional[int]:
        sql = '''INSERT INTO Driver (Name, Salary, Contact, StartDate, EndDate, CPF, RG, CNH, ExtraInfo)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, driver.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar motorista: {e}")
                raise
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Driver]:
        sql = '''SELECT * FROM Driver'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Driver.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar motoristas: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        sql = '''SELECT * FROM Driver WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (driver_id,))
                row = cursor.fetchone()
                return Driver.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar motorista: {e}")
            finally:
                conn.close()
        return None

    def update(self, driver: Driver) -> bool:
        sql = '''UPDATE Driver \
                 SET Name      = ?, \
                     Salary    = ?, \
                     Contact   = ?, \
                     StartDate = ?, \
                     EndDate   = ?, \
                     CPF       = ?, \
                     RG        = ?, \
                     CNH       = ?, \
                     ExtraInfo = ?
                 WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                to_tuple = driver.to_tuple()
                cursor.execute(sql, (*to_tuple, driver.driver_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar motorista: {e}")
            finally:
                conn.close()
        return False

    def delete(self, driver_id: int) -> bool:
        sql = '''DELETE FROM Driver WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (driver_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar motorista: {e}")
            finally:
                conn.close()
        return False