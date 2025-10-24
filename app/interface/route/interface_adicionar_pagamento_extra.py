import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime

from app.repositories.route_extra_payment_repository import RouteExtraPaymentRepository
from app.models.route_extra_payment import RouteExtraPayment
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.vehicle_repository import VehicleRepository


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


class InterfaceAddExtraPayment:
    def __init__(self, parent, db_path, route_id):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id
        self.route_extra_payment_repo = RouteExtraPaymentRepository(self.db_path)
        self.receipt_path = None

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

    def show(self):
        if not self.route_id:
            messagebox.showerror("Erro", "Selecione uma rota antes de adicionar um pagamento extra.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Adicionar Pagamento Extra", font=self.font_title, bg=self.bg_main,
                 fg=self.accent).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(pady=10, padx=(350, 0), anchor="nw")
        main_frame.columnconfigure(0, weight=1)

        sub_frame = tk.Frame(main_frame, bg=self.bg_main)
        sub_frame.grid(row=0, column=0)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, padding=6, fieldbackground=self.bg_button,
                        foreground=self.fg_text)
        style.configure("TButton", font=self.font_button, padding=10,
                        background=self.bg_button, foreground=self.fg_text)
        style.map("TButton",
                  background=[("active", self.accent)],
                  foreground=[("active", self.fg_text)])
        style.configure("Placeholder.TEntry", foreground="#7a7a7a")

        fields_frame = tk.Frame(sub_frame, bg=self.bg_main)
        fields_frame.pack(fill="x", padx=10, pady=5)

        fields_frame.columnconfigure(0, weight=0, minsize=150)
        fields_frame.columnconfigure(1, weight=1)
        fields_frame.columnconfigure(2, weight=0)

        ttk.Label(fields_frame, text="Data do Pagamento*:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        date_frame = tk.Frame(fields_frame, bg=self.bg_main)
        date_frame.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        date_entry = tk.Entry(date_frame, width=25, font=self.font_entry, bg=self.bg_button, fg=self.fg_text,
                              insertbackground=self.fg_text, state="readonly")
        date_entry.pack(side="left", padx=5)
        date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(date_frame, text="Selecionar Data", command=lambda: self.open_calendar(date_entry),
                          bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(fields_frame, text="Valor*:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        amount_entry = ttk.Entry(fields_frame, width=27, validate="key",
                                 validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        amount_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        add_placeholder(amount_entry, "Ex.: 500.00")

        ttk.Label(fields_frame, text="Descrição:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        description_entry = ttk.Entry(fields_frame, width=27)
        description_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        add_placeholder(description_entry, "Ex.: Pagamento extra por viagem")

        ttk.Label(fields_frame, text="Comprovante:").grid(row=3, column=0, sticky="e", padx=10, pady=10)
        receipt_frame = tk.Frame(fields_frame, bg=self.bg_main)
        receipt_frame.grid(row=3, column=1, sticky="w", padx=10, pady=10)
        self.receipt_entry = ttk.Entry(receipt_frame, width=27)
        self.receipt_entry.pack(side="left", padx=0)
        add_placeholder(self.receipt_entry, "Selecione um arquivo")
        ListRoundedButton(receipt_frame, text="Selecionar Arquivo", command=self.select_file, bg=self.bg_button,
                          fg=self.fg_text, font=self.font_button).pack(side="left", padx=8)

        button_frame = tk.Frame(sub_frame, bg=self.bg_main)
        button_frame.pack(pady=20)

        ListRoundedButton(button_frame, text="Salvar",
                          command=lambda: self.save(date_entry, amount_entry, description_entry), bg=self.bg_button,
                          fg=self.fg_text, font=self.font_button).pack(side="left", padx=10)
        ListRoundedButton(button_frame, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text,
                          font=self.font_button).pack(side="left", padx=10)

        ttk.Label(sub_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"),
                  foreground=self.fg_text).pack(pady=15)

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

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.config(state="normal")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
            date_entry.config(state="readonly")

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf"), ("JPEG", "*.jpg"), ("PNG", "*.png")])
        if file_path:
            self.receipt_path = file_path
            self.receipt_entry.delete(0, tk.END)
            self.receipt_entry.insert(0, file_path)

    def save(self, date_entry, amount_entry, description_entry):
        payment_date_str = date_entry.get().strip()
        amount = float(get_entry_value(amount_entry).replace(',', '.') or 0.0)
        description = get_entry_value(description_entry)
        receipt = None
        if self.receipt_path:
            try:
                with open(self.receipt_path, 'rb') as f:
                    receipt = f.read()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o comprovante: {str(e)}")
                return

        if not all([payment_date_str, amount, self.route_id]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            payment_date = datetime.strptime(payment_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            payment = RouteExtraPayment(None, self.route_id, payment_date, amount, receipt, description)
            result = self.route_extra_payment_repo.add(payment)
            if result:
                messagebox.showinfo("Sucesso", "Pagamento extra adicionado com sucesso!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar o pagamento extra.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Formato de data inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.repositories.route_repository import RouteRepository
        repo = RouteRepository(self.db_path)
        from app.interface.route.interface_extra_payments import InterfaceRouteExtraPayments
        interface = InterfaceRouteExtraPayments(self.parent, self.db_path, self.route_id,
                                                repo.get_by_id(self.route_id).name)
        interface.show()
