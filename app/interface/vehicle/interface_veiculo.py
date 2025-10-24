import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from app.components.list_rounded_button import ListRoundedButton
from app.repositories.vehicle_repository import VehicleRepository
from app.interface.vehicle.interface_cadastrar_veiculo import InterfaceCadastrarVeiculo
from app.interface.vehicle.interface_cadastrar_abastecimento import InterfaceAddRefueling
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
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Veículos",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 12), background=self.bg_main,
                        fieldbackground=self.bg_main, foreground=self.fg_text)
        style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"), background=self.accent, foreground="#ffffff")
        style.map("Treeview", background=[("selected", "#333333")], foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(list_frame, columns=(
            "Placa", "Nome", "Assentos", "Km/L", "Tanque (L)", "Data Compra",
            "Data Venda", "Valor Compra", "Valor Venda", "Ano Fabricação"
        ), show="headings", height=15)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Cadastrar Veículo", self.cadastrar_veiculo),
            ("Editar Veículo", self.editar_veiculo),
            ("Manutenções", self.adicionar_manutencao),
            ("Abastecimentos", self.adicionar_abastecimento),
            ("Excluir Veículo", self.confirm_delete)
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
                font=("Segoe UI", 11, "bold"),
                shadow=True
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_vehicles()

    def load_vehicles(self):
        self.tree.delete(*self.tree.get_children())
        vehicles = self.vehicle_repo.get_all()

        def sort_key(vehicle):
            buy_date = getattr(vehicle, 'buy_date', '')
            if buy_date and isinstance(buy_date, str):
                try:
                    buy_date = datetime.strptime(buy_date, '%Y-%m-%d')
                except ValueError:
                    buy_date = datetime.min
            else:
                buy_date = datetime.min
            sell_date = getattr(vehicle, 'sell_date', None)
            is_sold = sell_date not in [None, ""] and sell_date != "Não vendido"
            return (is_sold, buy_date)

        vehicles = sorted(vehicles, key=sort_key)

        for vehicle in vehicles:
            vehicle_id = getattr(vehicle, 'vehicle_id', None)
            if vehicle_id is None or not str(vehicle_id).strip():
                continue

            buy_date = getattr(vehicle, 'buy_date', '') or ''
            if buy_date and isinstance(buy_date, str):
                buy_date = datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            sell_date = getattr(vehicle, 'sell_date', None)
            if sell_date and isinstance(sell_date, str):
                sell_date = datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            elif sell_date is None:
                sell_date = "Não vendido"

            purchase_value = getattr(vehicle, 'purchase_value', None)
            purchase_value_str = f"{float(purchase_value):.2f}" if purchase_value else "0.00"

            sale_value = getattr(vehicle, 'sale_value', None)
            sale_value_valid = sale_value is not None and isinstance(sale_value, (int, float, str)) and str(
                sale_value).replace('.', '').isdigit()
            sell_date_valid = sell_date not in ["Não vendido", None]

            if sale_value_valid and not sell_date_valid or not sale_value_valid and sell_date_valid:
                sale_value_str = "Não vendido"
                sell_date = "Não vendido"
            else:
                if sale_value_valid:
                    sale_value_str = f"{float(sale_value):.2f}"
                else:
                    sale_value_str = "Não vendido"

            self.tree.insert("", "end", iid=str(vehicle_id), values=(
                getattr(vehicle, 'license_plate', ''),
                getattr(vehicle, 'name', ''),
                getattr(vehicle, 'seats', ''),
                f"{float(getattr(vehicle, 'avg_km_per_liter', 0.0)):.1f}" if getattr(vehicle, 'avg_km_per_liter',
                                                                                     None) else '0.0',
                getattr(vehicle, 'fuel_tank_size', ''),
                buy_date,
                sell_date,
                purchase_value_str,
                sale_value_str,
                getattr(vehicle, 'manufacturing_year', '')
            ))

    def cadastrar_veiculo(self):
        interface = InterfaceCadastrarVeiculo(self.parent, self.db_path)
        interface.show()

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para excluir.")
            return
        vehicle_id = int(selected_item[0])
        vehicle_name = self.tree.item(vehicle_id, "values")[1]
        if messagebox.askyesno("Confirmação", f"Deseja excluir o veículo '{vehicle_name}'?"):
            if self.vehicle_repo.delete(vehicle_id):
                messagebox.showinfo("Sucesso", f"Veículo '{vehicle_name}' excluído!")
                self.load_vehicles()
            else:
                messagebox.showerror("Erro", "Falha ao excluir veículo.")

    def editar_veiculo(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        vehicle_id = int(selected_item[0])
        interface = InterfaceEditarVeiculo(self.parent, self.db_path, vehicle_id)
        interface.show()

    def adicionar_manutencao(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        vehicle_id = int(selected_item[0])
        vehicle_name = self.vehicle_repo.get_by_id(vehicle_id).name
        from app.interface.vehicle.interface_manutencao import InterfaceMaintenance
        interface = InterfaceMaintenance(self.parent, self.db_path, vehicle_id, vehicle_name)
        interface.show()

    def adicionar_abastecimento(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        vehicle_id = int(selected_item[0])
        vehicle_name = self.vehicle_repo.get_by_id(vehicle_id).name
        from app.interface.vehicle.interface_abastecimento import InterfaceFueling
        interface = InterfaceFueling(self.parent, self.db_path, vehicle_id, vehicle_name)
        interface.show()

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            vehicle_id = int(item)
            interface = InterfaceEditarVeiculo(self.parent, self.db_path, vehicle_id)
            interface.show()
