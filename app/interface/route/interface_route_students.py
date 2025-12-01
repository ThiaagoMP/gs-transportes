import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from app.components.list_rounded_button import ListRoundedButton
from app.interface.route.interface_manage_route_students import InterfaceGerenciarAlunosLinha
from app.interface.student.interface_pagamentos_aluno import InterfacePagamentosAluno
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.repositories.student_repository import StudentRepository
from app.interface.student.interface_cadastrar_aluno import InterfaceCadastrarAluno
from app.interface.student.interface_editar_aluno import InterfaceEditarAluno
from app.interface.student.interface_adicionar_linha import InterfaceAdicionarNaLinha


class InterfaceRouteStudents:
    def __init__(self, parent, db_path, route_id, route_name):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id
        self.route_name = route_name
        self.student_repo = StudentRepository(self.db_path)
        self.route_student_repo = RouteStudentRepository(self.db_path)

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
            text=f"Alunos da Rota {self.route_name}",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Container Treeview + Scrollbar
        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

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
            tree_container,
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

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Editar Aluno", self.editar_aluno),
            ("Gerenciar Alunos", self.adicionar_na_linha),
            ("Pagamentos", self.payments),
            ("Voltar", self.back),
        ]

        for text, cmd in actions:
            bg_color = self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=250,
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
        route_students = self.route_student_repo.get_students_by_route_id(int(self.route_id))
        for route_student in route_students:
            student_id = getattr(route_student, 'student_id', None)
            if student_id is None or not str(student_id).strip():
                continue

            student = self.student_repo.get_by_id(student_id)

            self.tree.insert("", "end", iid=str(student_id), values=(
                getattr(student, 'name', ''),
                getattr(student, 'contact', ''),
                getattr(student, 'address', ''),
                f"{float(getattr(student, 'contract_value', 0.0)):.2f}" if getattr(student, 'contract_value',
                                                                                   None) is not None else '0.00',
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
        try:
            interface = InterfaceGerenciarAlunosLinha(self.parent, self.db_path, self.route_id)
            interface.show()
        except Exception:
            messagebox.showerror("Erro", "Erro ao gerenciar alunos na linha.")

    def payments(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        student_id = int(selected_item[0])
        student = self.student_repo.get_by_id(student_id)
        interface = InterfacePagamentosAluno(self.parent, self.db_path, student)
        interface.show()

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        interface = InterfaceLinha(self.parent, self.db_path)
        interface.show()
