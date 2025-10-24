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
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text=f"Pagamentos de {self.student.name}",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=25, fill="x")

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
            columns=("Data", "Valor", "Info Extra"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Data", 150, False),
            ("Valor", 150, False),
            ("Info Extra", 250, True),
        ]

        for col, width, stretch in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=stretch)

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Adicionar Pagamento", self.adicionar_pagamento),
            ("Excluir Pagamento", self.excluir_pagamento),
            ("Baixar Comprovante", self.baixar_comprovante),
            ("Voltar", self.back)
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith(
                "Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=200,
                height=45,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold"),
                shadow=True
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_payments()

    def load_payments(self):
        self.tree.delete(*self.tree.get_children())
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
                f"{payment.amount:.2f}",
                payment.extra_info or ""
            ))

    def adicionar_pagamento(self):
        try:
            interface = InterfaceCadastrarPagamento(self.parent, self.db_path, self.student.student_id)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar pagamento: {str(e)}")

    def excluir_pagamento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um pagamento para excluir.")
            return

        payment_id = int(selected_item[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este pagamento?"):
            try:
                if self.payment_repo.delete(payment_id):
                    messagebox.showinfo("Sucesso", "Pagamento excluído com sucesso!")
                    self.load_payments()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir o pagamento.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir pagamento: {str(e)}")

    def baixar_comprovante(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um pagamento para baixar o comprovante.")
            return

        payment_id = int(selected_item[0])
        payment = self.payment_repo.get_by_id(payment_id)

        if not payment or not payment.receipt:
            messagebox.showinfo("Info", "Não há comprovante para este pagamento.")
            return

        receipt_bytes = payment.receipt

        if receipt_bytes[:4] == b"%PDF":
            ext = ".pdf"
        elif receipt_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"
        else:
            ext = ".bin"

        nome_sanitizado = "".join(c for c in self.student.name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        data_str = payment.payment_date.strftime("%d%m%Y") if hasattr(payment.payment_date, "strftime") else str(
            payment.payment_date)
        initial_filename = f"comprovante_{nome_sanitizado}_{data_str}{ext}"

        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("PDF", "*.pdf"), ("JPEG", "*.jpg"), ("PNG", "*.png")],
            initialfile=initial_filename,
            title="Salvar Comprovante"
        )

        if not file_path:
            return

        try:
            with open(file_path, "wb") as f:
                f.write(receipt_bytes)
            messagebox.showinfo("Sucesso", f"Comprovante salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {str(e)}")

    def back(self):
        from app.interface.student.interface_aluno import InterfaceAluno
        interface = InterfaceAluno(self.parent, self.db_path)
        interface.show()
