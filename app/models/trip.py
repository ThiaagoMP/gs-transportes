from typing import Optional, Tuple
from datetime import date

class Trip:
    def __init__(self, trip_id: Optional[int], vehicle_id: int, additional_expenses: float, total_km: float, passenger_fare: float, passenger_count: int, start_date: date, end_date: date, description: Optional[str]):
        self.trip_id = trip_id
        self.vehicle_id = vehicle_id
        self.additional_expenses = additional_expenses
        self.total_km = total_km
        self.passenger_fare = passenger_fare
        self.passenger_count = passenger_count
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

    def to_tuple(self) -> Tuple:
        return (self.vehicle_id, self.additional_expenses, self.total_km, self.passenger_fare, self.passenger_count, self.start_date, self.end_date, self.description)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Trip':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])