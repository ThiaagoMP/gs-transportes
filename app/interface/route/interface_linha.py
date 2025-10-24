import tkinter as tk
from tkinter import ttk, messagebox

from app.interface.route.interface_expense_payments import InterfaceRouteExpensePayments
from app.interface.route.interface_extra_payments import InterfaceRouteExtraPayments
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.interface.route.interface_cadastrar_linha import InterfaceCadastrarLinha
from app.interface.route.interface_editar_linha import InterfaceEditarLinha
from app.interface.route.interface_adicionar_pagamento_extra import InterfaceAddExtraPayment
from app.interface.route.interface_adicionar_despesa_extra import InterfaceAddExpensePayment
from app.components.list_rounded_button import ListRoundedButton


class InterfaceLinha:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.route_repo = RouteRepository(self.db_path)
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
            text="Linhas",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 12),
                        background=self.bg_main,
                        fieldbackground=self.bg_main,
                        foreground=self.fg_text,
                        rowheight=28)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 13, "bold"),
                        background=self.accent,
                        foreground="#ffffff")
        style.map("Treeview",
                  background=[("selected", "#333333")],
                  foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(
            list_frame,
            columns=("Nome", "Placa do Veículo", "Km Médio", "Período", "Tempo Médio (min)", "Ativo"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Nome", 150),
            ("Placa do Veículo", 120),
            ("Km Médio", 80),
            ("Período", 100),
            ("Tempo Médio (min)", 130),
            ("Ativo", 80),
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Cadastrar Linha", self.cadastrar_linha),
            ("Editar Linha", self.editar_linha),
            ("Pagamentos Extras", self.adicionar_pagamento_extra),
            ("Despesas Extras", self.adicionar_despesa_extra),
            ("Excluir Linha", self.confirm_delete)
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith(
                "Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=210,
                height=50,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold"),
                shadow=True
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_linhas()

    def load_linhas(self):
        self.tree.delete(*self.tree.get_children())
        linhas = self.route_repo.get_all()
        for linha in linhas:
            route_id = getattr(linha, 'route_id', None)
            if not route_id:
                continue

            vehicle_id = getattr(linha, 'vehicle_id', None)
            vehicle_plate = self.get_vehicle_plate(vehicle_id) if vehicle_id else "N/A"

            self.tree.insert("", "end", iid=str(route_id), values=(
                getattr(linha, 'name', ''),
                vehicle_plate,
                f"{float(getattr(linha, 'avg_km', 0.0)):.1f}" if getattr(linha, 'avg_km', None) is not None else '0.0',
                getattr(linha, 'period', ''),
                getattr(linha, 'avg_time_minutes', ''),
                "Sim" if getattr(linha, 'active', 0) else "Não"
            ))

    def get_vehicle_plate(self, vehicle_id):
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        return getattr(vehicle, 'license_plate', 'N/A') if vehicle else 'N/A'

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                route_id = int(item)
                InterfaceEditarLinha(self.parent, self.db_path, route_id).show()
            except ValueError:
                messagebox.showerror("Erro", "ID da linha inválido.")

    def cadastrar_linha(self):
        try:
            InterfaceCadastrarLinha(self.parent, self.db_path).show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a interface de cadastro: {str(e)}")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma linha para excluir.")
            return

        route_id = selected_item[0]
        try:
            route_id = int(route_id)
        except ValueError:
            messagebox.showerror("Erro", "ID da linha inválido.")
            return

        linha_name = self.tree.item(route_id, "values")[0]
        if messagebox.askyesno("Confirmação", f"Excluir a linha '{linha_name}' (ID {route_id})?"):
            if self.route_repo.delete(route_id):
                messagebox.showinfo("Sucesso", f"Linha '{linha_name}' excluída com sucesso!")
                self.load_linhas()
            else:
                messagebox.showerror("Erro", "Falha ao excluir a linha.")

    def editar_linha(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma linha para editar.")
            return
        try:
            route_id = int(selected_item[0])
            InterfaceEditarLinha(self.parent, self.db_path, route_id).show()
        except ValueError:
            messagebox.showerror("Erro", "ID da linha inválido.")

    def adicionar_pagamento_extra(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        try:
            route_id = int(selected_item[0])
            route_name = self.route_repo.get_by_id(route_id).name
            InterfaceRouteExtraPayments(self.parent, self.db_path, route_id, route_name).show()
        except ValueError:
            messagebox.showerror("Erro", "ID inválido.")

    def adicionar_despesa_extra(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return
        try:
            route_id = int(selected_item[0])
            route_name = self.route_repo.get_by_id(route_id).name
            InterfaceRouteExpensePayments(self.parent, self.db_path, route_id, route_name).show()
        except ValueError:
            messagebox.showerror("Erro", "ID inválido.")
