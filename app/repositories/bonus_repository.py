import sqlite3
from typing import List, Optional
from models.bonus import Bonus
from database import create_connection

class BonusRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, bonus_tuple: tuple) -> Optional[int]:
        sql = '''INSERT INTO Bonus (DriverID, Description, Receipt, BonusDate, Amount)
                    VALUES (?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, bonus_tuple)
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar bônus: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Bonus]:
        sql = '''SELECT * FROM Bonus'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Bonus.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar bônus: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, bonus_id: int) -> Optional[Bonus]:
        sql = '''SELECT * FROM Bonus WHERE BonusID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (bonus_id,))
                row = cursor.fetchone()
                return Bonus.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar bônus: {e}")
            finally:
                conn.close()
        return None

    def update(self, bonus: Bonus) -> bool:
        sql = '''UPDATE Bonus SET DriverID = ?, Description = ?, Receipt = ?, BonusDate = ?, Amount = ?
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
        sql = '''DELETE FROM Bonus WHERE BonusID = ?'''
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
        sql = '''DELETE FROM Bonus WHERE DriverID = ?'''
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