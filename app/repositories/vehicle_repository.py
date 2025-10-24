import sqlite3
from typing import List, Optional

from app.database import create_connection
from app.models.vehicle import Vehicle

class VehicleRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, vehicle: Vehicle) -> Optional[int]:
        sql = '''INSERT INTO Vehicle (AvgKmPerLiter, LicensePlate, Seats, FuelTankSize, Name, BuyDate, SellDate, PurchaseValue, SaleValue, ManufacturingYear)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                tuple_data = vehicle.to_tuple()
                expected_length = 10
                if len(tuple_data) != expected_length:
                    print(f"ERRO: Número incorreto de valores no tuple. Esperado {expected_length}, recebido {len(tuple_data)}: {tuple_data}")
                    return None
                cursor.execute(sql, tuple_data)
                conn.commit()
                last_id = cursor.lastrowid
                return last_id
            except sqlite3.Error as e:
                print(f"ERRO ao adicionar veículo: {e}")
                return None
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Vehicle]:
        sql = '''SELECT * FROM Vehicle'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Vehicle.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar veículos: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        sql = '''SELECT * FROM Vehicle WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                row = cursor.fetchone()
                return Vehicle.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar veículo: {e}")
            finally:
                conn.close()
        return None

    def update(self, vehicle: Vehicle) -> bool:
        sql = '''UPDATE Vehicle SET AvgKmPerLiter = ?, LicensePlate = ?, Seats = ?, FuelTankSize = ?, Name = ?, BuyDate = ?, SellDate = ?, PurchaseValue = ?, SaleValue = ?, ManufacturingYear = ?
                 WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*vehicle.to_tuple(), vehicle.vehicle_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar veículo: {e}")
            finally:
                conn.close()
        return False

    def delete(self, vehicle_id: int) -> bool:
        sql = '''DELETE FROM Vehicle WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar veículo: {e}")
            finally:
                conn.close()
        return False