import sqlite3
from typing import List, Optional
from app.models.driver_bonus import DriverBonus
from app.database import create_connection

class DriverBonusRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, bonus: DriverBonus) -> Optional[int]:
        sql = '''INSERT INTO DriverBonus (DriverID, Description, Receipt, BonusDate, Amount)
                 VALUES (?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                values = (bonus.driver_id, bonus.description, sqlite3.Binary(bonus.receipt) if bonus.receipt else None, bonus.bonus_date, bonus.amount)
                cursor.execute(sql, values)
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar bônus: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[DriverBonus]:
        sql = '''SELECT * FROM DriverBonus'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [DriverBonus.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar bônus: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, bonus_id: int) -> Optional[DriverBonus]:
        sql = '''SELECT * FROM DriverBonus WHERE BonusID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (bonus_id,))
                row = cursor.fetchone()
                return DriverBonus.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar bônus: {e}")
            finally:
                conn.close()
        return None

    def update(self, bonus: DriverBonus) -> bool:
        sql = '''UPDATE DriverBonus SET DriverID = ?, Description = ?, Receipt = ?, BonusDate = ?, Amount = ?
                 WHERE BonusID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*bonus.to_tuple(), bonus.bonus_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar bônus: {e}")
            finally:
                conn.close()
        return False

    def delete(self, bonus_id: int) -> bool:
        sql = '''DELETE FROM DriverBonus WHERE BonusID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (bonus_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar bônus: {e}")
            finally:
                conn.close()
        return False

    def delete_by_driver_id(self, driver_id: int) -> bool:
        sql = '''DELETE FROM DriverBonus WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (driver_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar bônus por DriverID: {e}")
            finally:
                conn.close()
        return False