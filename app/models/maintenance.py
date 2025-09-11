from datetime import date
from typing import Optional, Tuple

class Maintenance:
    def __init__(self, maintenance_id: Optional[int], vehicle_id: int, service_provider: str, start_date: date, end_date: date, description: Optional[str], receipt: Optional[bytes], amount: float, preventive: bool, mileage_at_service: float):
        self.maintenance_id = maintenance_id
        self.vehicle_id = vehicle_id
        self.service_provider = service_provider
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.receipt = receipt
        self.amount = amount
        self.preventive = preventive
        self.mileage_at_service = mileage_at_service

    def to_tuple(self) -> Tuple:
        return (self.vehicle_id, self.service_provider, self.start_date, self.end_date, self.description, self.receipt, self.amount, int(self.preventive), self.mileage_at_service)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Maintenance':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], bool(row[8]), row[9])