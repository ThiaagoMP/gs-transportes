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
        self.bg_button = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        canvas = tk.Canvas(self.parent, bg=self.bg_main, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.parent.winfo_width())
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(
            scrollable_frame,
            text="Detalhes da viagem",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(10, 5))

        trip = self.trip_repo.get_by_id(self.trip_id)
        if not trip:
            messagebox.showerror("Erro", "Viagem não encontrada.")
            return

        vehicle = self.vehicle_repo.get_by_id(getattr(trip, "vehicle_id", None))
        vehicle_plate = getattr(vehicle, "license_plate", "---").upper() if vehicle else "---"
        avg_km_l = getattr(vehicle, "avg_km_per_liter", 1) if vehicle else 1

        fare = float(getattr(trip, "passenger_fare", 0.0) or 0)
        count = int(getattr(trip, "passenger_count", 0) or 0)
        expenses = float(getattr(trip, "additional_expenses", 0.0) or 0)
        total_km = float(getattr(trip, "total_km", 0.0) or 0)
        bruto = fare * count
        lucro = bruto - expenses
        gas = total_km / avg_km_l if avg_km_l != 0 else 0

        detalhes = [
            ("Placa", vehicle_plate),
            ("Estimativa (L)", f"{gas:.2f}"),
            ("Bruto (R$)", f"{bruto:.2f}"),
            ("Despesas (R$)", f"{expenses:.2f}"),
            ("Lucro (R$)", f"{lucro:.2f}"),
            ("Valor p/ pass.", f"{fare:.2f}"),
            ("Qtd. passageiros", str(count)),
            ("Total KM", f"{total_km:.2f}"),
            ("Início", self.format_date(getattr(trip, "start_date", ""))),
            ("Fim", self.format_date(getattr(trip, "end_date", "")))
        ]

        info_grid = tk.Frame(scrollable_frame, bg=self.bg_main)
        info_grid.pack(padx=20, pady=5, fill="x")

        for idx, (label_text, value_text) in enumerate(detalhes):
            row = idx // 2
            col = (idx % 2) * 2

            tk.Label(
                info_grid, text=label_text + ":", font=("Segoe UI", 8, "bold"),
                bg=self.bg_main, fg="#8e8e93"
            ).grid(row=row, column=col, sticky="e", padx=(10, 5), pady=2)

            color = self.fg_text
            if "Lucro" in label_text:
                color = "#00ff7f"
            elif "Despesas" in label_text:
                color = "#ff4c4c"

            lbl_val = tk.Label(
                info_grid, text=value_text, font=("Segoe UI", 9, "bold"),
                bg=self.bg_button, fg=color, width=18, anchor="w", padx=8, pady=2
            )
            lbl_val.grid(row=row, column=col + 1, sticky="w", pady=2)

        desc_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        desc_frame.pack(padx=20, pady=5, fill="x")

        tk.Label(
            desc_frame, text="Descrição:", font=("Segoe UI", 8, "bold"),
            bg=self.bg_main, fg="#8e8e93"
        ).pack(anchor="w", padx=10)

        tk.Label(
            desc_frame, text=(getattr(trip, "description", "") or "---").upper(),
            font=("Segoe UI", 9), bg=self.bg_button, fg=self.fg_text,
            anchor="w", padx=10, pady=5, wraplength=600, justify="left"
        ).pack(fill="x", padx=10, pady=2)

        tk.Label(
            scrollable_frame, text="Motoristas escalados", font=("Segoe UI", 10, "bold"),
            bg=self.bg_main, fg=self.accent
        ).pack(pady=(10, 5))

        tree_container = tk.Frame(scrollable_frame, bg=self.bg_main)
        tree_container.pack(padx=20, fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25,
                        background="#2c2c2e", fieldbackground="#2c2c2e", foreground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background="#3a3f47", foreground="#ffffff", borderwidth=1)

        self.tree_drivers = ttk.Treeview(
            tree_container, columns=("Nome", "Contato", "Salario"), show="headings", height=3
        )
        self.tree_drivers.heading("Nome", text="Nome")
        self.tree_drivers.heading("Contato", text="Contato")
        self.tree_drivers.heading("Salario", text="Salário (R$)")
        self.tree_drivers.column("Nome", width=250)
        self.tree_drivers.column("Contato", width=150)
        self.tree_drivers.column("Salario", width=120)
        self.tree_drivers.pack(fill="x")

        driver_ids = self.trip_driver_repo.get_driver_ids_by_trip(self.trip_id)
        for d_id in driver_ids:
            d = self.driver_repo.get_by_id(d_id)
            if d:
                self.tree_drivers.insert("", "end", values=(d.name.upper(), d.contact, f"{d.salary:.2f}"))

        btn_container = tk.Frame(scrollable_frame, bg=self.bg_main)
        btn_container.pack(fill="x", pady=15)

        btns_inner = tk.Frame(btn_container, bg=self.bg_main)
        btns_inner.pack(expand=True)

        ListRoundedButton(
            btns_inner, text="Voltar", command=self.voltar,
            width=150, height=35, bg="#3a3f47", fg=self.fg_text
        ).pack(side="left")

    def format_date(self, date_value):
        if not date_value: return "---"
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                return date_value
        return date_value.strftime("%d/%m/%Y") if hasattr(date_value, "strftime") else str(date_value)

    def voltar(self):
        from app.interface.trip.interface_viagens import InterfaceViagem
        InterfaceViagem(self.parent, self.db_path).show()