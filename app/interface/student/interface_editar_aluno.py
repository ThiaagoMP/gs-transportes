import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.student_repository import StudentRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.route_student_repository import RouteStudentRepository
from app.models.student import Student
from app.components.list_rounded_button import ListRoundedButton


def add_placeholder(entry, placeholder):
    entry._ph_text = placeholder
    entry._ph_active = False

    def _show_placeholder():
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.configure(fg="#7a7a7a")
        entry._ph_active = True

    def _hide_placeholder():
        entry.delete(0, tk.END)
        entry.configure(fg="#ffffff")
        entry._ph_active = False

    def on_focus_in(_):
        if entry._ph_active: _hide_placeholder()

    def on_focus_out(_):
        if not entry.get(): _show_placeholder()

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    _show_placeholder()


def get_entry_value(entry) -> str:
    text = entry.get().strip()
    if getattr(entry, "_ph_active", False) or text == getattr(entry, "_ph_text", None):
        return ""
    return text


class InterfaceEditarAluno:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.student_repo = StudentRepository(self.db_path)
        self.route_repo = RouteRepository(self.db_path)
        self.route_student_repo = RouteStudentRepository(self.db_path)
        self.student = self.student_repo.get_by_id(student_id) if student_id else None

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 22, "bold")
        self.font_label = ("Segoe UI", 11)
        self.font_entry = ("Segoe UI", 11)

    def show(self):
        if not self.student:
            messagebox.showerror("Erro", "Aluno não encontrado.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="Editar aluno", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(
            pady=(15, 10))

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True)

        container = tk.Frame(main_frame, bg=self.bg_main)
        container.pack(anchor="center")

        fields_data = [
            ("Nome*:", self.student.name, "Ex.: João Silva"),
            ("Contato*:", self.student.contact, "Ex.: (11) 99999-9999"),
            ("Endereço*:", self.student.address, "Ex.: Rua das Flores, 123"),
            ("Informações extras:", self.student.extra_info, "Ex.: Aluno especial"),
            ("Valor do contrato (R$)*:", str(self.student.contract_value), "Ex.: 500.00"),
            ("Dia de vencimento*:", str(self.student.due_day), "Ex.: 15"),
            ("RG*:", self.student.rg, "Ex.: 12.345.678-9"),
            ("CPF*:", self.student.cpf, "Ex.: 123.456.789-00")
        ]

        self.entries = {}

        for i, (lbl_txt, val, ph) in enumerate(fields_data):
            tk.Label(container, text=lbl_txt, font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=i,
                                                                                                           column=0,
                                                                                                           sticky="e",
                                                                                                           padx=10,
                                                                                                           pady=4)
            ent = tk.Entry(container, width=50, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                           insertbackground="white", borderwidth=0)
            ent.grid(row=i, column=1, sticky="w", padx=10, pady=4)
            if val and str(val).strip():
                ent.insert(0, str(val))
            else:
                add_placeholder(ent, ph)
            self.entries[lbl_txt] = ent

        routes_frame = tk.LabelFrame(container, text="Linhas vinculadas", font=("Segoe UI", 10, "bold"),
                                     bg=self.bg_main, fg=self.accent, padx=5, pady=5)
        routes_frame.grid(row=len(fields_data), column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        canvas = tk.Canvas(routes_frame, bg=self.bg_main, height=80, highlightthickness=0)
        scrollbar = tk.Scrollbar(routes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.route_vars, self.route_ids = [], []
        current_routes = [rs.route_id for rs in self.route_student_repo.get_by_student_id(self.student_id)]

        for route in self.route_repo.get_all():
            var = tk.IntVar(value=1 if route.route_id in current_routes else 0)
            chk = tk.Checkbutton(scrollable_frame, text=getattr(route, 'name', '').upper(), variable=var,
                                 bg=self.bg_main, activebackground=self.bg_main, fg=self.fg_text,
                                 activeforeground=self.accent, selectcolor=self.bg_field, font=("Segoe UI", 9),
                                 highlightthickness=0, bd=0)
            chk.pack(anchor="w", padx=5, pady=1)
            self.route_vars.append(var)
            self.route_ids.append(route.route_id)

        btn_frame = tk.Frame(container, bg=self.bg_main)
        btn_frame.grid(row=len(fields_data) + 1, column=0, columnspan=2, pady=15)

        btns_inner = tk.Frame(btn_frame, bg=self.bg_main)
        btns_inner.pack(expand=True)

        ListRoundedButton(btns_inner, text="Atualizar dados", command=self.process_update, bg=self.accent,
                          fg=self.fg_text, width=180, height=40).pack(side="left", padx=10)
        ListRoundedButton(btns_inner, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, width=130,
                          height=40).pack(side="left", padx=10)

    def process_update(self):
        data = {lbl: get_entry_value(ent) for lbl, ent in self.entries.items()}
        try:
            val_contract_str = data["Valor do contrato (R$)*:"].replace(',', '.')
            val_contract = float(val_contract_str or 0.0)
            val_due_str = data["Dia de vencimento*:"]
            val_due = int(val_due_str or 0)

            if not all([data["Nome*:"], data["Contato*:"], data["Endereço*:"], val_contract_str, val_due_str]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return

            student = Student(self.student_id, data["Contato*:"], data["Endereço*:"], data["Nome*:"],
                              data["Informações extras:"], val_contract, val_due, data["RG*:"], data["CPF*:"])
            if self.student_repo.update(student):
                self.update_routes()
                messagebox.showinfo("Sucesso", "Dados atualizados com sucesso.")
                self.back()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {str(e)}")

    def update_routes(self):
        current = set([rs.route_id for rs in self.route_student_repo.get_by_student_id(self.student_id)])
        selected = set([self.route_ids[i] for i, var in enumerate(self.route_vars) if var.get() == 1])
        for r_id in (current - selected):
            today = datetime.now().strftime('%Y-%m-%d')
            self.route_student_repo.update_end_date(r_id, self.student_id, today)
        for r_id in (selected - current):
            self.route_student_repo.add_student_to_route(r_id, self.student_id)

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        InterfaceAluno(self.parent, self.db_path).show()