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
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_button = ("Segoe UI", 12)
        self.font_item = ("Segoe UI", 11)

        self.show()

    def show(self):
        route = self.route_repo.get_by_id(self.route_id)
        if not route:
            messagebox.showerror("Erro", "Linha não encontrada.")
            return

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text=f"Gerenciar Alunos da Linha: {route.name}",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(pady=10, padx=0, fill="both", expand=True)

        header_frame = tk.Frame(main_frame, bg=self.bg_main)
        header_frame.pack(fill="x", padx=0, pady=(10, 0))

        headers = ["Nome", "Contato", "Endereço", "CPF", "Na Rota"]
        for i, header in enumerate(headers):
            lbl = tk.Label(
                header_frame,
                text=header,
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_main,
                fg=self.accent,
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=8, pady=5, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1 if i < 4 else 0, uniform="col")

        list_frame = tk.LabelFrame(
            main_frame,
            text="Alunos",
            font=self.font_label,
            bg=self.bg_main,
            fg=self.accent
        )
        list_frame.pack(fill="both", expand=True, padx=0, pady=10)

        canvas = tk.Canvas(list_frame, bg=self.bg_main, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_scrollable_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfigure(window_id, width=canvas_width)

        def _on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", _on_scrollable_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        students = self.student_repo.get_all()
        route_students = self.route_student_repo.get_students_by_route_id(self.route_id)
        active_student_ids = {rs.student_id for rs in route_students if rs.end_date is None}

        self.student_vars = {}

        for i, student in enumerate(students):
            if not student.student_id:
                continue

            var = tk.BooleanVar(value=student.student_id in active_student_ids)
            self.student_vars[student.student_id] = var

            student_frame = tk.Frame(scrollable_frame, bg=self.bg_button)
            student_frame.pack(fill="x", padx=0, pady=5)

            tk.Label(student_frame, text=student.name or "N/A",
                     font=self.font_item, bg=self.bg_button, fg=self.fg_text,
                     anchor="w").grid(row=0, column=0, padx=(12,8), pady=5, sticky="w")
            tk.Label(student_frame, text=student.contact or "N/A",
                     font=self.font_item, bg=self.bg_button, fg=self.fg_text,
                     anchor="w").grid(row=0, column=1, padx=8, pady=5, sticky="w")
            tk.Label(student_frame, text=student.address or "N/A",
                     font=self.font_item, bg=self.bg_button, fg=self.fg_text,
                     anchor="w").grid(row=0, column=2, padx=8, pady=5, sticky="w")
            tk.Label(student_frame, text=student.cpf or "N/A",
                     font=self.font_item, bg=self.bg_button, fg=self.fg_text,
                     anchor="w").grid(row=0, column=3, padx=8, pady=5, sticky="w")

            chk = tk.Checkbutton(
                student_frame,
                variable=var,
                bg=self.bg_button,
                fg=self.fg_text,
                activebackground=self.bg_button,
                activeforeground=self.fg_text,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
                selectcolor=self.bg_button
            )
            chk.grid(row=0, column=4, padx=(6, 12), pady=5, sticky="w")

            for col in range(4):
                student_frame.grid_columnconfigure(col, weight=1, uniform="col")
            student_frame.grid_columnconfigure(4, weight=0)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=20)

        ListRoundedButton(
            button_frame,
            text="Salvar",
            command=self.save_changes,
            bg=self.bg_button,
            fg=self.fg_text,
            font=self.font_button
        ).pack(side="left", padx=10)

        ListRoundedButton(
            button_frame,
            text="Voltar",
            command=self.back,
            bg=self.bg_button,
            fg=self.fg_text,
            font=self.font_button
        ).pack(side="left", padx=10)


    def save_changes(self):
        all_route_students = self.route_student_repo.get_students_by_route_id(self.route_id)
        current_active_student_ids = {rs.student_id for rs in all_route_students if rs.end_date is None}
        selected_student_ids = {student_id for student_id, var in self.student_vars.items() if var.get()}

        for student_id in current_active_student_ids - selected_student_ids:
            self.route_student_repo.update_end_date(
                self.route_id, student_id, datetime.now().strftime('%Y-%m-%d')
            )

        for student_id in selected_student_ids - current_active_student_ids:
            existing_rs = next((rs for rs in all_route_students if rs.student_id == student_id), None)
            if existing_rs:
                self.route_student_repo.update_end_date(self.route_id, student_id, None)
            else:
                from app.models.route_student import RouteStudent
                route_student = RouteStudent(self.route_id, student_id,
                                             datetime.now().strftime('%Y-%m-%d'), None)
                success = self.route_student_repo.add(route_student)
                if not success:
                    self.route_student_repo.update_end_date(self.route_id, student_id, None)

        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
        self.back()

    def back(self):
        from app.interface.route.interface_route_students import InterfaceRouteStudents
        repo = RouteRepository(self.db_path)
        interface = InterfaceRouteStudents(self.parent, self.db_path,self.route_id, repo.get_by_id(self.route_id).name)
        interface.show()
