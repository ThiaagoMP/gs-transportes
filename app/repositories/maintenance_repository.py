import sqlite3
from typing import List, Optional
from app.models.maintenance import Maintenance
from app.database import create_connection

class MaintenanceRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, maintenance: Maintenance) -> Optional[int]:
        sql = '''INSERT INTO Maintenance (VehicleID, ServiceProvider, StartDate, EndDate, Description, Receipt, Amount, Preventive, MileageAtService)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, maintenance.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar manutenção: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Maintenance]:
        sql = '''SELECT * FROM Maintenance'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Maintenance.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar manutenções: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, maintenance_id: int) -> Optional[Maintenance]:
        sql = '''SELECT * FROM Maintenance WHERE MaintenanceID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (maintenance_id,))
                row = cursor.fetchone()
                return Maintenance.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar manutenção: {e}")
            finally:
                conn.close()
        return None

    def update(self, maintenance: Maintenance) -> bool:
        sql = '''UPDATE Maintenance SET VehicleID = ?, ServiceProvider = ?, StartDate = ?, EndDate = ?, Description = ?, Receipt = ?, Amount = ?, Preventive = ?, MileageAtService = ?
                 WHERE MaintenanceID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*maintenance.to_tuple(), maintenance.maintenance_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar manutenção: {e}")
            finally:
                conn.close()
        return False

    def delete(self, maintenance_id: int) -> bool:
        sql = '''DELETE FROM Maintenance WHERE MaintenanceID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (maintenance_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar manutenção: {e}")
            finally:
                conn.close()
        return False