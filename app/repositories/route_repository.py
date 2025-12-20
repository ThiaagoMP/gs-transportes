import sqlite3
from typing import List, Optional
from app.models.route import Route
from app.database import create_connection

class RouteRepository:
    def __init__(self, db_file: str):
        self.db_file = db_file

    def add(self, route: Route) -> Optional[int]:
        sql = '''INSERT INTO Route (VehicleID, AvgKm, Period, AvgTimeMinutes, Name, Active, ContractValue)
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''
        conn = create_connection(self.db_file)
        if conn:
            try:

                cursor = conn.cursor()
                cursor.execute(sql, route.to_tuple())
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Erro ao adicionar rota: {e}")
            finally:
                conn.close()
        return None

    def get_all(self) -> List[Route]:
        sql = '''SELECT * FROM Route'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [Route.from_db_row(row) for row in rows]
            except sqlite3.Error as e:
                print(f"Erro ao listar rotas: {e}")
            finally:
                conn.close()
        return []

    def count_routes_by_vehicle(self, vehicle_id: int) -> int:
        sql = "SELECT COUNT(*) FROM Route WHERE VehicleID = ? AND ACTIVE = 1"
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (vehicle_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
            except sqlite3.Error as e:
                print(f"Erro ao contar rotas do veículo: {e}")
            finally:
                conn.close()
        return 0

    def get_by_id(self, route_id: int) -> Optional[Route]:
        sql = '''SELECT * FROM Route WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                row = cursor.fetchone()
                return Route.from_db_row(row) if row else None
            except sqlite3.Error as e:
                print(f"Erro ao buscar rota: {e}")
            finally:
                conn.close()
        return None

    def update(self, route: Route) -> bool:
        sql = '''UPDATE Route 
                 SET VehicleID = ?, AvgKm = ?, Period = ?, AvgTimeMinutes = ?, 
                     Name = ?, Active = ?, ContractValue = ?
                 WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (*route.to_tuple(), route.route_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao atualizar rota: {e}")
            finally:
                conn.close()
        return False

    def calcular_resultados_esperados(self, route_id: int) -> dict:
        try:
            conn = create_connection(self.db_file)
            cursor = conn.cursor()

            # 1️⃣ Buscar informações da rota
            cursor.execute("""
                           SELECT VehicleID, AvgKm, ContractValue
                           FROM Route
                           WHERE RouteID = ?
                           """, (route_id,))
            route_row = cursor.fetchone()
            if not route_row:
                return None

            vehicle_id, avg_km, contract_value = route_row

            # 2️⃣ Buscar consumo médio do veículo
            cursor.execute("""
                           SELECT AvgKmPerLiter
                           FROM Vehicle
                           WHERE VehicleID = ?
                           """, (vehicle_id,))
            vehicle_row = cursor.fetchone()
            if not vehicle_row:
                return None
            avg_km_per_liter = vehicle_row[0]

            # 3️⃣ Contar número de alunos na rota
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM RouteStudent
                           WHERE RouteID = ?
                           """, (route_id,))
            qtd_alunos = cursor.fetchone()[0]

            # 4️⃣ Calcular valores
            faturamento_mensal = qtd_alunos * contract_value
            despesas_mensais = avg_km / avg_km_per_liter
            lucro_mensal = faturamento_mensal - despesas_mensais

            # 5️⃣ Versões anuais (x12)
            faturamento_anual = faturamento_mensal * 12
            despesas_anuais = despesas_mensais * 12
            lucro_anual = lucro_mensal * 12

            return {
                "qtd_alunos": qtd_alunos,
                "faturamento_mensal": faturamento_mensal,
                "despesas_mensais": despesas_mensais,
                "lucro_mensal": lucro_mensal,
                "faturamento_anual": faturamento_anual,
                "despesas_anuais": despesas_anuais,
                "lucro_anual": lucro_anual
            }

        except Exception as e:
            print(f"Erro ao calcular resultados esperados: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def delete(self, route_id: int) -> bool:
        sql = '''DELETE FROM Route WHERE RouteID = ?'''
        conn = create_connection(self.db_file)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (route_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Erro ao deletar rota: {e}")
            finally:
                conn.close()
        return False
