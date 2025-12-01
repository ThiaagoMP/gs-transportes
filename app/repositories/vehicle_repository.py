import sqlite3
from typing import List, Optional

from app.database import create_connection
from app.models.vehicle import Vehicle

class VehicleRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, vehicle: Vehicle) -> Optional[int]:
        sql = '''INSERT INTO Vehicle (AvgKmPerLiter, LicensePlate, Seats, FuelTankSize, Name, BuyDate, SellDate, PurchaseValue, SaleValue, ManufacturingYear)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                tuple_data = vehicle.to_tuple()
                expected_length = 10
                if len(tuple_data) != expected_length:
                    print(f"ERRO: Número incorreto de valores no tuple. Esperado {expected_length}, recebido {len(tuple_data)}: {tuple_data}")
                    return None
                cursor.execute(sql, tuple_data)
                conn.commit()
                last_id = cursor.lastrowid
                return last_id
            except sqlite3.Error as e:
                print(f"ERRO ao adicionar veículo: {e}")
                return None
            finally:
                conn.close()
        return None

    def get_faturamento_bruto(self, vehicle_id: int):
        """Retorna o faturamento bruto das rotas ativas do veículo."""
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT
                        SUM(r.ContractValue * (
                            SELECT COUNT(*) FROM RouteStudent rs WHERE rs.RouteID = r.RouteID
                        )) AS Total,
                        SUM(
                            CASE WHEN strftime('%Y', rs.StartDate) = strftime('%Y', 'now')
                            THEN r.ContractValue * (
                                SELECT COUNT(*) FROM RouteStudent rs2 WHERE rs2.RouteID = r.RouteID
                            ) END
                        ) AS Ano,
                        SUM(
                            CASE WHEN strftime('%Y-%m', rs.StartDate) = strftime('%Y-%m', 'now')
                            THEN r.ContractValue * (
                                SELECT COUNT(*) FROM RouteStudent rs3 WHERE rs3.RouteID = r.RouteID
                            ) END
                        ) AS Mes
                    FROM Route r
                    LEFT JOIN RouteStudent rs ON r.RouteID = rs.RouteID
                    WHERE r.VehicleID = ? AND r.Active = 1
                """
                cursor.execute(query, (vehicle_id,))
                row = cursor.fetchone()
                return {"total": row[0] or 0, "ano": row[1] or 0, "mes": row[2] or 0}
            except sqlite3.Error as e:
                print(f"Erro ao calcular faturamento bruto: {e}")
            finally:
                conn.close()
        return {"total": 0, "ano": 0, "mes": 0}

    def get_valor_abastecimentos(self, vehicle_id: int):
        """Retorna o valor total gasto em abastecimentos (total, ano e mês)."""
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT
                        SUM(PricePerLiter * Liters) AS Total,
                        SUM(CASE WHEN strftime('%Y', RefuelingDate) = strftime('%Y', 'now') THEN PricePerLiter * Liters END) AS Ano,
                        SUM(CASE WHEN strftime('%Y-%m', RefuelingDate) = strftime('%Y-%m', 'now') THEN PricePerLiter * Liters END) AS Mes
                    FROM Refueling
                    WHERE VehicleID = ?
                """
                cursor.execute(query, (vehicle_id,))
                row = cursor.fetchone()
                return {"total": row[0] or 0, "ano": row[1] or 0, "mes": row[2] or 0}
            except sqlite3.Error as e:
                print(f"Erro ao calcular valor de abastecimentos: {e}")
            finally:
                conn.close()
        return {"total": 0, "ano": 0, "mes": 0}

    def get_valor_manutencoes(self, vehicle_id: int):
        """Retorna o valor total gasto em manutenções (total, ano e mês)."""
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT
                        SUM(Amount) AS Total,
                        SUM(CASE WHEN strftime('%Y', EndDate) = strftime('%Y', 'now') THEN Amount END) AS Ano,
                        SUM(CASE WHEN strftime('%Y-%m', EndDate) = strftime('%Y-%m', 'now') THEN Amount END) AS Mes
                    FROM Maintenance
                    WHERE VehicleID = ?
                """
                cursor.execute(query, (vehicle_id,))
                row = cursor.fetchone()
                return {"total": row[0] or 0, "ano": row[1] or 0, "mes": row[2] or 0}
            except sqlite3.Error as e:
                print(f"Erro ao calcular valor de manutenções: {e}")
            finally:
                conn.close()
        return {"total": 0, "ano": 0, "mes": 0}

    def get_vehicle_profit(self, vehicle_id: int, period: str = "total") -> float:
        conn = create_connection(self.db_file)
        if not conn:
            return 0.0

        try:
            cursor = conn.cursor()

            # filtros para período, usando os aliases corretos nas consultas que precisam deles
            date_filter_trip = ""
            date_filter_refuel = ""
            date_filter_maint = ""
            date_filter_expense_in_sub = ""
            if period == "year":
                date_filter_trip = "AND strftime('%Y', Trip.StartDate) = strftime('%Y', 'now')"
                date_filter_refuel = "AND strftime('%Y', Refueling.RefuelingDate) = strftime('%Y', 'now')"
                date_filter_maint = "AND strftime('%Y', Maintenance.StartDate) = strftime('%Y', 'now')"
                # para a subquery que usa alias REP, referenciar REP.PaymentDate
                date_filter_expense_in_sub = "AND strftime('%Y', REP.PaymentDate) = strftime('%Y', 'now')"
            elif period == "month":
                date_filter_trip = "AND strftime('%Y-%m', Trip.StartDate) = strftime('%Y-%m', 'now')"
                date_filter_refuel = "AND strftime('%Y-%m', Refueling.RefuelingDate) = strftime('%Y-%m', 'now')"
                date_filter_maint = "AND strftime('%Y-%m', Maintenance.StartDate) = strftime('%Y-%m', 'now')"
                date_filter_expense_in_sub = "AND strftime('%Y-%m', REP.PaymentDate) = strftime('%Y-%m', 'now')"

            # 1) Lucro de rotas: receita por rota menos salários dos motoristas e despesas da rota (via RouteExpensePayment)
            # Observação: usamos JOINs através de RouteDriver para pegar os motoristas ligados a cada rota.
            # A subquery soma as despesas da rota filtrando por REP.PaymentDate quando necessário.
            cursor.execute(
                "SELECT "
                "COALESCE(SUM(r.ContractValue * (SELECT COUNT(*) FROM RouteStudent rs WHERE rs.RouteID = r.RouteID)), 0) "
                "- COALESCE(SUM(d.Salary), 0) "
                "- COALESCE(SUM((SELECT COALESCE(SUM(REP.Amount), 0) FROM RouteExpensePayment REP WHERE REP.RouteID = r.RouteID " + date_filter_expense_in_sub + ")), 0) "
                                                                                                                                                                 "FROM Route r "
                                                                                                                                                                 "LEFT JOIN RouteDriver rd ON rd.RouteID = r.RouteID "
                                                                                                                                                                 "LEFT JOIN Driver d ON d.DriverID = rd.DriverID "
                                                                                                                                                                 "WHERE r.VehicleID = ? AND r.ACTIVE = 1",
                (vehicle_id,)
            )
            lucro_rotas = cursor.fetchone()[0] or 0.0

            # 2) Faturamento das viagens (passenger_fare * passenger_count)
            cursor.execute(
                "SELECT COALESCE(SUM(Trip.PassengerFare * Trip.PassengerCount), 0) "
                "FROM Trip WHERE Trip.VehicleID = ? " + date_filter_trip,
                (vehicle_id,)
            )
            faturamento_viagens = cursor.fetchone()[0] or 0.0

            # 3) Despesas adicionais das viagens (AdditionalExpenses)
            cursor.execute(
                "SELECT COALESCE(SUM(Trip.AdditionalExpenses), 0) "
                "FROM Trip WHERE Trip.VehicleID = ? " + date_filter_trip,
                (vehicle_id,)
            )
            despesas_viagens = cursor.fetchone()[0] or 0.0

            # 4) Despesas com combustível: PricePerLiter * Liters
            cursor.execute(
                "SELECT COALESCE(SUM(Refueling.PricePerLiter * Refueling.Liters), 0) "
                "FROM Refueling WHERE Refueling.VehicleID = ? " + date_filter_refuel,
                (vehicle_id,)
            )
            despesas_combustivel = cursor.fetchone()[0] or 0.0

            # 5) Despesas com manutenção: Maintenance.Amount
            cursor.execute(
                "SELECT COALESCE(SUM(Maintenance.Amount), 0) "
                "FROM Maintenance WHERE Maintenance.VehicleID = ? " + date_filter_maint,
                (vehicle_id,)
            )
            despesas_manutencao = cursor.fetchone()[0] or 0.0

            # lucro final: lucro_rotas + faturamento_viagens - (despesas_viagens + despesas_combustivel + despesas_manutencao)
            lucro_final = (lucro_rotas + faturamento_viagens) - (
                        despesas_viagens + despesas_combustivel + despesas_manutencao)
            return round(lucro_final, 2)

        except Exception as e:
            print("Erro ao calcular lucro do veículo:", e)
            return 0.0
        finally:
            conn.close()

    def get_lucro(self, vehicle_id: int):
        """Calcula o lucro líquido do veículo (total, ano e mês)."""
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()

                faturamento = self.get_faturamento_bruto(vehicle_id)
                abastecimentos = self.get_valor_abastecimentos(vehicle_id)
                manutencoes = self.get_valor_manutencoes(vehicle_id)

                cursor.execute("""
                    SELECT
                        SUM(d.Salary) AS SalarioTotal,
                        SUM(
                            (SELECT SUM(Amount) FROM RouteExpensePayment rep WHERE rep.RouteID = r.RouteID)
                        ) AS DespesasAdicionais
                    FROM Route r
                    LEFT JOIN RouteDriver rd ON r.RouteID = rd.RouteID
                    LEFT JOIN Driver d ON rd.DriverID = d.DriverID
                    WHERE r.VehicleID = ?
                """, (vehicle_id,))
                row = cursor.fetchone()
                salario_total = row[0] or 0
                despesas_adicionais = row[1] or 0

                lucro_total = faturamento["total"] - (salario_total + despesas_adicionais + abastecimentos["total"] + manutencoes["total"])
                lucro_ano = faturamento["ano"] - (abastecimentos["ano"] + manutencoes["ano"])
                lucro_mes = faturamento["mes"] - (abastecimentos["mes"] + manutencoes["mes"])

                return {"total": lucro_total, "ano": lucro_ano, "mes": lucro_mes}
            except sqlite3.Error as e:
                print(f"Erro ao calcular lucro: {e}")
            finally:
                conn.close()
        return {"total": 0, "ano": 0, "mes": 0}


    def get_all(self) -> List[Vehicle]:
        sql = '''SELECT * FROM Vehicle'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Vehicle.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar veículos: {e}")
            finally:
                conn.close()
        return []

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        sql = '''SELECT * FROM Vehicle WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                row = cursor.fetchone()
                return Vehicle.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar veículo: {e}")
            finally:
                conn.close()
        return None

    def update(self, vehicle: Vehicle) -> bool:
        sql = '''UPDATE Vehicle SET AvgKmPerLiter = ?, LicensePlate = ?, Seats = ?, FuelTankSize = ?, Name = ?, BuyDate = ?, SellDate = ?, PurchaseValue = ?, SaleValue = ?, ManufacturingYear = ?
                 WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*vehicle.to_tuple(), vehicle.vehicle_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar veículo: {e}")
            finally:
                conn.close()
        return False

    def delete(self, vehicle_id: int) -> bool:
        sql = '''DELETE FROM Vehicle WHERE VehicleID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar veículo: {e}")
            finally:
                conn.close()
        return False