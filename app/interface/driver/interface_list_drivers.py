import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from app.interface.driver.interface_edit_driver import InterfaceEditDriver
from app.interface.driver.interface_list_bonus import InterfaceBonificacoesMotorista
from app.repositories.driver_repository import DriverRepository
from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.interface.driver.interface_add_driver_bonus import InterfaceAddDriverBonus
from app.interface.driver.interface_register_driver import InterfaceRegisterDriver

class InterfaceListDrivers:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)
        self.bonus_repo = DriverBonusRepository(self.db_path)
        self.font_title = ("Segoe UI", 28, "bold")
        self.font_label = ("Segoe UI", 16)
        self.font_tree = ("Segoe UI", 14)
        self.row_height = 35
        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent_color = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(
            self.parent,
            text="Motoristas",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent_color
        ).pack(pady=40)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=self.font_tree,
            rowheight=self.row_height,
            background=self.bg_main,
            fieldbackground=self.bg_main,
            foreground=self.fg_text
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 16, "bold"),
            background=self.accent_color,
            foreground=self.fg_text
        )

        self.tree = ttk.Treeview(
            list_frame,
            columns=("Nome", "Salário", "Contato", "Data Contratado", "Data Demitido"),
            show="headings",
            height=15
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.column("Nome", width=300)
        self.tree.column("Salário", width=150)
        self.tree.column("Contato", width=250)
        self.tree.column("Data Contratado", width=150)
        self.tree.column("Data Demitido", width=150)
        self.tree.pack(fill="both", expand=True, pady=20)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=15)

        from app.components.list_rounded_button import ListRoundedButton

        inner_frame = tk.Frame(button_frame, bg=self.bg_main)
        inner_frame.pack()

        btns = [
            ("Cadastrar Motorista", self.register_driver, self.bg_button),
            ("Editar Motorista", self.edit_selected_driver, self.bg_button),
            ("Visualizar Lucros", self.visualize_profits, self.bg_button),
            ("Bonificações", self.add_bonus, self.bg_button),
            ("Excluir Motorista", self.delete_driver, "#f44336")
        ]

        for i, (text, cmd, color) in enumerate(btns):
            btn = ListRoundedButton(inner_frame, text=text, width=220, height=50, fg=self.fg_text, bg=color, command=cmd)
            btn.pack(side="left", padx=10)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.load_drivers()

    def load_drivers(self):
        self.tree.delete(*self.tree.get_children())
        drivers = self.driver_repo.get_all()
        drivers.sort(key=lambda x: (x.end_date is not None, datetime.strptime(x.start_date, '%Y-%m-%d') if x.start_date else datetime.min))
        for driver in drivers:
            start_date = driver.start_date if driver.start_date else ""
            if start_date and isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            end_date = driver.end_date if driver.end_date else ""
            if end_date and isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            self.tree.insert("", "end", iid=str(driver.driver_id), values=(driver.name, f"{driver.salary:.2f}", driver.contact, start_date, end_date))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            driver_id = int(item)
            self.edit_driver(driver_id)

    def edit_selected_driver(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um motorista para editar.")
            return
        driver_id = int(selected_item[0])
        driver = self.driver_repo.get_by_id(driver_id)
        if driver:
            self.edit_driver(driver_id)
        else:
            messagebox.showerror("Erro", "Motorista não encontrado.")

    def edit_driver(self, driver_id):
        for widget in self.parent.winfo_children():
            widget.destroy()
        driver = self.driver_repo.get_by_id(driver_id)
        interface = InterfaceEditDriver(self.parent, self.db_path, driver)
        interface.pack(fill="both", expand=True)

    def visualize_profits(self):
        messagebox.showinfo("Aviso", "Funcionalidade 'Visualizar Lucros' ainda não implementada.")

    def add_bonus(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um motorista para adicionar bonificação.")
            return
        driver_id = int(selected_item[0])
        driver = self.driver_repo.get_by_id(driver_id)
        if driver:
            InterfaceBonificacoesMotorista(self.parent, self.db_path, driver_id, driver.name)
        else:
            messagebox.showerror("Erro", "Motorista não encontrado.")

    def register_driver(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        interface = InterfaceRegisterDriver(self.parent, self.db_path)
        interface.show()

    def delete_driver(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um motorista para excluir.")
            return
        driver_id = int(selected_item[0])
        driver = self.driver_repo.get_by_id(driver_id)
        if driver:
            confirm = messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o motorista '{driver.name}'?")
            if confirm:
                try:
                    self.bonus_repo.delete_by_driver_id(driver_id)
                    self.driver_repo.delete(driver_id)
                    messagebox.showinfo("Sucesso", f"Motorista '{driver.name}' e seus bônus excluídos com sucesso!")
                    self.show()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao excluir motorista ou bônus: {str(e)}")
        else:
            messagebox.showerror("Erro", "Motorista não encontrado.")
