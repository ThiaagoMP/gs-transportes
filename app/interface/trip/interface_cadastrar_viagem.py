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
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Cadastrar Viagem",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="center"
        ).pack(pady=(20, 30), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(pady=(20, 10), padx=30, fill="both", expand=True)

        main_frame.columnconfigure(0, weight=0, minsize=200)
        main_frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=("Segoe UI", 12), padding=6, fieldbackground=self.bg_button, foreground=self.fg_text)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10,
                        background=self.bg_button, foreground=self.fg_text)
        style.map("TButton", background=[("active", self.accent)], foreground=[("active", self.fg_text)])
        style.configure("Placeholder.TEntry", foreground="#333333", fieldbackground="#666666")

        validate_number_cmd = self.parent.register(self.validate_number)
        validate_decimal_cmd = self.parent.register(self.validate_decimal)

        ttk.Label(main_frame, text="Veículo Utilizado*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        vehicles = self.vehicle_repo.get_all()
        vehicle_options = [f"{v.name} (ID: {v.vehicle_id})" for v in vehicles if v.vehicle_id]
        self.vehicle_combobox = ttk.Combobox(main_frame, values=vehicle_options, width=45, state="readonly")
        self.vehicle_combobox.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        if vehicle_options:
            self.vehicle_combobox.set(vehicle_options[0])

        ttk.Label(main_frame, text="Despesas Adicionais (R$)*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        self.additional_expenses_entry = ttk.Entry(main_frame, width=45, validate="key",
                                                  validatecommand=(validate_decimal_cmd, "%P"))
        self.additional_expenses_entry.grid(row=1, column=1, padx=15, pady=15, sticky="w")
        add_placeholder(self.additional_expenses_entry, "Ex.: 500.00")

        ttk.Label(main_frame, text="Quilometragem Total (km)*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        self.total_km_entry = ttk.Entry(main_frame, width=45, validate="key",
                                       validatecommand=(validate_number_cmd, "%P"))
        self.total_km_entry.grid(row=2, column=1, padx=15, pady=15, sticky="w")
        add_placeholder(self.total_km_entry, "Ex.: 1000")

        ttk.Label(main_frame, text="Valor por Passageiro (R$)*:").grid(row=3, column=0, sticky="e", padx=15, pady=15)
        self.passenger_fare_entry = ttk.Entry(main_frame, width=45, validate="key",
                                             validatecommand=(validate_decimal_cmd, "%P"))
        self.passenger_fare_entry.grid(row=3, column=1, padx=15, pady=15, sticky="w")
        add_placeholder(self.passenger_fare_entry, "Ex.: 50.00")

        ttk.Label(main_frame, text="Quantidade de Passageiros*:").grid(row=4, column=0, sticky="e", padx=15, pady=15)
        self.passenger_count_entry = ttk.Entry(main_frame, width=45, validate="key",
                                              validatecommand=(validate_number_cmd, "%P"))
        self.passenger_count_entry.grid(row=4, column=1, padx=15, pady=15, sticky="w")
        add_placeholder(self.passenger_count_entry, "Ex.: 10")

        ttk.Label(main_frame, text="Data de Início*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        date_frame = tk.Frame(main_frame, bg=self.bg_main)
        date_frame.grid(row=5, column=1, sticky="w", padx=15, pady=15)
        self.start_date_entry = tk.Entry(date_frame, width=43, font=("Segoe UI", 12), bg="#666666", fg=self.fg_text, insertbackground=self.fg_text, state="readonly")
        self.start_date_entry.pack(side="left", padx=0)
        self.start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(date_frame, text="Selecionar Data", command=lambda: self.open_calendar(self.start_date_entry), bg=self.bg_button, fg=self.fg_text, font=("Segoe UI", 10)).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Data de Fim*:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        end_date_frame = tk.Frame(main_frame, bg=self.bg_main)
        end_date_frame.grid(row=6, column=1, sticky="w", padx=15, pady=15)
        self.end_date_entry = tk.Entry(end_date_frame, width=43, font=("Segoe UI", 12), bg="#666666", fg=self.fg_text, insertbackground=self.fg_text, state="readonly")
        self.end_date_entry.pack(side="left", padx=0)
        ListRoundedButton(end_date_frame, text="Selecionar Data", command=lambda: self.open_calendar(self.end_date_entry), bg=self.bg_button, fg=self.fg_text, font=("Segoe UI", 10)).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Descrição:").grid(row=7, column=0, sticky="e", padx=15, pady=15)
        self.description_entry = ttk.Entry(main_frame, width=45, foreground=self.fg_text)
        self.description_entry.grid(row=7, column=1, padx=15, pady=15, sticky="w")
        add_placeholder(self.description_entry, "Ex.: Viagem de teste")

        drivers_frame = tk.LabelFrame(main_frame, text="Motoristas", font=("Segoe UI", 14), bg=self.bg_main, fg=self.accent)
        drivers_frame.grid(row=8, column=0, columnspan=1, padx=15, pady=15, sticky="ew")

        canvas_drivers = tk.Canvas(drivers_frame, bg=self.bg_main, highlightthickness=0)
        scrollbar_drivers = tk.Scrollbar(drivers_frame, orient="vertical", command=canvas_drivers.yview)
        scrollable_frame_drivers = tk.Frame(canvas_drivers, bg=self.bg_main)

        scrollable_frame_drivers.bind("<Configure>", lambda e: canvas_drivers.configure(scrollregion=canvas_drivers.bbox("all")))
        canvas_drivers.create_window((0, 0), window=scrollable_frame_drivers, anchor="nw")
        canvas_drivers.configure(yscrollcommand=scrollbar_drivers.set)
        canvas_drivers.pack(side="left", fill="both", expand=True)
        scrollbar_drivers.pack(side="right", fill="y")

        self.driver_vars = {}
        drivers = self.driver_repo.get_all()
        active_drivers = [d for d in drivers if not d.end_date]
        for i, driver in enumerate(active_drivers):
            if driver.driver_id:
                var = tk.BooleanVar()
                self.driver_vars[driver.driver_id] = var
                chk = tk.Checkbutton(scrollable_frame_drivers,
                                     text=f"{driver.name} (ID: {driver.driver_id})",
                                     variable=var,
                                     bg=self.bg_main,
                                     fg=self.fg_text,
                                     activebackground=self.bg_main,
                                     selectcolor=self.bg_main,
                                     wraplength=180)
                chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        button_frame = tk.Frame(self.parent, bg=self.bg_main)
        button_frame.place(relx=0.5, rely=0.95, anchor="center")

        ListRoundedButton(button_frame, text="Salvar", command=lambda: self.save_trip(
            self.vehicle_combobox, self.additional_expenses_entry, self.total_km_entry, self.passenger_fare_entry,
            self.passenger_count_entry, self.start_date_entry, self.end_date_entry, self.description_entry
        ), bg=self.bg_button, fg=self.fg_text, hover_bg=self.accent, width=200, height=45, font=("Segoe UI", 11, "bold")).pack()

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.config(state="normal")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
            date_entry.config(state="readonly")
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def validate_number(self, P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

    def validate_decimal(self, P):
        if not P:
            return True
        return all(c.isdigit() or c in ".," for c in P) and P.count('.') <= 1

    def save_trip(self, vehicle_combobox, additional_expenses_entry, total_km_entry, passenger_fare_entry, passenger_count_entry,
                  start_date_entry, end_date_entry, description_entry):
        vehicle_text = vehicle_combobox.get()
        vehicle_id = int(vehicle_text.split("ID: ")[1].split(")")[0]) if vehicle_text else 0
        additional_expenses = float(get_entry_value(additional_expenses_entry).replace(',', '.') or 0.0)
        total_km = float(get_entry_value(total_km_entry) or 0.0)
        passenger_fare = float(get_entry_value(passenger_fare_entry).replace(',', '.') or 0.0)
        passenger_count = int(get_entry_value(passenger_count_entry) or 0)
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip() or datetime.now().strftime('%d/%m/%Y')
        description = get_entry_value(description_entry)

        if not any(var.get() for var in self.driver_vars.values()):
            messagebox.showerror("Erro", "Selecione pelo menos um motorista.")
            return

        if not all([vehicle_id, total_km, passenger_fare, passenger_count, start_date, end_date]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
            end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
            start_date_sql = start_date_obj.strftime('%Y-%m-%d')
            end_date_sql = end_date_obj.strftime('%Y-%m-%d')

            trip = Trip(None, vehicle_id, additional_expenses, total_km, passenger_fare, passenger_count, start_date_sql, end_date_sql, description)
            trip_id = self.trip_repo.add(trip)
            if trip_id:
                for driver_id, var in self.driver_vars.items():
                    if var.get():
                        trip_driver = TripDriver(trip_id, driver_id)
                        self.trip_driver_repo.add(trip_driver)

                messagebox.showinfo("Sucesso", f"Viagem cadastrada com ID {trip_id} e motoristas associados!")
                vehicle_combobox.set("")
                additional_expenses_entry.delete(0, tk.END)
                total_km_entry.delete(0, tk.END)
                passenger_fare_entry.delete(0, tk.END)
                passenger_count_entry.delete(0, tk.END)
                start_date_entry.delete(0, tk.END)
                start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
                end_date_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)
                for var in self.driver_vars.values():
                    var.set(False)
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar a viagem.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.trip.interface_viagens import InterfaceViagem
        interface = InterfaceViagem(self.parent, self.db_path)
        interface.show()
