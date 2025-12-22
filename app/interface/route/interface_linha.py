import tkinter as tk
from tkinter import ttk, messagebox

from app.interface.route.interface_expense_payments import InterfaceRouteExpensePayments
from app.interface.route.interface_extra_payments import InterfaceRouteExtraPayments
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.interface.route.interface_cadastrar_linha import InterfaceCadastrarLinha
from app.interface.route.interface_editar_linha import InterfaceEditarLinha
from app.components.list_rounded_button import ListRoundedButton

class InterfaceLinha:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.route_repo = RouteRepository(self.db_path)
        self.vehicle_repo = VehicleRepository(self.db_path)

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
        header_frame.pack(pady=(15, 5), padx=25, fill="x")

        tk.Label(
            header_frame,
            text="Linhas de transporte",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=25, pady=5, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=28,
                        background=self.bg_field,
                        fieldbackground=self.bg_field,
                        foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background=self.accent,
                        foreground="#ffffff",
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Nome", "Placa", "Km", "Periodo", "Tempo", "Status"),
            show="headings",
            height=12
        )

        headers = [
            ("Nome", 180, "w"),
            ("Placa", 100, "center"),
            ("Km", 90, "center"),
            ("Periodo", 100, "center"),
            ("Tempo", 110, "center"),
            ("Status", 90, "center")
        ]

        for col, width, anchor in headers:
            self.tree.heading(col, text=col )
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=15, fill="x")

        inner_btn_frame = tk.Frame(button_frame, bg=self.bg_main)
        inner_btn_frame.pack(anchor="center")

        actions = [
            ("Novo", self.cadastrar_linha, self.accent),
            ("Editar", self.editar_linha, self.bg_button),
            ("Pagos extras", self.adicionar_pagamento_extra, self.bg_button),
            ("Despesas", self.adicionar_despesa_extra, self.bg_button),
            ("Alunos", self.abrir_alunos, self.bg_button),
            ("Detalhes", self.abrir_detalhes, self.bg_button),
            ("Excluir", self.confirm_delete, "#b3261e")
        ]

        for text, cmd, color in actions:
            ListRoundedButton(
                inner_btn_frame,
                text=text,
                command=cmd,
                width=115,
                height=38,
                bg=color,
                fg=self.fg_text,
                font=("Segoe UI", 8, "bold")
            ).pack(side="left", padx=3)

        self.load_linhas()

    def load_linhas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        linhas = self.route_repo.get_all()
        for linha in linhas:
            route_id = getattr(linha, 'route_id', None)
            if not route_id: continue

            vehicle_id = getattr(linha, 'vehicle_id', None)
            plate = self.get_vehicle_plate(vehicle_id) if vehicle_id else "N/A"

            self.tree.insert("", "end", iid=str(route_id), values=(
                getattr(linha, 'name', '').upper(),
                plate,
                f"{float(getattr(linha, 'avg_km', 0.0)):.1f} KM",
                getattr(linha, 'period', '').upper(),
                f"{getattr(linha, 'avg_time_minutes', '')} MIN",
                "ATIVO" if getattr(linha, 'active', 0) else "INATIVO"
            ))

    def get_vehicle_plate(self, vehicle_id):
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        return getattr(vehicle, 'license_plate', 'N/A') if vehicle else 'N/A'

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            InterfaceEditarLinha(self.parent, self.db_path, int(item)).show()

    def cadastrar_linha(self):
        InterfaceCadastrarLinha(self.parent, self.db_path).show()

    def abrir_detalhes(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        from app.interface.route.interface_route_details import InterfaceDetalhesLinha
        InterfaceDetalhesLinha(self.parent, self.db_path, int(selected[0])).show()

    def confirm_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return

        rid = int(selected[0])
        name = self.tree.item(rid, "values")[0]
        if messagebox.askyesno("Confirmação", f"Excluir a linha '{name}'?"):
            if self.route_repo.delete(rid):
                self.load_linhas()

    def editar_linha(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        InterfaceEditarLinha(self.parent, self.db_path, int(selected[0])).show()

    def adicionar_pagamento_extra(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        rid = int(selected[0])
        name = self.route_repo.get_by_id(rid).name
        InterfaceRouteExtraPayments(self.parent, self.db_path, rid, name).show()

    def adicionar_despesa_extra(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        rid = int(selected[0])
        name = self.route_repo.get_by_id(rid).name
        InterfaceRouteExpensePayments(self.parent, self.db_path, rid, name).show()

    def abrir_alunos(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        from app.interface.route.interface_route_students import InterfaceRouteStudents
        rid = int(selected[0])
        name = self.route_repo.get_by_id(rid).name
        InterfaceRouteStudents(self.parent, self.db_path, rid, name).show()