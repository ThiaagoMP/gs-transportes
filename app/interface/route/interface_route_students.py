import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from app.components.list_rounded_button import ListRoundedButton
from app.interface.route.interface_manage_route_students import InterfaceGerenciarAlunosLinha
from app.interface.student.interface_pagamentos_aluno import InterfacePagamentosAluno
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.student_repository import StudentRepository
from app.interface.student.interface_cadastrar_aluno import InterfaceCadastrarAluno
from app.interface.student.interface_editar_aluno import InterfaceEditarAluno

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
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(pady=(15, 5), padx=25, fill="x")

        tk.Label(
            header_frame,
            text=f"ALUNOS: {self.route_name.upper()}",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=25, pady=5, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 9),
                        rowheight=28,
                        background=self.bg_field,
                        fieldbackground=self.bg_field,
                        foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 9, "bold"),
                        background=self.accent,
                        foreground="#ffffff",
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Nome", "Contato", "Endereco", "Valor", "Venc", "RG", "CPF"),
            show="headings",
            height=12
        )

        headers = [
            ("Nome", 160, "w"),
            ("Contato", 100, "center"),
            ("Endereço", 220, "w"),
            ("Valor", 90, "e"),
            ("Vencimento", 50, "center"),
            ("RG", 90, "center"),
            ("CPF", 110, "center")
        ]

        for col, width, anchor in headers:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=15, fill="x")

        inner_btn_frame = tk.Frame(button_frame, bg=self.bg_main)
        inner_btn_frame.pack(anchor="center")

        actions = [
            ("Editar aluno", self.editar_aluno),
            ("Vincular/Gerenciar", self.adicionar_na_linha),
            ("Pagamentos", self.payments),
            ("Voltar", self.back),
        ]

        for text, cmd in actions:
            ListRoundedButton(
                inner_btn_frame,
                text=text,
                command=cmd,
                width=160,
                height=38,
                bg=self.bg_button,
                fg=self.fg_text,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=8)

        self.load_students()

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        route_students = self.route_student_repo.get_students_by_route_id(int(self.route_id))
        for rs in route_students:
            s_id = getattr(rs, 'student_id', None)
            if s_id is None: continue

            s = self.student_repo.get_by_id(s_id)
            if not s: continue

            self.tree.insert("", "end", iid=str(s_id), values=(
                getattr(s, 'name', '').upper(),
                getattr(s, 'contact', ''),
                getattr(s, 'address', '').upper(),
                f"R$ {float(getattr(s, 'contract_value', 0.0)):.2f}",
                getattr(s, 'due_day', ''),
                getattr(s, 'rg', ''),
                getattr(s, 'cpf', '')
            ))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            InterfaceEditarAluno(self.parent, self.db_path, int(item)).show()

    def editar_aluno(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        InterfaceEditarAluno(self.parent, self.db_path, int(selected[0])).show()

    def adicionar_na_linha(self):
        InterfaceGerenciarAlunosLinha(self.parent, self.db_path, self.route_id).show()

    def payments(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        student = self.student_repo.get_by_id(int(selected[0]))
        InterfacePagamentosAluno(self.parent, self.db_path, student).show()

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        InterfaceLinha(self.parent, self.db_path).show()