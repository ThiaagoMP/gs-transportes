from typing import List, Optional
from app.models.driver import Driver
from app.database import create_connection

import sqlite3
from datetime import datetime, timedelta
import random


class DriverRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def create(self, driver: Driver) -> Optional[int]:
        sql = '''INSERT INTO Driver (Name, Salary, Contact, StartDate, EndDate, CPF, RG, CNH, ExtraInfo)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, driver.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao criar motorista: {e}")
                raise
            finally:
                conn.close()
        return None

    def sum_driver_salaries_by_route(self, route_id: int) -> float:
        conn = create_connection(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT IFNULL(SUM(d.Salary), 0)
                       FROM Driver d
                                INNER JOIN RouteDriver rd ON d.DriverID = rd.DriverID
                       WHERE rd.RouteID = ?
                       """, (route_id,))

        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] is not None else 0.0

    def populate_random_drivers(self, qtd: int = 200):
        first_names = ["Carlos", "Maria", "João", "Ana", "Lucas", "Fernanda", "Pedro", "Juliana", "Ricardo", "Larissa"]
        last_names = ["Silva", "Souza", "Pereira", "Costa", "Oliveira", "Rodrigues", "Almeida", "Lima", "Gomes",
                      "Barbosa"]

        for _ in range(qtd):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            salary = round(random.uniform(2000, 7000), 2)
            contact = f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            start_date = datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2500))
            end_date = None if random.random() < 0.8 else start_date + timedelta(days=random.randint(100, 1000))
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            rg = str(random.randint(1000000, 9999999))
            cnh = str(random.randint(10000000000, 99999999999))
            extra_info = random.choice([
                "",
                "Motorista de viagens longas",
                "Disponível para plantões",
                "Trabalha meio período"
            ])

            driver = Driver(
                driver_id=None,
                name=name,
                salary=salary,
                contact=contact,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                cpf=cpf,
                rg=rg,
                cnh=cnh,
                extra_info=extra_info
            )

            self.create(driver)

        print(f"{qtd} motoristas inseridos com sucesso!")



    def get_all(self) -> List[Driver]:
        sql = '''SELECT *
                 FROM Driver'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Driver.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar motoristas: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        sql = '''SELECT *
                 FROM Driver
                 WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (driver_id,))
                row = cursor.fetchone()
                return Driver.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar motorista: {e}")
            finally:
                conn.close()
        return None

    def update(self, driver: Driver) -> bool:
        sql = '''UPDATE Driver \
                 SET Name      = ?, \
                     Salary    = ?, \
                     Contact   = ?, \
                     StartDate = ?, \
                     EndDate   = ?, \
                     CPF       = ?, \
                     RG        = ?, \
                     CNH       = ?, \
                     ExtraInfo = ?
                 WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                to_tuple = driver.to_tuple()
                cursor.execute(sql, (*to_tuple, driver.driver_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar motorista: {e}")
            finally:
                conn.close()
        return False

    def delete(self, driver_id: int) -> bool:
        sql = '''DELETE
                 FROM Driver
                 WHERE DriverID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (driver_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar motorista: {e}")
            finally:
                conn.close()
        return False
