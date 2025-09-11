from typing import Optional, Tuple

class Route:
    def __init__(self, route_id: Optional[int], vehicle_id: int, avg_km: float, period: str, avg_time_minutes: int, name: str, active: bool):
        self.route_id = route_id
        self.vehicle_id = vehicle_id
        self.avg_km = avg_km
        self.period = period
        self.avg_time_minutes = avg_time_minutes
        self.name = name
        self.active = active

    def to_tuple(self) -> Tuple:
        return (self.vehicle_id, self.avg_km, self.period, self.avg_time_minutes, self.name, int(self.active))

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Route':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))