import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
import tkinter.filedialog as filedialog
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.models.student_payment import StudentPayment

class InterfaceCadastrarPagamento:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.payment_repo = StudentPaymentRepository(self.db_path)
        self.selected_file = None

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Cadastrar Pagamento", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#1976d2").pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")
        style.configure("TCheckbutton", font=("Segoe UI", 12), background="#ffffff", foreground="#000000")
        style.map("TCheckbutton",
                  background=[("active", "#e0e0e0")],
                  foreground=[("active", "#000000")])

        # Campos
        ttk.Label(main_frame, text="Valor (R$)*:").grid(row=0, column=0, sticky="e", padx=15, pady=10)
        amount_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        amount_entry.grid(row=0, column=1, columnspan=2, padx=15, pady=10, sticky="w")

        ttk.Label(main_frame, text="Pago*:").grid(row=1, column=0, sticky="e", padx=15, pady=10)
        paid_var = tk.BooleanVar(value=False)
        paid_check = ttk.Checkbutton(main_frame, variable=paid_var, style="TCheckbutton", text="Sim")
        paid_check.grid(row=1, column=1, columnspan=2, padx=15, pady=10, sticky="w")

        ttk.Label(main_frame, text="Data*:").grid(row=2, column=0, sticky="e", padx=15, pady=10)
        date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        date_entry.grid(row=2, column=1, columnspan=2, padx=15, pady=10, sticky="w")
        date_entry.set_date(datetime.now().strftime('%d/%m/%Y'))  # 10/09/2025

        ttk.Label(main_frame, text="Comprovante*:").grid(row=3, column=0, sticky="e", padx=15, pady=10)
        self.receipt_entry = ttk.Entry(main_frame, width=45)
        self.receipt_entry.grid(row=3, column=1, padx=15, pady=10, sticky="w")
        ttk.Button(main_frame, text="Selecionar Arquivo", style="TButton", command=self.select_file).grid(row=3, column=2, padx=5, pady=10, sticky="w")

        ttk.Label(main_frame, text="Informações Extras:").grid(row=4, column=0, sticky="e", padx=15, pady=10)
        extra_info_entry = ttk.Entry(main_frame, width=45)
        extra_info_entry.grid(row=4, column=1, columnspan=2, padx=15, pady=10, sticky="w")

        # Botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="Salvar", style="TButton", command=lambda: self.save_payment(
            amount_entry, paid_var, date_entry, extra_info_entry
        )).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Voltar", style="TButton", command=self.back).pack(side="left", padx=10)

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

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            self.selected_file = file_path
            self.receipt_entry.delete(0, tk.END)
            self.receipt_entry.insert(0, file_path)

    def save_payment(self, amount_entry, paid_var, date_entry, extra_info_entry):
        amount = float(amount_entry.get().replace(',', '.') or 0.0)
        paid = 1 if paid_var.get() else 0
        date = date_entry.get().strip()
        extra_info = extra_info_entry.get().strip()

        if not all([amount, date]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        receipt = None
        if self.selected_file:
            try:
                with open(self.selected_file, 'rb') as f:
                    receipt = f.read()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler o arquivo: {str(e)}")
                return

        try:
            date_obj = datetime.strptime(date, '%d/%m/%Y')
            payment_date = date_obj.strftime('%Y-%m-%d')

            payment = StudentPayment(None, self.student_id, receipt, payment_date, amount, paid, extra_info)
            payment_id = self.payment_repo.add(payment)
            if payment_id:
                messagebox.showinfo("Sucesso", f"Pagamento cadastrado com ID {payment_id}!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar o pagamento.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        interface = InterfaceAluno(self.parent, self.db_path)
        interface.show()