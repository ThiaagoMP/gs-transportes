import sqlite3
from typing import List, Optional
from app.models.refueling import Refueling
from app.database import create_connection


class RefuelingRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, refueling: Refueling) -> Optional[int]:
        sql = '''INSERT INTO Refueling (VehicleID, PricePerLiter, Liters, KmTraveled, Description, RefuelingDate,
                                        Receipt, GasStation, FuelType)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, refueling.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar abastecimento: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Refueling]:
        sql = '''SELECT *
                 FROM Refueling'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Refueling.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar abastecimentos: {e}")
            finally:
                conn.close()
        return []

    def get_all_by_vehicle_id(self, vehicle_id: int) -> List[Refueling]:
        sql = '''SELECT * \
                 FROM Refueling \
                 WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                rows = cursor.fetchall()
                return [Refueling.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar abastecimentos por veículo: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, refueling_id: int) -> Optional[Refueling]:
        sql = '''SELECT *
                 FROM Refueling
                 WHERE RefuelingID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (refueling_id,))
                row = cursor.fetchone()
                return Refueling.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar abastecimento: {e}")
            finally:
                conn.close()
        return None

    def update(self, refueling: Refueling) -> bool:
        sql = '''UPDATE Refueling
                 SET VehicleID     = ?,
                     PricePerLiter = ?,
                     Liters        = ?,
                     KmTraveled    = ?,
                     GasStation    = ?,
                     FuelType      = ?,
                     Description   = ?,
                     RefuelingDate = ?,
                     Receipt       = ?
                 WHERE RefuelingID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*refueling.to_tuple(), refueling.refueling_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar abastecimento: {e}")
            finally:
                conn.close()
        return False

    def delete(self, refueling_id: int) -> bool:
        sql = '''DELETE
                 FROM Refueling
                 WHERE RefuelingID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (refueling_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar abastecimento: {e}")
            finally:
                conn.close()
        return False
