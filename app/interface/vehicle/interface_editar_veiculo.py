import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle

class InterfaceEditarVeiculo:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.vehicle = self.vehicle_repo.get_by_id(vehicle_id) if vehicle_id else None

    def show(self):
        if not self.vehicle:
            messagebox.showerror("Erro", "Veículo não encontrado.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Editar Veículo", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#1976d2").pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")

        # Campos
        ttk.Label(main_frame, text="Placa*:").grid(row=0, column=0, sticky="e", padx=15, pady=10)
        license_plate_entry = ttk.Entry(main_frame, width=45)
        license_plate_entry.grid(row=0, column=1, padx=15, pady=10, sticky="w")
        license_plate_entry.insert(0, getattr(self.vehicle, 'license_plate', ''))

        ttk.Label(main_frame, text="Nome*:").grid(row=1, column=0, sticky="e", padx=15, pady=10)
        name_entry = ttk.Entry(main_frame, width=45)
        name_entry.grid(row=1, column=1, padx=15, pady=10, sticky="w")
        name_entry.insert(0, getattr(self.vehicle, 'name', ''))

        ttk.Label(main_frame, text="Assentos*:").grid(row=2, column=0, sticky="e", padx=15, pady=10)
        seats_entry = ttk.Entry(main_frame, width=45)
        seats_entry.grid(row=2, column=1, padx=15, pady=10, sticky="w")
        seats_entry.insert(0, str(getattr(self.vehicle, 'seats', '')))

        ttk.Label(main_frame, text="Km/L*:").grid(row=3, column=0, sticky="e", padx=15, pady=10)
        avg_km_per_liter_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        avg_km_per_liter_entry.grid(row=3, column=1, padx=15, pady=10, sticky="w")
        avg_km_per_liter_entry.insert(0, str(float(getattr(self.vehicle, 'avg_km_per_liter', 0.0))))

        ttk.Label(main_frame, text="Tanque (L)*:").grid(row=4, column=0, sticky="e", padx=15, pady=10)
        fuel_tank_size_entry = ttk.Entry(main_frame, width=45)
        fuel_tank_size_entry.grid(row=4, column=1, padx=15, pady=10, sticky="w")
        fuel_tank_size_entry.insert(0, str(getattr(self.vehicle, 'fuel_tank_size', '')))

        ttk.Label(main_frame, text="Data Compra*:").grid(row=5, column=0, sticky="e", padx=15, pady=10)
        buy_date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        buy_date_entry.grid(row=5, column=1, padx=15, pady=10, sticky="w")
        buy_date = getattr(self.vehicle, 'buy_date', '')
        if buy_date and isinstance(buy_date, str):
            buy_date_entry.set_date(datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y'))

        ttk.Label(main_frame, text="Data Venda:").grid(row=6, column=0, sticky="e", padx=15, pady=10)
        sell_date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        sell_date_entry.grid(row=6, column=1, padx=15, pady=10, sticky="w")
        sell_date = getattr(self.vehicle, 'sell_date', '')
        if sell_date and isinstance(sell_date, str) and sell_date != "Não vendido":
            sell_date_entry.set_date(datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y'))

        ttk.Label(main_frame, text="Valor Compra (R$)*:").grid(row=7, column=0, sticky="e", padx=15, pady=10)
        purchase_value_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        purchase_value_entry.grid(row=7, column=1, padx=15, pady=10, sticky="w")
        purchase_value_entry.insert(0, str(float(getattr(self.vehicle, 'purchase_value', 0.0))))

        ttk.Label(main_frame, text="Valor Venda (R$):").grid(row=8, column=0, sticky="e", padx=15, pady=10)
        sale_value_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        sale_value_entry.grid(row=8, column=1, padx=15, pady=10, sticky="w")
        sale_value = getattr(self.vehicle, 'sale_value', '')
        if sale_value and isinstance(sale_value, (int, float, str)) and sale_value != "Não vendido":
            sale_value_entry.insert(0, str(float(sale_value)))

        ttk.Label(main_frame, text="Ano Fabricação*:").grid(row=9, column=0, sticky="e", padx=15, pady=10)
        manufacturing_year_entry = ttk.Entry(main_frame, width=45)
        manufacturing_year_entry.grid(row=9, column=1, padx=15, pady=10, sticky="w")
        manufacturing_year_entry.insert(0, str(getattr(self.vehicle, 'manufacturing_year', '')))

        # Botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Salvar", style="TButton", command=lambda: self.save_vehicle(
            license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry, fuel_tank_size_entry,
            buy_date_entry, sell_date_entry, purchase_value_entry, sale_value_entry, manufacturing_year_entry
        )).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Voltar", style="TButton", command=self.back).pack(side="left", padx=10)

    def validate_decimal(self, P):
        if not P:
            return True
        for c in P:
            if not (c.isdigit() or c in ".,"):
                return False
        P = P.replace(',', '.')
        if P.count('.') > 1:
            return False
        return True

    def save_vehicle(self, license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry, fuel_tank_size_entry,
                     buy_date_entry, sell_date_entry, purchase_value_entry, sale_value_entry, manufacturing_year_entry):
        license_plate = license_plate_entry.get().strip()
        name = name_entry.get().strip()
        seats = seats_entry.get().strip()
        avg_km_per_liter = float(avg_km_per_liter_entry.get().replace(',', '.') or 0.0)
        fuel_tank_size = fuel_tank_size_entry.get().strip()
        buy_date = buy_date_entry.get().strip()
        sell_date = sell_date_entry.get().strip() if sell_date_entry.get().strip() else None
        purchase_value = float(purchase_value_entry.get().replace(',', '.') or 0.0)
        sale_value = float(sale_value_entry.get().replace(',', '.') or 0.0) if sale_value_entry.get().strip() else None
        manufacturing_year = manufacturing_year_entry.get().strip()

        if not all([license_plate, name, seats, avg_km_per_liter, fuel_tank_size, buy_date, purchase_value, manufacturing_year]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            buy_date_obj = datetime.strptime(buy_date, '%d/%m/%Y')
            buy_date = buy_date_obj.strftime('%Y-%m-%d')
            if sell_date:
                sell_date_obj = datetime.strptime(sell_date, '%d/%m/%Y')
                sell_date = sell_date_obj.strftime('%Y-%m-%d')

            updated_vehicle = Vehicle(
                self.vehicle_id, avg_km_per_liter, license_plate, int(seats), int(fuel_tank_size), name,
                buy_date, sell_date, purchase_value, sale_value, int(manufacturing_year)
            )
            if self.vehicle_repo.update(updated_vehicle):
                messagebox.showinfo("Sucesso", f"Veículo com ID {self.vehicle_id} atualizado com sucesso!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao atualizar o veículo.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceVeiculo
        interface = InterfaceVeiculo(self.parent, self.db_path)
        interface.show()