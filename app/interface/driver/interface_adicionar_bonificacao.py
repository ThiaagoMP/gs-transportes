import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.bonus_repository import BonusRepository

class InterfaceAdicionarBonificacao:
    def __init__(self, parent, db_path, driver_id, driver_name):
        self.parent = parent
        self.db_path = db_path
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.bonus_repo = BonusRepository(self.db_path)
        self.selected_file_path = tk.StringVar()
        self.receipt_data = None
        self.create_interface()

    def create_interface(self):
        # Limpar o conteúdo atual
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text=f"Adicionar Bonificação - {self.driver_name}",
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
        ttk.Label(main_frame, text="Descrição:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        description_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(validate_cmd, "%P", "description", 255))
        description_entry.grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Data da Bonificação*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        bonus_date_entry = DateEntry(
            main_frame, width=43, date_pattern="dd/mm/yyyy", background="#1976d2", foreground="#ffffff",
            state="normal", style="my.DateEntry"
        )
        bonus_date_entry.grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Valor (R$)*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        amount_entry = ttk.Entry(main_frame, width=45)
        amount_entry.grid(row=2, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Comprovante (Opcional):").grid(row=3, column=0, sticky="ne", padx=15, pady=15)
        ttk.Button(
            main_frame,
            text="Selecionar Comprovante",
            style="Action.TButton",
            command=self.select_file
        ).grid(row=3, column=1, padx=15, pady=15, sticky="w")
        ttk.Label(main_frame, textvariable=self.selected_file_path).grid(row=3, column=1, padx=15, pady=5, sticky="w")

        # Frame para botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Salvar",
            style="Action.TButton",
            command=lambda: self.save_bonus(description_entry, bonus_date_entry, amount_entry)
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Voltar",
            style="Action.TButton",
            command=self.back
        ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic")).grid(row=5, column=0, columnspan=2, pady=15)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            self.selected_file_path.set(file_path)
            try:
                with open(file_path, 'rb') as file:
                    self.receipt_data = file.read()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler o arquivo: {str(e)}")
                self.receipt_data = None
                self.selected_file_path.set("")

    def validate_input(self, P, field, max_length):
        if not P:
            return True
        max_length = int(max_length)
        clean_text = ''.join(c for c in P if c.isalnum() or c.isspace())
        return len(clean_text) <= max_length

    def save_bonus(self, description_entry, bonus_date_entry, amount_entry):
        description = description_entry.get().strip()
        bonus_date = bonus_date_entry.get().strip()
        amount = amount_entry.get().strip()
        receipt = self.receipt_data

        if not bonus_date:
            messagebox.showerror("Erro", "Preencha a Data da Bonificação.")
            return
        if not amount:
            messagebox.showerror("Erro", "Preencha o Valor.")
            return
        if len(description) > 255:
            messagebox.showerror("Erro", "Descrição deve ter no máximo 255 caracteres.")
            return

        try:
            bonus_date_obj = datetime.strptime(bonus_date, '%d/%m/%Y')
            current_date = datetime.now()
            if bonus_date_obj > current_date:
                messagebox.showerror("Erro", "Data da Bonificação não pode ser posterior a hoje.")
                return
            bonus_date_sql = bonus_date_obj.strftime('%Y-%m-%d')
            amount_float = float(amount)

            # Criar tupla na ordem correta: (driver_id, description, receipt, bonus_date, amount)
            bonus_tuple = (self.driver_id, description if description else None, receipt, bonus_date_sql, amount_float)

            # Inserir no repositório
            bonus_id = self.bonus_repo.add(bonus_tuple)
            if bonus_id is not None:
                messagebox.showinfo("Sucesso", f"Bonificação de R${amount_float:.2f} adicionada com sucesso para {self.driver_name}!")
                self.back()
            else:
                messagebox.showerror("Erro", f"Falha ao adicionar bonificação para {self.driver_name}.")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data ou valor inválido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar bonificação: {str(e)}. Verifique se o DriverID {self.driver_id} é válido.")

    def back(self):
        from app.interface.driver.interface_visualizar_editar_motorista import InterfaceVisualizarEditar
        interface = InterfaceVisualizarEditar(self.parent, self.db_path)
        interface.show()