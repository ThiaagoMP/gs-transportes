from typing import Optional, Tuple

class Driver:
    def __init__(self, driver_id: Optional[int], name: str, salary: float, contact: str, start_date: str, end_date: Optional[str], cpf: str, rg: str, cnh: str, extra_info: Optional[str]):
        self.driver_id = driver_id
        self.name = name
        self.salary = salary
        self.contact = contact
        self.start_date = start_date
        self.end_date = end_date
        self.cpf = cpf
        self.rg = rg
        self.cnh = cnh
        self.extra_info = extra_info

    def to_tuple(self) -> Tuple:
        return self.name, self.salary, self.contact, self.start_date, self.end_date, self.cpf, self.rg, self.cnh, self.extra_info

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Driver':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])