import tkinter as tk
from tkinter import ttk, messagebox
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.route_expense_payment_repository import RouteExpensePaymentRepository
from app.repositories.route_extra_payment_repository import RouteExtraPaymentRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_driver_repository import RouteDriverRepository


class InterfaceDetalhesLinha:
    def __init__(self, parent, db_path, route_id):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id

        self.route_repo = RouteRepository(db_path)
        self.vehicle_repo = VehicleRepository(db_path)
        self.student_repo = RouteStudentRepository(db_path)
        self.expense_repo = RouteExpensePaymentRepository(db_path)
        self.extra_repo = RouteExtraPaymentRepository(db_path)
        self.driver_repo = DriverRepository(db_path)
        self.route_driver_repo = RouteDriverRepository(db_path)

        self.route = self.route_repo.get_by_id(route_id)

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
            text="Detalhes da Linha",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 10))

        frame = tk.Frame(self.parent, bg=self.bg_main)
        frame.pack(padx=40, pady=10, fill="both", expand=True)

        vehicle = self.vehicle_repo.get_by_id(self.route.vehicle_id)
        vehicle_name = getattr(vehicle, 'name', 'Desconhecido')
        vehicle_plate = getattr(vehicle, 'license_plate', 'N/A')
        consumo_medio = getattr(vehicle, 'avg_km_per_liter', 1)

        qtd_alunos = self.student_repo.count_students_in_route(self.route.route_id)
        salario_motoristas = self.driver_repo.sum_driver_salaries_by_route(self.route.route_id)

        faturamento_esperado = qtd_alunos * self.route.contract_value
        despesas_esperadas = salario_motoristas + (self.route.avg_km / consumo_medio)
        lucro_esperado = faturamento_esperado - despesas_esperadas

        detalhes = {
            "Nome da Linha": self.route.name,
            "Veículo Associado": f"{vehicle_name} ({vehicle_plate})",
            "Km Médio": f"{self.route.avg_km:.2f} km",
            "Período": self.route.period,
            "Tempo Médio (min)": str(self.route.avg_time_minutes),
            "Contrato Ativo": "Sim" if self.route.active else "Não",
            "Valor do Contrato (R$)": f"{self.route.contract_value:.2f}",
            "Quantidade de Alunos": str(qtd_alunos),
            "Faturamento Esperado (R$)": f"{faturamento_esperado:.2f}",
            "Despesas Esperadas (R$)": f"{despesas_esperadas:.2f}",
            "Lucro Esperado (R$)": f"{lucro_esperado:.2f}",
        }

        for i, (label_text, value_text) in enumerate(detalhes.items()):
            tk.Label(
                frame,
                text=label_text + ":",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_main,
                fg=self.fg_text
            ).grid(row=i, column=0, sticky="e", padx=(10, 10), pady=5)

            color = self.fg_text
            if "Lucro" in label_text:
                color = "#00ff7f"
            elif "Despesas" in label_text:
                color = "#ff4c4c"
            elif "Faturamento" in label_text:
                color = "#ffa500"

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
            text="Motoristas da Linha:",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 5))

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

        driver_ids = self.route_driver_repo.get_driver_ids_by_route(self.route.route_id)
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

    def voltar(self):
        from app.interface.route.interface_linha import InterfaceLinha
        interface = InterfaceLinha(self.parent, self.db_path)
        interface.show()
