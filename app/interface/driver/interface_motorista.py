import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.driver_repository import DriverRepository
from app.models.driver import Driver

class InterfaceMotorista:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)

    def show(self):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Cadastrar Motorista",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        # Frame principal
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")  # Tema compatível com Windows 7
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")

        # Função de validação
        validate_cmd = self.parent.register(self.validate_input)

        # Campos do formulário
        ttk.Label(main_frame, text="Nome*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        name_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "name", 50))
        name_entry.grid(row=0, column=1, padx=15, pady=15)
        name_entry.insert(0, "Ex.: João Silva")
        name_entry.bind("<FocusIn>", lambda e: name_entry.delete(0, tk.END) if name_entry.get() == "Ex.: João Silva" else None)

        ttk.Label(main_frame, text="Salário (R$)*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        salary_entry = ttk.Entry(main_frame, width=45)
        salary_entry.grid(row=1, column=1, padx=15, pady=15)
        salary_entry.insert(0, "Ex.: 2500.00")
        salary_entry.bind("<FocusIn>", lambda e: salary_entry.delete(0, tk.END) if salary_entry.get() == "Ex.: 2500.00" else None)

        ttk.Label(main_frame, text="Contato*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        contact_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "contact", 100))
        contact_entry.grid(row=2, column=1, padx=15, pady=15)
        contact_entry.insert(0, "Ex.: joao@email.com")
        contact_entry.bind("<FocusIn>", lambda e: contact_entry.delete(0, tk.END) if contact_entry.get() == "Ex.: joao@email.com" else None)

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
        end_date_entry.delete(0, tk.END)  # Garantir que venha vazio
        ttk.Button(
            end_date_frame,
            text="🗑 Limpar",
            style="TButton",
            command=lambda: self.clear_end_date(end_date_entry)
        ).grid(row=1, column=0, pady=5)

        ttk.Label(main_frame, text="CPF*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        cpf_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "cpf", 11))
        cpf_entry.grid(row=5, column=1, padx=15, pady=15)
        cpf_entry.insert(0, "Ex.: 123.456.789-00")
        cpf_entry.bind("<FocusIn>", lambda e: cpf_entry.delete(0, tk.END) if cpf_entry.get() == "Ex.: 123.456.789-00" else None)
        cpf_entry.bind("<KeyRelease>", lambda e: self.format_cpf(cpf_entry))

        ttk.Label(main_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        rg_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "rg", 9))
        rg_entry.grid(row=6, column=1, padx=15, pady=15)
        rg_entry.insert(0, "Ex.: 12.345.678-9")
        rg_entry.bind("<FocusIn>", lambda e: rg_entry.delete(0, tk.END) if rg_entry.get() == "Ex.: 12.345.678-9" else None)
        rg_entry.bind("<KeyRelease>", lambda e: self.format_rg(rg_entry))

        ttk.Label(main_frame, text="CNH*:").grid(row=7, column=0, sticky="e", padx=15, pady=15)
        cnh_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "cnh", 20))
        cnh_entry.grid(row=7, column=1, padx=15, pady=15)
        cnh_entry.insert(0, "Ex.: 12345678901")
        cnh_entry.bind("<FocusIn>", lambda e: cnh_entry.delete(0, tk.END) if cnh_entry.get() == "Ex.: 12345678901" else None)

        ttk.Label(main_frame, text="Informações Extras:").grid(row=8, column=0, sticky="ne", padx=15, pady=15)
        extra_info_entry = tk.Text(main_frame, width=45, height=3, font=("Segoe UI", 12))
        extra_info_entry.grid(row=8, column=1, padx=15, pady=15)
        extra_info_entry.insert("1.0", "Opcional")
        extra_info_entry.bind("<FocusIn>", lambda e: extra_info_entry.delete("1.0", tk.END) if extra_info_entry.get("1.0", tk.END).strip() == "Opcional" else None)
        extra_info_entry.bind("<Key>", lambda e: self.limit_text(extra_info_entry, 255))

        # Frame para botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Cadastrar",
            style="TButton",
            command=lambda: self.save_driver(
                name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Limpar",
            style="TButton",
            command=lambda: self.clear_form(
                name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=10, column=0, columnspan=2, pady=15)

    def edit(self, driver_id):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Editar Motorista",
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        ).pack(pady=25)

        # Frame principal
        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")  # Tema compatível com Windows 7
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")

        # Função de validação
        validate_cmd = self.parent.register(self.validate_input)

        # Campos do formulário
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
        end_date_entry.delete(0, tk.END)  # Forçar vazio ao abrir edição

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
        driver = self.driver_repo.read(driver_id)
        if driver:
            name_entry.insert(0, driver.name)
            salary_entry.insert(0, str(driver.salary))
            contact_entry.insert(0, driver.contact)
            if driver.start_date:
                start_date_entry.set_date(datetime.strptime(driver.start_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
            if driver.cpf:
                cpf_entry.insert(0, f"{driver.cpf[:3]}.{driver.cpf[3:6]}.{driver.cpf[6:9]}-{driver.cpf[9:]}")
            if driver.rg:
                rg_entry.insert(0, f"{driver.rg[:2]}.{driver.rg[2:5]}.{driver.rg[5:8]}-{driver.rg[8:]}")
            if driver.cnh:
                cnh_entry.insert(0, driver.cnh)
            if driver.extra_info and driver.extra_info != "Opcional":
                extra_info_entry.insert("1.0", driver.extra_info)

        # Frame para botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Salvar",
            style="TButton",
            command=lambda: self.update_driver(
                driver_id, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Limpar",
            style="TButton",
            command=lambda: self.clear_form(
                name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=10, column=0, columnspan=2, pady=15)

    def validate_input(self, P, field, max_length):
        if not P:
            return True
        max_length = int(max_length)  # Garantir que max_length seja inteiro
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
            end_date_sql = None  # Forçar Data de Término como NULL ao salvar
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
            self.clear_form(name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry)
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar motorista: {str(e)}")

    def save_driver(self, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name = name_entry.get().strip()
        salary = salary_entry.get().strip()
        contact = contact_entry.get().strip()
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        cpf = cpf_entry.get().strip().replace(".", "").replace("-", "")
        rg = rg_entry.get().strip().replace(".", "").replace("-", "")
        cnh = cnh_entry.get().strip()
        extra_info = extra_info_entry.get("1.0", tk.END).strip()

        if not name or name == "Ex.: João Silva":
            messagebox.showerror("Erro", "Preencha o campo Nome.")
            return
        if not salary or salary == "Ex.: 2500.00":
            messagebox.showerror("Erro", "Preencha o campo Salário.")
            return
        if not contact or contact == "Ex.: joao@email.com":
            messagebox.showerror("Erro", "Preencha o campo Contato.")
            return
        if not start_date:
            messagebox.showerror("Erro", "Preencha o campo Data de Início.")
            return
        if not cpf or cpf == "12345678900":
            messagebox.showerror("Erro", "Preencha o campo CPF.")
            return
        if not rg or rg == "12345678":
            messagebox.showerror("Erro", "Preencha o campo RG.")
            return
        if not cnh or cnh == "Ex.: 12345678901":
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
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
                if end_date_obj < start_date_obj:
                    messagebox.showerror("Erro", "Data de Término não pode ser anterior à Data de Início.")
                    return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido.")
            return

        try:
            salary = float(salary)
            start_date_sql = start_date_obj.strftime('%Y-%m-%d')
            end_date_sql = end_date_obj.strftime('%Y-%m-%d') if end_date else None
            extra_info = None if extra_info == "Opcional" else extra_info
            driver = Driver(None, name, salary, contact, start_date_sql, end_date_sql, cpf, rg, cnh, extra_info)
            self.driver_repo.create(driver)
            messagebox.showinfo("Sucesso", f"Motorista '{name}' cadastrado com sucesso!")
            self.clear_form(name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry)
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar motorista: {str(e)}")