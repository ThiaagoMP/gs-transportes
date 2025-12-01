import sqlite3
from datetime import datetime
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

    def count_by_vehicle(self, vehicle_id: int, period: str = "total") -> int:
        base_sql = "SELECT COUNT(*) FROM Maintenance WHERE VehicleID = ?"
        params = [vehicle_id]

        if period == "year":
            base_sql += " AND strftime('%Y', StartDate) = ?"
            params.append(datetime.now().strftime("%Y"))
        elif period == "month":
            base_sql += " AND strftime('%Y-%m', StartDate) = ?"
            params.append(datetime.now().strftime("%Y-%m"))

        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(base_sql, params)
                result = cursor.fetchone()
                return result[0] if result else 0
            except sqlite3.Error as e:
                print(f"Erro ao contar manutenções do veículo: {e}")
            finally:
                conn.close()
        return 0

    def sum_cost_by_vehicle(self, vehicle_id: int, period: str = "total") -> float:
        conn = create_connection(self.db_file)
        if not conn:
            return 0.0

        try:
            cursor = conn.cursor()

            date_filter = ""
            if period == "year":
                date_filter = "AND strftime('%Y', Maintenance.StartDate) = strftime('%Y', 'now')"
            elif period == "month":
                date_filter = "AND strftime('%Y-%m', Maintenance.StartDate) = strftime('%Y-%m', 'now')"

            cursor.execute(
                "SELECT COALESCE(SUM(Maintenance.Amount), 0) FROM Maintenance WHERE VehicleID = ? " + date_filter,
                (vehicle_id,)
            )
            result = cursor.fetchone()[0]
            return round(result or 0.0, 2)
        except Exception as e:
            print("Erro ao somar valor de manutenções:", e)
            return 0.0
        finally:
            conn.close()

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