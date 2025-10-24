from typing import Optional

class RouteExpensePayment:
    def __init__(self, expense_payment_id: Optional[int], route_id: int, payment_date: str, amount: float, receipt: bytes, description: str):
        self.expense_payment_id = expense_payment_id
        self.route_id = route_id
        self.payment_date = payment_date
        self.amount = amount
        self.receipt = receipt
        self.description = description

    @classmethod
    def from_db_row(cls, row):
        if row is None:
            return None
        return cls(row[0], row[1], row[2], row[3], row[4], row[5] if row[5] else "")