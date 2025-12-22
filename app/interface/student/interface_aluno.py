import tkinter as tk
from tkinter import ttk, messagebox

from app.components.list_rounded_button import ListRoundedButton
from app.interface.student.interface_pagamentos_aluno import InterfacePagamentosAluno
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.repositories.student_repository import StudentRepository
from app.interface.student.interface_cadastrar_aluno import InterfaceCadastrarAluno
from app.interface.student.interface_editar_aluno import InterfaceEditarAluno
from app.interface.student.interface_adicionar_linha import InterfaceAdicionarNaLinha


class InterfaceAluno:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.student_repo = StudentRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Alunos",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(15, 5), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=20, pady=5, fill="both", expand=True)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 11),
                        rowheight=28,
                        background=self.bg_field,
                        fieldbackground=self.bg_field,
                        foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        background=self.accent,
                        foreground="#ffffff",
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        tree_container = tk.Frame(list_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Nome", "Contato", "Endereço", "Valor Contrato", "Dia Vencimento", "RG", "CPF"),
            show="headings",
            height=12
        )

        col_defs = [
            ("Nome", 180),
            ("Contato", 130),
            ("Endereço", 230),
            ("Valor Contrato", 120),
            ("Dia Vencimento", 110),
            ("RG", 110),
            ("CPF", 120),
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(fill="x", pady=15)

        buttons_container = tk.Frame(button_frame, bg=self.bg_main)
        buttons_container.pack(expand=True)

        actions = [
            ("Cadastrar aluno", self.cadastrar_aluno),
            ("Editar aluno", self.editar_aluno),
            ("Pagamentos", self.payments),
            ("Excluir aluno", self.confirm_delete),
        ]

        for text, cmd in actions:
            bg_color = "#b3261e" if "Excluir" in text else self.bg_button
            ListRoundedButton(
                buttons_container,
                text=text,
                command=cmd,
                width=190,
                height=45,
                bg=bg_color,
                fg=self.fg_text,
                font=("Segoe UI", 12, "bold")
            ).pack(side="left", padx=8, pady=5)

        self.load_students()

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        students = self.student_repo.get_all()
        students.sort(key=lambda s: getattr(s, 'name', '').lower() if getattr(s, 'name', '') else '')
        for student in students:
            sid = getattr(student, 'student_id', None)
            if sid is None: continue
            self.tree.insert("", "end", iid=str(sid), values=(
                getattr(student, 'name', ''),
                getattr(student, 'contact', ''),
                getattr(student, 'address', ''),
                f"R$ {float(getattr(student, 'contract_value', 0.0)):.2f}",
                getattr(student, 'due_day', ''),
                getattr(student, 'rg', ''),
                getattr(student, 'cpf', '')
            ))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                InterfaceEditarAluno(self.parent, self.db_path, int(item)).show()
            except ValueError:
                messagebox.showerror("Erro", "Identificador inválido.")

    def cadastrar_aluno(self):
        InterfaceCadastrarAluno(self.parent, self.db_path).show()

    def confirm_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        sid = int(selected[0])
        name = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirmação", f"Deseja excluir '{name}'?"):
            if self.student_repo.delete_by_student_id(sid):
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso.")
                self.load_students()
            else:
                messagebox.showerror("Erro", "Falha ao realizar a exclusão.")

    def editar_aluno(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        InterfaceEditarAluno(self.parent, self.db_path, int(selected[0])).show()

    def payments(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno.")
            return
        student = self.student_repo.get_by_id(int(selected[0]))
        if student:
            InterfacePagamentosAluno(self.parent, self.db_path, student).show()