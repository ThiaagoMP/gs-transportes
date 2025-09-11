import sqlite3
from typing import List, Optional
from models.trip_driver import TripDriver
from database import create_connection

class TripDriverRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, trip_driver: TripDriver) -> bool:
        sql = '''INSERT INTO TripDriver (TripID, DriverID)
                 VALUES (?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, trip_driver.to_tuple())
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Erro ao adicionar relação viagem-motorista: {e}")
            finally:
                conn.close()
        return False

    def get_all(self) -> List[TripDriver]:
        sql = '''SELECT * FROM TripDriver'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [TripDriver.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar relações viagem-motorista: {e}")
            finally:
                conn.close()
        return []

    def get_by_ids(self, trip_id: int, driver_id: int) -> Optional[TripDriver]:
        sql = '''SELECT * FROM TripDriver WHERE TripID = ? AND DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (trip_id, driver_id))
                row = cursor.fetchone()
                return TripDriver.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar relação viagem-motorista: {e}")
            finally:
                conn.close()
        return None

    def update(self, trip_driver: TripDriver) -> bool:
        return False  # Não há campos para atualizar, apenas chaves primárias

    def delete(self, trip_id: int, driver_id: int) -> bool:
        sql = '''DELETE FROM TripDriver WHERE TripID = ? AND DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (trip_id, driver_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar relação viagem-motorista: {e}")
            finally:
                conn.close()
        return False