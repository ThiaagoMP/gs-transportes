import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.models.route_expense_payment import RouteExpensePayment
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.route_expense_payment_repository import RouteExpensePaymentRepository
from app.repositories.route_repository import RouteRepository


def add_placeholder(entry, placeholder):
    entry._ph_text = placeholder
    entry._ph_active = False

    def _show_placeholder():
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.config(fg="#7a7a7a")
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


class InterfaceAddExpensePayment:
    def __init__(self, parent, db_path, route_id):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id
        self.despesa_extra_repo = RouteExpensePaymentRepository(self.db_path)
        self.receipt_path = None

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 18, "bold")
        self.font_label = ("Segoe UI", 10, "bold")
        self.font_entry = ("Segoe UI", 11)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header = tk.Label(self.parent, text="ADICIONAR DESPESA EXTRA", font=self.font_title, bg=self.bg_main,
                          fg=self.accent)
        header.pack(pady=(15, 10))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(expand=True, fill="both", padx=20)

        fields_frame = tk.Frame(container, bg=self.bg_main)
        fields_frame.pack(pady=5)

        tk.Label(fields_frame, text="DATA DO PAGAMENTO:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(
            row=0, column=0, sticky="e", padx=10, pady=8)

        date_container = tk.Frame(fields_frame, bg=self.bg_main)
        date_container.grid(row=0, column=1, sticky="w", padx=10, pady=8)

        self.date_value = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_display = tk.Label(
            date_container,
            textvariable=self.date_value,
            width=18,
            font=self.font_entry,
            bg=self.bg_field,
            fg=self.fg_text,
            anchor="w",
            padx=10
        )
        self.date_display.pack(side="left", padx=(0, 5), ipady=6)

        ListRoundedButton(date_container, text="Data", command=self.open_calendar,
                          bg=self.bg_button, fg=self.fg_text, width=110, height=34).pack(side="left")

        tk.Label(fields_frame, text="VALOR (R$):", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=1,
                                                                                                             column=0,
                                                                                                             sticky="e",
                                                                                                             padx=10,
                                                                                                             pady=8)
        self.amount_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field, fg=self.fg_text,
                                     insertbackground=self.fg_text, relief="flat", borderwidth=0)
        self.amount_entry.grid(row=1, column=1, sticky="w", padx=10, pady=8, ipady=7)
        add_placeholder(self.amount_entry, "0.00")

        tk.Label(fields_frame, text="DESCRIÇÃO:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=2,
                                                                                                            column=0,
                                                                                                            sticky="e",
                                                                                                            padx=10,
                                                                                                            pady=8)
        self.description_entry = tk.Entry(fields_frame, width=35, font=self.font_entry, bg=self.bg_field,
                                          fg=self.fg_text, insertbackground=self.fg_text, relief="flat", borderwidth=0)
        self.description_entry.grid(row=2, column=1, sticky="w", padx=10, pady=8, ipady=7)
        add_placeholder(self.description_entry, "DESCREVA A DESPESA")

        tk.Label(fields_frame, text="COMPROVANTE:", font=self.font_label, bg=self.bg_main, fg="#8e8e93").grid(row=3,
                                                                                                              column=0,
                                                                                                              sticky="e",
                                                                                                              padx=10,
                                                                                                              pady=8)
        receipt_container = tk.Frame(fields_frame, bg=self.bg_main)
        receipt_container.grid(row=3, column=1, sticky="w", padx=10, pady=8)

        self.receipt_entry = tk.Entry(receipt_container, width=22, font=self.font_entry, bg=self.bg_field,
                                      fg=self.fg_text, insertbackground=self.fg_text, relief="flat", borderwidth=0)
        self.receipt_entry.pack(side="left", padx=(0, 5), ipady=7)
        add_placeholder(self.receipt_entry, "ARQUIVO")

        ListRoundedButton(receipt_container, text="BUSCAR", command=self.select_file, bg=self.bg_button,
                          fg=self.fg_text, width=90, height=34).pack(side="left")

        btn_frame = tk.Frame(container, bg=self.bg_main)
        btn_frame.pack(pady=25)

        ListRoundedButton(btn_frame, text="Salvar despesa", command=self.save_despesa, bg=self.accent, fg=self.fg_text,
                          width=170, height=42).pack(side="left", padx=10)
        ListRoundedButton(btn_frame, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, width=120,
                          height=42).pack(side="left", padx=10)

    def open_calendar(self):
        def callback(selected_date):
            self.date_value.set(selected_date.strftime('%d/%m/%Y'))

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos", "*.pdf;*.jpg;*.png")])
        if path:
            self.receipt_path = path
            self.receipt_entry.config(fg=self.fg_text)
            self.receipt_entry.delete(0, tk.END)
            self.receipt_entry.insert(0, path.split("/")[-1])

    def save_despesa(self):
        d_str = self.date_value.get()
        a_text = get_entry_value(self.amount_entry).replace(',', '.')
        desc = get_entry_value(self.description_entry).upper()

        if not a_text or a_text == "0.00":
            messagebox.showerror("ERRO", "INFORME O VALOR")
            return

        try:
            val = float(a_text)
            blob = None
            if self.receipt_path:
                with open(self.receipt_path, 'rb') as f:
                    blob = f.read()

            p_date = datetime.strptime(d_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            obj = RouteExpensePayment(None, self.route_id, p_date, val, blob, desc)
            if self.despesa_extra_repo.add(obj):
                messagebox.showinfo("SUCESSO", "DESPESA REGISTRADA")
                self.back()
        except Exception as e:
            messagebox.showerror("ERRO", str(e))

    def back(self):
        from app.interface.route.interface_expense_payments import InterfaceRouteExpensePayments
        repo = RouteRepository(self.db_path)
        InterfaceRouteExpensePayments(self.parent, self.db_path, self.route_id,
                                      repo.get_by_id(self.route_id).name).show()