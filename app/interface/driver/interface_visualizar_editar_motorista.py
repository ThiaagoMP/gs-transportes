import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.driver_repository import DriverRepository
from app.repositories.bonus_repository import BonusRepository
from app.models.driver import Driver
from app.interface.driver.interface_adicionar_bonificacao import InterfaceAdicionarBonificacao
from app.interface.driver.interface_motorista import InterfaceMotorista

class InterfaceVisualizarEditar:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)
        self.bonus_repo = BonusRepository(self.db_path)

    def show(self):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Motoristas",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        # Frame principal dividido em duas colunas
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Frame para a lista de motoristas (esquerda)
        list_frame = tk.Frame(main_frame, bg="#ffffff")
        list_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")  # Tema compatível com Windows 7
        style.configure("Treeview", font=("Segoe UI", 12), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"), background="#2196f3", foreground="#ffffff")
        style.configure("Delete.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#f44336", foreground="#ffffff")
        style.map("Delete.TButton",
                  background=[("active", "#d32f2f")],
                  foreground=[("active", "#ffffff")])
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("Action.TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])

        # Treeview pra listar motoristas
        self.tree = ttk.Treeview(list_frame, columns=("Nome", "Salário", "Contato", "Data Contratado", "Data Demitido"), show="headings", height=15)
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Salário", text="Salário (R$)")
        self.tree.heading("Contato", text="Contato")
        self.tree.heading("Data Contratado", text="Data Contratado")
        self.tree.heading("Data Demitido", text="Data Demitido")
        self.tree.column("Nome", width=200)
        self.tree.column("Salário", width=100)
        self.tree.column("Contato", width=200)
        self.tree.column("Data Contratado", width=120)
        self.tree.column("Data Demitido", width=120)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Frame para botões
        button_frame = tk.Frame(list_frame, bg="#ffffff")
        button_frame.pack(side="bottom", pady=10)

        ttk.Button(
            button_frame,
            text="Cadastrar",
            style="Action.TButton",
            command=self.cadastrar_motorista
        ).pack(side="left", padx=5)

        # Botões de ação (Editar, Visualizar Lucros, Adicionar Bonificação, Excluir)
        action_frame = tk.Frame(list_frame, bg="#ffffff")
        action_frame.pack(side="bottom", pady=5)
        ttk.Button(
            action_frame,
            text="Editar",
            style="Action.TButton",
            command=self.edit_selected_driver
        ).pack(side="left", padx=5)
        ttk.Button(
            action_frame,
            text="Visualizar Lucros",
            style="Action.TButton",
            command=self.visualize_profits
        ).pack(side="left", padx=5)
        ttk.Button(
            action_frame,
            text="Adicionar Bonificação",
            style="Action.TButton",
            command=self.add_bonus
        ).pack(side="left", padx=5)
        ttk.Button(
            action_frame,
            text="Excluir",
            style="Delete.TButton",
            command=self.delete_driver
        ).pack(side="left", padx=5)

        # Binding para duplo clique
        self.tree.bind("<Double-1>", self.on_double_click)

        # Carregar motoristas
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

        tk.Label(
            self.parent,
            text="Editar Motorista",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")

        validate_cmd = self.parent.register(self.validate_input)

        ttk.Label(main_frame, text="Nome*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        name_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "name", 50))
        name_entry.grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Salário (R$)*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        salary_entry = ttk.Entry(main_frame, width=45)
        salary_entry.grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Contato*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        contact_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "contact", 100))
        contact_entry.grid(row=2, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Data de Início*:").grid(row=3, column=0, sticky="e", padx=15, pady=15)
        start_date_entry = DateEntry(
            main_frame, width=43, date_pattern="dd/mm/yyyy", background="#1976d2", foreground="#ffffff",
            state="normal", style="my.DateEntry"
        )
        start_date_entry.grid(row=3, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Data de Término:").grid(row=4, column=0, sticky="e", padx=15, pady=15)
        end_date_frame = tk.Frame(main_frame, bg="#ffffff")
        end_date_frame.grid(row=4, column=1, padx=15, pady=15)
        end_date_entry = DateEntry(
            end_date_frame, width=43, date_pattern="dd/mm/yyyy", background="#1976d2", foreground="#ffffff",
            state="normal", style="my.DateEntry"
        )
        end_date_entry.grid(row=0, column=0)
        end_date_entry.delete(0, tk.END)

        ttk.Label(main_frame, text="CPF*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        cpf_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "cpf", 11))
        cpf_entry.grid(row=5, column=1, padx=15, pady=15)
        cpf_entry.bind("<KeyRelease>", lambda e: self.format_cpf(cpf_entry))

        ttk.Label(main_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        rg_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "rg", 9))
        rg_entry.grid(row=6, column=1, padx=15, pady=15)
        rg_entry.bind("<KeyRelease>", lambda e: self.format_rg(rg_entry))

        ttk.Label(main_frame, text="CNH*:").grid(row=7, column=0, sticky="e", padx=15, pady=15)
        cnh_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "cnh", 20))
        cnh_entry.grid(row=7, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Informações Extras:").grid(row=8, column=0, sticky="ne", padx=15, pady=15)
        extra_info_entry = tk.Text(main_frame, width=45, height=3, font=("Segoe UI", 12))
        extra_info_entry.grid(row=8, column=1, padx=15, pady=15)

        # Carregar dados do motorista
        driver = self.driver_repo.get_by_id(driver_id)
        if driver:
            name_entry.insert(0, driver.name or "")
            salary_entry.insert(0, str(driver.salary) if driver.salary is not None else "")
            contact_entry.insert(0, driver.contact or "")
            if driver.start_date:
                start_date_entry.set_date(datetime.strptime(driver.start_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
            if driver.end_date:
                end_date_entry.set_date(datetime.strptime(driver.end_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
            if driver.cpf:
                cpf_entry.insert(0, f"{driver.cpf[:3]}.{driver.cpf[3:6]}.{driver.cpf[6:9]}-{driver.cpf[9:]}")
            if driver.rg:
                rg_entry.insert(0, f"{driver.rg[:2]}.{driver.rg[2:5]}.{driver.rg[5:8]}-{driver.rg[8:]}")
            if driver.cnh:
                cnh_entry.insert(0, driver.cnh or "")
            if driver.extra_info and driver.extra_info != "Opcional":
                extra_info_entry.insert("1.0", driver.extra_info or "")
        else:
            messagebox.showerror("Erro", f"Motorista com ID {driver_id} não encontrado.")

        # Frame para botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Salvar",
            style="Action.TButton",
            command=lambda: self.update_driver(
                driver_id, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Voltar",
            style="Action.TButton",
            command=self.show
        ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=10, column=0, columnspan=2, pady=15)

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
            InterfaceAdicionarBonificacao(self.parent, self.db_path, driver_id, driver.name)
        else:
            messagebox.showerror("Erro", "Motorista não encontrado.")

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
                    # Remover bônus associados ao motorista
                    self.bonus_repo.delete_by_driver_id(driver_id)
                    # Remover o motorista
                    self.driver_repo.delete(driver_id)
                    messagebox.showinfo("Sucesso", f"Motorista '{driver.name}' e seus bônus excluídos com sucesso!")
                    self.show()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao excluir motorista ou bônus: {str(e)}")
        else:
            messagebox.showerror("Erro", "Motorista não encontrado.")

    def cadastrar_motorista(self):
        try:
            interface = InterfaceMotorista(self.parent, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a interface de cadastro: {str(e)}")

    def validate_input(self, P, field, max_length):
        if not P:
            return True
        max_length = int(max_length)
        if field == "cpf":
            clean_text = ''.join(c for c in P if c.isdigit())
            return len(clean_text) <= max_length
        elif field == "rg":
            clean_text = ''.join(c for c in P if c.isdigit())
            return len(clean_text) <= max_length
        else:
            clean_text = ''.join(c for c in P if c.isalnum() or c.isspace())
            return len(clean_text) <= max_length

    def limit_text(self, text_widget, max_length):
        content = text_widget.get("1.0", tk.END).strip()
        if len(content) > max_length:
            text_widget.delete(f"{max_length + 1}.0", tk.END)

    def clear_end_date(self, end_date_entry):
        end_date_entry.delete(0, tk.END)

    def clear_form(self, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name_entry.delete(0, tk.END)
        name_entry.insert(0, "Ex.: João Silva")
        salary_entry.delete(0, tk.END)
        salary_entry.insert(0, "Ex.: 2500.00")
        contact_entry.delete(0, tk.END)
        contact_entry.insert(0, "Ex.: joao@email.com")
        start_date_entry.delete(0, tk.END)
        self.clear_end_date(end_date_entry)
        cpf_entry.delete(0, tk.END)
        cpf_entry.insert(0, "Ex.: 123.456.789-00")
        rg_entry.delete(0, tk.END)
        rg_entry.insert(0, "Ex.: 12.345.678-9")
        cnh_entry.delete(0, tk.END)
        cnh_entry.insert(0, "Ex.: 12345678901")
        extra_info_entry.delete("1.0", tk.END)
        extra_info_entry.insert("1.0", "Opcional")

    def format_cpf(self, entry):
        current = entry.get().replace(".", "").replace("-", "")
        if len(current) > 11:
            current = current[:11]
        if all(c.isdigit() for c in current):
            if len(current) > 9:
                formatted = f"{current[:3]}.{current[3:6]}.{current[6:9]}-{current[9:]}"
            elif len(current) > 6:
                formatted = f"{current[:3]}.{current[3:6]}.{current[6:]}"
            elif len(current) > 3:
                formatted = f"{current[:3]}.{current[3:]}"
            else:
                formatted = current
            entry.delete(0, tk.END)
            entry.insert(0, formatted)

    def format_rg(self, entry):
        current = entry.get().replace(".", "").replace("-", "")
        if len(current) > 9:
            current = current[:9]
        if all(c.isdigit() for c in current):
            if len(current) > 6:
                formatted = f"{current[:2]}.{current[2:5]}.{current[5:8]}-{current[8:]}"
            elif len(current) > 2:
                formatted = f"{current[:2]}.{current[2:]}"
            else:
                formatted = current
            entry.delete(0, tk.END)
            entry.insert(0, formatted)

    def update_driver(self, driver_id, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name = name_entry.get().strip()
        salary = salary_entry.get().strip()
        contact = contact_entry.get().strip()
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        cpf = cpf_entry.get().strip().replace(".", "").replace("-", "")
        rg = rg_entry.get().strip().replace(".", "").replace("-", "")
        cnh = cnh_entry.get().strip()
        extra_info = extra_info_entry.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Erro", "Preencha o campo Nome.")
            return
        if not salary:
            messagebox.showerror("Erro", "Preencha o campo Salário.")
            return
        if not contact:
            messagebox.showerror("Erro", "Preencha o campo Contato.")
            return
        if not start_date:
            messagebox.showerror("Erro", "Preencha o campo Data de Início.")
            return
        if not cpf:
            messagebox.showerror("Erro", "Preencha o campo CPF.")
            return
        if not rg:
            messagebox.showerror("Erro", "Preencha o campo RG.")
            return
        if not cnh:
            messagebox.showerror("Erro", "Preencha o campo CNH.")
            return
        if len(name) > 50:
            messagebox.showerror("Erro", "Nome deve ter no máximo 50 caracteres.")
            return
        if len(contact) > 100:
            messagebox.showerror("Erro", "Contato deve ter no máximo 100 caracteres.")
            return
        if len(cpf) > 11:
            messagebox.showerror("Erro", "CPF deve ter exatamente 11 dígitos.")
            return
        if len(rg) > 9:
            messagebox.showerror("Erro", "RG deve ter no máximo 9 dígitos.")
            return
        if len(cnh) > 20:
            messagebox.showerror("Erro", "CNH deve ter no máximo 20 caracteres.")
            return
        if extra_info and len(extra_info) > 255:
            messagebox.showerror("Erro", "Informações Extras devem ter no máximo 255 caracteres.")
            return

        try:
            start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
            current_date = datetime.now()
            if start_date_obj > current_date:
                messagebox.showerror("Erro", "Data de Início não pode ser posterior a hoje.")
                return
            end_date_sql = None
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
                if end_date_obj < start_date_obj:
                    messagebox.showerror("Erro", "Data de Término não pode ser anterior à Data de Início.")
                    return
                else:
                    end_date_sql = end_date_obj.strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido.")
            return

        try:
            salary = float(salary)
            start_date_sql = start_date_obj.strftime('%Y-%m-%d')
            driver = Driver(driver_id, name, salary, contact, start_date_sql, end_date_sql, cpf, rg, cnh, extra_info)
            self.driver_repo.update(driver)
            messagebox.showinfo("Sucesso", f"Motorista '{name}' atualizado com sucesso!")
            self.show()
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar motorista: {str(e)}")