# repo_reports.py
# => Cole estas funções no seu módulo/repositório (cada função recebe db_path, start_date, end_date, filtros opcionais)
# Datas de entrada devem estar em 'YYYY-MM-DD' (as funções da interface farão a conversão).

import sqlite3
from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional

Row = Tuple[str, str, str, str, float, Optional[dict]]
# (date, category, plate_or_route, description, amount, extra_info_dict)

def _open_conn(db_path):
    return sqlite3.connect(db_path)

def get_maintenances(db_path: str, start: str, end: str,
                     vehicle_plate: Optional[str]=None,
                     route_name: Optional[str]=None,
                     driver_name: Optional[str]=None) -> List[Row]:
    """
    Retorna manutenções: (StartDate, 'Manutenção', LicensePlate, Description, Amount, {})
    """
    q = """
    SELECT m.StartDate, v.LicensePlate, m.Description, m.Amount
    FROM Maintenance m
    JOIN Vehicle v ON m.VehicleID = v.VehicleID
    LEFT JOIN Route r ON r.VehicleID = v.VehicleID
    LEFT JOIN TripDriver td ON td.TripID IN (SELECT TripID FROM Trip WHERE VehicleID = v.VehicleID)
    LEFT JOIN Driver d ON d.DriverID = td.DriverID
    WHERE date(m.StartDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    if vehicle_plate and vehicle_plate != "Todos":
        q += " AND v.LicensePlate = ?"
        params.append(vehicle_plate)
    if route_name and route_name != "Todos":
        q += " AND r.Name = ?"
        params.append(route_name)
    if driver_name and driver_name != "Todos":
        q += " AND d.Name = ?"
        params.append(driver_name)

    rows: List[Row] = []
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for r in cur.fetchall():
                date_s, plate, desc, amount = r
                rows.append((date_s, "Manutenção", plate or "", desc or "", float(amount or 0.0), {}))
    except sqlite3.Error:
        # caller can log/ignorar
        pass
    return rows

def get_refuelings(db_path: str, start: str, end: str,
                   vehicle_plate: Optional[str]=None,
                   route_name: Optional[str]=None,
                   driver_name: Optional[str]=None) -> List[Row]:
    """
    Retorna abastecimentos: (RefuelingDate, 'Abastecimento', LicensePlate, Description, TotalCost, {'liters':..., 'price_per_liter':...})
    Observação: na sua tabela Refueling os campos são: PricePerLiter, Liters, RefuelingDate.
    Calculamos custo = PricePerLiter * Liters.
    """
    q = """
    SELECT r.RefuelingDate, v.LicensePlate, r.Description, r.PricePerLiter, r.Liters
    FROM Refueling r
    JOIN Vehicle v ON r.VehicleID = v.VehicleID
    LEFT JOIN Route rt ON rt.VehicleID = v.VehicleID
    LEFT JOIN TripDriver td ON td.TripID IN (SELECT TripID FROM Trip WHERE VehicleID = v.VehicleID)
    LEFT JOIN Driver d ON d.DriverID = td.DriverID
    WHERE date(r.RefuelingDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    if vehicle_plate and vehicle_plate != "Todos":
        q += " AND v.LicensePlate = ?"
        params.append(vehicle_plate)
    if route_name and route_name != "Todos":
        q += " AND rt.Name = ?"
        params.append(route_name)
    if driver_name and driver_name != "Todos":
        q += " AND d.Name = ?"
        params.append(driver_name)

    rows: List[Row] = []
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for r in cur.fetchall():
                date_s, plate, desc, price_per_liter, liters = r
                price_per_liter = float(price_per_liter or 0.0)
                liters = float(liters or 0.0)
                amount = price_per_liter * liters
                extra = {"liters": liters, "price_per_liter": price_per_liter}
                rows.append((date_s, "Abastecimento", plate or "", desc or "", float(amount), extra))
    except sqlite3.Error:
        pass
    return rows

def get_driver_bonuses(db_path: str, start: str, end: str,
                       driver_name: Optional[str]=None) -> List[Row]:
    """
    Retorna bônus de motoristas (DriverBonus): (BonusDate, 'Bônus', DriverName, Description, Amount, {})
    """
    q = """
    SELECT db.BonusDate, d.Name, db.Description, db.Amount
    FROM DriverBonus db
    JOIN Driver d ON db.DriverID = d.DriverID
    WHERE date(db.BonusDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    if driver_name and driver_name != "Todos":
        q += " AND d.Name = ?"
        params.append(driver_name)
    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for r in cur.fetchall():
                date_s, name, desc, amount = r
                rows.append((date_s, "Bônus Motorista", name or "", desc or "", float(amount or 0.0), {}))
    except sqlite3.Error:
        pass
    return rows

def get_driver_salaries_proportional(db_path: str, start: str, end: str,
                                     vehicle_plate: Optional[str]=None,
                                     route_name: Optional[str]=None,
                                     driver_name: Optional[str]=None) -> List[Row]:
    """
    Retorna salário proporcional ao período em relatório.
    Saída: (date_range_repr, 'Salário', DriverName, 'Período X dias', amount, {'days':n})
    - Salary diário = Salary / 30
    - Para cada driver, computa overlap entre [start,end] e [Driver.StartDate, Driver.EndDate or today]
    - Se houver filtro por veículo/rota: aplica apenas se o driver estiver associado à rota (RouteDriver) ou ao TripDriver em trips no período.
    """
    # convert to date objects
    s_dt = datetime.strptime(start, "%Y-%m-%d").date()
    e_dt = datetime.strptime(end, "%Y-%m-%d").date()

    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()

            # base drivers (aplica filtro driver_name)
            q = "SELECT DriverID, Name, Salary, StartDate, EndDate FROM Driver"
            params = []
            if driver_name and driver_name != "Todos":
                q += " WHERE Name = ?"
                params.append(driver_name)
            cur.execute(q, params)
            drivers = cur.fetchall()

            for drv in drivers:
                did, name, salary, ds, de = drv
                salary = float(salary or 0.0)
                try:
                    drv_start = datetime.strptime(ds, "%Y-%m-%d").date()
                except Exception:
                    drv_start = date(1970,1,1)
                try:
                    drv_end = datetime.strptime(de, "%Y-%m-%d").date() if de else date.today()
                except Exception:
                    drv_end = date.today()

                # overlap
                overlap_start = max(s_dt, drv_start)
                overlap_end = min(e_dt, drv_end)
                if overlap_start > overlap_end:
                    # sem sobreposição, pular
                    continue
                days = (overlap_end - overlap_start).days + 1
                amount = salary / 30.0 * days

                # se filtros por veículo/rota aplicam, verificar associação:
                if vehicle_plate and vehicle_plate != "Todos":
                    # verificar se driver está vinculado a rota cujo vehicle tem essa placa
                    cur.execute("""
                        SELECT 1 FROM RouteDriver rd
                        JOIN Route r ON rd.RouteID = r.RouteID
                        JOIN Vehicle v ON r.VehicleID = v.VehicleID
                        WHERE rd.DriverID = ? AND v.LicensePlate = ?
                        LIMIT 1
                    """, (did, vehicle_plate))
                    if cur.fetchone() is None:
                        continue
                if route_name and route_name != "Todos":
                    cur.execute("""
                        SELECT 1 FROM RouteDriver rd
                        JOIN Route r ON rd.RouteID = r.RouteID
                        WHERE rd.DriverID = ? AND r.Name = ?
                        LIMIT 1
                    """, (did, route_name))
                    if cur.fetchone() is None:
                        continue
                if driver_name and driver_name != "Todos":
                    # já filtrado
                    pass

                desc = f"{overlap_start.strftime('%d/%m/%Y')} a {overlap_end.strftime('%d/%m/%Y')} ({days} dias)"
                rows.append((overlap_start.strftime("%Y-%m-%d"), "Salário (proporcional)", name or "", desc, float(amount), {"days": days}))
    except sqlite3.Error:
        pass
    return rows

def get_student_payments(db_path: str, start: str, end: str,
                         vehicle_plate: Optional[str]=None,
                         route_name: Optional[str]=None,
                         driver_name: Optional[str]=None) -> List[Row]:
    """
    Retorna pagamentos de alunos (StudentPayment) que caem no período.
    Para filtrar por rota/veículo: verifica RouteStudent vínculo do aluno (considerando StartDate/EndDate da matrícula).
    Saída: (PaymentDate, 'Pagamento Aluno', RouteName-or-empty, StudentName, Amount, {})
    """
    q = """
    SELECT sp.PaymentDate, s.Name as StudentName, sp.Amount, rs.RouteID
    FROM StudentPayment sp
    JOIN Student s ON sp.StudentID = s.StudentID
    LEFT JOIN RouteStudent rs ON rs.StudentID = s.StudentID
        AND (rs.EndDate IS NULL OR date(rs.EndDate) >= date(?)) AND date(rs.StartDate) <= date(?)
    WHERE date(sp.PaymentDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end, start, end]
    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            fetched = cur.fetchall()
            for payment_date, student_name, amount, route_id in fetched:
                route_name_val = ""
                plate_val = ""
                if route_id:
                    # obter nome da rota e vehicle plate
                    cur.execute("SELECT Name, VehicleID FROM Route WHERE RouteID = ?", (route_id,))
                    rr = cur.fetchone()
                    if rr:
                        route_name_val = rr[0]
                        vehicle_id = rr[1]
                        cur.execute("SELECT LicensePlate FROM Vehicle WHERE VehicleID = ?", (vehicle_id,))
                        vrow = cur.fetchone()
                        if vrow:
                            plate_val = vrow[0]
                # aplicar filtros
                if vehicle_plate and vehicle_plate != "Todos":
                    if plate_val != vehicle_plate:
                        continue
                if route_name and route_name != "Todos":
                    if route_name_val != route_name:
                        continue
                if driver_name and driver_name != "Todos":
                    # verificar se driver está associado à rota
                    if not route_id:
                        continue
                    cur.execute("""
                        SELECT 1 FROM RouteDriver rd
                        JOIN Driver d ON rd.DriverID = d.DriverID
                        WHERE rd.RouteID = ? AND d.Name = ?
                        LIMIT 1
                    """, (route_id, driver_name))
                    if cur.fetchone() is None:
                        continue

                rows.append((payment_date, "Pagamento Aluno", route_name_val or plate_val or "", student_name or "", float(amount or 0.0), {}))
    except sqlite3.Error:
        pass
    return rows

def get_route_extra_payments(db_path: str, start: str, end: str,
                             route_name: Optional[str]=None) -> List[Row]:
    """
    RouteExtraPayment (ganhos): (PaymentDate, 'Pagamento Extra Rota', RouteName, Description, Amount, {})
    """
    q = """
    SELECT rep.PaymentDate, r.Name, rep.Description, rep.Amount
    FROM RouteExtraPayment rep
    JOIN Route r ON rep.RouteID = r.RouteID
    WHERE date(rep.PaymentDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    if route_name and route_name != "Todos":
        q += " AND r.Name = ?"
        params.append(route_name)
    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for pd, rname, desc, amount in cur.fetchall():
                rows.append((pd, "Pagamento Extra Rota", rname or "", desc or "", float(amount or 0.0), {}))
    except sqlite3.Error:
        pass
    return rows

def get_route_expense_payments(db_path: str, start: str, end: str,
                               route_name: Optional[str]=None) -> List[Row]:
    """
    RouteExpensePayment (despesas): (PaymentDate, 'Despesa Rota', RouteName, Description, Amount, {})
    """
    q = """
    SELECT rep.PaymentDate, r.Name, rep.Description, rep.Amount
    FROM RouteExpensePayment rep
    JOIN Route r ON rep.RouteID = r.RouteID
    WHERE date(rep.PaymentDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    if route_name and route_name != "Todos":
        q += " AND r.Name = ?"
        params.append(route_name)
    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for pd, rname, desc, amount in cur.fetchall():
                rows.append((pd, "Despesa Rota", rname or "", desc or "", float(amount or 0.0), {}))
    except sqlite3.Error:
        pass
    return rows

def get_trips_profit(db_path: str, start: str, end: str,
                     vehicle_plate: Optional[str]=None,
                     driver_name: Optional[str]=None,
                     route_name: Optional[str]=None) -> List[Row]:
    """
    Calcula lucro das viagens: (StartDate, 'Lucro Viagem', PlateOrVehicle, Description(TripID), profit, {})
    Lucro = PassengerFare * PassengerCount - AdditionalExpenses
    """
    q = """
    SELECT t.TripID, t.VehicleID, t.StartDate, t.PassengerFare, t.PassengerCount, t.AdditionalExpenses
    FROM Trip t
    WHERE date(t.StartDate) BETWEEN date(?) AND date(?)
    """
    params = [start, end]
    rows=[]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q, params)
            for trip_id, vehicle_id, startdate, fare, pcount, add_exp in cur.fetchall():
                # obter placa
                cur.execute("SELECT LicensePlate FROM Vehicle WHERE VehicleID = ?", (vehicle_id,))
                vrow = cur.fetchone()
                plate = vrow[0] if vrow else ""
                # aplicar filtro vehicle
                if vehicle_plate and vehicle_plate != "Todos":
                    if plate != vehicle_plate:
                        continue
                # aplicar filter driver: verificar TripDriver
                if driver_name and driver_name != "Todos":
                    cur.execute("""
                        SELECT 1 FROM TripDriver td
                        JOIN Driver d ON td.DriverID = d.DriverID
                        WHERE td.TripID = ? AND d.Name = ? LIMIT 1
                    """, (trip_id, driver_name))
                    if cur.fetchone() is None:
                        continue
                # aplicar route_name: verificar se route vinculada ao vehicle tem esse nome
                if route_name and route_name != "Todos":
                    cur.execute("SELECT Name FROM Route WHERE VehicleID = ?", (vehicle_id,))
                    rr = cur.fetchone()
                    if not rr or rr[0] != route_name:
                        continue

                fare = float(fare or 0.0)
                pcount = int(pcount or 0)
                add_exp = float(add_exp or 0.0)
                profit = fare * pcount - add_exp
                desc = f"Trip {trip_id}"
                rows.append((startdate, "Lucro Viagem", plate or "", desc, float(profit), {}))
    except sqlite3.Error:
        pass
    return rows


# MÉTODOS FALTANTES PARA report_repository.py

def get_vehicle_plate_map(db_path: str) -> dict:
    """
    Retorna um dicionário {placa: nome_do_veiculo} de todos os veículos.
    Necessário para o dashboard de Lucro por Veículo.
    """
    q = "SELECT LicensePlate, Name FROM Vehicle"
    vehicle_map = {}
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()
            cur.execute(q)
            # Converte a lista de tuplas (placa, nome) para um dicionário
            vehicle_map = {row[0]: row[1] for row in cur.fetchall()}
    except sqlite3.Error:
        pass
    return vehicle_map


def get_route_receipts(db_path: str, start: str, end: str) -> dict:
    """
    Agrega as receitas (Pagamento Aluno + Pagamento Extra Rota) por nome da Rota.
    Retorna um dicionário {RouteName: TotalReceipts}.
    Necessário para o gráfico de Receita por Linha (Pie Chart).
    """
    # 1. Pagamentos de Alunos (associados à rota)
    q_students = """
                 SELECT r.Name, SUM(sp.Amount)
                 FROM StudentPayment sp
                          JOIN Student s ON sp.StudentID = s.StudentID
                          JOIN RouteStudent rs ON rs.StudentID = s.StudentID
                     AND (rs.EndDate IS NULL OR date (rs.EndDate) >= date (?)) AND date (rs.StartDate) <= date (?)
                     JOIN Route r \
                 ON rs.RouteID = r.RouteID
                 WHERE date (sp.PaymentDate) BETWEEN date (?) AND date (?)
                 GROUP BY r.Name \
                 """
    # 2. Pagamentos Extras de Rota
    q_extras = """
               SELECT r.Name, SUM(rep.Amount)
               FROM RouteExtraPayment rep
                        JOIN Route r ON rep.RouteID = r.RouteID
               WHERE date (rep.PaymentDate) BETWEEN date (?) AND date (?)
               GROUP BY r.Name \
               """

    receipts_by_route = defaultdict(float)

    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()

            # Executa alunos
            params_students = [start, end, start, end]
            cur.execute(q_students, params_students)
            for rname, amount in cur.fetchall():
                receipts_by_route[rname or "Rota Desconhecida"] += float(amount or 0.0)

            # Executa extras
            params_extras = [start, end]
            cur.execute(q_extras, params_extras)
            for rname, amount in cur.fetchall():
                receipts_by_route[rname or "Rota Desconhecida"] += float(amount or 0.0)

    except sqlite3.Error:
        pass

    return dict(receipts_by_route)


def get_all_receipts_monthly(db_path: str, start: str, end: str) -> dict:
    """
    Retorna receitas mensais detalhadas: pagamentos de alunos e pagamentos extras de linha.
    Retorna: {"student_payments": {"YYYY-MM": valor, ...}, "route_extras": {"YYYY-MM": valor, ...}}
    Necessário para o gráfico Fluxo Financeiro Mensal Detalhado.
    """
    monthly_receipts = {"student_payments": defaultdict(float), "route_extras": defaultdict(float)}

    # 1. Pagamentos de Alunos por mês
    q_students = """
                 SELECT strftime('%Y-%m', sp.PaymentDate), SUM(sp.Amount)
                 FROM StudentPayment sp
                 WHERE date (sp.PaymentDate) BETWEEN date (?) AND date (?)
                 GROUP BY 1 \
                 """
    # 2. Pagamentos Extras de Rota por mês
    q_extras = """
               SELECT strftime('%Y-%m', rep.PaymentDate), SUM(rep.Amount)
               FROM RouteExtraPayment rep
               WHERE date (rep.PaymentDate) BETWEEN date (?) AND date (?)
               GROUP BY 1 \
               """

    params = [start, end]
    try:
        with _open_conn(db_path) as conn:
            cur = conn.cursor()

            # Alunos
            cur.execute(q_students, params)
            for month, amount in cur.fetchall():
                monthly_receipts["student_payments"][month] += float(amount or 0.0)

            # Extras
            cur.execute(q_extras, params)
            for month, amount in cur.fetchall():
                monthly_receipts["route_extras"][month] += float(amount or 0.0)

    except sqlite3.Error:
        pass

    return {k: dict(v) for k, v in monthly_receipts.items()}


def get_all_expenses_monthly(db_path: str, start: str, end: str) -> dict:
    """
    Agrega despesas totais (Manutenção, Abastecimento, Salários, Bônus, Despesas de Rota) por mês.
    Retorna um dicionário {"YYYY-MM": TotalExpenses}.
    Necessário para os gráficos de Despesas Totais por Mês e Fluxo Financeiro Mensal Detalhado.
    """
    expenses_by_month = defaultdict(float)

    # 1. Manutenções
    maint_rows = get_maintenances(db_path, start, end)
    for date_s, _, _, _, amount, _ in maint_rows:
        month = date_s[:7]
        expenses_by_month[month] += abs(amount)  # Amount é negativo no report_rows, mas é positivo aqui

    # 2. Abastecimentos
    refuel_rows = get_refuelings(db_path, start, end)
    for date_s, _, _, _, amount, _ in refuel_rows:
        month = date_s[:7]
        expenses_by_month[month] += abs(amount)

    # 3. Bônus de Motorista
    bonus_rows = get_driver_bonuses(db_path, start, end)
    for date_s, _, _, _, amount, _ in bonus_rows:
        month = date_s[:7]
        expenses_by_month[month] += abs(amount)

    # 4. Salários Proporcionais
    salary_rows = get_driver_salaries_proportional(db_path, start, end)
    for date_s, _, _, _, amount, _ in salary_rows:
        month = date_s[:7]
        expenses_by_month[month] += abs(amount)

    # 5. Despesas de Rota
    route_exp_rows = get_route_expense_payments(db_path, start, end)
    for date_s, _, _, _, amount, _ in route_exp_rows:
        month = date_s[:7]
        expenses_by_month[month] += abs(amount)

    return dict(expenses_by_month)

