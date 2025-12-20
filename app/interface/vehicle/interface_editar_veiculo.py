import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton

class InterfaceEditarVeiculo:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.vehicle = self.vehicle_repo.get_by_id(vehicle_id) if vehicle_id else None

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

    def show(self):
        if not self.vehicle:
            messagebox.showerror("Erro", "Veículo não encontrado.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Editar Veículo", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg=self.bg_main, width=800)
        main_frame.pack(padx=30, pady=10, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, padding=6, fieldbackground=self.bg_button, foreground=self.fg_text)
        style.configure("TButton", font=self.font_button, padding=10,
                        background=self.bg_button, foreground=self.fg_text)
        style.map("TButton",
                  background=[("active", self.accent)],
                  foreground=[("active", self.fg_text)])
        style.configure("Placeholder.TEntry", foreground="#7a7a7a")

        ttk.Label(main_frame, text="Placa*:").grid(row=0, column=0, sticky="e", padx=(0, 10), pady=10)
        license_plate_entry = ttk.Entry(main_frame, width=64)
        license_plate_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        license_plate_entry.insert(0, getattr(self.vehicle, 'license_plate', ''))

        ttk.Label(main_frame, text="Nome*:").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=10)
        name_entry = ttk.Entry(main_frame, width=64)
        name_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=10)
        name_entry.insert(0, getattr(self.vehicle, 'name', ''))

        ttk.Label(main_frame, text="Assentos*:").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=10)
        seats_entry = ttk.Entry(main_frame, width=64)
        seats_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=10)
        seats_entry.insert(0, str(getattr(self.vehicle, 'seats', '')))

        ttk.Label(main_frame, text="Km/L*:").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=10)
        avg_km_per_liter_entry = ttk.Entry(main_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        avg_km_per_liter_entry.grid(row=3, column=1, sticky="w", padx=(0, 10), pady=10)
        avg_km_per_liter_entry.insert(0, str(float(getattr(self.vehicle, 'avg_km_per_liter', 0.0))))

        ttk.Label(main_frame, text="Tanque (L)*:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=10)
        fuel_tank_size_entry = ttk.Entry(main_frame, width=64)
        fuel_tank_size_entry.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=10)
        fuel_tank_size_entry.insert(0, str(getattr(self.vehicle, 'fuel_tank_size', '')))

        ttk.Label(main_frame, text="Data Compra*:").grid(row=5, column=0, sticky="e", padx=(0, 10), pady=10)
        buy_date_frame = tk.Frame(main_frame, bg=self.bg_main)
        buy_date_frame.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=10)
        buy_date_entry = tk.Entry(buy_date_frame, width=55, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, insertbackground=self.fg_text)
        buy_date_entry.pack(side="left", padx=5)
        buy_date = getattr(self.vehicle, 'buy_date', '')
        if buy_date and isinstance(buy_date, str):
            buy_date_entry.insert(0, datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
        else:
            buy_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(buy_date_frame, text="Selecionar Data", command=lambda: self.open_calendar(buy_date_entry), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Data Venda:").grid(row=6, column=0, sticky="e", padx=(0, 10), pady=10)
        sell_date_frame = tk.Frame(main_frame, bg=self.bg_main)
        sell_date_frame.grid(row=6, column=1, sticky="w", padx=(0, 10), pady=10)
        sell_date_entry = tk.Entry(sell_date_frame, width=55, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, insertbackground=self.fg_text)
        sell_date_entry.pack(side="left", padx=5)
        sell_date = getattr(self.vehicle, 'sell_date', '')
        if sell_date and isinstance(sell_date, str) and sell_date != "Não vendido":
            sell_date_entry.insert(0, datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
        ListRoundedButton(sell_date_frame, text="Selecionar Data", command=lambda: self.open_calendar(sell_date_entry), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)
        ListRoundedButton(sell_date_frame, text="Limpar", command=lambda: self.clear_sell_date(sell_date_entry), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Valor Compra (R$)*:").grid(row=7, column=0, sticky="e", padx=(0, 10), pady=10)
        purchase_value_entry = ttk.Entry(main_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        purchase_value_entry.grid(row=7, column=1, sticky="w", padx=(0, 10), pady=10)
        purchase_value_entry.insert(0, str(float(getattr(self.vehicle, 'purchase_value', 0.0))))

        ttk.Label(main_frame, text="Valor Venda (R$):").grid(row=8, column=0, sticky="e", padx=(0, 10), pady=10)
        sale_value_entry = ttk.Entry(main_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        sale_value_entry.grid(row=8, column=1, sticky="w", padx=(0, 10), pady=10)
        sale_value = getattr(self.vehicle, 'sale_value', '')
        if sale_value and isinstance(sale_value, (int, float, str)) and sale_value != "Não vendido":
            sale_value_entry.insert(0, str(float(sale_value)))

        ttk.Label(main_frame, text="Ano Fabricação*:").grid(row=9, column=0, sticky="e", padx=(0, 10), pady=10)
        manufacturing_year_entry = ttk.Entry(main_frame, width=64)
        manufacturing_year_entry.grid(row=9, column=1, sticky="w", padx=(0, 10), pady=10)
        manufacturing_year_entry.insert(0, str(getattr(self.vehicle, 'manufacturing_year', '')))

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        ListRoundedButton(button_frame, text="Salvar", command=lambda: self.save_vehicle(
            license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry, fuel_tank_size_entry,
            buy_date_entry, sell_date_entry, purchase_value_entry, sale_value_entry, manufacturing_year_entry
        ), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)
        ListRoundedButton(button_frame, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"), foreground=self.fg_text).grid(row=11, column=0, columnspan=2, pady=15)

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

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def clear_sell_date(self, sell_date_entry):
        sell_date_entry.delete(0, tk.END)

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

        if sell_date and buy_date:
            buy_date_obj = datetime.strptime(buy_date, '%d/%m/%Y')
            sell_date_obj = datetime.strptime(sell_date, '%d/%m/%Y')
            if sell_date_obj <= buy_date_obj:
                messagebox.showerror("Erro", "Data de Venda deve ser posterior à Data de Compra.")
                return

        if (sale_value is not None and sale_value > 0) and not sell_date:
            messagebox.showerror("Erro", "Se Valor de Venda estiver preenchido, Data de Venda também deve estar.")
            return
        if sell_date and (sale_value is None or sale_value == 0):
            messagebox.showerror("Erro", "Se Data de Venda estiver preenchida, Valor de Venda também deve estar.")
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
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        interface = InterfaceListVehicles(self.parent, self.db_path)
        interface.show()
