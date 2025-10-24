import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from app.repositories.driver_repository import DriverRepository
from app.models.driver import Driver
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

class InterfaceRegisterDriver:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)

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

        tk.Label(self.parent, text="Cadastrar Motorista", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=25)

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

        ttk.Label(sub_frame, text="Nome*:").grid(row=0, column=0, sticky="e", padx=(0, 10), pady=10)
        name_entry = ttk.Entry(sub_frame, width=50)
        name_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(name_entry, "Ex.: João Silva")

        ttk.Label(sub_frame, text="Salário (R$)*:").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=10)
        salary_entry = ttk.Entry(sub_frame, width=50, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        salary_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(salary_entry, "Ex.: 2500.00")

        ttk.Label(sub_frame, text="Contato*:").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=10)
        contact_entry = ttk.Entry(sub_frame, width=50)
        contact_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(contact_entry, "Ex.: joao@email.com")

        ttk.Label(sub_frame, text="Data de Início*:").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=10)
        date_frame = tk.Frame(sub_frame, bg=self.bg_main)
        date_frame.grid(row=3, column=1, sticky="w", padx=(0, 10), pady=10)
        start_date_entry = tk.Entry(date_frame, width=45, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, insertbackground=self.fg_text, state="readonly")
        start_date_entry.pack(side="left", padx=0)
        start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(date_frame, text="Selecionar Data", command=lambda: self.open_calendar(start_date_entry), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(sub_frame, text="Data de Término:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=10)
        end_date_frame = tk.Frame(sub_frame, bg=self.bg_main)
        end_date_frame.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=10)
        end_date_entry = tk.Entry(end_date_frame, width=45, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, insertbackground=self.fg_text, state="readonly")
        end_date_entry.pack(side="left", padx=0)
        ListRoundedButton(end_date_frame, text="Selecionar Data", command=lambda: self.open_calendar(end_date_entry), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)
        ListRoundedButton(end_date_frame, text="Limpar", command=lambda: end_date_entry.delete(0, tk.END), bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(sub_frame, text="CPF*:").grid(row=5, column=0, sticky="e", padx=(0, 10), pady=10)
        cpf_entry = ttk.Entry(sub_frame, width=50, validate="key", validatecommand=(self.parent.register(self.validate_and_format_cpf), "%P", "%s", "%W"))
        cpf_entry.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(cpf_entry, "Ex.: 123.456.789-00")

        ttk.Label(sub_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=(0, 10), pady=10)
        rg_entry = ttk.Entry(sub_frame, width=50, validate="key", validatecommand=(self.parent.register(self.validate_and_format_rg), "%P", "%s", "%W"))
        rg_entry.grid(row=6, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(rg_entry, "Ex.: 12.345.678-9")

        ttk.Label(sub_frame, text="CNH*:").grid(row=7, column=0, sticky="e", padx=(0, 10), pady=10)
        cnh_entry = ttk.Entry(sub_frame, width=50)
        cnh_entry.grid(row=7, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(cnh_entry, "Ex.: 12345678901")

        ttk.Label(sub_frame, text="Informações Extras:").grid(row=8, column=0, sticky="e", padx=(0, 10), pady=10)
        extra_info_entry = tk.Text(sub_frame, width=45, height=3, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, insertbackground=self.fg_text)
        extra_info_entry.grid(row=8, column=1, sticky="w", padx=(0, 10), pady=10)
        extra_info_entry.insert("1.0", "Opcional")
        extra_info_entry.bind("<FocusIn>", lambda e: extra_info_entry.delete("1.0", tk.END) if extra_info_entry.get("1.0", tk.END).strip() == "Opcional" else None)

        button_frame = tk.Frame(sub_frame, bg=self.bg_main)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        inner_button_frame = tk.Frame(button_frame, bg=self.bg_main)
        inner_button_frame.pack(anchor="center")
        ListRoundedButton(inner_button_frame, text="Cadastrar", command=lambda:
            self.save_driver(name_entry, salary_entry, contact_entry, start_date_entry,
                             end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry),
                                    bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=10)
        ListRoundedButton(inner_button_frame, text="Voltar", command=self.back, bg=self.bg_button,
                          fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(sub_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"), foreground=self.fg_text).grid(row=10, column=0, columnspan=2, pady=15)

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

    def format_cpf(self, digits):
        if len(digits) <= 3:
            return digits
        elif len(digits) <= 6:
            return f"{digits[:3]}.{digits[3:]}"
        elif len(digits) <= 9:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        else:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def format_rg(self, digits):
        if len(digits) <= 2:
            return digits
        elif len(digits) <= 5:
            return f"{digits[:2]}.{digits[2:]}"
        elif len(digits) <= 8:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:]}"
        else:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8:]}"

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.config(state="normal")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
            date_entry.config(state="readonly")
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def save_driver(self, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name = get_entry_value(name_entry)
        salary = float(get_entry_value(salary_entry).replace(',', '.') or 0.0)
        contact = get_entry_value(contact_entry)
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        cpf = get_entry_value(cpf_entry).replace(".", "").replace("-", "")
        rg = get_entry_value(rg_entry).replace(".", "").replace("-", "")
        cnh = get_entry_value(cnh_entry)
        extra_info = extra_info_entry.get("1.0", tk.END).strip() or None

        if not all([name, salary, contact, start_date, cpf, rg, cnh]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        if len(cpf) != 11:
            messagebox.showerror("Erro", "CPF deve ter exatamente 11 dígitos.")
            return

        if len(rg) > 9:
            messagebox.showerror("Erro", "RG deve ter no máximo 9 dígitos.")
            return

        try:
            start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
            end_date_obj = datetime.strptime(end_date, '%d/%m/%Y') if end_date else None
            if end_date_obj and end_date_obj < start_date_obj:
                messagebox.showerror("Erro", "Data de Término não pode ser anterior à Data de Início.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido.")
            return

        try:
            driver = Driver(None, name, salary, contact, start_date_obj.strftime('%Y-%m-%d'), end_date_obj.strftime('%Y-%m-%d') if end_date_obj else None, cpf, rg, cnh, extra_info)
            self.driver_repo.create(driver)
            messagebox.showinfo("Sucesso", f"Motorista '{name}' cadastrado com sucesso!")
            self.clear_form(name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar motorista: {str(e)}")

    def clear_form(self, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name_entry.delete(0, tk.END)
        salary_entry.delete(0, tk.END)
        contact_entry.delete(0, tk.END)
        start_date_entry.delete(0, tk.END)
        start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        end_date_entry.delete(0, tk.END)
        cpf_entry.delete(0, tk.END)
        rg_entry.delete(0, tk.END)
        cnh_entry.delete(0, tk.END)
        extra_info_entry.delete("1.0", tk.END)
        extra_info_entry.insert("1.0", "Opcional")

    def back(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        interface = InterfaceListDrivers(self.parent, self.db_path)
        interface.show()
