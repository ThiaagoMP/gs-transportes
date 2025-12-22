import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tkinter.filedialog as filedialog
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.models.student_payment import StudentPayment
from app.components.custom_calendar import CustomCalendar
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

class InterfaceCadastrarPagamento:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.payment_repo = StudentPaymentRepository(self.db_path)
        self.selected_file = None
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

        tk.Label(self.parent, text="Cadastrar pagamento", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=(15, 10))

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True)

        container = tk.Frame(main_frame, bg=self.bg_main)
        container.pack(anchor="center", pady=10)

        tk.Label(container, text="Valor (R$)*:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.amount_entry = tk.Entry(container, width=45, font=self.font_entry, bg=self.bg_field, fg=self.fg_text, insertbackground="white", borderwidth=0)
        self.amount_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        add_placeholder(self.amount_entry, "Ex.: 500.00")

        tk.Label(container, text="Data*:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        date_frame = tk.Frame(container, bg=self.bg_main)
        date_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.date_entry = tk.Entry(date_frame, width=30, font=self.font_entry, bg=self.bg_field, fg=self.fg_text, insertbackground="white", borderwidth=0)
        self.date_entry.pack(side="left", padx=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(date_frame, text="Calendário", command=lambda: self.open_calendar(self.date_entry), bg=self.bg_button, fg=self.fg_text, width=110, height=32).pack(side="left")

        tk.Label(container, text="Comprovante*:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        receipt_frame = tk.Frame(container, bg=self.bg_main)
        receipt_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.receipt_entry = tk.Entry(receipt_frame, width=30, font=self.font_entry, bg=self.bg_field, fg=self.fg_text, insertbackground="white", borderwidth=0)
        self.receipt_entry.pack(side="left", padx=(0, 10))
        add_placeholder(self.receipt_entry, "Selecione um arquivo")
        ListRoundedButton(receipt_frame, text="Arquivo", command=self.select_file, bg=self.bg_button, fg=self.fg_text, width=110, height=32).pack(side="left")

        tk.Label(container, text="Informações extras:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.extra_info_entry = tk.Entry(container, width=45, font=self.font_entry, bg=self.bg_field, fg=self.fg_text, insertbackground="white", borderwidth=0)
        self.extra_info_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        add_placeholder(self.extra_info_entry, "Ex.: Pagamento adiantado")

        footer_btn_frame = tk.Frame(container, bg=self.bg_main)
        footer_btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        btns_inner = tk.Frame(footer_btn_frame, bg=self.bg_main)
        btns_inner.pack(expand=True)

        ListRoundedButton(btns_inner, text="Salvar pagamento", command=lambda: self.save_payment(self.amount_entry, self.date_entry, self.extra_info_entry), bg=self.accent, fg=self.fg_text, width=180, height=42).pack(side="left", padx=10)
        ListRoundedButton(btns_inner, text="Voltar", command=self.back, bg=self.bg_button, fg=self.fg_text, width=120, height=42).pack(side="left", padx=10)

        tk.Label(container, text="* Campos obrigatórios", font=("Segoe UI", 9, "italic"), bg=self.bg_main, fg="#aaaaaa").grid(row=5, column=0, columnspan=2)

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Imagem/PDF", "*.pdf *.jpg *.jpeg *.png")])
        if file_path:
            self.selected_file = file_path
            self.receipt_entry.delete(0, tk.END)
            self.receipt_entry.insert(0, file_path)
            self.receipt_entry._ph_active = False
            self.receipt_entry.configure(fg="#ffffff")

    def save_payment(self, amount_entry, date_entry, extra_info_entry):
        amount_str = get_entry_value(amount_entry).replace(',', '.')
        date = date_entry.get().strip()
        extra_info = get_entry_value(extra_info_entry)
        if not amount_str or not date:
            messagebox.showerror("Erro", "Preencha o valor e a data corretamente.")
            return
        try:
            amount = float(amount_str)
            receipt = None
            if self.selected_file:
                with open(self.selected_file, 'rb') as f:
                    receipt = f.read()
            date_obj = datetime.strptime(date, '%d/%m/%Y')
            payment_date = date_obj.strftime('%Y-%m-%d')
            payment = StudentPayment(None, self.student_id, receipt, payment_date, amount, 1, extra_info)
            if self.payment_repo.add(payment):
                messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso.")
                self.back()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o pagamento.")
        except ValueError: messagebox.showerror("Erro", "Os dados inseridos são inválidos.")
        except Exception as e: messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def back(self):
        from app.repositories.student_repository import StudentRepository
        repo = StudentRepository(self.db_path)
        from app.interface.student.interface_pagamentos_aluno import InterfacePagamentosAluno
        InterfacePagamentosAluno(self.parent, self.db_path, repo.get_by_id(self.student_id)).show()