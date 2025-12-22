import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.components.list_rounded_button import ListRoundedButton
from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.interface.driver.interface_add_driver_bonus import InterfaceAddDriverBonus

class InterfaceBonificacoesMotorista:
    def __init__(self, parent, db_path, driver_id, driver_name):
        self.parent = parent
        self.db_path = db_path
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.bonus_repo = DriverBonusRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"
        self.show()

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            header_frame,
            text=f"Bonificações: {self.driver_name.title()}",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=20, pady=5, fill="both", expand=True)

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=30,
                        background="#2c2c2e",
                        fieldbackground="#2c2c2e",
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
            show="headings"
        )

        self.tree.heading("Data", text="Data")
        self.tree.heading("Valor", text="Valor (R$)")
        self.tree.heading("Descricao", text="Descrição")

        self.tree.column("Data", width=120, anchor="center")
        self.tree.column("Valor", width=120, anchor="center")
        self.tree.column("Descricao", width=400, anchor="w")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)

        button_frame = tk.Frame(self.parent, bg=self.bg_main)
        button_frame.pack(side="bottom", pady=20)

        actions = [
            ("Adicionar", self.adicionar_bonus),
            ("Comprovante", self.baixar_comprovante),
            ("Excluir", self.excluir_bonus),
            ("Voltar", self.back)
        ]

        for text, cmd in actions:
            bg_color = "#b00020" if text == "Excluir" else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=140,
                height=38,
                bg=bg_color,
                fg=self.fg_text
            )
            btn.pack(side="left", padx=10)

        self.load_bonuses()

    def load_bonuses(self):
        self.tree.delete(*self.tree.get_children())
        try:
            all_bonuses = self.bonus_repo.get_all()
            driver_bonuses = [b for b in all_bonuses if int(b.driver_id) == int(self.driver_id)]
            driver_bonuses.sort(key=lambda b: str(b.bonus_date), reverse=True)

            for bonus in driver_bonuses:
                date_val = bonus.bonus_date
                if isinstance(date_val, str) and "-" in date_val:
                    try:
                        date_display = datetime.strptime(date_val, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        date_display = date_val
                elif hasattr(date_val, 'strftime'):
                    date_display = date_val.strftime('%d/%m/%Y')
                else:
                    date_display = str(date_val)

                self.tree.insert("", "end", iid=str(bonus.bonus_id), values=(
                    date_display,
                    f"R$ {float(bonus.amount):.2f}",
                    (bonus.description or "").capitalize()
                ))
        except Exception:
            pass

    def adicionar_bonus(self):
        try:
            interface = InterfaceAddDriverBonus(self.parent, self.db_path, self.driver_id, self.driver_name)
            interface.show()
        except Exception:
            messagebox.showerror("Erro", "Não foi possível abrir a tela.")

    def excluir_bonus(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um registro.")
            return

        if messagebox.askyesno("Confirmar", "Excluir esta bonificação?"):
            try:
                if self.bonus_repo.delete(int(selected[0])):
                    messagebox.showinfo("Sucesso", "Registro excluído.")
                    self.load_bonuses()
            except Exception:
                messagebox.showerror("Erro", "Falha ao excluir.")

    def baixar_comprovante(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um registro.")
            return

        bonus = self.bonus_repo.get_by_id(int(selected[0]))
        if not bonus or not bonus.receipt:
            messagebox.showinfo("Informação", "Sem comprovante digitalizado.")
            return

        receipt_bytes = bonus.receipt
        ext = ".pdf"
        if receipt_bytes[:2] == b"\xff\xd8": ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n": ext = ".png"

        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("PDF", "*.pdf"), ("Imagens", "*.jpg;*.png")],
            initialfile=f"Bonus_{self.driver_id}_{selected[0]}",
            title="Salvar arquivo"
        )

        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(receipt_bytes)
                messagebox.showinfo("Sucesso", "Arquivo salvo.")
            except Exception:
                messagebox.showerror("Erro", "Falha ao salvar.")

    def back(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        InterfaceListDrivers(self.parent, self.db_path).show()