import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.refueling_repository import RefuelingRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.maintenance_repository import MaintenanceRepository

class InterfaceVehicleDetails:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.trip_repo = TripRepository(self.db_path)
        self.fuel_repo = RefuelingRepository(self.db_path)
        self.maintenance_repo = MaintenanceRepository(self.db_path)
        self.route_repo = RouteRepository(self.db_path)
        self.vehicle = self.vehicle_repo.get_by_id(vehicle_id)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Detalhes do Veículo",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 10))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(padx=40, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        buy_date = self.format_date(self.vehicle.buy_date)
        sell_date = self.format_date(self.vehicle.sell_date) if self.vehicle.sell_date else "-"

        viagens_total = self.trip_repo.count_trips_by_vehicle(self.vehicle.vehicle_id, period="total")
        viagens_ano = self.trip_repo.count_trips_by_vehicle(self.vehicle.vehicle_id, period="year")
        viagens_mes = self.trip_repo.count_trips_by_vehicle(self.vehicle.vehicle_id, period="month")

        abastecimentos_total = self.fuel_repo.count_by_vehicle(self.vehicle.vehicle_id, period="total")
        abastecimentos_ano = self.fuel_repo.count_by_vehicle(self.vehicle.vehicle_id, period="year")
        abastecimentos_mes = self.fuel_repo.count_by_vehicle(self.vehicle.vehicle_id, period="month")

        manut_total = self.maintenance_repo.count_by_vehicle(self.vehicle.vehicle_id, period="total")
        manut_ano = self.maintenance_repo.count_by_vehicle(self.vehicle.vehicle_id, period="year")
        manut_mes = self.maintenance_repo.count_by_vehicle(self.vehicle.vehicle_id, period="month")

        linhas_atuais = self.route_repo.count_routes_by_vehicle(self.vehicle.vehicle_id)

        valor_abast_total = self.fuel_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "total")
        valor_abast_ano = self.fuel_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "year")
        valor_abast_mes = self.fuel_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "month")

        valor_manut_total = self.maintenance_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "total")
        valor_manut_ano = self.maintenance_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "year")
        valor_manut_mes = self.maintenance_repo.sum_cost_by_vehicle(self.vehicle.vehicle_id, "month")

        lucro_total = self.vehicle_repo.get_vehicle_profit(self.vehicle.vehicle_id, "total")
        lucro_ano = self.vehicle_repo.get_vehicle_profit(self.vehicle.vehicle_id, "year")
        lucro_mes = self.vehicle_repo.get_vehicle_profit(self.vehicle.vehicle_id, "month")

        detalhes = {
            "Nome": self.vehicle.name,
            "Placa": self.vehicle.license_plate,
            "Quantidade de Assentos": str(self.vehicle.seats),
            "Média km/L": str(self.vehicle.avg_km_per_liter),
            "Tamanho do Tanque (L)": str(self.vehicle.fuel_tank_size),
            "Data de Compra": buy_date,
            "Data de Venda": sell_date,
            "Quantidade de viagens feitas (Total)": str(viagens_total),
            "Quantidade de viagens feitas (Ano)": str(viagens_ano),
            "Quantidade de viagens feitas (Mês)": str(viagens_mes),
            "Quantidade de abastecimentos feitos (Total)": str(abastecimentos_total),
            "Quantidade de abastecimentos feitos (Ano)": str(abastecimentos_ano),
            "Quantidade de abastecimentos feitos (Mês)": str(abastecimentos_mes),
            "Quantidade de manutenções feitas (Total)": str(manut_total),
            "Quantidade de manutenções feitas (Ano)": str(manut_ano),
            "Quantidade de manutenções feitas (Mês)": str(manut_mes),
            "Quantidade de linhas atuais": str(linhas_atuais),
            "Valor de abastecimentos (Total)": str(valor_abast_total),
            "Valor de abastecimentos (Ano)": str(valor_abast_ano),
            "Valor de abastecimentos (Mês)": str(valor_abast_mes),
            "Valor de manutenções (Total)": str(valor_manut_total),
            "Valor de manutenções (Ano)": str(valor_manut_ano),
            "Valor de manutenções (Mês)": str(valor_manut_mes),
            "Lucro total": str(lucro_total),
            "Lucro ano": str(lucro_ano),
            "Lucro mês": str(lucro_mes)
        }

        for i, (label_text, value_text) in enumerate(detalhes.items()):
            tk.Label(
                scrollable_frame,
                text=label_text + ":",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_main,
                fg=self.fg_text
            ).grid(row=i, column=0, sticky="e", padx=(10, 10), pady=5)

            tk.Label(
                scrollable_frame,
                text=value_text,
                font=("Segoe UI", 12),
                bg=self.bg_button,
                fg=self.fg_text,
                anchor="w",
                width=40,
                padx=8,
                pady=4
            ).grid(row=i, column=1, sticky="w", pady=5)

        btn_voltar = ListRoundedButton(
            self.parent,
            text="Voltar",
            command=self.voltar,
            width=200,
            height=50,
            bg=self.bg_button,
            fg=self.fg_text,
            hover_bg=self.accent,
            font=("Segoe UI", 11, "bold")
        )
        btn_voltar.pack(pady=20)

    def format_date(self, date_value):
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                return date_value
        return str(date_value)

    def voltar(self):
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        interface = InterfaceListVehicles(self.parent, self.db_path)
        interface.show()
