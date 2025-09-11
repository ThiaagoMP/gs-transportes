from datetime import date
from typing import Optional, Tuple

class Refueling:
    def __init__(self, refueling_id: Optional[int], vehicle_id: int, price_per_liter: float, liters: int, km_traveled: float, description: Optional[str], refueling_date: date, receipt: Optional[bytes], fuel_station: str, fuel_type: str):
        self.refueling_id = refueling_id
        self.vehicle_id = vehicle_id
        self.price_per_liter = price_per_liter
        self.liters = liters
        self.km_traveled = km_traveled
        self.description = description
        self.refueling_date = refueling_date
        self.receipt = receipt
        self.fuel_station = fuel_station
        self.fuel_type = fuel_type

    def to_tuple(self) -> Tuple:
        return (self.vehicle_id, self.price_per_liter, self.liters, self.km_traveled, self.description, self.refueling_date, self.receipt, self.fuel_station, self.fuel_type)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Refueling':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])