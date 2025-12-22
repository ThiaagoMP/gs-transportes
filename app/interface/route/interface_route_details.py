import tkinter as tk
from tkinter import ttk
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
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(pady=(15, 10), padx=25, fill="x")

        tk.Label(
            header_frame,
            text=f"DETALHES DA LINHA: {self.route.name.upper()}",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(side="left")

        main_container = tk.Frame(self.parent, bg=self.bg_main)
        main_container.pack(padx=25, pady=5, fill="both", expand=True)

        left_frame = tk.Frame(main_container, bg=self.bg_main)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        vehicle = self.vehicle_repo.get_by_id(self.route.vehicle_id)
        v_name = getattr(vehicle, 'name', 'N/A')
        v_plate = getattr(vehicle, 'license_plate', 'N/A')
        consumo = getattr(vehicle, 'avg_km_per_liter', 1) or 1

        qtd_alunos = self.student_repo.count_students_in_route(self.route.route_id)
        salarios = self.driver_repo.sum_driver_salaries_by_route(self.route.route_id)

        faturamento = qtd_alunos * self.route.contract_value
        custo_comb = (self.route.avg_km / consumo) * 6.0
        despesas = salarios + custo_comb
        lucro = faturamento - despesas

        detalhes = [
            ("VEÍCULO", f"{v_name.upper()} ({v_plate.upper()})", self.fg_text),
            ("KM MÉDIO", f"{self.route.avg_km:.2f} KM", self.fg_text),
            ("PERÍODO / TEMPO", f"{self.route.period.upper()} - {self.route.avg_time_minutes} MIN", self.fg_text),
            ("STATUS", "ATIVO" if self.route.active else "INATIVO", self.fg_text),
            ("ALUNOS ATIVOS", str(qtd_alunos), self.fg_text),
            ("FATURAMENTO", f"R$ {faturamento:.2f}", "#ffa500"),
            ("DESPESAS PREVISTAS", f"R$ {despesas:.2f}", "#ff4c4c"),
            ("LUCRO ESTIMADO", f"R$ {lucro:.2f}", "#00ff7f")
        ]

        for lbl_txt, val_txt, color in detalhes:
            row = tk.Frame(left_frame, bg=self.bg_main)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=f"{lbl_txt}:", font=("Segoe UI", 9, "bold"),
                     bg=self.bg_main, fg="#8e8e93", width=18, anchor="e").pack(side="left", padx=5)

            tk.Label(row, text=val_txt, font=("Segoe UI", 10),
                     bg=self.bg_field, fg=color, anchor="w", padx=10).pack(side="left", fill="x", expand=True, ipady=3)

        right_frame = tk.Frame(main_container, bg=self.bg_main)
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="MOTORISTAS ESCALADOS", font=("Segoe UI", 10, "bold"),
                 bg=self.bg_main, fg=self.accent).pack(pady=(0, 5), anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=28,
                        background=self.bg_field, fieldbackground=self.bg_field, foreground=self.fg_text, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background=self.accent, foreground=self.fg_text)

        tree_container = tk.Frame(right_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        self.tree_drivers = ttk.Treeview(tree_container, columns=("Nome", "Salario"), show="headings", height=8)
        self.tree_drivers.heading("Nome", text="Nome")
        self.tree_drivers.heading("Salario", text="Salário")
        self.tree_drivers.column("Nome", width=180, anchor="w")
        self.tree_drivers.column("Salario", width=90, anchor="e")

        scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_drivers.yview)
        self.tree_drivers.configure(yscrollcommand=scroll.set)
        self.tree_drivers.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        d_ids = self.route_driver_repo.get_driver_ids_by_route(self.route.route_id)
        for d_id in d_ids:
            d = self.driver_repo.get_by_id(d_id)
            if d:
                self.tree_drivers.insert("", "end", values=(d.name.upper(), f"R$ {d.salary:.2f}"))

        btn_container = tk.Frame(self.parent, bg=self.bg_main)
        btn_container.pack(pady=20)

        ListRoundedButton(
            btn_container,
            text="Voltar para listagem",
            command=self.voltar,
            width=200,
            height=40,
            bg=self.bg_button,
            fg=self.fg_text,
            font=("Segoe UI", 9, "bold")
        ).pack()

    def voltar(self):
        from app.interface.route.interface_linha import InterfaceLinha
        InterfaceLinha(self.parent, self.db_path).show()