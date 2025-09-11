from typing import Optional, Tuple

class Student:
    def __init__(self, student_id: Optional[int], contact: str, address: str, name: str, extra_info: Optional[str], contract_value: float, due_day: int, rg: str, cpf: str):
        self.student_id = student_id
        self.contact = contact
        self.address = address
        self.name = name
        self.extra_info = extra_info
        self.contract_value = contract_value
        self.due_day = due_day
        self.rg = rg
        self.cpf = cpf

    def to_tuple(self) -> Tuple:
        return self.contact, self.address, self.name, self.extra_info, self.contract_value, self.due_day, self.rg, self.cpf

    @classmethod
    def from_db_row(cls, row: Tuple) -> 'Student':
        return cls(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])