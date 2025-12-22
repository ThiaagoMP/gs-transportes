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
        self.bg_card = "#2c2c2e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.fg_dim = "#aaaaaa"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        # Header
        header = tk.Frame(self.parent, bg=self.bg_main)
        header.pack(fill="x", padx=30, pady=(20, 10))

        tk.Label(header, text=f"Detalhes: {self.vehicle.name}", font=("Segoe UI", 22, "bold"),
                 bg=self.bg_main, fg=self.accent).pack(side="left")

        ListRoundedButton(header, text="Voltar", command=self.voltar, width=100, height=35,
                          bg=self.bg_button, fg=self.fg_text).pack(side="right")

        # Scrollable Area
        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def _resize_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", _resize_canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.render_content()

    def create_card(self, parent, title, data_dict, row, col):
        card = tk.Frame(parent, bg=self.bg_card, padx=15, pady=15, highlightthickness=1, highlightbackground="#3a3f47")
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        tk.Label(card, text=title, font=("Segoe UI", 13, "bold"), bg=self.bg_card, fg=self.accent).pack(anchor="w",
                                                                                                        pady=(0, 10))

        for label, value in data_dict.items():
            row_f = tk.Frame(card, bg=self.bg_card)
            row_f.pack(fill="x", pady=2)
            tk.Label(row_f, text=label, font=("Segoe UI", 10), bg=self.bg_card, fg=self.fg_dim).pack(side="left")
            tk.Label(row_f, text=value, font=("Segoe UI", 10, "bold"), bg=self.bg_card, fg=self.fg_text).pack(
                side="right")
        return card

    def render_content(self):
        v = self.vehicle
        id = v.vehicle_id

        # Grid layout para cards
        self.scrollable_frame.columnconfigure((0, 1), weight=1)

        # CARD 1: Informações Técnicas (Emoji removido)
        tech_data = {
            "Placa": v.license_plate,
            "Assentos": str(v.seats),
            "Média Consumo": f"{v.avg_km_per_liter} km/L",
            "Tanque": f"{v.fuel_tank_size} L",
            "Compra": self.format_date(v.buy_date),
            "Venda": self.format_date(v.sell_date) if v.sell_date else "Ativo"
        }
        self.create_card(self.scrollable_frame, "Informações Técnicas", tech_data, 0, 0)

        # CARD 2: Operacional (Emoji removido)
        ops_data = {
            "Total de Viagens": str(self.trip_repo.count_trips_by_vehicle(id, "total")),
            "Viagens (Ano)": str(self.trip_repo.count_trips_by_vehicle(id, "year")),
            "Linhas Atuais": str(self.route_repo.count_routes_by_vehicle(id)),
            "Abastecimentos": str(self.fuel_repo.count_by_vehicle(id, "total")),
            "Manutenções": str(self.maintenance_repo.count_by_vehicle(id, "total"))
        }
        self.create_card(self.scrollable_frame, "Operacional", ops_data, 0, 1)

        # CARD 3: Financeiro (Emoji removido)
        fuel_total = self.fuel_repo.sum_cost_by_vehicle(id, "total")
        maint_total = self.maintenance_repo.sum_cost_by_vehicle(id, "total")
        costs_data = {
            "Total Abastecimento": f"R$ {fuel_total:,.2f}",
            "Gasto Abast. (Mês)": f"R$ {self.fuel_repo.sum_cost_by_vehicle(id, 'month'):,.2f}",
            "Total Manutenção": f"R$ {maint_total:,.2f}",
            "Gasto Manut. (Mês)": f"R$ {self.maintenance_repo.sum_cost_by_vehicle(id, 'month'):,.2f}",
            "Custo Operacional": f"R$ {(fuel_total + maint_total):,.2f}"
        }
        self.create_card(self.scrollable_frame, "Custos Acumulados", costs_data, 1, 0)

        # CARD 4: Performance e Lucro (Emoji removido)
        profit_total = self.vehicle_repo.get_vehicle_profit(id, "total")
        profit_data = {
            "Lucro Total": f"R$ {profit_total:,.2f}",
            "Lucro (Ano)": f"R$ {self.vehicle_repo.get_vehicle_profit(id, 'year'):,.2f}",
            "Lucro (Mês)": f"R$ {self.vehicle_repo.get_vehicle_profit(id, 'month'):,.2f}",
            "Margem Estimada": "Ver Relatórios"
        }
        card_lucro = self.create_card(self.scrollable_frame, "Resultado Financeiro", profit_data, 1, 1)

        # Manter o destaque visual do lucro
        for child in card_lucro.winfo_children():
            if isinstance(child, tk.Frame):
                labels = child.winfo_children()
                if len(labels) > 1 and labels[0].cget("text") == "Lucro Total":
                    labels[1].configure(fg="#4cd964", font=("Segoe UI", 12, "bold"))

    def format_date(self, date_value):
        if not date_value or date_value in ["None", ""]: return "-"
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return str(date_value)

    def voltar(self):
        self.parent.unbind_all("<MouseWheel>")
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        InterfaceListVehicles(self.parent, self.db_path).show()