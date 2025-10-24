import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from app.models.route_driver import RouteDriver
from app.repositories.route_repository import RouteRepository
from app.models.route import Route
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_driver_repository import RouteDriverRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.route_student_repository import RouteStudentRepository
from app.models.route_student import RouteStudent
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

class InterfaceCadastrarLinha:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.route_repo = RouteRepository(self.db_path)
        self.vehicle_repo = VehicleRepository(self.db_path)
        self.driver_repo = DriverRepository(self.db_path)
        self.route_driver_repo = RouteDriverRepository(self.db_path)
        self.student_repo = StudentRepository(self.db_path)
        self.route_student_repo = RouteStudentRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Cadastrar Linha", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(pady=10, padx=(350, 0), anchor="nw")
        main_frame.columnconfigure(0, weight=1)

        sub_frame = tk.Frame(main_frame, bg=self.bg_main)
        sub_frame.grid(row=0, column=0)

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
        style.configure("TCheckbutton", font=self.font_entry, background=self.bg_main, foreground=self.fg_text)
        style.map("TCheckbutton",
                  background=[("active", self.bg_button)],
                  foreground=[("active", self.fg_text)])
        style.configure("TCombobox", fieldbackground=self.bg_button, background=self.bg_button, foreground=self.fg_text, arrowcolor=self.fg_text)

        fields_frame = tk.Frame(sub_frame, bg=self.bg_main)
        fields_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(fields_frame, text="Veículo*:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        vehicles = self.vehicle_repo.get_all()
        vehicle_options = [f"{v.name} (ID: {v.vehicle_id})" for v in vehicles if v.vehicle_id]
        self.vehicle_combobox = ttk.Combobox(fields_frame, values=vehicle_options, width=25, state="readonly", style="TCombobox")
        self.vehicle_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        if vehicle_options:
            self.vehicle_combobox.set(vehicle_options[0])

        ttk.Label(fields_frame, text="Km Médio*:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        avg_km_entry = ttk.Entry(fields_frame, width=25, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        avg_km_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        add_placeholder(avg_km_entry, "Ex.: 50.5")

        ttk.Label(fields_frame, text="Período*:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        period_options = ["Matutino", "Vespertino", "Noturno", "Integral"]
        self.period_combobox = ttk.Combobox(fields_frame, values=period_options, width=25, state="readonly", style="TCombobox")
        self.period_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.period_combobox.set(period_options[0])

        ttk.Label(fields_frame, text="Tempo Médio (min)*:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        avg_time_minutes_entry = ttk.Entry(fields_frame, width=25, validate="key", validatecommand=(self.parent.register(self.validate_number), "%P"))
        avg_time_minutes_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        add_placeholder(avg_time_minutes_entry, "Ex.: 60")

        ttk.Label(fields_frame, text="Nome*:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        name_entry = ttk.Entry(fields_frame, width=25)
        name_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        add_placeholder(name_entry, "Ex.: Linha Centro")

        ttk.Label(fields_frame, text="Ativo*:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        active_var = tk.BooleanVar(value=True)
        active_check = ttk.Checkbutton(fields_frame, variable=active_var, style="TCheckbutton", text="Sim")
        active_check.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        ListRoundedButton(fields_frame, text="Salvar", command=lambda: self.save_linha(self.vehicle_combobox, avg_km_entry, self.period_combobox, avg_time_minutes_entry, name_entry, active_var), bg=self.bg_button, fg=self.fg_text, font=self.font_button).grid(row=0, column=7, sticky="e", padx=20, pady=5)

        drivers_students_frame = tk.Frame(sub_frame, bg=self.bg_main)
        drivers_students_frame.pack(fill="x", padx=10, pady=5)

        drivers_frame = tk.LabelFrame(drivers_students_frame, text="Motoristas", font=self.font_label, bg=self.bg_main, fg=self.fg_text)
        drivers_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        canvas_drivers = tk.Canvas(drivers_frame, bg=self.bg_main, width=200)
        scrollbar_drivers = tk.Scrollbar(drivers_frame, orient="vertical", command=canvas_drivers.yview)
        scrollable_frame_drivers = tk.Frame(canvas_drivers, bg=self.bg_main)

        scrollable_frame_drivers.bind(
            "<Configure>",
            lambda e: canvas_drivers.configure(scrollregion=canvas_drivers.bbox("all"))
        )

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
                chk = tk.Checkbutton(scrollable_frame_drivers, text=f"{driver.name} (ID: {driver.driver_id})", variable=var, bg=self.bg_main, fg=self.fg_text, activebackground=self.bg_button, selectcolor=self.bg_button, wraplength=180)
                chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        students_frame = tk.LabelFrame(drivers_students_frame, text="Alunos", font=self.font_label, bg=self.bg_main, fg=self.fg_text)
        students_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        canvas_students = tk.Canvas(students_frame, bg=self.bg_main, width=200)
        scrollbar_students = tk.Scrollbar(students_frame, orient="vertical", command=canvas_students.yview)
        scrollable_frame_students = tk.Frame(canvas_students, bg=self.bg_main)

        scrollable_frame_students.bind(
            "<Configure>",
            lambda e: canvas_students.configure(scrollregion=canvas_students.bbox("all"))
        )

        canvas_students.create_window((0, 0), window=scrollable_frame_students, anchor="nw")
        canvas_students.configure(yscrollcommand=scrollbar_students.set)

        canvas_students.pack(side="left", fill="both", expand=True)
        scrollbar_students.pack(side="right", fill="y")

        self.student_vars = {}
        students = self.student_repo.get_all()
        for i, student in enumerate(students):
            if student.student_id:
                var = tk.BooleanVar()
                self.student_vars[student.student_id] = var
                chk = tk.Checkbutton(scrollable_frame_students, text=f"{student.name} (ID: {student.student_id})", variable=var, bg=self.bg_main, fg=self.fg_text, activebackground=self.bg_button, selectcolor=self.bg_button, wraplength=180)
                chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        ttk.Label(sub_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"), foreground=self.fg_text).pack(pady=15)

    def validate_number(self, P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

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

    def save_linha(self, vehicle_combobox, avg_km_entry, period_combobox, avg_time_minutes_entry, name_entry, active_var):
        vehicle_text = vehicle_combobox.get()
        vehicle_id = int(vehicle_text.split("ID: ")[1].split(")")[0]) if vehicle_text else 0
        avg_km = float(get_entry_value(avg_km_entry).replace(',', '.') or 0.0)
        period = period_combobox.get().strip()
        avg_time_minutes = int(get_entry_value(avg_time_minutes_entry) or 0)
        name = get_entry_value(name_entry)
        active = 1 if active_var.get() else 0

        if not all([vehicle_id, avg_km, period, avg_time_minutes, name]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            route = Route(None, vehicle_id, avg_km, period, avg_time_minutes, name, active)
            route_id = self.route_repo.add(route)
            if route_id:
                for driver_id, var in self.driver_vars.items():
                    if var.get():
                        route_driver = RouteDriver(route_id, driver_id)
                        self.route_driver_repo.add(route_driver)

                for student_id, var in self.student_vars.items():
                    if var.get():
                        route_student = RouteStudent(route_id, student_id, datetime.now().strftime('%Y-%m-%d'), None)
                        self.route_student_repo.add(route_student)

                messagebox.showinfo("Sucesso", f"Linha cadastrada com ID {route_id} e motoristas/alunos associados!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar a linha.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        interface = InterfaceLinha(self.parent, self.db_path)
        interface.show()
