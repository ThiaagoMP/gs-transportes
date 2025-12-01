import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.trip_driver_repository import TripDriverRepository
from app.repositories.driver_repository import DriverRepository
from app.components.list_rounded_button import ListRoundedButton

class InterfaceTripDetails:
    def __init__(self, parent, db_path, trip_id):
        self.parent = parent
        self.db_path = db_path
        self.trip_id = trip_id

        self.trip_repo = TripRepository(self.db_path)
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.trip_driver_repo = TripDriverRepository(self.db_path)
        self.driver_repo = DriverRepository(self.db_path)

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
            text="Detalhes da Viagem",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 10))

        trip = self.trip_repo.get_by_id(self.trip_id)
        if not trip:
            messagebox.showerror("Erro", "Viagem não encontrada.")
            return

        vehicle = self.vehicle_repo.get_by_id(getattr(trip, "vehicle_id", None))
        vehicle_plate = getattr(vehicle, "license_plate", "Desconhecido") if vehicle else "Desconhecido"
        avg_km_per_liter = getattr(vehicle, "avg_km_per_liter", 1) if vehicle else 1

        passenger_fare = float(getattr(trip, "passenger_fare", 0.0) or 0)
        passenger_count = int(getattr(trip, "passenger_count", 0) or 0)
        expenses = float(getattr(trip, "additional_expenses", 0.0) or 0)
        total_km = float(getattr(trip, "total_km", 0.0) or 0)
        faturamento_bruto = passenger_fare * passenger_count
        lucro = faturamento_bruto - expenses
        gasto_gasolina = total_km / avg_km_per_liter if avg_km_per_liter != 0 else 0

        start_date = self.format_date(getattr(trip, "start_date", ""))
        end_date = self.format_date(getattr(trip, "end_date", ""))
        descricao = getattr(trip, "description", "") or "-"

        frame = tk.Frame(self.parent, bg=self.bg_main)
        frame.pack(padx=40, pady=20, fill="x")

        detalhes = {
            "Placa do Veículo": vehicle_plate,
            "Gasto aproximado de gasolina (L)": f"{gasto_gasolina:.2f}",
            "Faturamento Bruto (R$)": f"R$ {faturamento_bruto:.2f}",
            "Despesas (R$)": f"R$ {expenses:.2f}",
            "Lucro (R$)": f"R$ {lucro:.2f}",
            "Valor por Passageiro (R$)": f"R$ {passenger_fare:.2f}",
            "Quantidade de Passageiros": str(passenger_count),
            "Total de KM": f"{total_km:.2f} km",
            "Data de Início": start_date,
            "Data de Fim": end_date,
            "Descrição": descricao,
        }

        for i, (label_text, value_text) in enumerate(detalhes.items()):
            tk.Label(
                frame,
                text=label_text + ":",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_main,
                fg=self.fg_text
            ).grid(row=i, column=0, sticky="nw", padx=(10, 20), pady=5)

            if label_text == "Descrição":
                text_box = tk.Text(
                    frame,
                    font=("Segoe UI", 12),
                    bg=self.bg_button,
                    fg=self.fg_text,
                    width=40,
                    height=5,
                    wrap="word",
                    padx=8,
                    pady=4
                )
                text_box.insert("1.0", value_text)
                text_box.config(state="disabled")
                text_box.grid(row=i, column=1, sticky="w", pady=5)
            else:
                color = self.fg_text
                if "Lucro" in label_text:
                    color = "#00ff7f"
                elif "Despesas" in label_text:
                    color = "#ff4c4c"

                tk.Label(
                    frame,
                    text=value_text,
                    font=("Segoe UI", 12),
                    bg=self.bg_button,
                    fg=color,
                    anchor="w",
                    width=40,
                    padx=8,
                    pady=4
                ).grid(row=i, column=1, sticky="w", pady=5)

        tk.Label(
            self.parent,
            text="Motoristas que participaram desta viagem:",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(10, 5))

        drivers_frame = tk.Frame(self.parent, bg=self.bg_main)
        drivers_frame.pack(padx=40, pady=5, fill="both", expand=True)

        tree_frame = tk.Frame(drivers_frame, bg=self.bg_main)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree_drivers = ttk.Treeview(
            tree_frame,
            columns=("Nome", "Contato", "Salário"),
            show="headings",
            yscrollcommand=tree_scroll.set,
            height=8
        )
        tree_scroll.config(command=self.tree_drivers.yview)

        self.tree_drivers.heading("Nome", text="Nome")
        self.tree_drivers.heading("Contato", text="Contato")
        self.tree_drivers.heading("Salário", text="Salário (R$)")

        self.tree_drivers.column("Nome", width=250)
        self.tree_drivers.column("Contato", width=200)
        self.tree_drivers.column("Salário", width=150)

        self.tree_drivers.pack(fill="both", expand=True)

        driver_ids = self.trip_driver_repo.get_driver_ids_by_trip(self.trip_id)
        for driver_id in driver_ids:
            driver = self.driver_repo.get_by_id(driver_id)
            if driver:
                self.tree_drivers.insert("", "end", values=(driver.name, driver.contact, f"R$ {driver.salary:.2f}"))

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
        btn_voltar.pack(pady=25)

    def format_date(self, date_value):
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                return date_value
        elif isinstance(date_value, datetime):
            return date_value.strftime("%d/%m/%Y")
        return str(date_value)

    def voltar(self):
        from app.interface.trip.interface_viagens import InterfaceViagem
        interface = InterfaceViagem(self.parent, self.db_path)
        interface.show()
