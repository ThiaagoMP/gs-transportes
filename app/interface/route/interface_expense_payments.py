import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.components.list_rounded_button import ListRoundedButton
from app.interface.route.interface_adicionar_despesa_extra import InterfaceAddExpensePayment
from app.repositories.route_expense_payment_repository import RouteExpensePaymentRepository

class InterfaceRouteExpensePayments:
    def __init__(self, parent, db_path, route_id, route_name):
        self.parent = parent
        self.db_path = db_path
        self.route_id = route_id
        self.route_name = route_name
        self.expense_payment_repo = RouteExpensePaymentRepository(self.db_path)

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
        header_frame.pack(pady=(15, 5), padx=20, fill="x")

        tk.Label(
            header_frame,
            text=f"PAGAMENTOS DE DESPESAS: {self.route_name.upper()}",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=20, pady=5, fill="both", expand=True)

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=28,
                        background=self.bg_field,
                        fieldbackground=self.bg_field,
                        foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background=self.accent,
                        foreground="#ffffff",
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Data", "Valor", "Descricao"),
            show="headings",
            height=12
        )

        self.tree.heading("Data", text="DATA")
        self.tree.heading("Valor", text="VALOR (R$)")
        self.tree.heading("Descricao", text="DESCRIÇÃO")

        self.tree.column("Data", width=120, anchor="center", stretch=False)
        self.tree.column("Valor", width=120, anchor="e", stretch=False)
        self.tree.column("Descricao", width=300, anchor="w", stretch=True)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=15, fill="x")

        inner_button_frame = tk.Frame(button_frame, bg=self.bg_main)
        inner_button_frame.pack(anchor="center")

        btns = [
            ("Adicionar", self.adicionar_pagamento_despesa, self.bg_button),
            ("Recibo", self.baixar_comprovante, self.bg_button),
            ("Excluir", self.excluir_pagamento_despesa, "#b3261e"),
            ("Voltar", self.back, self.bg_button)
        ]

        for text, cmd, color in btns:
            ListRoundedButton(
                inner_button_frame,
                text=text,
                command=cmd,
                width=140,
                height=38,
                bg=color,
                fg=self.fg_text,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=8)

        self.load_expense_payments()

    def load_expense_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_payments = self.expense_payment_repo.get_all()
        route_payments = [p for p in all_payments if p.route_id == self.route_id]
        route_payments.sort(key=lambda p: str(p.payment_date), reverse=True)

        for payment in route_payments:
            p_date = payment.payment_date
            if isinstance(p_date, str):
                try:
                    date_display = datetime.strptime(p_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    date_display = p_date
            elif hasattr(p_date, "strftime"):
                date_display = p_date.strftime('%d/%m/%Y')
            else:
                date_display = str(p_date)

            self.tree.insert("", "end", iid=str(payment.expense_payment_id), values=(
                date_display,
                f"{float(payment.amount):.2f}",
                payment.description or ""
            ))

    def adicionar_pagamento_despesa(self):
        InterfaceAddExpensePayment(self.parent, self.db_path, self.route_id).show()

    def excluir_pagamento_despesa(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item.")
            return

        if messagebox.askyesno("Confirmação", "Excluir este pagamento?"):
            if self.expense_payment_repo.delete(int(selected[0])):
                self.load_expense_payments()

    def baixar_comprovante(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento.")
            return

        payment = self.expense_payment_repo.get_by_id(int(selected[0]))
        if not payment or not payment.receipt:
            messagebox.showinfo("Info", "Sem comprovante salvo.")
            return

        receipt_bytes = payment.receipt
        ext = ".bin"
        if receipt_bytes.startswith(b"%PDF"): ext = ".pdf"
        elif receipt_bytes.startswith(b"\xff\xd8"): ext = ".jpg"
        elif receipt_bytes.startswith(b"\x89PNG"): ext = ".png"

        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Arquivos", f"*{ext}")],
            initialfile=f"recibo_{payment.expense_payment_id}{ext}"
        )

        if file_path:
            with open(file_path, "wb") as f:
                f.write(receipt_bytes)
            messagebox.showinfo("Sucesso", "Salvo.")

    def back(self):
        from app.interface.route.interface_linha import InterfaceLinha
        InterfaceLinha(self.parent, self.db_path).show()