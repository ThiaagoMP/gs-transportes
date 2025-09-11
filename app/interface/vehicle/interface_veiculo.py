import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry

from app.interface.vehicle.interface_cadastrar_viagem import InterfaceCadastrarViagem
from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle
from app.interface.vehicle.interface_cadastrar_veiculo import InterfaceCadastrarVeiculo
from app.interface.vehicle.interface_cadastrar_manutencao import InterfaceCadastrarManutencao
from app.interface.vehicle.interface_cadastrar_abastecimento import InterfaceCadastrarAbastecimento
from app.interface.vehicle.interface_editar_veiculo import InterfaceEditarVeiculo


class InterfaceVeiculo:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_repo = VehicleRepository(self.db_path)

    def show(self):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Veículos",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        # Frame principal
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Frame para a lista de veículos
        list_frame = tk.Frame(main_frame, bg="#ffffff")
        list_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")  # Tema compatível com Windows 7
        style.configure("Treeview", font=("Segoe UI", 12), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"), background="#2196f3", foreground="#ffffff")
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50",
                        foreground="#ffffff")
        style.map("Action.TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("Delete.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#f44336",
                        foreground="#ffffff")
        style.map("Delete.TButton",
                  background=[("active", "#e57373")],
                  foreground=[("active", "#ffffff")])

        # Treeview pra listar veículos
        self.tree = ttk.Treeview(list_frame, columns=("Placa", "Nome", "Assentos", "Km/L", "Tanque (L)", "Data Compra",
                                                      "Data Venda", "Valor Compra", "Valor Venda", "Ano Fabricação"),
                                 show="headings", height=15)
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Assentos", text="Assentos")
        self.tree.heading("Km/L", text="Km/L")
        self.tree.heading("Tanque (L)", text="Tanque (L)")
        self.tree.heading("Data Compra", text="Data Compra")
        self.tree.heading("Data Venda", text="Data Venda")
        self.tree.heading("Valor Compra", text="Valor Compra (R$)")
        self.tree.heading("Valor Venda", text="Valor Venda (R$)")
        self.tree.heading("Ano Fabricação", text="Ano Fabricação")
        self.tree.column("Placa", width=100)
        self.tree.column("Nome", width=150)
        self.tree.column("Assentos", width=70)
        self.tree.column("Km/L", width=70)
        self.tree.column("Tanque (L)", width=80)
        self.tree.column("Data Compra", width=100)
        self.tree.column("Data Venda", width=100)
        self.tree.column("Valor Compra", width=100)
        self.tree.column("Valor Venda", width=100)
        self.tree.column("Ano Fabricação", width=100)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Vincular duplo clique
        self.tree.bind("<Double-1>", self.on_double_click)

        # Frame para os botões
        button_frame = tk.Frame(list_frame, bg="#ffffff")
        button_frame.pack(side="bottom", pady=10)

        ttk.Button(
            button_frame,
            text="Cadastrar",
            style="Action.TButton",
            command=self.cadastrar_veiculo
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Excluir",
            style="Delete.TButton",  # Botão vermelho
            command=self.confirm_delete
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Editar",
            style="Action.TButton",
            command=self.editar_veiculo
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Adicionar Manutenção",
            style="Action.TButton",
            command=self.adicionar_manutencao
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Adicionar Abastecimento",
            style="Action.TButton",
            command=self.adicionar_abastecimento
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Adicionar Viagem",
            style="Action.TButton",
            command=self.adicionar_viagem
        ).pack(side="left", padx=5)

        # Carregar veículos
        self.load_vehicles()

    def load_vehicles(self):
        self.tree.delete(*self.tree.get_children())
        vehicles = self.vehicle_repo.get_all()

        # Ordenar veículos: primeiro os não vendidos por Data Compra (crescente), depois os vendidos
        def sort_key(vehicle):
            buy_date = getattr(vehicle, 'buy_date', '')
            if buy_date and isinstance(buy_date, str):
                try:
                    buy_date = datetime.strptime(buy_date, '%Y-%m-%d')
                except ValueError:
                    buy_date = datetime.min  # Valor mínimo se a data for inválida
            else:
                buy_date = datetime.min
            sell_date = getattr(vehicle, 'sell_date', None)
            is_sold = sell_date not in [None, ""] and sell_date != "Não vendido"
            return (is_sold, buy_date)  # is_sold False (não vendido) vem primeiro, ordenado por buy_date

        vehicles = sorted(vehicles, key=sort_key)

        for vehicle in vehicles:
            # Garantir que vehicle_id seja um valor válido
            vehicle_id = getattr(vehicle, 'vehicle_id', None)
            if vehicle_id is None:
                print(f"AVISO: VehicleID ausente para veículo {vehicle.name or 'sem nome'}")
                continue  # Pula se o ID for None
            elif not str(vehicle_id).strip():
                print(f"AVISO: VehicleID vazio ou inválido para veículo {vehicle.name or 'sem nome'}: {vehicle_id}")
                continue

            # Tratar datas e valores
            buy_date = getattr(vehicle, 'buy_date', '') or ''
            if buy_date and isinstance(buy_date, str):
                buy_date = datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            sell_date = getattr(vehicle, 'sell_date', None)
            if sell_date and isinstance(sell_date, str):
                sell_date = datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            elif sell_date is None:
                sell_date = "Não vendido"

            # Tratar valores numéricos e validar SaleValue/SellDate
            purchase_value = getattr(vehicle, 'purchase_value', None)
            if purchase_value is None or (
                    isinstance(purchase_value, str) and not purchase_value.replace('.', '').replace('-', '').isdigit()):
                purchase_value_str = '0.00'
                print(f"AVISO: PurchaseValue inválido para veículo {vehicle.name}: {purchase_value}")
            else:
                purchase_value_str = f"{float(purchase_value):.2f}"

            sale_value = getattr(vehicle, 'sale_value', None)
            sale_value_valid = sale_value is not None and (
                        not isinstance(sale_value, str) or sale_value.replace('.', '').replace('-', '').isdigit())
            sell_date_valid = sell_date not in ["Não vendido", None] if isinstance(sell_date,
                                                                                   str) else sell_date is not None

            if sale_value_valid and not sell_date_valid:
                print(
                    f"AVISO: SaleValue preenchido ({sale_value}) mas SellDate inválido ({sell_date}) para veículo {vehicle.name}. Ambos ajustados para 'Não vendido'.")
                sale_value_str = "Não vendido"
                sell_date = "Não vendido"
            elif not sale_value_valid and sell_date_valid:
                print(
                    f"AVISO: SellDate preenchido ({sell_date}) mas SaleValue inválido ({sale_value}) para veículo {vehicle.name}. Ambos ajustados para 'Não vendido'.")
                sale_value_str = "Não vendido"
                sell_date = "Não vendido"
            else:
                if sale_value_valid:
                    sale_value_str = f"{float(sale_value):.2f}"
                else:
                    sale_value_str = "Não vendido"

            # Inserir no Treeview com o vehicle_id como iid
            self.tree.insert("", "end", iid=str(vehicle_id), values=(
                getattr(vehicle, 'license_plate', ''),
                getattr(vehicle, 'name', ''),
                getattr(vehicle, 'seats', ''),
                f"{float(getattr(vehicle, 'avg_km_per_liter', 0.0)):.1f}" if getattr(vehicle, 'avg_km_per_liter',
                                                                                     None) is not None else '0.0',
                getattr(vehicle, 'fuel_tank_size', ''),
                buy_date,
                sell_date,
                purchase_value_str,
                sale_value_str,
                getattr(vehicle, 'manufacturing_year', '')
            ))
            print(f"DEBUG: Inserido veículo com ID {vehicle_id}, Nome: {vehicle.name}")

    def cadastrar_veiculo(self):
        try:
            interface = InterfaceCadastrarVeiculo(self.parent, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a interface de cadastro: {str(e)}")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para excluir.")
            return

        # Usar o iid diretamente como vehicle_id em vez de "text"
        vehicle_id = selected_item[0]  # O iid é o primeiro item da seleção
        if not vehicle_id or not vehicle_id.strip():
            messagebox.showerror("Erro", "ID do veículo inválido.")
            return
        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            messagebox.showerror("Erro", "ID do veículo inválido (não é um número).")
            return

        # Buscar o nome do veículo a partir dos valores da linha selecionada
        vehicle_name = self.tree.item(vehicle_id, "values")[1]  # Nome está na coluna 1
        if messagebox.askyesno("Confirmação",
                               f"Tem certeza que deseja excluir o veículo '{vehicle_name}' (ID: {vehicle_id})?"):
            if self.vehicle_repo.delete(vehicle_id):
                messagebox.showinfo("Sucesso", f"Veículo '{vehicle_name}' excluído com sucesso!")
                self.load_vehicles()
            else:
                messagebox.showerror("Erro", "Falha ao excluir o veículo.")

    def editar_veiculo(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar.")
            return
        vehicle_id = selected_item[0]
        try:
            vehicle_id = int(vehicle_id)
            interface = InterfaceEditarVeiculo(self.parent, self.db_path, vehicle_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do veículo inválido.")

    def adicionar_manutencao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para adicionar manutenção.")
            return
        vehicle_id = selected_item[0]
        try:
            vehicle_id = int(vehicle_id)
            interface = InterfaceCadastrarManutencao(self.parent, self.db_path, vehicle_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do veículo inválido.")

    def adicionar_abastecimento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para adicionar abastecimento.")
            return
        vehicle_id = selected_item[0]
        try:
            vehicle_id = int(vehicle_id)
            interface = InterfaceCadastrarAbastecimento(self.parent, self.db_path, vehicle_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do veículo inválido.")

    def adicionar_viagem(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para adicionar uma viagem.")
            return
        vehicle_id = selected_item[0]
        try:
            vehicle_id = int(vehicle_id)
            interface = InterfaceCadastrarViagem(self.parent, self.db_path, vehicle_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do veículo inválido.")

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                vehicle_id = int(item)
                interface = InterfaceEditarVeiculo(self.parent, self.db_path, vehicle_id)
                interface.show()
            except ValueError:
                messagebox.showerror("Erro", "ID do veículo inválido.")