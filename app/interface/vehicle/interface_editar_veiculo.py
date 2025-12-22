import tkinter as tk
from tkinter import ttk, messagebox
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

        self.font_title = ("Segoe UI", 22, "bold")
        self.font_label = ("Segoe UI", 12, "bold")
        self.font_entry = ("Segoe UI", 11)
        self.font_button = ("Segoe UI", 9, "bold")

    def show(self):
        if not self.vehicle:
            messagebox.showerror("Erro", "Veículo não encontrado.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="Editar veículo", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(
            pady=(15, 10))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, fieldbackground=self.bg_button, foreground=self.fg_text)

        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)

        def create_field(row, label_text, value, is_decimal=False):
            ttk.Label(scrollable_frame, text=label_text).grid(row=row, column=0, sticky="e", padx=10, pady=8)
            entry = ttk.Entry(scrollable_frame, width=40)
            if is_decimal:
                entry.configure(validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
            entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
            entry.insert(0, value)
            return entry

        license_plate_entry = create_field(0, "Placa*:", getattr(self.vehicle, 'license_plate', ''))
        name_entry = create_field(1, "Nome*:", getattr(self.vehicle, 'name', ''))
        seats_entry = create_field(2, "Assentos*:", str(getattr(self.vehicle, 'seats', '')))
        avg_km_per_liter_entry = create_field(3, "Km/L*:", str(float(getattr(self.vehicle, 'avg_km_per_liter', 0.0))),
                                              True)
        fuel_tank_size_entry = create_field(4, "Tanque (L)*:", str(getattr(self.vehicle, 'fuel_tank_size', '')))

        ttk.Label(scrollable_frame, text="Data compra*:").grid(row=5, column=0, sticky="e", padx=10, pady=8)
        buy_date_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        buy_date_frame.grid(row=5, column=1, sticky="w", padx=10, pady=8)
        buy_date_entry = tk.Entry(buy_date_frame, width=20, font=self.font_entry, bg=self.bg_button, fg=self.fg_text,
                                  insertbackground=self.fg_text)
        buy_date_entry.pack(side="left", padx=(0, 5))

        buy_date = getattr(self.vehicle, 'buy_date', '')
        if buy_date and isinstance(buy_date, str):
            buy_date_entry.insert(0, datetime.strptime(buy_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
        else:
            buy_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        ListRoundedButton(buy_date_frame, text="Calendário", command=lambda: self.open_calendar(buy_date_entry),
                          width=100, height=30, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left")

        ttk.Label(scrollable_frame, text="Data venda:").grid(row=6, column=0, sticky="e", padx=10, pady=8)
        sell_date_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        sell_date_frame.grid(row=6, column=1, sticky="w", padx=10, pady=8)
        sell_date_entry = tk.Entry(sell_date_frame, width=20, font=self.font_entry, bg=self.bg_button, fg=self.fg_text,
                                   insertbackground=self.fg_text)
        sell_date_entry.pack(side="left", padx=(0, 5))

        sell_date = getattr(self.vehicle, 'sell_date', '')
        if sell_date and isinstance(sell_date, str) and sell_date != "Não vendido":
            sell_date_entry.insert(0, datetime.strptime(sell_date, '%Y-%m-%d').strftime('%d/%m/%Y'))

        ListRoundedButton(sell_date_frame, text="Calendário", command=lambda: self.open_calendar(sell_date_entry),
                          width=100, height=30, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left", padx=2)
        ListRoundedButton(sell_date_frame, text="Limpar", command=lambda: self.clear_sell_date(sell_date_entry),
                          width=70, height=30, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left")

        purchase_value_entry = create_field(7, "Valor compra (R$)*:",
                                            str(float(getattr(self.vehicle, 'purchase_value', 0.0))), True)

        sale_value_raw = getattr(self.vehicle, 'sale_value', '')
        sale_val_str = str(float(sale_value_raw)) if (sale_value_raw and sale_value_raw != "Não vendido") else ""
        sale_value_entry = create_field(8, "Valor venda (R$):", sale_val_str, True)

        manufacturing_year_entry = create_field(9, "Ano fabricação*:",
                                                str(getattr(self.vehicle, 'manufacturing_year', '')))

        button_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        button_frame.grid(row=10, column=0, columnspan=2, pady=30)

        ListRoundedButton(button_frame, text="Salvar alterações", command=lambda: self.save_vehicle(
            license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry, fuel_tank_size_entry,
            buy_date_entry, sell_date_entry, purchase_value_entry, sale_value_entry, manufacturing_year_entry
        ), width=180, height=45, bg=self.accent, fg=self.fg_text, font=self.font_button).pack(side="left", padx=10)

        ListRoundedButton(button_frame, text="Cancelar", command=self.back,
                          width=140, height=45, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left", padx=10)

        ttk.Label(scrollable_frame, text="* Campos obrigatórios", font=("Segoe UI", 10, "italic"),
                  foreground="#aaaaaa").grid(row=11, column=0, columnspan=2, pady=(0, 20))

        self.parent.update_idletasks()
        canvas.itemconfig(canvas_window, width=canvas.winfo_width())

    def validate_decimal(self, P):
        if not P: return True
        P_mod = P.replace(',', '.')
        try:
            if P_mod in (".", "-"): return True
            float(P_mod)
            return True
        except:
            return False

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def clear_sell_date(self, sell_date_entry):
        sell_date_entry.delete(0, tk.END)

    def save_vehicle(self, license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry, fuel_tank_size_entry,
                     buy_date_entry, sell_date_entry, purchase_value_entry, sale_value_entry, manufacturing_year_entry):
        try:
            license_plate = license_plate_entry.get().strip()
            name = name_entry.get().strip()
            seats = seats_entry.get().strip()
            avg_km_per_liter = float(avg_km_per_liter_entry.get().replace(',', '.') or 0.0)
            fuel_tank_size = fuel_tank_size_entry.get().strip()
            buy_date_str = buy_date_entry.get().strip()
            sell_date_str = sell_date_entry.get().strip()
            purchase_value = float(purchase_value_entry.get().replace(',', '.') or 0.0)
            sale_value = float(sale_value_entry.get().replace(',', '.') or 0.0) if sell_date_str else None
            manufacturing_year = manufacturing_year_entry.get().strip()

            if not all([license_plate, name, seats, buy_date_str, fuel_tank_size, manufacturing_year]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return

            buy_date = datetime.strptime(buy_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            sell_date = datetime.strptime(sell_date_str, '%d/%m/%Y').strftime('%Y-%m-%d') if sell_date_str else None

            updated_vehicle = Vehicle(
                self.vehicle_id, avg_km_per_liter, license_plate, int(seats), int(fuel_tank_size), name,
                buy_date, sell_date, purchase_value, sale_value, int(manufacturing_year)
            )

            if self.vehicle_repo.update(updated_vehicle):
                messagebox.showinfo("Sucesso", "Veículo atualizado!")
                self.back()
            else:
                messagebox.showerror("Erro", "Erro ao atualizar no banco de dados.")
        except Exception as e:
            messagebox.showerror("Erro", f"Dados inválidos: {e}")

    def back(self):
        self.parent.unbind_all("<MouseWheel>")
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        interface = InterfaceListVehicles(self.parent, self.db_path)
        interface.show()