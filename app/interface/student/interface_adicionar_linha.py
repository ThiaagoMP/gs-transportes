import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.repositories.route_student_repository import RouteStudentRepository


class InterfaceAdicionarNaLinha:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.route_student_repo = RouteStudentRepository(self.db_path)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Adicionar Aluno à Linha", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#1976d2").pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "#ffffff")])

        ttk.Label(main_frame, text="Selecionar Linha (em desenvolvimento):").pack(pady=15)
        ttk.Button(main_frame, text="Salvar", style="TButton", command=self.save).pack(pady=10)
        ttk.Button(main_frame, text="Voltar", style="TButton", command=self.back).pack(pady=10)

    def save(self):
        messagebox.showinfo("Info", "Funcionalidade em desenvolvimento. Aluno ID {} será associado a uma linha.".format(self.student_id))
        self.back()

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        interface = InterfaceAluno(self.parent, self.db_path)
        interface.show()