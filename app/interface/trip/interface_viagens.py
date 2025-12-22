import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.components.list_rounded_button import ListRoundedButton

class InterfaceViagem:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.trip_repo = TripRepository(self.db_path)
        self.vehicle_repo = VehicleRepository(self.db_path)

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
            text="Lista de viagens",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=10)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True, padx=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=30,
            background="#2c2c2e",
            fieldbackground="#2c2c2e",
            foreground=self.fg_text,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=self.accent,
            foreground="#ffffff",
            borderwidth=1
        )
        style.map(
            "Treeview",
            background=[("selected", self.accent)],
            foreground=[("selected", "#ffffff")]
        )

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Veiculo", "Bruto", "Despesas", "Lucro", "Inicio", "Fim", "Desc"),
            show="headings",
            selectmode="browse"
        )

        col_defs = [
            ("Veiculo", "Veículo", 100),
            ("Bruto", "Bruto (R$)", 100),
            ("Despesas", "Despesas (R$)", 100),
            ("Lucro", "Lucro (R$)", 100),
            ("Inicio", "Início", 95),
            ("Fim", "Fim", 95),
            ("Desc", "Descrição", 180)
        ]

        for col_id, text, width in col_defs:
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, anchor="center" if col_id != "Desc" else "w")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(self.parent, bg=self.bg_main)
        button_frame.pack(fill="x", pady=20)

        btns_inner = tk.Frame(button_frame, bg=self.bg_main)
        btns_inner.pack(expand=True)

        actions = [
            ("Nova viagem", self.cadastrar_viagem, self.accent),
            ("Editar", self.editar_viagem, self.bg_button),
            ("Detalhes", self.abrir_detalhes, self.bg_button),
            ("Excluir", self.confirm_delete, "#b00020")
        ]

        for text, cmd, color in actions:
            ListRoundedButton(
                btns_inner,
                text=text,
                command=cmd,
                width=150,
                height=38,
                bg=color,
                fg=self.fg_text
            ).pack(side="left", padx=8)

        self.load_trips()

    def load_trips(self):
        self.tree.delete(*self.tree.get_children())
        try:
            trips = self.trip_repo.get_all()
            for trip in trips:
                trip_id = getattr(trip, 'trip_id', None)
                if not trip_id: continue

                vehicle_id = getattr(trip, 'vehicle_id', None)
                placa = "-"
                if vehicle_id:
                    vehicle = self.vehicle_repo.get_by_id(vehicle_id)
                    if vehicle:
                        placa = getattr(vehicle, "license_plate", "-").upper()

                fare = float(getattr(trip, 'passenger_fare', 0) or 0)
                count = int(getattr(trip, 'passenger_count', 0) or 0)
                exp = float(getattr(trip, 'additional_expenses', 0) or 0)

                bruto = fare * count
                lucro = bruto - exp

                start = self.format_date(getattr(trip, 'start_date', ''))
                end = self.format_date(getattr(trip, 'end_date', ''))
                desc = (getattr(trip, 'description', '') or '-').upper()

                self.tree.insert("", "end", iid=str(trip_id), values=(
                    placa,
                    f"{bruto:.2f}",
                    f"{exp:.2f}",
                    f"{lucro:.2f}",
                    start,
                    end,
                    desc
                ))
        except Exception:
            pass

    def format_date(self, date_value):
        if not date_value: return "-"
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                return date_value
        return date_value.strftime('%d/%m/%Y') if hasattr(date_value, 'strftime') else str(date_value)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
            InterfaceEditarViagem(self.parent, self.db_path, int(item)).show()

    def cadastrar_viagem(self):
        from app.interface.trip.interface_cadastrar_viagem import InterfaceCadastrarViagem
        InterfaceCadastrarViagem(self.parent, self.db_path).show()

    def editar_viagem(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma viagem.")
            return
        from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
        InterfaceEditarViagem(self.parent, self.db_path, int(sel[0])).show()

    def confirm_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma viagem.")
            return
        if messagebox.askyesno("Confirmar", "Deseja excluir permanentemente esta viagem?"):
            if self.trip_repo.delete(int(sel[0])):
                self.load_trips()

    def abrir_detalhes(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma viagem.")
            return
        from app.interface.trip.interface_trip_details import InterfaceTripDetails
        InterfaceTripDetails(self.parent, self.db_path, int(sel[0])).show()