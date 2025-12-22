import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.interface.driver.interface_edit_driver import InterfaceEditDriver
from app.interface.driver.interface_list_bonus import InterfaceBonificacoesMotorista
from app.repositories.driver_repository import DriverRepository
from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.interface.driver.interface_register_driver import InterfaceRegisterDriver
from app.components.list_rounded_button import ListRoundedButton


class InterfaceListDrivers:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)
        self.bonus_repo = DriverBonusRepository(self.db_path)
        self.font_title = ("Segoe UI", 22, "bold")
        self.font_tree = ("Segoe UI", 11)
        self.row_height = 32
        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent_color = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Gestão de motoristas",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent_color
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True, padx=30, pady=10)

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=self.font_tree,
            rowheight=self.row_height,
            background="#2c2c2e",
            fieldbackground="#2c2c2e",
            foreground=self.fg_text,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            background=self.accent_color,
            foreground=self.fg_text,
            borderwidth=1
        )
        style.map("Treeview", background=[("selected", "#4a4a4c")])

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Nome", "Salario", "Contato", "Data Contratado", "Data Demitido"),
            show="headings",
            selectmode="browse"
        )

        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.heading("Nome", text="Nome Completo")
        self.tree.heading("Salario", text="Salario (R$)")
        self.tree.heading("Contato", text="Telefone/Contato")
        self.tree.heading("Data Contratado", text="Data Admissao")
        self.tree.heading("Data Demitido", text="Data Rescisao")

        self.tree.column("Nome", width=350, anchor="w", stretch=True)
        self.tree.column("Salario", width=150, anchor="center", stretch=False)
        self.tree.column("Contato", width=200, anchor="center", stretch=False)
        self.tree.column("Data Contratado", width=180, anchor="center", stretch=False)
        self.tree.column("Data Demitido", width=180, anchor="center", stretch=False)

        v_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")

        button_container = tk.Frame(self.parent, bg=self.bg_main)
        button_container.pack(fill="x", side="bottom", pady=25)

        inner_button_frame = tk.Frame(button_container, bg=self.bg_main)
        inner_button_frame.pack()

        btns = [
            ("Novo Motorista", self.register_driver, self.bg_button),
            ("Editar", self.edit_selected_driver, self.bg_button),
            ("Detalhes", self.driver_details, self.bg_button),
            ("Bonificações", self.add_bonus, self.bg_button),
            ("Excluir", self.delete_driver, "#b00020")
        ]

        for text, cmd, color in btns:
            btn = ListRoundedButton(
                inner_button_frame,
                text=text,
                width=160,
                height=40,
                fg=self.fg_text,
                bg=color,
                command=cmd
            )
            btn.pack(side="left", padx=12)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.load_drivers()

    def load_drivers(self):
        self.tree.delete(*self.tree.get_children())
        drivers = self.driver_repo.get_all()
        drivers.sort(key=lambda x: (x.end_date is not None,
                                    datetime.strptime(x.start_date, '%Y-%m-%d') if x.start_date else datetime.min))
        for driver in drivers:
            start_date = driver.start_date if driver.start_date else ""
            if start_date and isinstance(start_date, str):
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    pass
            end_date = driver.end_date if driver.end_date else ""
            if end_date and isinstance(end_date, str):
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    pass
            self.tree.insert("", "end", iid=str(driver.driver_id),
                             values=(driver.name, f"{driver.salary:.2f}", driver.contact, start_date, end_date))

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
        self.edit_driver(driver_id)

    def edit_driver(self, driver_id):
        for widget in self.parent.winfo_children():
            widget.destroy()
        driver = self.driver_repo.get_by_id(driver_id)
        InterfaceEditDriver(self.parent, self.db_path, driver)

    def driver_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um motorista para visualizar detalhes.")
            return
        driver_id = int(selected_item[0])
        from app.interface.driver.interface_driver_details import InterfaceDriverDetails
        interface = InterfaceDriverDetails(self.parent, self.db_path, driver_id)
        interface.show()

    def add_bonus(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um motorista para gerenciar bonificações.")
            return
        driver_id = int(selected_item[0])
        driver = self.driver_repo.get_by_id(driver_id)
        if driver:
            InterfaceBonificacoesMotorista(self.parent, self.db_path, driver_id, driver.name)
        else:
            messagebox.showerror("Erro", "Motorista nao encontrado.")

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
            confirm = messagebox.askyesno("Confirmacao", f"Deseja realmente excluir o motorista '{driver.name}'?")
            if confirm:
                try:
                    self.bonus_repo.delete_by_driver_id(driver_id)
                    self.driver_repo.delete(driver_id)
                    messagebox.showinfo("Sucesso", f"Motorista '{driver.name}' e seus registros excluidos com sucesso.")
                    self.show()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao excluir motorista: {str(e)}")
        else:
            messagebox.showerror("Erro", "Motorista nao encontrado.")