import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle

def add_placeholder(entry: ttk.Entry, placeholder: str):
    entry._ph_text = placeholder
    entry._ph_active = False
    entry._orig_validate = entry.cget("validate")
    entry._orig_vcmd = entry.cget("validatecommand")
    entry._orig_style = entry.cget("style") or "TEntry"

    def _disable_validation():
        entry.configure(validate="none")

    def _restore_validation():
        entry.configure(validate=entry._orig_validate, validatecommand=entry._orig_vcmd)

    def _show_placeholder():
        _disable_validation()
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.configure(style="Placeholder.TEntry")
        entry._ph_active = True
        _restore_validation()

    def _hide_placeholder():
        _disable_validation()
        entry.delete(0, tk.END)
        entry.configure(style=entry._orig_style or "TEntry")
        entry._ph_active = False
        _restore_validation()

    def on_focus_in(_):
        if entry._ph_active:
            _hide_placeholder()

    def on_focus_out(_):
        if not entry.get():
            _show_placeholder()

    entry.bind("<FocusIn>", on_focus_in, add="+")
    entry.bind("<FocusOut>", on_focus_out, add="+")
    _show_placeholder()

def get_entry_value(entry: ttk.Entry) -> str:
    text = entry.get().strip()
    if getattr(entry, "_ph_active", False):
        return ""
    if text == getattr(entry, "_ph_text", None):
        return ""
    return text

