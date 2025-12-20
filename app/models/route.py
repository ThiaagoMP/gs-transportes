from typing import Optional, Tuple

class Route:
    def __init__(
        self,
        route_id: Optional[int],
        vehicle_id: int,
        avg_km: float,
        period: str,
        avg_time_minutes: int,
        name: str,
        active: bool,
        contract_value: float
    ):
        self.route_id = route_id
        self.vehicle_id = vehicle_id
        self.avg_km = avg_km
        self.period = period
        self.avg_time_minutes = avg_time_minutes
        self.name = name
        self.active = active
        self.contract_value = contract_value

    def to_tuple(self) -> Tuple:
        return (
            self.vehicle_id,
            self.avg_km,
            self.period,
            self.avg_time_minutes,
            self.name,
            int(self.active),
            self.contract_value
        )

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Route':
        return cls(
            route_id=row[0],
            vehicle_id=row[1],
            avg_km=row[2],
            contract_value=row[3],
            period=row[4],
            avg_time_minutes=row[5],
            name=row[6],
            active=bool(row[7]),

        )
