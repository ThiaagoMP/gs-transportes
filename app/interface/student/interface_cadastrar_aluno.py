import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from app.repositories.student_repository import StudentRepository
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
    if getattr(entry, "_ph_active", False):
        return ""
    if text == getattr(entry, "_ph_text", None):
        return ""
    return text

class InterfaceCadastrarAluno:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.student_repo = StudentRepository(self.db_path)

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

        tk.Label(self.parent, text="Cadastrar Aluno", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=25)

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

        ttk.Label(sub_frame, text="Contato*:").grid(row=0, column=0, sticky="e", padx=(0, 10), pady=10)
        contact_entry = ttk.Entry(sub_frame, width=64)
        contact_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(contact_entry, "Ex.: (11) 99999-9999")

        ttk.Label(sub_frame, text="Endereço*:").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=10)
        address_entry = ttk.Entry(sub_frame, width=64)
        address_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(address_entry, "Ex.: Rua das Flores, 123")

        ttk.Label(sub_frame, text="Nome*:").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=10)
        name_entry = ttk.Entry(sub_frame, width=64)
        name_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(name_entry, "Ex.: João Silva")

        ttk.Label(sub_frame, text="Informações Extras:").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=10)
        extra_info_entry = ttk.Entry(sub_frame, width=64)
        extra_info_entry.grid(row=3, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(extra_info_entry, "Ex.: Aluno especial")

        ttk.Label(sub_frame, text="Valor do Contrato (R$)*:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=10)
        contract_value_entry = ttk.Entry(sub_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        contract_value_entry.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(contract_value_entry, "Ex.: 500.00")

        ttk.Label(sub_frame, text="Dia de Vencimento*:").grid(row=5, column=0, sticky="e", padx=(0, 10), pady=10)
        due_day_entry = ttk.Entry(sub_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_number_max), "%P", 2))
        due_day_entry.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(due_day_entry, "Ex.: 15")

        ttk.Label(sub_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=(0, 10), pady=10)
        rg_entry = ttk.Entry(sub_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_and_format_rg), "%P", "%s", "%W"))
        rg_entry.grid(row=6, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(rg_entry, "Ex.: 12.345.678-9")

        ttk.Label(sub_frame, text="CPF*:").grid(row=7, column=0, sticky="e", padx=(0, 10), pady=10)
        cpf_entry = ttk.Entry(sub_frame, width=64, validate="key", validatecommand=(self.parent.register(self.validate_and_format_cpf), "%P", "%s", "%W"))
        cpf_entry.grid(row=7, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(cpf_entry, "Ex.: 123.456.789-00")

        button_frame = tk.Frame(sub_frame, bg=self.bg_main)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ListRoundedButton(button_frame, text="Salvar", command=lambda: self.save_student(
            contact_entry, address_entry, name_entry, extra_info_entry, contract_value_entry, due_day_entry, rg_entry, cpf_entry
        ), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ListRoundedButton(button_frame, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(sub_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"), foreground=self.fg_text).grid(row=9, column=0, columnspan=2, pady=15)

    def validate_number(self, P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

    def validate_number_max(self, P, max_len):
        if not P:
            return True
        if not all(c.isdigit() for c in P):
            return False
        return len(P) <= int(max_len)

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

    def validate_and_format_rg(self, P, S, W):
        if not P:
            return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 9:
            return False
        formatted = self.format_rg(digits)
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
        return True

    def validate_and_format_cpf(self, P, S, W):
        if not P:
            return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 11:
            return False
        formatted = self.format_cpf(digits)
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
        return True

    def format_rg(self, digits):
        if len(digits) <= 2:
            return digits
        elif len(digits) <= 5:
            return f"{digits[:2]}.{digits[2:]}"
        elif len(digits) <= 8:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:]}"
        else:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8:]}"

    def format_cpf(self, digits):
        if len(digits) <= 3:
            return digits
        elif len(digits) <= 6:
            return f"{digits[:3]}.{digits[3:]}"
        elif len(digits) <= 9:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        else:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def save_student(self, contact_entry, address_entry, name_entry, extra_info_entry, contract_value_entry, due_day_entry, rg_entry, cpf_entry):
        contact = get_entry_value(contact_entry)
        address = get_entry_value(address_entry)
        name = get_entry_value(name_entry)
        extra_info = get_entry_value(extra_info_entry)
        contract_value = float(get_entry_value(contract_value_entry).replace(',', '.') or 0.0)
        due_day = int(get_entry_value(due_day_entry) or 0)
        rg = get_entry_value(rg_entry)
        cpf = get_entry_value(cpf_entry)

        clean_rg = ''.join(c for c in rg if c.isalnum())
        clean_cpf = ''.join(c for c in cpf if c.isdigit())

        if not all([contact, address, name, contract_value, due_day, clean_rg, clean_cpf]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        if due_day < 1 or due_day > 31:
            messagebox.showerror("Erro", "O dia de vencimento deve estar entre 1 e 31.")
            return

        if len(clean_rg) > 12:
            messagebox.showerror("Erro", "O RG deve ter no máximo 12 caracteres (ignorando . e -).")
            return

        if len(clean_cpf) != 11:
            messagebox.showerror("Erro", "O CPF deve ter exatamente 11 dígitos (ignorando . e -).")
            return

        try:
            student = Student(None, contact, address, name, extra_info, contract_value, due_day, rg, cpf)
            student_id = self.student_repo.add(student)
            if student_id:
                messagebox.showinfo("Sucesso", f"Aluno cadastrado com ID {student_id}!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar o aluno.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        interface = InterfaceAluno(self.parent, self.db_path)
        interface.show()
