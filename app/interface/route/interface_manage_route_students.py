import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from app.repositories.student_repository import StudentRepository
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.route_repository import RouteRepository
from app.components.list_rounded_button import ListRoundedButton

class InterfaceGerenciarAlunosLinha:
    def __init__(self, parent, db_path, route_id):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id

        self.student_repo = StudentRepository(self.db_path)
        self.route_student_repo = RouteStudentRepository(self.db_path)
        self.route_repo = RouteRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_card = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 20, "bold")
        self.font_header = ("Segoe UI", 10, "bold")
        self.font_item = ("Segoe UI", 10)

    def show(self):
        route = self.route_repo.get_by_id(self.route_id)
        if not route:
            messagebox.showerror("Erro", "Linha nao encontrada.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_top = tk.Frame(self.parent, bg=self.bg_main)
        header_top.pack(pady=(15, 10), padx=25, fill="x")

        tk.Label(
            header_top,
            text=f"VINCULAR ALUNOS: {route.name.upper()}",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=25, pady=0, fill="both", expand=True)

        header_cols = tk.Frame(main_frame, bg=self.bg_main, height=35)
        header_cols.pack(fill="x", padx=5)
        header_cols.pack_propagate(False)

        cols = [("Nome", 0.25), ("Contato", 0.15), ("Endereço", 0.35), ("CPF", 0.15), ("Vincular", 0.1)]

        curr_x = 0.0
        for text, weight in cols:
            tk.Label(
                header_cols,
                text=text.upper(),
                font=self.font_header,
                bg=self.bg_main,
                fg=self.accent,
                anchor="w"
            ).place(relx=curr_x, rely=0, relwidth=weight, relheight=1)
            curr_x += weight

        container = tk.Frame(main_frame, bg=self.bg_main)
        container.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_main)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1180)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_students()

        btn_container = tk.Frame(self.parent, bg=self.bg_main)
        btn_container.pack(pady=15)

        ListRoundedButton(
            btn_container,
            text="Salvar alterações",
            command=self.save_changes,
            bg=self.accent,
            fg=self.fg_text,
            width=180,
            height=40
        ).pack(side="left", padx=10)

        ListRoundedButton(
            btn_container,
            text="Voltar",
            command=self.back,
            bg=self.bg_button,
            fg=self.fg_text,
            width=120,
            height=40
        ).pack(side="left", padx=10)

    def load_students(self):
        students = self.student_repo.get_all()
        route_students = self.route_student_repo.get_students_by_route_id(self.route_id)
        active_ids = {rs.student_id for rs in route_students if rs.end_date is None}

        self.student_vars = {}

        if not students:
            tk.Label(self.scrollable_frame, text="Nenhum aluno cadastrado.", font=self.font_item, bg=self.bg_main, fg=self.fg_text).pack(pady=20)
            return

        for student in students:
            if not student.student_id: continue

            var = tk.BooleanVar(value=student.student_id in active_ids)
            self.student_vars[student.student_id] = var

            f = tk.Frame(self.scrollable_frame, bg=self.bg_card, height=38)
            f.pack(fill="x", pady=1, padx=2)
            f.pack_propagate(False)

            weights = [0.25, 0.15, 0.35, 0.15, 0.1]
            data = [student.name, student.contact, student.address, student.cpf]

            curr_x = 0.0
            for i, text in enumerate(data):
                tk.Label(
                    f,
                    text=str(text or "---").upper(),
                    font=self.font_item,
                    bg=self.bg_card,
                    fg=self.fg_text,
                    anchor="w"
                ).place(relx=curr_x, rely=0, relwidth=weights[i], relheight=1)
                curr_x += weights[i]

            chk_frame = tk.Frame(f, bg=self.bg_card)
            chk_frame.place(relx=curr_x, rely=0, relwidth=weights[4], relheight=1)

            tk.Checkbutton(
                chk_frame,
                variable=var,
                bg=self.bg_card,
                activebackground=self.bg_card,
                selectcolor=self.bg_main,
                bd=0,
                highlightthickness=0
            ).pack(expand=True)

    def save_changes(self):
        all_rs = self.route_student_repo.get_students_by_route_id(self.route_id)
        active_ids = {rs.student_id for rs in all_rs if rs.end_date is None}
        selected_ids = {s_id for s_id, var in self.student_vars.items() if var.get()}
        today = datetime.now().strftime('%Y-%m-%d')

        for s_id in active_ids - selected_ids:
            self.route_student_repo.update_end_date(self.route_id, s_id, today)

        for s_id in selected_ids - active_ids:
            existing = next((rs for rs in all_rs if rs.student_id == s_id), None)
            if existing:
                self.route_student_repo.update_end_date(self.route_id, s_id, None)
            else:
                from app.models.route_student import RouteStudent
                self.route_student_repo.add(RouteStudent(self.route_id, s_id, today, None))

        messagebox.showinfo("Sucesso", "Lista de alunos atualizada!")
        self.back()

    def back(self):
        from app.interface.route.interface_route_students import InterfaceRouteStudents
        route = self.route_repo.get_by_id(self.route_id)
        name = route.name if route else "Rota"
        InterfaceRouteStudents(self.parent, self.db_path, self.route_id, name).show()