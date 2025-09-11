import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from app.repositories.student_repository import StudentRepository
from app.models.student import Student
from app.interface.student.interface_cadastrar_aluno import InterfaceCadastrarAluno
from app.interface.student.interface_editar_aluno import InterfaceEditarAluno
from app.interface.student.interface_adicionar_linha import InterfaceAdicionarNaLinha
from app.interface.student.interface_cadastrar_pagamento import InterfaceCadastrarPagamento

class InterfaceAluno:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.student_repo = StudentRepository(self.db_path)

    def show(self):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Alunos",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        # Frame principal
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Frame para a lista de alunos
        list_frame = tk.Frame(main_frame, bg="#ffffff")
        list_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")  # Tema compatível com Windows 7
        style.configure("Treeview", font=("Segoe UI", 12), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"), background="#2196f3", foreground="#ffffff")
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("Action.TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("Delete.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#f44336", foreground="#ffffff")
        style.map("Delete.TButton",
                  background=[("active", "#e57373")],
                  foreground=[("active", "#ffffff")])

        # Treeview pra listar alunos
        self.tree = ttk.Treeview(list_frame, columns=("Nome", "Contato", "Endereço", "Valor Contrato", "Dia Vencimento", "RG", "CPF"),
                                 show="headings", height=15)
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Contato", text="Contato")
        self.tree.heading("Endereço", text="Endereço")
        self.tree.heading("Valor Contrato", text="Valor Contrato (R$)")
        self.tree.heading("Dia Vencimento", text="Dia Vencimento")
        self.tree.heading("RG", text="RG")
        self.tree.heading("CPF", text="CPF")
        self.tree.column("Nome", width=150)
        self.tree.column("Contato", width=120)
        self.tree.column("Endereço", width=200)
        self.tree.column("Valor Contrato", width=100)
        self.tree.column("Dia Vencimento", width=100)
        self.tree.column("RG", width=100)
        self.tree.column("CPF", width=120)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Vincular duplo clique
        self.tree.bind("<Double-1>", self.on_double_click)

        # Frame para os botões
        button_frame = tk.Frame(list_frame, bg="#ffffff")
        button_frame.pack(side="bottom", pady=10)

        ttk.Button(
            button_frame,
            text="Cadastrar",
            style="Action.TButton",
            command=self.cadastrar_aluno
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Excluir",
            style="Delete.TButton",
            command=self.confirm_delete
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Editar",
            style="Action.TButton",
            command=self.editar_aluno
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Adicionar na Linha",
            style="Action.TButton",
            command=self.adicionar_na_linha
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Adicionar Pagamento",
            style="Action.TButton",
            command=self.adicionar_pagamento
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Visualizar",
            style="Action.TButton",
            command=self.visualizar
        ).pack(side="left", padx=5)

        # Carregar alunos
        self.load_students()

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        students = self.student_repo.get_all()
        for student in students:
            student_id = getattr(student, 'student_id', None)
            if student_id is None:
                print(f"AVISO: StudentID ausente para aluno {student.name or 'sem nome'}")
                continue
            elif not str(student_id).strip():
                print(f"AVISO: StudentID vazio ou inválido para aluno {student.name or 'sem nome'}: {student_id}")
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
            print(f"DEBUG: Inserido aluno com ID {student_id}, Nome: {student.name}")

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
            messagebox.showerror("Erro", f"Erro ao abrir a interface de cadastro: {str(e)}")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")
            return

        student_id = selected_item[0]
        if not student_id or not student_id.strip():
            messagebox.showerror("Erro", "ID do aluno inválido.")
            return
        try:
            student_id = int(student_id)
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido (não é um número).")
            return

        # Buscar o nome do aluno a partir dos valores da linha selecionada
        student_name = self.tree.item(student_id, "values")[0]  # Nome está na coluna 0
        if messagebox.askyesno("Confirmação",
                               f"Tem certeza que deseja excluir o aluno '{student_name}' (ID: {student_id})?"):
            if self.student_repo.delete(student_id):
                messagebox.showinfo("Sucesso", f"Aluno '{student_name}' excluído com sucesso!")
                self.load_students()
            else:
                messagebox.showerror("Erro", "Falha ao excluir o aluno.")

    def editar_aluno(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
            return
        student_id = selected_item[0]
        try:
            student_id = int(student_id)
            interface = InterfaceEditarAluno(self.parent, self.db_path, student_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido.")

    def adicionar_na_linha(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para adicionar a uma linha.")
            return
        student_id = selected_item[0]
        try:
            student_id = int(student_id)
            interface = InterfaceAdicionarNaLinha(self.parent, self.db_path, student_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido.")

    def adicionar_pagamento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para adicionar um pagamento.")
            return
        student_id = selected_item[0]
        try:
            student_id = int(student_id)
            interface = InterfaceCadastrarPagamento(self.parent, self.db_path, student_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno inválido.")

    def visualizar(self):
        messagebox.showinfo("Info", "Funcionalidade de Visualizar em desenvolvimento.")