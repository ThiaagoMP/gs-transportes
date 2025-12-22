import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# Mantendo seus imports originais
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.vehicle_repository import VehicleRepository
from app.interface.vehicle.interface_cadastrar_veiculo import InterfaceCadastrarVeiculo
from app.interface.vehicle.interface_editar_veiculo import InterfaceEditarVeiculo


class InterfaceListVehicles:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_repo = VehicleRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        # CORREÇÃO: Limpa absolutamente tudo antes de começar
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        # Cabeçalho
        self.header = tk.Frame(self.parent, bg=self.bg_main, height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        tk.Label(
            self.header,
            text="Veículos",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).place(relx=0.02, rely=0.5, anchor="w")

        self.main_frame = tk.Frame(self.parent, bg=self.bg_main)
        self.main_frame.pack(fill="both", expand=True)

        self.build_table()
        self.build_buttons()
        self.load_vehicles()

    def build_table(self):
        list_frame = tk.Frame(self.main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=("Segoe UI", 11),
            background=self.bg_main,
            fieldbackground=self.bg_main,
            foreground=self.fg_text,
            rowheight=30
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background=self.accent,
            foreground="#ffffff"
        )
        style.map(
            "Treeview",
            background=[("selected", "#333333")],
            foreground=[("selected", "#ffffff")]
        )

        # Frame para conter a Treeview e as Scrollbars
        tree_container = tk.Frame(list_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_container, orient="vertical")
        y_scroll.pack(side="right", fill="y")

        x_scroll = ttk.Scrollbar(tree_container, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            tree_container,
            columns=(
                "Placa", "Nome", "Assentos", "Km/L", "Tanque (L)",
                "Data Compra", "Data Venda", "Valor Compra",
                "Valor Venda", "Ano Fabricação"
            ),
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        self.tree.pack(fill="both", expand=True)

        # Configuração das colunas com largura mínima e permissão para esticar
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            # minwidth permite que a barra horizontal apareça se a janela for muito pequena
            self.tree.column(col, width=115, minwidth=100, anchor="center", stretch=True)

        self.tree.bind("<Double-1>", self.on_double_click)

    def build_buttons(self):
        # Frame que centraliza os botões e permite que eles respirem
        button_container = tk.Frame(self.main_frame, bg=self.bg_main)
        button_container.pack(fill="x", pady=15)

        button_frame = tk.Frame(button_container, bg=self.bg_main)
        button_frame.pack(expand=True)

        actions = [
            ("Cadastrar Veículo", self.cadastrar_veiculo),
            ("Editar Veículo", self.editar_veiculo),
            ("Detalhes", self.vehicle_details),
            ("Manutenções", self.adicionar_manutencao),
            ("Abastecimentos", self.adicionar_abastecimento),
            ("Excluir Veículo", self.confirm_delete)
        ]

        for i, (text, cmd) in enumerate(actions):
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
            # Reduzido largura de 210 para 165 e fonte para 10 para caber em telas menores
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=165,
                height=45,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 10, "bold"),
                shadow=True
            )
            btn.grid(row=0, column=i, padx=5, pady=5)

    def load_vehicles(self):
        self.tree.delete(*self.tree.get_children())
        vehicles = self.vehicle_repo.get_all()

        def sort_key(vehicle):
            buy_date_str = getattr(vehicle, 'buy_date', '')
            try:
                buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d') if buy_date_str else datetime.min
            except Exception:
                buy_date = datetime.min
            sell_date = getattr(vehicle, 'sell_date', None)
            is_sold = sell_date not in [None, "", "Não vendido"]
            return (is_sold, buy_date)

        for vehicle in sorted(vehicles, key=sort_key):
            vehicle_id = getattr(vehicle, 'vehicle_id', None)
            if not vehicle_id:
                continue

            buy_date = getattr(vehicle, 'buy_date', '')
            if buy_date:
                try:
                    buy_date = datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass

            sell_date = getattr(vehicle, 'sell_date', None)
            if sell_date and sell_date != "Não vendido":
                try:
                    sell_date = datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass
            else:
                sell_date = "Não vendido"

            purchase_val = getattr(vehicle, 'purchase_value', 0)
            sale_val = getattr(vehicle, 'sale_value', 0)

            p_format = f"{float(purchase_val):.2f}" if purchase_val else "0.00"
            s_format = f"{float(sale_val):.2f}" if (sale_val and sell_date != "Não vendido") else "Não vendido"

            self.tree.insert("", "end", iid=str(vehicle_id), values=(
                getattr(vehicle, 'license_plate', ''),
                getattr(vehicle, 'name', ''),
                getattr(vehicle, 'seats', ''),
                f"{float(getattr(vehicle, 'avg_km_per_liter', 0)):.1f}",
                getattr(vehicle, 'fuel_tank_size', ''),
                buy_date,
                sell_date,
                p_format,
                s_format,
                getattr(vehicle, 'manufacturing_year', '')
            ))

    def cadastrar_veiculo(self):
        InterfaceCadastrarVeiculo(self.parent, self.db_path).show()

    def editar_veiculo(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar.")
            return
        InterfaceEditarVeiculo(self.parent, self.db_path, int(selected[0])).show()

    def confirm_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um veículo para excluir.")
            return
        vehicle_id = int(selected[0])
        name = self.tree.item(selected[0], "values")[1]
        if messagebox.askyesno("Confirmação", f"Deseja excluir o veículo '{name}'?"):
            if self.vehicle_repo.delete(vehicle_id):
                self.load_vehicles()

    def adicionar_manutencao(self):
        selected = self.tree.selection()
        if not selected:
            return
        vehicle_id = int(selected[0])
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        from app.interface.vehicle.interface_manutencao import InterfaceMaintenance
        InterfaceMaintenance(self.parent, self.db_path, vehicle_id, vehicle.name).show()

    def adicionar_abastecimento(self):
        selected = self.tree.selection()
        if not selected:
            return
        vehicle_id = int(selected[0])
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        from app.interface.vehicle.interface_abastecimento import InterfaceFueling
        InterfaceFueling(self.parent, self.db_path, vehicle_id, vehicle.name).show()

    def vehicle_details(self):
        selected = self.tree.selection()
        if not selected:
            return
        from app.interface.vehicle.interface_vehicle_details import InterfaceVehicleDetails
        InterfaceVehicleDetails(self.parent, self.db_path, int(selected[0])).show()

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            InterfaceEditarVeiculo(self.parent, self.db_path, int(item)).show()