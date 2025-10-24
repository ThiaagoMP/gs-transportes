from typing import Optional, Tuple
from datetime import date

class DriverBonus:
    def __init__(self, bonus_id: Optional[int], driver_id: int, description: Optional[str], receipt: Optional[bytes], bonus_date: date, amount: float):
        self.bonus_id = bonus_id
        self.driver_id = driver_id
        self.description = description
        self.receipt = receipt
        self.bonus_date = bonus_date
        self.amount = amount

    def to_tuple(self) -> Tuple:
        return self.driver_id, self.description, self.receipt, self.bonus_date, self.amount

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'DriverBonus':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5])