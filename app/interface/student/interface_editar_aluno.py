import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.repositories.student_repository import StudentRepository
from app.models.student import Student

class InterfaceEditarAluno:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.student_repo = StudentRepository(self.db_path)
        self.student = self.student_repo.get_by_id(student_id) if student_id else None

    def show(self):
        if not self.student:
            messagebox.showerror("Erro", "Aluno não encontrado.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Editar Aluno", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#1976d2").pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "#ffffff")])

        # Campos
        ttk.Label(main_frame, text="Contato*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        contact_entry = ttk.Entry(main_frame, width=45)
        contact_entry.insert(0, self.student.contact)
        contact_entry.grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Endereço*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        address_entry = ttk.Entry(main_frame, width=45)
        address_entry.insert(0, self.student.address)
        address_entry.grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Nome*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        name_entry = ttk.Entry(main_frame, width=45)
        name_entry.insert(0, self.student.name)
        name_entry.grid(row=2, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Informações Extras:").grid(row=3, column=0, sticky="e", padx=15, pady=15)
        extra_info_entry = ttk.Entry(main_frame, width=45)
        extra_info_entry.insert(0, self.student.extra_info)
        extra_info_entry.grid(row=3, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Valor do Contrato (R$)*:").grid(row=4, column=0, sticky="e", padx=15, pady=15)
        contract_value_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        contract_value_entry.insert(0, str(self.student.contract_value))
        contract_value_entry.grid(row=4, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Dia de Vencimento*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        due_day_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_number), "%P"))
        due_day_entry.insert(0, str(self.student.due_day))
        due_day_entry.grid(row=5, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        rg_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_rg), "%P", "%s"))
        rg_entry.insert(0, self.student.rg)
        rg_entry.grid(row=6, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="CPF*:").grid(row=7, column=0, sticky="e", padx=15, pady=15)
        cpf_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_cpf), "%P", "%s"))
        cpf_entry.insert(0, self.student.cpf)
        cpf_entry.grid(row=7, column=1, padx=15, pady=15)

        # Botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Salvar", style="TButton", command=lambda: self.save_student(
            contact_entry, address_entry, name_entry, extra_info_entry, contract_value_entry, due_day_entry, rg_entry, cpf_entry
        )).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Voltar", style="TButton", command=self.back).pack(side="left", padx=5)

    def validate_number(self, P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

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

    def validate_rg(self, P, S):
        if not P:
            return True
        clean_p = ''.join(c for c in P if c.isalnum())
        return len(clean_p) <= 12 and all(c.isalnum() for c in clean_p)

    def validate_cpf(self, P, S):
        if not P:
            return True
        clean_p = ''.join(c for c in P if c.isdigit())
        return len(clean_p) <= 11 and all(c.isdigit() for c in clean_p)

    def save_student(self, contact_entry, address_entry, name_entry, extra_info_entry, contract_value_entry, due_day_entry, rg_entry, cpf_entry):
        contact = contact_entry.get().strip()
        address = address_entry.get().strip()
        name = name_entry.get().strip()
        extra_info = extra_info_entry.get().strip()
        contract_value = float(contract_value_entry.get().replace(',', '.') or 0.0)
        due_day = int(due_day_entry.get() or 0)
        rg = rg_entry.get().strip()
        cpf = cpf_entry.get().strip()

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
            student = Student(self.student_id, contact, address, name, extra_info, contract_value, due_day, rg, cpf)
            if self.student_repo.update(student):
                messagebox.showinfo("Sucesso", f"Aluno com ID {self.student_id} atualizado com sucesso!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao atualizar o aluno.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        interface = InterfaceAluno(self.parent, self.db_path)
        interface.show()