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
            text="Lista de Viagens",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=("Segoe UI", 12),
            background=self.bg_main,
            fieldbackground=self.bg_main,
            foreground=self.fg_text
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 13, "bold"),
            background=self.accent,
            foreground="#ffffff"
        )
        style.map(
            "Treeview",
            background=[("selected", "#333333")],
            foreground=[("selected", "#ffffff")]
        )

        # Frame container para Treeview + Scrollbar
        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(
            tree_container,
            columns=("Veículo", "Faturamento Bruto", "Despesas", "Lucro", "Data de Início", "Data de Fim", "Descrição"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Veículo", 150),
            ("Faturamento Bruto", 160),
            ("Despesas", 120),
            ("Lucro", 120),
            ("Data de Início", 140),
            ("Data de Fim", 140),
            ("Descrição", 250)
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Posicionando Treeview e Scrollbar corretamente
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self.on_double_click)

        # Botões
        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Cadastrar Viagem", self.cadastrar_viagem),
            ("Editar Viagem", self.editar_viagem),
            ("Excluir Viagem", self.confirm_delete),
            ("Detalhes", self.abrir_detalhes)
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=210,
                height=50,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold")
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_trips()

    def load_trips(self):
        self.tree.delete(*self.tree.get_children())
        trips = self.trip_repo.get_all()

        for trip in trips:
            trip_id = getattr(trip, 'trip_id', None)
            if trip_id is None or not str(trip_id).strip():
                continue

            # Buscar placa do veículo
            vehicle_id = getattr(trip, 'vehicle_id', None)
            placa = "Desconhecido"
            if vehicle_id:
                vehicle = self.vehicle_repo.get_by_id(vehicle_id)
                if vehicle and getattr(vehicle, "license_plate", None):
                    placa = vehicle.license_plate

            # Calcular faturamento, despesas e lucro
            passenger_fare = float(getattr(trip, 'passenger_fare', 0.0) or 0)
            passenger_count = int(getattr(trip, 'passenger_count', 0) or 0)
            expenses = float(getattr(trip, 'additional_expenses', 0.0) or 0)

            faturamento_bruto = passenger_fare * passenger_count
            lucro = faturamento_bruto - expenses

            # Datas formatadas
            start_date_display = self.format_date(getattr(trip, 'start_date', ''))
            end_date_display = self.format_date(getattr(trip, 'end_date', ''))

            descricao = getattr(trip, 'description', '') or '-'

            self.tree.insert("", "end", iid=str(trip_id), values=(
                placa,
                f"{faturamento_bruto:.2f}",
                f"{expenses:.2f}",
                f"{lucro:.2f}",
                start_date_display,
                end_date_display,
                descricao
            ))

    def format_date(self, date_value):
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                return date_value
        elif isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        return str(date_value)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                trip_id = int(item)
                from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
                interface = InterfaceEditarViagem(self.parent, self.db_path, trip_id)
                interface.show()
            except ValueError:
                messagebox.showerror("Erro", "ID da viagem inválido.")

    def cadastrar_viagem(self):
        try:
            from app.interface.trip.interface_cadastrar_viagem import InterfaceCadastrarViagem
            interface = InterfaceCadastrarViagem(self.parent, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o cadastro: {str(e)}")

    def editar_viagem(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma viagem para editar.")
            return
        try:
            trip_id = int(selected_item[0])
            from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
            interface = InterfaceEditarViagem(self.parent, self.db_path, trip_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID da viagem inválido.")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma viagem para excluir.")
            return

        trip_id = selected_item[0]
        try:
            trip_id = int(trip_id)
        except ValueError:
            messagebox.showerror("Erro", "ID inválido.")
            return

        if messagebox.askyesno("Confirmação", f"Deseja realmente excluir a viagem com ID {trip_id}?"):
            if self.trip_repo.delete(trip_id):
                messagebox.showinfo("Sucesso", "Viagem excluída com sucesso!")
                self.load_trips()
            else:
                messagebox.showerror("Erro", "Falha ao excluir a viagem.")

    def abrir_detalhes(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma viagem para ver os detalhes.")
            return
        try:
            trip_id = int(selected_item[0])
            from app.interface.trip.interface_trip_details import InterfaceTripDetails
            interface = InterfaceTripDetails(self.parent, self.db_path, trip_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID da viagem inválido.")
