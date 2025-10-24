import sqlite3
from typing import List, Optional
from app.models.trip import Trip
from app.database import create_connection

class TripRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, trip: Trip) -> Optional[int]:
        sql = '''INSERT INTO Trip (VehicleID, AdditionalExpenses, TotalKm, PassengerFare, PassengerCount, StartDate, EndDate, Description)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, trip.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar viagem: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Trip]:
        sql = '''SELECT * FROM Trip'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Trip.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar viagens: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        sql = '''SELECT * FROM Trip WHERE TripID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (trip_id,))
                row = cursor.fetchone()
                return Trip.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar viagem: {e}")
            finally:
                conn.close()
        return None

    def update(self, trip: Trip) -> bool:
        sql = '''UPDATE Trip SET VehicleID = ?, AdditionalExpenses = ?, TotalKm = ?, PassengerFare = ?, PassengerCount = ?, StartDate = ?, EndDate = ?, Description = ?
                 WHERE TripID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*trip.to_tuple(), trip.trip_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar viagem: {e}")
            finally:
                conn.close()
        return False

    def delete(self, trip_id: int) -> bool:
        sql = '''DELETE FROM Trip WHERE TripID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (trip_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar viagem: {e}")
            finally:
                conn.close()
        return False