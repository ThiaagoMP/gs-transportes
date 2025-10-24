import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from app.components.list_rounded_button import ListRoundedButton
from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.models.driver_bonus import DriverBonus
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

        tk.Label(
            self.parent,
            text=f"Bonificações de {self.driver_name}",
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
            columns=("Data", "Valor", "Descrição"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Data", 150, False),
            ("Valor", 150, False),
            ("Descrição", 250, True),
        ]

        for col, width, stretch in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=stretch)

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Adicionar Bonificação", self.adicionar_bonus),
            ("Baixar Comprovante", self.baixar_comprovante),
            ("Voltar", self.back),
            ("Excluir Bonificação", self.excluir_bonus)
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
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

        self.load_bonuses()

    def load_bonuses(self):
        self.tree.delete(*self.tree.get_children())
        all_bonuses = self.bonus_repo.get_all()
        driver_bonuses = [b for b in all_bonuses if b.driver_id == self.driver_id]

        driver_bonuses.sort(key=lambda b: b.bonus_date, reverse=True)

        for bonus in driver_bonuses:
            if isinstance(bonus.bonus_date, str):
                try:
                    date_obj = datetime.strptime(bonus.bonus_date, '%Y-%m-%d')
                    date_display = date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    date_display = bonus.bonus_date
            elif isinstance(bonus.bonus_date, datetime):
                date_display = bonus.bonus_date.strftime('%d/%m/%Y')
            else:
                date_display = str(bonus.bonus_date)

            self.tree.insert("", "end", iid=str(bonus.bonus_id), values=(
                date_display,
                f"{bonus.amount:.2f}",
                bonus.description or ""
            ))

    def adicionar_bonus(self):
        try:
            interface = InterfaceAddDriverBonus(self.parent, self.db_path, self.driver_id, self.driver_name)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar bonificação: {str(e)}")

    def excluir_bonus(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma bonificação para excluir.")
            return

        bonus_id = int(selected_item[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir esta bonificação?"):
            try:
                if self.bonus_repo.delete(bonus_id):
                    messagebox.showinfo("Sucesso", "Bonificação excluída com sucesso!")
                    self.load_bonuses()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir a bonificação.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir bonificação: {str(e)}")

    def baixar_comprovante(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma bonificação para baixar o comprovante.")
            return

        bonus_id = int(selected_item[0])
        bonus = self.bonus_repo.get_by_id(bonus_id)

        if not bonus or not bonus.receipt:
            messagebox.showinfo("Info", "Não há comprovante para esta bonificação.")
            return

        receipt_bytes = bonus.receipt

        if receipt_bytes[:4] == b"%PDF":
            ext = ".pdf"
        elif receipt_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"
        else:
            ext = ".bin"

        nome_sanitizado = "".join(c for c in self.driver_name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        data_str = bonus.bonus_date.strftime("%d%m%Y") if hasattr(bonus.bonus_date, "strftime") else str(
            bonus.bonus_date)
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
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        interface = InterfaceListDrivers(self.parent, self.db_path)
        interface.show()
