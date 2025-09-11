from typing import Optional, Tuple
from datetime import date

class StudentPayment:
    def __init__(self, student_payment_id: Optional[int], student_id: int, receipt: Optional[bytes], payment_date: date, amount: float, paid: bool, extra_info: Optional[str] = None):
        self.student_payment_id = student_payment_id
        self.student_id = student_id
        self.receipt = receipt
        self.payment_date = payment_date
        self.amount = amount
        self.paid = paid
        self.extra_info = extra_info

    def to_tuple(self) -> Tuple:
        return self.student_id, self.receipt, self.payment_date, self.amount, int(self.paid), self.extra_info

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'StudentPayment':
        return cls(row[0], row[1], row[2], row[3], row[4], bool(row[5]), row[6] if row[6] else None)