class InterfaceCadastrarVeiculo:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_repo = VehicleRepository(self.db_path)

    @staticmethod
    def validate_input(P, field, max_length):
        if not P:
            return True
        max_length = int(max_length)
        clean_text = ''.join(c for c in P if c.isalnum() or c.isspace())
        return len(clean_text) <= max_length

    @staticmethod
    def validate_number(P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

    @staticmethod
    def validate_decimal(P):
        if not P:
            return True
        for c in P:
            if not (c.isdigit() or c in ".,"):
                return False
        P = P.replace(',', '.')
        if P.count('.') > 1:
            return False
        return True

    @staticmethod
    def validate_plate(P):
        if not P:
            return True
        clean_text = ''.join(c for c in P if c.isalnum() or c == '-')
        return len(clean_text.replace('-', '')) <= 7

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(
            self.parent,
            text="Cadastrar Veículo",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10,
                        background="#4CAF50", foreground="#ffffff")
        style.map("TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")
        style.configure("Placeholder.TEntry", foreground="#7a7a7a")

        validate_cmd = self.parent.register(InterfaceCadastrarVeiculo.validate_input)
        validate_number = self.parent.register(InterfaceCadastrarVeiculo.validate_number)
        validate_decimal = self.parent.register(InterfaceCadastrarVeiculo.validate_decimal)
        validate_plate = self.parent.register(InterfaceCadastrarVeiculo.validate_plate)

        ttk.Label(main_frame, text="Placa*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        license_plate_entry = ttk.Entry(main_frame, width=45, validate="key",
                                        validatecommand=(validate_plate, "%P"))
        license_plate_entry.grid(row=0, column=1, padx=15, pady=15)
        add_placeholder(license_plate_entry, "Ex.: ABC-1234")

        ttk.Label(main_frame, text="Nome*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        name_entry = ttk.Entry(main_frame, width=45, validate="key",
                               validatecommand=(validate_cmd, "%P", "name", 50))
        name_entry.grid(row=1, column=1, padx=15, pady=15)
        add_placeholder(name_entry, "Ex.: Ônibus 1")

        ttk.Label(main_frame, text="Assentos*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        seats_entry = ttk.Entry(main_frame, width=45, validate="key",
                                validatecommand=(validate_number, "%P"))
        seats_entry.grid(row=2, column=1, padx=15, pady=15)
        add_placeholder(seats_entry, "Ex.: 30")

        ttk.Label(main_frame, text="Km/L*:").grid(row=3, column=0, sticky="e", padx=15, pady=15)
        avg_km_per_liter_entry = ttk.Entry(main_frame, width=45, validate="key",
                                           validatecommand=(validate_decimal, "%P"))
        avg_km_per_liter_entry.grid(row=3, column=1, padx=15, pady=15)
        add_placeholder(avg_km_per_liter_entry, "Ex.: 10.5")

        ttk.Label(main_frame, text="Tanque (L)*:").grid(row=4, column=0, sticky="e", padx=15, pady=15)
        fuel_tank_size_entry = ttk.Entry(main_frame, width=45, validate="key",
                                         validatecommand=(validate_number, "%P"))
        fuel_tank_size_entry.grid(row=4, column=1, padx=15, pady=15)
        add_placeholder(fuel_tank_size_entry, "Ex.: 60")

        ttk.Label(main_frame, text="Data Compra*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        buy_date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        buy_date_entry.grid(row=5, column=1, padx=15, pady=15)
        today = datetime.now().strftime('%d/%m/%Y')  # 09/09/2025
        buy_date_entry.set_date(today)

        ttk.Label(main_frame, text="Data Venda:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        sell_date_frame = tk.Frame(main_frame, bg="#ffffff")
        sell_date_frame.grid(row=6, column=1, padx=15, pady=15)
        sell_date_entry = DateEntry(sell_date_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        sell_date_entry.grid(row=0, column=0)
        sell_date_entry.delete(0, tk.END)
        sell_date_entry.bind("<FocusIn>", lambda e: None)
        ttk.Button(sell_date_frame, text="Limpar", style="TButton", command=lambda: self.clear_sell_date(sell_date_entry)).grid(row=1, column=0, pady=5)

        ttk.Label(main_frame, text="Valor Compra*:").grid(row=7, column=0, sticky="e", padx=15, pady=15)
        purchase_value_entry = ttk.Entry(main_frame, width=45, validate="key",
                                         validatecommand=(validate_decimal, "%P"))
        purchase_value_entry.grid(row=7, column=1, padx=15, pady=15)
        add_placeholder(purchase_value_entry, "Ex.: 50000.00")

        ttk.Label(main_frame, text="Valor Venda:").grid(row=8, column=0, sticky="e", padx=15, pady=15)
        sale_value_entry = ttk.Entry(main_frame, width=45, validate="key",
                                     validatecommand=(validate_decimal, "%P"))
        sale_value_entry.grid(row=8, column=1, padx=15, pady=15)
        add_placeholder(sale_value_entry, "Ex.: 30000.00")

        ttk.Label(main_frame, text="Ano Fabricação*:").grid(row=9, column=0, sticky="e", padx=15, pady=15)
        manufacturing_year_entry = ttk.Entry(main_frame, width=45, validate="key",
                                             validatecommand=(validate_number, "%P"))
        manufacturing_year_entry.grid(row=9, column=1, padx=15, pady=15)
        add_placeholder(manufacturing_year_entry, "Ex.: 2022")

        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Salvar",
            style="TButton",
            command=lambda: self.save_vehicle(
                license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry,
                fuel_tank_size_entry, buy_date_entry, sell_date_entry, purchase_value_entry,
                sale_value_entry, manufacturing_year_entry
            )
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Voltar",
            style="TButton",
            command=self.back
        ).pack(side="left", padx=5)

        self.parent.bind('<Control-s>', lambda e: self.save_vehicle(
            license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry,
            fuel_tank_size_entry, buy_date_entry, sell_date_entry, purchase_value_entry,
            sale_value_entry, manufacturing_year_entry
        ))
        self.parent.bind('<Control-z>', lambda e: self.back())

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=11, column=0, columnspan=2, pady=15)

    def save_vehicle(self, license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry,
                     fuel_tank_size_entry, buy_date_entry, sell_date_entry, purchase_value_entry,
                     sale_value_entry, manufacturing_year_entry):
        license_plate = get_entry_value(license_plate_entry).replace('-', '')
        name = get_entry_value(name_entry)
        seats = get_entry_value(seats_entry)
        avg_km_per_liter = get_entry_value(avg_km_per_liter_entry).replace(',', '.')
        fuel_tank_size = get_entry_value(fuel_tank_size_entry)
        buy_date = buy_date_entry.get().strip()
        sell_date_raw = sell_date_entry.get().strip()
        sell_date = sell_date_raw if sell_date_raw else None
        purchase_value = get_entry_value(purchase_value_entry).replace(',', '.')
        sale_value_raw = get_entry_value(sale_value_entry)
        sale_value = sale_value_raw.replace(',', '.') if sale_value_raw else None
        manufacturing_year = get_entry_value(manufacturing_year_entry)

        if not all([license_plate, name, seats, avg_km_per_liter, fuel_tank_size, buy_date, purchase_value, manufacturing_year]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if len(license_plate) > 7:
            messagebox.showerror("Erro", "Placa deve ter no máximo 7 caracteres (sem hífen).")
            return
        if len(name) > 50:
            messagebox.showerror("Erro", "Nome deve ter no máximo 50 caracteres.")
            return

        # Validação: SaleValue e SellDate devem estar ambos preenchidos ou ambos vazios
        if (sale_value and not sell_date) or (sell_date and not sale_value):
            messagebox.showwarning("Aviso", "Ambos Valor de Venda e Data de Venda devem estar preenchidos ou vazios.")
            return

        try:
            seats = int(seats)
            avg_km_per_liter = float(avg_km_per_liter)
            fuel_tank_size = int(fuel_tank_size)
            purchase_value = float(purchase_value) if purchase_value else 0.0  # Garantir conversão só se houver valor
            manufacturing_year = int(manufacturing_year)
            buy_date_obj = datetime.strptime(buy_date, '%d/%m/%Y')
            buy_date_sql = buy_date_obj.strftime('%Y-%m-%d')
            sell_date_sql = datetime.strptime(sell_date, '%d/%m/%Y').strftime('%Y-%m-%d') if sell_date else None
            sale_value = float(sale_value) if sale_value else None

            vehicle = Vehicle(
                None, avg_km_per_liter, license_plate, seats, fuel_tank_size, name,
                buy_date_sql, sell_date_sql, purchase_value, sale_value, manufacturing_year
            )
            self.vehicle_repo.add(vehicle)
            messagebox.showinfo("Sucesso", f"Veículo '{name}' cadastrado com sucesso!")
            self.back()
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar veículo: {str(e)}")

    def clear_sell_date(self, sell_date_entry):
        sell_date_entry.delete(0, tk.END)

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceVeiculo
        interface = InterfaceVeiculo(self.parent, self.db_path)
        interface.show()