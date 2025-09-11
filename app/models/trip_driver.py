from typing import Tuple

class TripDriver:
    def __init__(self, trip_id: int, driver_id: int):
        self.trip_id = trip_id
        self.driver_id = driver_id

    def to_tuple(self) -> Tuple:
        return (self.trip_id, self.driver_id)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'TripDriver':
        return cls(row[0], row[1])