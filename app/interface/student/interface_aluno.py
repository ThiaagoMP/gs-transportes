import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from app.components.list_rounded_button import ListRoundedButton
from app.interface.student.interface_pagamentos_aluno import InterfacePagamentosAluno
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.repositories.student_repository import StudentRepository
from app.interface.student.interface_cadastrar_aluno import InterfaceCadastrarAluno
from app.interface.student.interface_editar_aluno import InterfaceEditarAluno
from app.interface.student.interface_adicionar_linha import InterfaceAdicionarNaLinha
from app.interface.student.interface_cadastrar_pagamento import InterfaceCadastrarPagamento


class InterfaceAluno:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.student_repo = StudentRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Alunos",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20,10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 12),
                        background=self.bg_main,
                        fieldbackground=self.bg_main,
                        foreground=self.fg_text)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 13, "bold"),
                        background=self.accent,
                        foreground="#ffffff")
        style.map("Treeview",
                  background=[("selected", "#333333")],
                  foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(
            list_frame,
            columns=("Nome", "Contato", "Endereço", "Valor Contrato", "Dia Vencimento", "RG", "CPF"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Nome", 150),
            ("Contato", 120),
            ("Endereço", 200),
            ("Valor Contrato", 120),
            ("Dia Vencimento", 100),
            ("RG", 100),
            ("CPF", 120),
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Cadastrar Aluno", self.cadastrar_aluno),
            ("Editar Aluno", self.editar_aluno),
            ("Adicionar na Linha", self.adicionar_na_linha),
            ("Pagamentos", self.payments),
            ("Excluir Aluno", self.confirm_delete),
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=210,
                height=50,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold"),
                shadow=True
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_students()

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        students = self.student_repo.get_all()
        for student in students:
            student_id = getattr(student, 'student_id', None)
            if student_id is None or not str(student_id).strip():
                continue

            self.tree.insert("", "end", iid=str(student_id), values=(
                getattr(student, 'name', ''),
                getattr(student, 'contact', ''),
                getattr(student, 'address', ''),
                f"{float(getattr(student, 'contract_value', 0.0)):.2f}" if getattr(student, 'contract_value', None) is not None else '0.00',
                getattr(student, 'due_day', ''),
                getattr(student, 'rg', ''),
                getattr(student, 'cpf', '')
            ))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                student_id = int(item)
                interface = InterfaceEditarAluno(self.parent, self.db_path, student_id)
                interface.show()
            except ValueError:
                messagebox.showerror("Erro", "ID do aluno inválido.")

    def cadastrar_aluno(self):
        try:
            interface = InterfaceCadastrarAluno(self.parent, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o cadastro: {str(e)}")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")
            return

        student_id = selected_item[0]
        if not student_id.strip():
            messagebox.showerror("Erro", "ID do aluno inválido.")
            return

        try:
            student_id = int(student_id)
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido (não é um número).")
            return

        student_name = self.tree.item(student_id, "values")[0]
        if messagebox.askyesno("Confirmação",
                               f"Deseja realmente excluir o aluno '{student_name}'?"):
            if self.student_repo.delete(student_id):
                messagebox.showinfo("Sucesso", f"Aluno '{student_name}' excluído com sucesso!")
                self.load_students()
            else:
                messagebox.showerror("Erro", "Falha ao excluir aluno.")

    def editar_aluno(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
            return
        try:
            student_id = int(selected_item[0])
            interface = InterfaceEditarAluno(self.parent, self.db_path, student_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido.")

    def adicionar_na_linha(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        try:
            student_id = int(selected_item[0])
            interface = InterfaceAdicionarNaLinha(self.parent, self.db_path, student_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido.")

    def payments(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        student_id = int(selected_item[0])
        student_repo = StudentRepository(self.db_path)
        student = student_repo.get_by_id(student_id)

        payment_repo = StudentPaymentRepository(self.db_path)
        all_payments = payment_repo.get_all()
        students_payments = [p for p in all_payments if p.student_id == student.student_id]

        interface = InterfacePagamentosAluno(self.parent, self.db_path, student)
        interface.show()

