from typing import Optional, Tuple
from datetime import date

class ExtraPayment:
    def __init__(self, extra_payment_id: Optional[int], route_id: int, payment_date: date, amount: float, receipt: Optional[bytes], description: Optional[str]):
        self.extra_payment_id = extra_payment_id
        self.route_id = route_id
        self.payment_date = payment_date
        self.amount = amount
        self.receipt = receipt
        self.description = description

    def to_tuple(self) -> Tuple:
        return (self.route_id, self.payment_date, self.amount, self.receipt, self.description)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'ExtraPayment':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5])