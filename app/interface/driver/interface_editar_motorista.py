import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.driver_repository import DriverRepository
from app.models.driver import Driver

class InterfaceEditarMotorista:
    def __init__(self, parent, db_path, driver):
        self.parent = parent
        self.db_path = db_path
        self.driver = driver
        self.driver_repo = DriverRepository(self.db_path)

    def show(self):
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
        style.configure("TLabel", font=("Segoe UI", 14))
        style.configure("TEntry", font=("Segoe UI", 12), padding=5)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton",
                  background=[("active", "#45a049")],
                  foreground=[("active", "#ffffff")])

        # Campos do formulário
        ttk.Label(main_frame, text="Nome*:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.insert(0, self.driver.name)

        ttk.Label(main_frame, text="Salário (R$)*:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        salary_entry = ttk.Entry(main_frame, width=40)
        salary_entry.grid(row=1, column=1, padx=10, pady=10)
        salary_entry.insert(0, str(self.driver.salary))

        ttk.Label(main_frame, text="Contato*:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        contact_entry = ttk.Entry(main_frame, width=40)
        contact_entry.grid(row=2, column=1, padx=10, pady=10)
        contact_entry.insert(0, self.driver.contact)

        ttk.Label(main_frame, text="Data de Início*:").grid(row=3, column=0, sticky="e", padx=10, pady=10)
        start_date_entry = DateEntry(
            main_frame, width=38, date_pattern="dd/mm/yyyy", background="#1976d2", foreground="#ffffff"
        )
        start_date_entry.grid(row=3, column=1, padx=10, pady=10)
        start_date_entry.set_date(datetime.strptime(self.driver.start_date, '%Y-%m-%d').strftime('%d/%m/%Y'))

        ttk.Label(main_frame, text="Data de Término:").grid(row=4, column=0, sticky="e", padx=10, pady=10)
        end_date_frame = tk.Frame(main_frame, bg="#ffffff")
        end_date_frame.grid(row=4, column=1, padx=10, pady=10)
        end_date_entry = DateEntry(
            end_date_frame, width=38, date_pattern="dd/mm/yyyy", background="#1976d2", foreground="#ffffff"
        )
        end_date_entry.grid(row=0, column=0)
        if self.driver.end_date:
            end_date_entry.set_date(datetime.strptime(self.driver.end_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
        else:
            end_date_entry.insert(0, "Opcional")

        ttk.Label(main_frame, text="CPF*:").grid(row=5, column=0, sticky="e", padx=10, pady=10)
        cpf_entry = ttk.Entry(main_frame, width=40)
        cpf_entry.grid(row=5, column=1, padx=10, pady=10)
        cpf_entry.insert(0, self.driver.cpf)

        ttk.Label(main_frame, text="RG*:").grid(row=6, column=0, sticky="e", padx=10, pady=10)
        rg_entry = ttk.Entry(main_frame, width=40)
        rg_entry.grid(row=6, column=1, padx=10, pady=10)
        rg_entry.insert(0, self.driver.rg)

        ttk.Label(main_frame, text="CNH*:").grid(row=7, column=0, sticky="e", padx=10, pady=10)
        cnh_entry = ttk.Entry(main_frame, width=40)
        cnh_entry.grid(row=7, column=1, padx=10, pady=10)
        cnh_entry.insert(0, self.driver.cnh)

        ttk.Label(main_frame, text="Informações Extras:").grid(row=8, column=0, sticky="ne", padx=10, pady=10)
        extra_info_entry = tk.Text(main_frame, width=40, height=3, font=("Segoe UI", 12))
        extra_info_entry.grid(row=8, column=1, padx=10, pady=10)
        if self.driver.extra_info:
            extra_info_entry.insert("1.0", self.driver.extra_info)

        # Frame para botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Salvar",
            style="TButton",
            command=lambda: self.save_driver(
                name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry
            )
        ).pack(side="left", padx=5)

        if self.driver.end_date:
            ttk.Button(
                button_frame,
                text="Remover Histórico",
                style="TButton",
                command=lambda: self.remove_history()
            ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=10, column=0, columnspan=2, pady=10)

    def save_driver(self, name_entry, salary_entry, contact_entry, start_date_entry, end_date_entry, cpf_entry, rg_entry, cnh_entry, extra_info_entry):
        name = name_entry.get().strip()
        salary = salary_entry.get().strip()
        contact = contact_entry.get().strip()
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        cpf = cpf_entry.get().strip()
        rg = rg_entry.get().strip()
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
        if len(cpf.replace(".", "").replace("-", "")) > 11:
            messagebox.showerror("Erro", "CPF deve ter exatamente 11 dígitos.")
            return
        if len(rg.replace(".", "").replace("-", "")) > 9:
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
            if end_date and end_date != "Opcional":
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
            end_date_sql = end_date_obj.strftime('%Y-%m-%d') if end_date and end_date != "Opcional" else None
            extra_info = None if extra_info == "" else extra_info
            updated_driver = Driver(self.driver.driver_id, name, salary, contact, start_date_sql, end_date_sql, cpf, rg, cnh, extra_info)
            self.driver_repo.update(updated_driver)
            messagebox.showinfo("Sucesso", f"Motorista '{name}' atualizado com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar motorista: {str(e)}")

    def remove_history(self):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover o histórico deste motorista?"):
            try:
                self.driver_repo.delete(self.driver.driver_id)
                messagebox.showinfo("Sucesso", f"Histórico do motorista '{self.driver.name}' removido com sucesso!")
                self.parent.destroy()  # Fechar a tela após remoção
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover histórico: {str(e)}")

    def convert_date_to_sql(self, date_str):
        if not date_str or date_str == "Opcional":
            return None
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Formato de data inválido.")