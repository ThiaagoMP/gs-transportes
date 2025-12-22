import tkinter as tk
from tkinter import ttk, messagebox
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
    if getattr(entry, "_ph_active", False) or text == getattr(entry, "_ph_text", None):
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
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 22, "bold")
        self.font_label = ("Segoe UI", 11)
        self.font_entry = ("Segoe UI", 11)
        self.font_button = ("Segoe UI", 9, "bold")

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="CADASTRAR LINHA", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(
            pady=(15, 10))

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True)

        container_form = tk.Frame(main_frame, bg=self.bg_main)
        container_form.pack(anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, fieldbackground=self.bg_field, foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Placeholder.TEntry", foreground="#7a7a7a", fieldbackground=self.bg_field)
        style.configure("TCombobox", fieldbackground=self.bg_field, background=self.bg_field, foreground=self.fg_text,
                        arrowcolor=self.fg_text)
        style.map("TCombobox", fieldbackground=[("readonly", self.bg_field)], foreground=[("readonly", self.fg_text)])

        fields_frame = tk.Frame(container_form, bg=self.bg_main)
        fields_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(fields_frame, text="Veículo*:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        vehicles = self.vehicle_repo.get_all()
        vehicle_options = [f"{v.name} (ID: {v.vehicle_id})" for v in vehicles if v.vehicle_id]
        self.vehicle_combobox = ttk.Combobox(fields_frame, values=vehicle_options, width=32, state="readonly",
                                             style="TCombobox")
        self.vehicle_combobox.grid(row=0, column=1, padx=5, pady=3, sticky="w")
        if vehicle_options: self.vehicle_combobox.set(vehicle_options[0])

        ttk.Label(fields_frame, text="Km Médio*:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        avg_km_entry = ttk.Entry(fields_frame, width=35, validate="key",
                                 validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        avg_km_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        add_placeholder(avg_km_entry, "Ex.: 50.5")

        ttk.Label(fields_frame, text="Período*:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        period_options = ["Matutino", "Vespertino", "Noturno", "Integral"]
        self.period_combobox = ttk.Combobox(fields_frame, values=period_options, width=32, state="readonly",
                                            style="TCombobox")
        self.period_combobox.grid(row=2, column=1, padx=5, pady=3, sticky="w")
        self.period_combobox.set(period_options[0])

        ttk.Label(fields_frame, text="Tempo (min)*:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        avg_time_minutes_entry = ttk.Entry(fields_frame, width=35, validate="key",
                                           validatecommand=(self.parent.register(self.validate_number), "%P"))
        avg_time_minutes_entry.grid(row=3, column=1, padx=5, pady=3, sticky="w")
        add_placeholder(avg_time_minutes_entry, "Ex.: 60")

        ttk.Label(fields_frame, text="Nome*:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        name_entry = ttk.Entry(fields_frame, width=35)
        name_entry.grid(row=4, column=1, padx=5, pady=3, sticky="w")
        add_placeholder(name_entry, "Ex.: Linha Centro")

        ttk.Label(fields_frame, text="Contrato (R$)*:").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        contract_value_entry = ttk.Entry(fields_frame, width=35, validate="key",
                                         validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        contract_value_entry.grid(row=5, column=1, padx=5, pady=3, sticky="w")
        add_placeholder(contract_value_entry, "Ex.: 1500.00")

        ttk.Label(fields_frame, text="Ativo:").grid(row=6, column=0, sticky="e", padx=5, pady=3)
        active_var = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(fields_frame, variable=active_var, bg=self.bg_main, fg=self.fg_text,
                                      selectcolor=self.bg_field, activebackground=self.bg_main,
                                      activeforeground=self.fg_text, text="Sim", font=self.font_entry)
        active_check.grid(row=6, column=1, padx=5, pady=3, sticky="w")

        lists_frame = tk.Frame(container_form, bg=self.bg_main)
        lists_frame.pack(fill="x", padx=10, pady=10)

        for title, repo_get, vars_dict in [("MOTORISTAS", self.driver_repo.get_all, "driver_vars"),
                                           ("ALUNOS", self.student_repo.get_all, "student_vars")]:
            frame = tk.LabelFrame(lists_frame, text=title, font=("Segoe UI", 9, "bold"), bg=self.bg_main,
                                  fg=self.accent, borderwidth=1, relief="flat")
            frame.pack(side="left", fill="both", expand=True, padx=5)

            canvas = tk.Canvas(frame, bg=self.bg_main, width=200, height=100, highlightthickness=0)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scroll_f = tk.Frame(canvas, bg=self.bg_main)

            scroll_f.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=scroll_f, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            res_dict = {}
            items = repo_get()
            for item in items:
                if title == "MOTORISTAS" and item.end_date: continue
                v = tk.BooleanVar()
                iid = item.driver_id if title == "MOTORISTAS" else item.student_id
                res_dict[iid] = v
                tk.Checkbutton(scroll_f, text=item.name.upper(), variable=v, bg=self.bg_main, fg=self.fg_text,
                               activebackground=self.bg_button, selectcolor=self.bg_button, font=("Segoe UI", 8)).pack(
                    anchor="w", padx=2)
            setattr(self, vars_dict, res_dict)

        btn_container = tk.Frame(container_form, bg=self.bg_main)
        btn_container.pack(pady=15)

        ListRoundedButton(btn_container, text="Salvar linha",
                          command=lambda: self.save_linha(self.vehicle_combobox, avg_km_entry, self.period_combobox,
                                                          avg_time_minutes_entry, name_entry, contract_value_entry,
                                                          active_var), bg=self.accent, fg=self.fg_text, width=180,
                          height=40).pack(side="left", padx=10)
        ListRoundedButton(btn_container, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text,
                          width=120, height=40).pack(side="left", padx=10)

    def validate_number(self, P):
        return P.isdigit() or P == ""

    def validate_decimal(self, P):
        if not P: return True
        p_fixed = P.replace(',', '.')
        return p_fixed.count('.') <= 1 and all(c.isdigit() or c == '.' for c in p_fixed)

    def save_linha(self, vehicle_combobox, avg_km_entry, period_combobox, avg_time_minutes_entry, name_entry,
                   contract_value_entry, active_var):
        vehicle_text = vehicle_combobox.get()
        try:
            v_id = int(vehicle_text.split("ID: ")[1].split(")")[0]) if "ID: " in vehicle_text else 0
        except:
            v_id = 0

        km = get_entry_value(avg_km_entry).replace(',', '.')
        time = get_entry_value(avg_time_minutes_entry)
        val = get_entry_value(contract_value_entry).replace(',', '.')
        name = get_entry_value(name_entry)
        period = period_combobox.get().strip()

        if not all([v_id, km, period, time, name, val]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            route = Route(None, v_id, float(km), period, int(time), name, 1 if active_var.get() else 0, float(val))
            rid = self.route_repo.add(route)
            if rid:
                for d_id, var in self.driver_vars.items():
                    if var.get(): self.route_driver_repo.add(RouteDriver(rid, d_id))
                for s_id, var in self.student_vars.items():
                    if var.get(): self.route_student_repo.add(
                        RouteStudent(rid, s_id, datetime.now().strftime('%Y-%m-%d'), None))
                messagebox.showinfo("Sucesso", "Linha cadastrada!")
                self.back()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        InterfaceLinha(self.parent, self.db_path).show()