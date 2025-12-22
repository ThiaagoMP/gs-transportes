import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.route_repository import RouteRepository
from app.components.list_rounded_button import ListRoundedButton


class InterfaceAdicionarNaLinha:
    def __init__(self, parent, db_path, student_id):
        self.parent = parent
        self.db_path = db_path
        self.student_id = student_id
        self.route_student_repo = RouteStudentRepository(self.db_path)
        self.route_repo = RouteRepository(self.db_path)

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
            text="Vincular aluno à linha",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=30, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=5, fill="both", expand=True)

        content_frame = tk.Frame(main_frame, bg=self.bg_field, pady=25, padx=25)
        content_frame.pack(pady=20)

        tk.Label(
            content_frame,
            text="Selecione a linha:",
            font=("Segoe UI", 13),
            bg=self.bg_field,
            fg=self.fg_text
        ).pack(pady=(0, 10), anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=self.bg_main,
                        background=self.bg_button,
                        foreground=self.fg_text,
                        darkcolor=self.bg_main,
                        lightcolor=self.bg_button,
                        arrowcolor=self.accent)

        self.route_combo = ttk.Combobox(content_frame, font=("Segoe UI", 12), state="readonly", width=40)
        self.route_combo.pack(fill="x", pady=10)

        routes = self.route_repo.get_all()
        self.route_map = {r.name: r.route_id for r in routes}
        self.route_combo['values'] = list(self.route_map.keys())

        btn_frame = tk.Frame(main_frame, bg=self.bg_main)
        btn_frame.pack(pady=20)

        buttons_container = tk.Frame(btn_frame, bg=self.bg_main)
        buttons_container.pack(expand=True)

        ListRoundedButton(
            buttons_container,
            text="Salvar vínculo",
            command=self.save,
            width=200,
            height=45,
            bg=self.accent,
            fg=self.fg_text,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=10)

        ListRoundedButton(
            buttons_container,
            text="Voltar",
            command=self.back,
            width=150,
            height=45,
            bg=self.bg_button,
            fg=self.fg_text,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=10)

    def save(self):
        selected_name = self.route_combo.get()
        if not selected_name:
            messagebox.showwarning("Aviso", "Selecione uma linha primeiro.")
            return

        route_id = self.route_map[selected_name]
        try:
            if self.route_student_repo.add_student_to_route(route_id, self.student_id):
                messagebox.showinfo("Sucesso", "Aluno vinculado com sucesso!")
                self.back()
            else:
                messagebox.showerror("Erro", "O aluno já está vinculado a esta linha.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        InterfaceAluno(self.parent, self.db_path).show()