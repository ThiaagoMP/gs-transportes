import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.models.driver_bonus import DriverBonus
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


class InterfaceAddDriverBonus:
    def __init__(self, parent, db_path, driver_id, driver_name):
        self.parent = parent
        self.db_path = db_path
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.bonus_repo = DriverBonusRepository(self.db_path)
        self.receipt_path = None

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 13)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10, "bold")

    def show(self):
        if not self.driver_id:
            messagebox.showerror("Erro", "Selecione um motorista antes de adicionar uma bonificação.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text=f"Adicionar bônus: {self.driver_name.title()}",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(40, 20))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(expand=True)

        form_frame = tk.Frame(container, bg=self.bg_main)
        form_frame.pack(padx=50)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, padding=8, fieldbackground=self.bg_field,
                        foreground=self.fg_text, borderwidth=0)
        style.configure("Placeholder.TEntry", foreground="#888888")

        ttk.Label(form_frame, text="Data do pagamento*:").grid(row=0, column=0, sticky="e", padx=15, pady=10)
        date_f = tk.Frame(form_frame, bg=self.bg_main)
        date_f.grid(row=0, column=1, sticky="w", pady=10)

        self.date_entry = tk.Entry(
            date_f, width=32, font=self.font_entry,
            bg=self.bg_field, fg=self.fg_text,
            disabledbackground=self.bg_field,
            disabledforeground=self.fg_text,
            relief="flat", borderwidth=0
        )
        self.date_entry.pack(side="left", ipady=7)
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.date_entry.config(state="disabled")

        ListRoundedButton(
            date_f, text="Data",
            command=lambda: self.open_calendar(self.date_entry),
            width=80, height=32, bg=self.accent, fg=self.fg_text
        ).pack(side="left", padx=10)

        ttk.Label(form_frame, text="Valor (R$)*:").grid(row=1, column=0, sticky="e", padx=15, pady=10)
        self.amount_entry = ttk.Entry(form_frame, width=55)
        self.amount_entry.configure(validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        self.amount_entry.grid(row=1, column=1, sticky="w", pady=10)
        add_placeholder(self.amount_entry, "Ex.: 500.00")

        ttk.Label(form_frame, text="Descrição:").grid(row=2, column=0, sticky="e", padx=15, pady=10)
        self.desc_entry = ttk.Entry(form_frame, width=55)
        self.desc_entry.grid(row=2, column=1, sticky="w", pady=10)
        add_placeholder(self.desc_entry, "Ex.: Bonificação por meta atingida")

        ttk.Label(form_frame, text="Comprovante:").grid(row=3, column=0, sticky="e", padx=15, pady=10)
        receipt_f = tk.Frame(form_frame, bg=self.bg_main)
        receipt_f.grid(row=3, column=1, sticky="w", pady=10)

        self.receipt_display = ttk.Entry(receipt_f, width=32)
        self.receipt_display.pack(side="left", ipady=7)
        add_placeholder(self.receipt_display, "Nenhum arquivo selecionado")

        ListRoundedButton(
            receipt_f, text="Selecionar",
            command=self.select_file,
            width=100, height=32, bg=self.bg_button, fg=self.fg_text
        ).pack(side="left", padx=10)

        actions_f = tk.Frame(form_frame, bg=self.bg_main)
        actions_f.grid(row=4, column=0, columnspan=2, pady=40)

        ListRoundedButton(
            actions_f, text="Confirmar bônus",
            command=self.save,
            width=200, height=45, bg=self.accent, fg=self.fg_text
        ).pack(side="left", padx=15)

        ListRoundedButton(
            actions_f, text="Cancelar",
            command=self.back,
            width=150, height=45, bg=self.bg_button, fg=self.fg_text
        ).pack(side="left", padx=15)

    def validate_decimal(self, P):
        if not P: return True
        try:
            temp = P.replace(',', '.')
            if temp == "." or temp == "": return True
            float(temp)
            return temp.count('.') <= 1
        except:
            return False

    def open_calendar(self, entry):
        def callback(date_obj):
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, date_obj.strftime('%d/%m/%Y'))
            entry.config(state="disabled")

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self):
        f_types = [("Documentos", "*.pdf;*.jpg;*.png")]
        path = filedialog.askopenfilename(filetypes=f_types)
        if path:
            self.receipt_path = path
            self.receipt_display.config(validate="none")
            self.receipt_display.delete(0, tk.END)
            self.receipt_display.insert(0, path.split("/")[-1])
            self.receipt_display.configure(style="TEntry")

    def save(self):
        self.date_entry.config(state="normal")
        date_str = self.date_entry.get()
        self.date_entry.config(state="disabled")

        amount_val = get_entry_value(self.amount_entry).replace(',', '.')
        description = get_entry_value(self.desc_entry)

        if not amount_val or not date_str:
            messagebox.showerror("Erro", "Preencha o valor e a data do bônus.")
            return

        try:
            amount = float(amount_val)
            bonus_date = datetime.strptime(date_str, '%d/%m/%Y')

            receipt_data = None
            if self.receipt_path:
                with open(self.receipt_path, 'rb') as f:
                    receipt_data = f.read()

            bonus = DriverBonus(
                bonus_id=None,
                driver_id=self.driver_id,
                description=description.capitalize() if description else "Sem descrição",
                receipt=receipt_data,
                bonus_date=bonus_date.strftime('%Y-%m-%d'),
                amount=amount
            )

            if self.bonus_repo.add(bonus):
                messagebox.showinfo("Sucesso", f"Bônus de R${amount:.2f} registrado.")
                self.back()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar no banco de dados.")

        except ValueError:
            messagebox.showerror("Erro", "Verifique o formato do valor financeiro.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def back(self):
        from app.interface.driver.interface_list_bonus import InterfaceBonificacoesMotorista
        InterfaceBonificacoesMotorista(self.parent, self.db_path, self.driver_id, self.driver_name).show()