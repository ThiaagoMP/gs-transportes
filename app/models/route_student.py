from typing import Optional, Tuple
from datetime import date

class RouteStudent:
    def __init__(self, route_id: int, student_id: int, start_date: date, end_date: Optional[date]):
        self.route_id = route_id
        self.student_id = student_id
        self.start_date = start_date
        self.end_date = end_date

    def to_tuple(self) -> Tuple:
        return (self.route_id, self.student_id, self.start_date, self.end_date)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'RouteStudent':
        return cls(row[0], row[1], row[2], row[3])