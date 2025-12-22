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


class InterfaceEditarLinha:
    def __init__(self, parent, db_path, route_id):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id
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
        route = self.route_repo.get_by_id(self.route_id)
        if not route:
            messagebox.showerror("Erro", "Linha nao encontrada.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="EDITAR LINHA", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(
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
        style.configure("TCombobox", fieldbackground=self.bg_field, background=self.bg_field, foreground=self.fg_text,
                        arrowcolor=self.fg_text)
        style.map("TCombobox", fieldbackground=[("readonly", self.bg_field)], foreground=[("readonly", self.fg_text)])

        fields_frame = tk.Frame(container_form, bg=self.bg_main)
        fields_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(fields_frame, text="Veiculo*:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        vehicles = self.vehicle_repo.get_all()
        vehicle_options = [f"{v.name} (ID: {v.vehicle_id})" for v in vehicles if v.vehicle_id]
        self.vehicle_combobox = ttk.Combobox(fields_frame, values=vehicle_options, width=32, state="readonly",
                                             style="TCombobox")
        self.vehicle_combobox.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        v_sel = next((v for v in vehicle_options if f"ID: {route.vehicle_id})" in v), "")
        if v_sel: self.vehicle_combobox.set(v_sel)

        ttk.Label(fields_frame, text="Km Medio*:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.avg_km_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                                     relief="flat", borderwidth=0, insertbackground=self.fg_text)
        self.avg_km_entry.insert(0, str(route.avg_km))
        self.avg_km_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w", ipady=3)

        ttk.Label(fields_frame, text="Periodo*:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        p_opts = ["Matutino", "Vespertino", "Noturno", "Integral"]
        self.period_combobox = ttk.Combobox(fields_frame, values=p_opts, width=32, state="readonly", style="TCombobox")
        self.period_combobox.grid(row=2, column=1, padx=5, pady=3, sticky="w")
        self.period_combobox.set(route.period)

        ttk.Label(fields_frame, text="Tempo (min)*:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.avg_time_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                                       relief="flat", borderwidth=0, insertbackground=self.fg_text)
        self.avg_time_entry.insert(0, str(route.avg_time_minutes))
        self.avg_time_entry.grid(row=3, column=1, padx=5, pady=3, sticky="w", ipady=3)

        ttk.Label(fields_frame, text="Nome*:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.name_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                                   relief="flat", borderwidth=0, insertbackground=self.fg_text)
        self.name_entry.insert(0, route.name)
        self.name_entry.grid(row=4, column=1, padx=5, pady=3, sticky="w", ipady=3)

        ttk.Label(fields_frame, text="Contrato (R$)*:").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        self.contract_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                                       relief="flat", borderwidth=0, insertbackground=self.fg_text)
        self.contract_entry.insert(0, str(route.contract_value))
        self.contract_entry.grid(row=5, column=1, padx=5, pady=3, sticky="w", ipady=3)

        ttk.Label(fields_frame, text="Ativo:").grid(row=6, column=0, sticky="e", padx=5, pady=3)
        active_var = tk.BooleanVar(value=bool(route.active))
        tk.Checkbutton(fields_frame, variable=active_var, bg=self.bg_main, fg=self.fg_text, selectcolor=self.bg_field,
                       activebackground=self.bg_main, activeforeground=self.fg_text, text="Sim",
                       font=self.font_entry).grid(row=6, column=1, padx=5, pady=3, sticky="w")

        lists_frame = tk.Frame(container_form, bg=self.bg_main)
        lists_frame.pack(fill="x", padx=10, pady=10)

        route_drivers = self.route_driver_repo.get_by_route_id(self.route_id)
        sel_driver_ids = {rd.driver_id for rd in route_drivers} if route_drivers else set()

        route_students = self.route_student_repo.get_students_by_route_id(self.route_id)
        sel_student_ids = {rs.student_id for rs in route_students if rs.end_date is None}

        for title, repo_get, vars_dict, selected_ids in [
            ("MOTORISTAS", self.driver_repo.get_all, "driver_vars", sel_driver_ids),
            ("ALUNOS", self.student_repo.get_all, "student_vars", sel_student_ids)
        ]:
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
                iid = item.driver_id if title == "MOTORISTAS" else item.student_id
                if title == "MOTORISTAS" and item.end_date and iid not in selected_ids: continue
                v = tk.BooleanVar(value=iid in selected_ids)
                res_dict[iid] = v
                tk.Checkbutton(scroll_f, text=item.name.upper(), variable=v, bg=self.bg_main, fg=self.fg_text,
                               activebackground=self.bg_button, selectcolor=self.bg_button, font=("Segoe UI", 8)).pack(
                    anchor="w", padx=2)
            setattr(self, vars_dict, res_dict)

        btn_container = tk.Frame(container_form, bg=self.bg_main)
        btn_container.pack(pady=15)

        ListRoundedButton(btn_container, text="Salvar alterações", command=lambda: self.save_linha(active_var),
                          bg=self.accent, fg=self.fg_text, width=180, height=40).pack(side="left", padx=10)
        ListRoundedButton(btn_container, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text,
                          width=120, height=40).pack(side="left", padx=10)

    def save_linha(self, active_var):
        v_text = self.vehicle_combobox.get()
        try:
            v_id = int(v_text.split("ID: ")[1].split(")")[0]) if "ID: " in v_text else 0
            avg_km = float(self.avg_km_entry.get().replace(',', '.'))
            avg_time = int(self.avg_time_entry.get())
            val = float(self.contract_entry.get().replace(',', '.'))
            name = self.name_entry.get().strip()
            period = self.vehicle_combobox.get()

            if not all([v_id, name]):
                messagebox.showerror("Erro", "Preencha os campos obrigatórios.")
                return

            route = Route(self.route_id, v_id, avg_km, self.period_combobox.get(), avg_time, name,
                          1 if active_var.get() else 0, val)

            if self.route_repo.update(route):
                self.route_driver_repo.delete_by_route_id(self.route_id)
                for d_id, var in self.driver_vars.items():
                    if var.get(): self.route_driver_repo.add(RouteDriver(self.route_id, d_id))

                all_rs = self.route_student_repo.get_students_by_route_id(self.route_id)
                curr_active = {rs.student_id for rs in all_rs if rs.end_date is None}
                sel_ids = {s_id for s_id, var in self.student_vars.items() if var.get()}

                for s_id in curr_active - sel_ids:
                    self.route_student_repo.update_end_date(self.route_id, s_id, datetime.now().strftime('%Y-%m-%d'))
                for s_id in sel_ids - curr_active:
                    existing = next((rs for rs in all_rs if rs.student_id == s_id), None)
                    if existing:
                        self.route_student_repo.update_end_date(self.route_id, s_id, None)
                    else:
                        self.route_student_repo.add(
                            RouteStudent(self.route_id, s_id, datetime.now().strftime('%Y-%m-%d'), None))

                messagebox.showinfo("Sucesso", "Linha atualizada!")
                self.back()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        InterfaceLinha(self.parent, self.db_path).show()