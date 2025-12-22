import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.repositories.driver_repository import DriverRepository
from app.models.driver import Driver
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton


def add_placeholder(entry, placeholder):
    entry._ph_text = placeholder
    entry._ph_active = False

    def _show_placeholder():
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.config(fg="#888888")
        entry._ph_active = True

    def _hide_placeholder():
        entry.delete(0, tk.END)
        entry.config(fg="#ffffff")
        entry._ph_active = False

    def on_focus_in(_):
        if entry._ph_active:
            _hide_placeholder()

    def on_focus_out(_):
        if not entry.get():
            _show_placeholder()

    entry.bind("<FocusIn>", on_focus_in, add="+")
    entry.bind("<FocusOut>", on_focus_out, add="+")
    _show_placeholder()


def get_entry_value(entry) -> str:
    text = entry.get().strip()
    if getattr(entry, "_ph_active", False) or text == getattr(entry, "_ph_text", None):
        return ""
    return text


class InterfaceRegisterDriver:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 18, "bold")
        self.font_label = ("Segoe UI", 9, "bold")
        self.font_entry = ("Segoe UI", 10)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Cadastrar motorista",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(15, 10))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(expand=True, fill="both")

        main_frame = tk.Frame(container, bg=self.bg_main)
        main_frame.pack(padx=20, pady=5)

        fields = [
            ("Nome completo*:", "Ex.: Joao Silva"),
            ("Salário (R$)*:", "0.00"),
            ("Contato*:", "(00) 00000-0000"),
            ("CPF*:", "000.000.000-00"),
            ("RG*:", "00.000.000-0"),
            ("CNH*:", "00000000000")
        ]

        self.entries = {}

        for i, (label_text, ph) in enumerate(fields):
            tk.Label(main_frame, text=label_text, font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=i, column=0, sticky="e", padx=10, pady=4)

            val_cmd = None
            if "Salário" in label_text:
                val_cmd = (self.parent.register(self.validate_decimal), "%P")
            elif "CPF" in label_text:
                val_cmd = (self.parent.register(self.validate_and_format_cpf), "%P", "%W")
            elif "RG" in label_text:
                val_cmd = (self.parent.register(self.validate_and_format_rg), "%P", "%W")

            entry = tk.Entry(
                main_frame, width=40, font=self.font_entry,
                bg=self.bg_field, fg=self.fg_text,
                insertbackground=self.fg_text, relief="flat", borderwidth=0
            )
            if val_cmd:
                entry.configure(validate="key", validatecommand=val_cmd)

            entry.grid(row=i, column=1, sticky="w", pady=4, ipady=5)
            add_placeholder(entry, ph)
            self.entries[label_text] = entry

        tk.Label(main_frame, text="Início*:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=6, column=0, sticky="e", padx=10, pady=4)
        start_date_f = tk.Frame(main_frame, bg=self.bg_main)
        start_date_f.grid(row=6, column=1, sticky="w", pady=4)

        self.start_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        tk.Label(
            start_date_f, textvariable=self.start_date_var, width=22, font=self.font_entry,
            bg=self.bg_field, fg=self.fg_text, anchor="w", padx=10
        ).pack(side="left", ipady=5)

        ListRoundedButton(
            start_date_f, text="Data",
            command=lambda: self.open_calendar(self.start_date_var),
            width=80, height=30, bg=self.accent, fg=self.fg_text
        ).pack(side="left", padx=5)

        tk.Label(main_frame, text="Término:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=7, column=0, sticky="e", padx=10, pady=4)
        end_date_f = tk.Frame(main_frame, bg=self.bg_main)
        end_date_f.grid(row=7, column=1, sticky="w", pady=4)

        self.end_date_var = tk.StringVar(value="")
        tk.Label(
            end_date_f, textvariable=self.end_date_var, width=22, font=self.font_entry,
            bg=self.bg_field, fg=self.fg_text, anchor="w", padx=10
        ).pack(side="left", ipady=5)

        ListRoundedButton(
            end_date_f, text="Data",
            command=lambda: self.open_calendar(self.end_date_var),
            width=80, height=30, bg=self.bg_button, fg=self.fg_text
        ).pack(side="left", padx=5)

        ListRoundedButton(
            end_date_f, text="X",
            command=self.clear_end_date,
            width=40, height=30, bg="#555555", fg=self.fg_text
        ).pack(side="left")

        tk.Label(main_frame, text="Extras:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=8, column=0, sticky="ne", padx=10, pady=8)
        self.extra_info = tk.Text(main_frame, width=38, height=3, font=self.font_entry,
                                  bg=self.bg_field, fg=self.fg_text,
                                  insertbackground=self.fg_text, relief="flat", padx=5, pady=5)
        self.extra_info.grid(row=8, column=1, sticky="w", pady=8)

        actions_f = tk.Frame(container, bg=self.bg_main)
        actions_f.pack(pady=15)

        ListRoundedButton(
            actions_f, text="Salvar cadastro",
            command=self.save_driver,
            width=180, height=40, bg=self.accent, fg=self.fg_text
        ).pack(side="left", padx=10)

        ListRoundedButton(
            actions_f, text="Voltar",
            command=self.back,
            width=120, height=40, bg=self.bg_button, fg=self.fg_text
        ).pack(side="left", padx=10)

    def validate_decimal(self, P):
        if not P: return True
        p_fixed = P.replace(',', '.')
        if p_fixed == "." or p_fixed == "": return True
        return p_fixed.count('.') <= 1 and all(c.isdigit() or c == '.' for c in p_fixed)

    def validate_and_format_cpf(self, P, W):
        if not P: return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 11: return False
        formatted = ""
        if len(digits) <= 3: formatted = digits
        elif len(digits) <= 6: formatted = f"{digits[:3]}.{digits[3:]}"
        elif len(digits) <= 9: formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        else: formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.after(1, lambda: self._update_entry(entry, formatted))
        return True

    def validate_and_format_rg(self, P, W):
        if not P: return True
        digits = ''.join(c for c in P if c.isdigit())
        if len(digits) > 9: return False
        formatted = ""
        if len(digits) <= 2: formatted = digits
        elif len(digits) <= 5: formatted = f"{digits[:2]}.{digits[2:]}"
        elif len(digits) <= 8: formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:]}"
        else: formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8:]}"
        if formatted != P:
            entry = self.parent.nametowidget(W)
            entry.after(1, lambda: self._update_entry(entry, formatted))
        return True

    def _update_entry(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def clear_end_date(self):
        self.end_date_var.set("")

    def open_calendar(self, var):
        def callback(date_obj):
            var.set(date_obj.strftime('%d/%m/%Y'))
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def save_driver(self):
        data = {k: get_entry_value(v) for k, v in self.entries.items()}
        if not all([data["Nome completo*:"], data["Salário (R$)*:"], data["Contato*:"], data["CPF*:"], data["RG*:"], data["CNH*:"]]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatorios.")
            return

        try:
            salary = float(data["Salário (R$)*:"].replace(',', '.'))
            start_str = self.start_date_var.get()
            end_str = self.end_date_var.get()
            start_dt = datetime.strptime(start_str, '%d/%m/%Y')
            end_dt = datetime.strptime(end_str, '%d/%m/%Y') if end_str else None

            if end_dt and end_dt < start_dt:
                messagebox.showerror("Erro", "Data de termino invalida.")
                return

            driver = Driver(
                driver_id=None,
                name=data["Nome completo*:"],
                salary=salary,
                contact=data["Contato*:"],
                start_date=start_dt.strftime('%Y-%m-%d'),
                end_date=end_dt.strftime('%Y-%m-%d') if end_dt else None,
                cpf=''.join(filter(str.isdigit, data["CPF*:"])),
                rg=''.join(filter(str.isdigit, data["RG*:"])),
                cnh=data["CNH*:"],
                extra_info=self.extra_info.get("1.0", tk.END).strip().upper()
            )

            self.driver_repo.create(driver)
            messagebox.showinfo("Sucesso", "Motorista cadastrado.")
            self.back()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        InterfaceListDrivers(self.parent, self.db_path).show()