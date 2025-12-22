import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.trip_repository import TripRepository
from app.models.trip import Trip
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.trip_driver_repository import TripDriverRepository
from app.models.trip_driver import TripDriver
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

class InterfaceCadastrarViagem:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.trip_repo = TripRepository(self.db_path)
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.driver_repo = DriverRepository(self.db_path)
        self.trip_driver_repo = TripDriverRepository(self.db_path)
        self.driver_vars = {}

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_input = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        canvas = tk.Canvas(self.parent, bg=self.bg_main, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.parent.winfo_width())
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(
            scrollable_frame,
            text="Cadastrar viagem",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(15, 10))

        main_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        main_frame.pack(pady=5, padx=30, fill="both", expand=True)

        main_frame.columnconfigure(0, weight=0, minsize=180)
        main_frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10), background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=("Segoe UI", 10), fieldbackground=self.bg_button, foreground=self.fg_text)
        style.configure("Placeholder.TEntry", foreground="#888888", fieldbackground=self.bg_button)

        validate_number_cmd = self.parent.register(self.validate_number)
        validate_decimal_cmd = self.parent.register(self.validate_decimal)

        ttk.Label(main_frame, text="Veículo*:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        vehicles = self.vehicle_repo.get_all()
        vehicle_options = [f"{v.name} (ID: {v.vehicle_id})" for v in vehicles if v.vehicle_id]
        self.vehicle_combobox = ttk.Combobox(main_frame, values=vehicle_options, width=40, state="readonly")
        self.vehicle_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        if vehicle_options:
            self.vehicle_combobox.set(vehicle_options[0])

        ttk.Label(main_frame, text="Despesas (R$)*:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.additional_expenses_entry = ttk.Entry(main_frame, width=42, validate="key", validatecommand=(validate_decimal_cmd, "%P"))
        self.additional_expenses_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        add_placeholder(self.additional_expenses_entry, "0.00")

        ttk.Label(main_frame, text="KM total*:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.total_km_entry = ttk.Entry(main_frame, width=42, validate="key", validatecommand=(validate_number_cmd, "%P"))
        self.total_km_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        add_placeholder(self.total_km_entry, "0")

        ttk.Label(main_frame, text="Valor p/ pass. (R$)*:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.passenger_fare_entry = ttk.Entry(main_frame, width=42, validate="key", validatecommand=(validate_decimal_cmd, "%P"))
        self.passenger_fare_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        add_placeholder(self.passenger_fare_entry, "0.00")

        ttk.Label(main_frame, text="Qtd. passageiros*:").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.passenger_count_entry = ttk.Entry(main_frame, width=42, validate="key", validatecommand=(validate_number_cmd, "%P"))
        self.passenger_count_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        add_placeholder(self.passenger_count_entry, "0")

        ttk.Label(main_frame, text="Início*:").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        date_frame_start = tk.Frame(main_frame, bg=self.bg_main)
        date_frame_start.grid(row=5, column=1, sticky="w", padx=10, pady=5)
        self.start_date_entry = tk.Entry(
            date_frame_start, width=30, font=("Segoe UI", 10),
            bg=self.bg_input, fg=self.fg_text,
            readonlybackground=self.bg_input, borderwidth=0,
            highlightthickness=1, highlightbackground=self.bg_button,
            state="readonly"
        )
        self.start_date_entry.pack(side="left")
        self.start_date_entry.config(state="normal")
        self.start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.start_date_entry.config(state="readonly")
        ListRoundedButton(date_frame_start, text="Data", command=lambda: self.open_calendar(self.start_date_entry), width=100, height=25, bg=self.bg_button, fg=self.fg_text).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Fim*:").grid(row=6, column=0, sticky="e", padx=10, pady=5)
        date_frame_end = tk.Frame(main_frame, bg=self.bg_main)
        date_frame_end.grid(row=6, column=1, sticky="w", padx=10, pady=5)
        self.end_date_entry = tk.Entry(
            date_frame_end, width=30, font=("Segoe UI", 10),
            bg=self.bg_input, fg=self.fg_text,
            readonlybackground=self.bg_input, borderwidth=0,
            highlightthickness=1, highlightbackground=self.bg_button,
            state="readonly"
        )
        self.end_date_entry.pack(side="left")
        ListRoundedButton(date_frame_end, text="Data", command=lambda: self.open_calendar(self.end_date_entry), width=100, height=25, bg=self.bg_button, fg=self.fg_text).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Descrição:").grid(row=7, column=0, sticky="e", padx=10, pady=5)
        self.description_entry = ttk.Entry(main_frame, width=42)
        self.description_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        add_placeholder(self.description_entry, "Opcional")

        drivers_frame = tk.LabelFrame(main_frame, text="Motoristas", font=("Segoe UI", 10, "bold"), bg=self.bg_main, fg=self.accent)
        drivers_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        d_container = tk.Frame(drivers_frame, bg=self.bg_main)
        d_container.pack(fill="x", padx=5, pady=5)

        self.driver_vars = {}
        drivers = self.driver_repo.get_all()
        active_drivers = [d for d in drivers if not d.end_date]
        for i, driver in enumerate(active_drivers):
            if driver.driver_id:
                var = tk.BooleanVar()
                self.driver_vars[driver.driver_id] = var
                chk = tk.Checkbutton(d_container, text=driver.name.upper(), variable=var, bg=self.bg_main, fg=self.fg_text,
                                     activebackground=self.bg_main, selectcolor="#2c2c2e", font=("Segoe UI", 9))
                chk.grid(row=i // 2, column=i % 2, sticky="w", padx=10)

        btn_container = tk.Frame(scrollable_frame, bg=self.bg_main)
        btn_container.pack(fill="x", pady=20)

        btns_inner = tk.Frame(btn_container, bg=self.bg_main)
        btns_inner.pack(expand=True)

        ListRoundedButton(btns_inner, text="Salvar viagem", command=lambda: self.save_trip(
            self.vehicle_combobox, self.additional_expenses_entry, self.total_km_entry, self.passenger_fare_entry,
            self.passenger_count_entry, self.start_date_entry, self.end_date_entry, self.description_entry
        ), bg=self.accent, fg=self.fg_text, width=180, height=40).pack(side="left", padx=10)

        ListRoundedButton(btns_inner, text="Voltar", command=self.back,
                          width=150, height=40, bg=self.bg_button, fg=self.fg_text).pack(side="left", padx=10)

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.config(state="normal")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
            date_entry.config(state="readonly")
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def validate_number(self, P):
        return not P or all(c.isdigit() for c in P)

    def validate_decimal(self, P):
        if not P: return True
        return all(c.isdigit() or c in ".," for c in P) and (P.count('.') + P.count(',') <= 1)

    def save_trip(self, vehicle_combobox, additional_expenses_entry, total_km_entry, passenger_fare_entry, passenger_count_entry,
                  start_date_entry, end_date_entry, description_entry):
        vehicle_text = vehicle_combobox.get()
        vehicle_id = int(vehicle_text.split("ID: ")[1].split(")")[0]) if vehicle_text else 0
        expenses = float(get_entry_value(additional_expenses_entry).replace(',', '.') or 0.0)
        km = float(get_entry_value(total_km_entry) or 0.0)
        fare = float(get_entry_value(passenger_fare_entry).replace(',', '.') or 0.0)
        p_count = int(get_entry_value(passenger_count_entry) or 0)
        s_date = start_date_entry.get().strip()
        e_date = end_date_entry.get().strip() or datetime.now().strftime('%d/%m/%Y')
        desc = get_entry_value(description_entry).upper()

        if not any(var.get() for var in self.driver_vars.values()):
            messagebox.showerror("Erro", "Selecione pelo menos um motorista.")
            return

        if not all([vehicle_id, km, fare, p_count, s_date, e_date]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            s_sql = datetime.strptime(s_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            e_sql = datetime.strptime(e_date, '%d/%m/%Y').strftime('%Y-%m-%d')

            trip = Trip(None, vehicle_id, expenses, km, fare, p_count, s_sql, e_sql, desc)
            trip_id = self.trip_repo.add(trip)
            if trip_id:
                for d_id, var in self.driver_vars.items():
                    if var.get():
                        self.trip_driver_repo.add(TripDriver(trip_id, d_id))
                messagebox.showinfo("Sucesso", "Viagem cadastrada com sucesso.")
                self.back()
        except Exception:
            messagebox.showerror("Erro", "Falha ao salvar a viagem.")

    def back(self):
        from app.interface.trip.interface_viagens import InterfaceViagem
        InterfaceViagem(self.parent, self.db_path).show()