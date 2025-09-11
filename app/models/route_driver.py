from typing import Tuple

class RouteDriver:
    def __init__(self, route_id: int, driver_id: int):
        self.route_id = route_id
        self.driver_id = driver_id

    def to_tuple(self) -> Tuple:
        return (self.route_id, self.driver_id)

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'RouteDriver':
        return cls(row[0], row[1])