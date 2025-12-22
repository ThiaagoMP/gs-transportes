import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.repositories.student_repository import StudentRepository
from app.repositories.route_repository import RouteRepository
from app.models.student import Student
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

class InterfaceCadastrarAluno:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.student_repo = StudentRepository(self.db_path)
        self.route_repo = RouteRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 22, "bold")
        self.font_label = ("Segoe UI", 11)
        self.font_entry = ("Segoe UI", 11)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="Cadastrar aluno", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=(15, 10))

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True)

        container = tk.Frame(main_frame, bg=self.bg_main)
        container.pack(anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, fieldbackground=self.bg_field, foreground=self.fg_text, insertcolor="white", borderwidth=0)
        style.configure("Placeholder.TEntry", foreground="#7a7a7a", fieldbackground=self.bg_field)

        fields = [
            ("Nome*:", "Ex.: João Silva"),
            ("Contato*:", "Ex.: (11) 99999-9999"),
            ("Endereço*:", "Ex.: Rua das Flores, 123"),
            ("Informações extras:", "Ex.: Aluno especial"),
            ("Valor do contrato (R$)*:", "Ex.: 500.00"),
            ("Dia de vencimento*:", "Ex.: 15"),
            ("RG*:", "Ex.: 12.345.678-9"),
            ("CPF*:", "Ex.: 123.456.789-00")
        ]

        self.entries = {}

        for i, (label_text, placeholder) in enumerate(fields):
            ttk.Label(container, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=4)

            val_cmd = None
            if "Valor" in label_text: val_cmd = (self.parent.register(self.validate_decimal), "%P")
            elif "Vencimento" in label_text: val_cmd = (self.parent.register(self.validate_number_max), "%P", 2)
            elif "RG" in label_text: val_cmd = (self.parent.register(self.validate_and_format_rg), "%P", "%s", "%W")
            elif "CPF" in label_text: val_cmd = (self.parent.register(self.validate_and_format_cpf), "%P", "%s", "%W")

            entry = ttk.Entry(container, width=45, validate="key", validatecommand=val_cmd)
            entry.grid(row=i, column=1, sticky="w", padx=10, pady=4)
            add_placeholder(entry, placeholder)
            self.entries[label_text] = entry

        routes_frame = tk.LabelFrame(container, text="Vincular linhas", font=("Segoe UI", 10, "bold"), bg=self.bg_main, fg=self.accent, padx=5, pady=5)
        routes_frame.grid(row=len(fields), column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        canvas_routes = tk.Canvas(routes_frame, bg=self.bg_main, height=80, highlightthickness=0)
        scrollbar_routes = tk.Scrollbar(routes_frame, orient="vertical", command=canvas_routes.yview)
        scrollable_frame_routes = tk.Frame(canvas_routes, bg=self.bg_main)

        scrollable_frame_routes.bind("<Configure>", lambda e: canvas_routes.configure(scrollregion=canvas_routes.bbox("all")))
        canvas_routes.create_window((0, 0), window=scrollable_frame_routes, anchor="nw")
        canvas_routes.configure(yscrollcommand=scrollbar_routes.set)
        canvas_routes.pack(side="left", fill="both", expand=True)
        scrollbar_routes.pack(side="right", fill="y")

        self.route_vars, self.routes = [], []
        for route in self.route_repo.get_all():
            var = tk.IntVar()
            chk = tk.Checkbutton(scrollable_frame_routes, text=getattr(route, 'name', '').upper(), variable=var, bg=self.bg_main, activebackground=self.bg_main, fg=self.fg_text, activeforeground=self.accent, selectcolor=self.bg_field, font=("Segoe UI", 9), highlightthickness=0, bd=0)
            chk.pack(anchor="w", padx=5, pady=1)
            self.route_vars.append(var)
            self.routes.append(route.route_id)

        button_frame = tk.Frame(container, bg=self.bg_main)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=15)

        btns_inner = tk.Frame(button_frame, bg=self.bg_main)
        btns_inner.pack(expand=True)

        ListRoundedButton(btns_inner, text="Salvar cadastro", command=self.process_save, bg=self.accent, fg=self.fg_text, width=180, height=40).pack(side="left", padx=10)
        ListRoundedButton(btns_inner, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, width=130, height=40).pack(side="left", padx=10)

        tk.Label(container, text="* Campos obrigatórios", font=("Segoe UI", 9, "italic"), bg=self.bg_main, fg="#aaaaaa").grid(row=len(fields) + 2, column=0, columnspan=2)

    def validate_number_max(self, P, max_len):
        return not P or (P.isdigit() and len(P) <= int(max_len))

    def validate_decimal(self, P):
        if not P: return True
        try:
            p_fixed = P.replace(',', '.')
            return p_fixed.count('.') <= 1 and all(c.isdigit() or c == '.' for c in p_fixed)
        except: return False

    def validate_and_format_rg(self, P, S, W):
        if not P: return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 9: return False
        formatted = self.format_rg(digits)
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
        return True

    def validate_and_format_cpf(self, P, S, W):
        if not P: return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 11: return False
        formatted = self.format_cpf(digits)
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
        return True

    def format_rg(self, digits):
        if len(digits) <= 2: return digits
        elif len(digits) <= 5: return f"{digits[:2]}.{digits[2:]}"
        elif len(digits) <= 8: return f"{digits[:2]}.{digits[2:5]}.{digits[5:]}"
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8:]}"

    def format_cpf(self, digits):
        if len(digits) <= 3: return digits
        elif len(digits) <= 6: return f"{digits[:3]}.{digits[3:]}"
        elif len(digits) <= 9: return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def process_save(self):
        data = {lbl: get_entry_value(ent) for lbl, ent in self.entries.items()}
        try:
            val_contract_str = data["Valor do contrato (R$)*:"].replace(',', '.')
            val_contract = float(val_contract_str or 0.0)
            due_day = int(data["Dia de vencimento*:"] or 0)
            if not all([data["Nome*:"], data["Contato*:"], data["Endereço*:"], val_contract_str, data["Dia de vencimento*:"]]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return
            selected_routes = [self.routes[i] for i, var in enumerate(self.route_vars) if var.get() == 1]
            student = Student(None, data["Contato*:"], data["Endereço*:"], data["Nome*:"], data["Informações extras:"], val_contract, due_day, data["RG*:"], data["CPF*:"])
            student_id = self.student_repo.add(student)
            if student_id:
                from app.repositories.route_student_repository import RouteStudentRepository
                rs_repo = RouteStudentRepository(self.db_path)
                for r_id in selected_routes: rs_repo.add_student_to_route(r_id, student_id)
                messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso.")
                self.back()
        except Exception as e: messagebox.showerror("Erro", f"Falha ao realizar o cadastro: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        InterfaceAluno(self.parent, self.db_path).show()