import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.interface.student.interface_cadastrar_pagamento import InterfaceCadastrarPagamento


class InterfacePagamentosAluno:
    def __init__(self, parent, db_path, student):
        self.parent = parent
        self.db_path = db_path
        self.student = student
        self.payment_repo = StudentPaymentRepository(self.db_path)

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
            text=f"Pagamentos: {self.student.name.title()}",
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
            columns=("Data", "Valor", "Info Extra"),
            show="headings",
            height=12
        )

        col_defs = [
            ("Data", 120),
            ("Valor", 120),
            ("Info Extra", 350),
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, anchor="center")

        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(fill="x", pady=15)

        btns_inner = tk.Frame(button_frame, bg=self.bg_main)
        btns_inner.pack(expand=True)

        actions = [
            ("Novo pagamento", self.adicionar_pagamento),
            ("Baixar comprovante", self.baixar_comprovante),
            ("Voltar", self.back),
            ("Excluir", self.excluir_pagamento)
        ]

        for text, cmd in actions:
            bg_color = "#b3261e" if "Excluir" in text else self.bg_button
            ListRoundedButton(
                btns_inner,
                text=text,
                command=cmd,
                width=180,
                height=42,
                bg=bg_color,
                fg=self.fg_text,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=8, pady=5)

        self.load_payments()

    def load_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_payments = self.payment_repo.get_all()
        student_payments = [p for p in all_payments if p.student_id == self.student.student_id]
        student_payments.sort(key=lambda p: p.payment_date, reverse=True)

        for payment in student_payments:
            if isinstance(payment.payment_date, str):
                try:
                    date_obj = datetime.strptime(payment.payment_date, '%Y-%m-%d')
                    date_display = date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    date_display = payment.payment_date
            elif isinstance(payment.payment_date, datetime):
                date_display = payment.payment_date.strftime('%d/%m/%Y')
            else:
                date_display = str(payment.payment_date)

            self.tree.insert("", "end", iid=str(payment.student_payment_id), values=(
                date_display,
                f"R$ {payment.amount:.2f}",
                payment.extra_info or ""
            ))

    def adicionar_pagamento(self):
        InterfaceCadastrarPagamento(self.parent, self.db_path, self.student.student_id).show()

    def excluir_pagamento(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento.")
            return

        pid = int(selected[0])
        if messagebox.askyesno("Confirmação", "Deseja excluir este pagamento?"):
            if self.payment_repo.delete(pid):
                messagebox.showinfo("Sucesso", "Pagamento excluído com sucesso.")
                self.load_payments()
            else:
                messagebox.showerror("Erro", "Falha ao realizar a exclusão.")

    def baixar_comprovante(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento.")
            return

        payment = self.payment_repo.get_by_id(int(selected[0]))
        if not payment or not payment.receipt:
            messagebox.showinfo("Informação", "Sem comprovante disponível para este registro.")
            return

        receipt_bytes = payment.receipt
        ext = ".bin"
        if receipt_bytes[:4] == b"%PDF":
            ext = ".pdf"
        elif receipt_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"

        name_clean = "".join(c for c in self.student.name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Documentos", "*.pdf *.jpg *.png")],
            initialfile=f"comprovante_{name_clean}{ext}",
            title="Salvar comprovante"
        )

        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(receipt_bytes)
                messagebox.showinfo("Sucesso", "Comprovante salvo com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        InterfaceAluno(self.parent, self.db_path).show()