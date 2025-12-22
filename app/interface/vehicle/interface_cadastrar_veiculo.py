import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton


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

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 22, "bold")
        self.font_label = ("Segoe UI", 12, "bold")
        self.font_entry = ("Segoe UI", 11)
        self.font_button = ("Segoe UI", 9, "bold")

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

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Cadastrar veículo",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(15, 10))

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
        style.configure("Placeholder.TEntry", foreground="#7a7a7a")

        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        validate_cmd = self.parent.register(InterfaceCadastrarVeiculo.validate_input)
        validate_number = self.parent.register(InterfaceCadastrarVeiculo.validate_number)
        validate_decimal = self.parent.register(InterfaceCadastrarVeiculo.validate_decimal)
        validate_plate = self.parent.register(InterfaceCadastrarVeiculo.validate_plate)

        def create_entry(row, label, v_cmd=None, ph=""):
            ttk.Label(scrollable_frame, text=label).grid(row=row, column=0, sticky="e", padx=10, pady=8)
            entry = ttk.Entry(scrollable_frame, width=40)
            if v_cmd:
                entry.configure(validate="key", validatecommand=v_cmd)
            entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
            if ph:
                add_placeholder(entry, ph)
            return entry

        license_plate_entry = create_entry(0, "Placa*:", (validate_plate, "%P"), "Ex.: ABC-1234")
        name_entry = create_entry(1, "Nome*:", (validate_cmd, "%P", "name", 50), "Ex.: Ônibus 1")
        seats_entry = create_entry(2, "Assentos*:", (validate_number, "%P"), "Ex.: 30")
        avg_km_per_liter_entry = create_entry(3, "Km/L*:", (validate_decimal, "%P"), "Ex.: 10.5")
        fuel_tank_size_entry = create_entry(4, "Tanque (L)*:", (validate_number, "%P"), "Ex.: 60")

        ttk.Label(scrollable_frame, text="Data compra*:").grid(row=5, column=0, sticky="e", padx=10, pady=8)
        buy_date_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        buy_date_frame.grid(row=5, column=1, sticky="w", padx=10, pady=8)
        buy_date_entry = tk.Entry(buy_date_frame, width=20, font=self.font_entry, bg=self.bg_button, fg=self.fg_text,
                                  insertbackground=self.fg_text)
        buy_date_entry.pack(side="left", padx=(0, 5))
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
        ListRoundedButton(sell_date_frame, text="Calendário", command=lambda: self.open_calendar(sell_date_entry),
                          width=100, height=30, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left", padx=2)
        ListRoundedButton(sell_date_frame, text="Limpar", command=lambda: self.clear_sell_date(sell_date_entry),
                          width=70, height=30, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(
            side="left")

        purchase_value_entry = create_entry(7, "Valor compra*:", (validate_decimal, "%P"), "Ex.: 50000.00")
        sale_value_entry = create_entry(8, "Valor venda:", (validate_decimal, "%P"), "Ex.: 30000.00")
        manufacturing_year_entry = create_entry(9, "Ano fabricação*:", (validate_number, "%P"), "Ex.: 2022")

        button_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        button_frame.grid(row=10, column=0, columnspan=2, pady=30)

        ListRoundedButton(
            button_frame,
            text="Salvar",
            command=lambda: self.save_vehicle(
                license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry,
                fuel_tank_size_entry, buy_date_entry, sell_date_entry, purchase_value_entry,
                sale_value_entry, manufacturing_year_entry
            ),
            width=180, height=45, bg=self.accent, fg=self.fg_text, font=self.font_button
        ).pack(side="left", padx=10)

        ListRoundedButton(
            button_frame,
            text="Voltar",
            command=self.back,
            width=140, height=45, bg=self.bg_button, fg=self.fg_text, font=self.font_button
        ).pack(side="left", padx=10)

        self.parent.bind('<Control-s>', lambda e: self.save_vehicle(
            license_plate_entry, name_entry, seats_entry, avg_km_per_liter_entry,
            fuel_tank_size_entry, buy_date_entry, sell_date_entry, purchase_value_entry,
            sale_value_entry, manufacturing_year_entry
        ))
        self.parent.bind('<Control-z>', lambda e: self.back())

        ttk.Label(scrollable_frame, text="* Campos obrigatórios", font=("Segoe UI", 10, "italic"),
                  foreground="#aaaaaa").grid(row=11, column=0, columnspan=2, pady=(0, 20))

        self.parent.update_idletasks()
        canvas.itemconfig(canvas_window, width=canvas.winfo_width())

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def clear_sell_date(self, sell_date_entry):
        sell_date_entry.delete(0, tk.END)

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

        if not all([license_plate, name, seats, avg_km_per_liter, fuel_tank_size, buy_date, purchase_value,
                    manufacturing_year]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            seats = int(seats)
            avg_km_per_liter = float(avg_km_per_liter)
            fuel_tank_size = int(fuel_tank_size)
            purchase_value = float(purchase_value)
            manufacturing_year = int(manufacturing_year)
            buy_date_sql = datetime.strptime(buy_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            sell_date_sql = datetime.strptime(sell_date, '%d/%m/%Y').strftime('%Y-%m-%d') if sell_date else None
            sale_value = float(sale_value) if sale_value else None

            vehicle = Vehicle(
                None, avg_km_per_liter, license_plate, seats, fuel_tank_size, name,
                buy_date_sql, sell_date_sql, purchase_value, sale_value, manufacturing_year
            )
            self.vehicle_repo.add(vehicle)
            messagebox.showinfo("Sucesso", f"Veículo '{name}' cadastrado com sucesso!")
            self.back()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")

    def back(self):
        self.parent.unbind_all("<MouseWheel>")
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        interface = InterfaceListVehicles(self.parent, self.db_path)
        interface.show()