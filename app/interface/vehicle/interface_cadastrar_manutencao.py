import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.repositories.maintenance_repository import MaintenanceRepository
from app.models.maintenance import Maintenance
from tkinter.filedialog import askopenfilename
import sqlite3
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton

def add_placeholder(entry: ttk.Entry, placeholder: str):
    entry._ph_text = placeholder
    entry._ph_active = False
    entry._orig_validate = entry.cget("validate")
    entry._orig_vcmd = entry.cget("validatecommand")
    entry._orig_style = entry.cget("style") or "TEntry"

    def _disable_validation():
        entry.configure(validate="none")

    def _restore_validation():
        entry.configure(validate=entry._orig_validate, validatecommand=entry._orig_vcmd)

    def _show_placeholder():
        _disable_validation()
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.configure(style="Placeholder.TEntry")
        entry._ph_active = True
        _restore_validation()

    def _hide_placeholder():
        _disable_validation()
        entry.delete(0, tk.END)
        entry.configure(style=entry._orig_style or "TEntry")
        entry._ph_active = False
        _restore_validation()

    def on_focus_in(_):
        if entry._ph_active:
            _hide_placeholder()

    def on_focus_out(_):
        if not entry.get():
            _show_placeholder()

    entry.bind("<FocusIn>", on_focus_in, add="+")
    entry.bind("<FocusOut>", on_focus_out, add="+")
    _show_placeholder()

def get_entry_value(entry: ttk.Entry) -> str:
    text = entry.get().strip()
    if getattr(entry, "_ph_active", False):
        return ""
    if text == getattr(entry, "_ph_text", None):
        return ""
    return text

class InterfaceAddMaintence:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.maintenance_repo = MaintenanceRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_secondary = "#2c2c2e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 24, "bold")
        self.font_label = ("Segoe UI", 11, "bold")
        self.font_entry = ("Segoe UI", 11)
        self.font_button = ("Segoe UI", 10, "bold")

    @staticmethod
    def validate_input(P, field, max_length):
        if not P: return True
        return len(P) <= int(max_length)

    @staticmethod
    def validate_decimal(P):
        if not P: return True
        P_mod = P.replace(',', '.')
        try:
            if P_mod in (".", "-"): return True
            float(P_mod)
            return True
        except: return False

    @staticmethod
    def validate_number(P):
        return not P or P.isdigit()

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((self.parent.winfo_width()//2, 0), window=scrollable_frame, anchor="n", width=700)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="Nova Manutenção", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(pady=(30, 20))

        form_card = tk.Frame(scrollable_frame, bg=self.bg_secondary, padx=30, pady=30)
        form_card.pack(fill="x", padx=40)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_secondary, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, fieldbackground=self.bg_button, foreground=self.fg_text, borderwidth=0)
        style.configure("Placeholder.TEntry", foreground="#8e8e93")
        style.configure("TCheckbutton", background=self.bg_secondary, foreground=self.fg_text)

        v_input = self.parent.register(self.validate_input)
        v_decimal = self.parent.register(self.validate_decimal)
        v_num = self.parent.register(self.validate_number)

        fields_frame = tk.Frame(form_card, bg=self.bg_secondary)
        fields_frame.pack(fill="x")
        fields_frame.columnconfigure(1, weight=1)

        def add_row(label, row):
            ttk.Label(fields_frame, text=label).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))

        add_row("Prestador de Serviço*:", 0)
        service_provider_entry = ttk.Entry(fields_frame, validate="key", validatecommand=(v_input, "%P", "name", 50))
        service_provider_entry.grid(row=0, column=1, sticky="ew", pady=10)
        add_placeholder(service_provider_entry, "Ex.: Oficina Mecânica Central")

        add_row("Data Início*:", 1)
        d_start_f = tk.Frame(fields_frame, bg=self.bg_secondary)
        d_start_f.grid(row=1, column=1, sticky="ew", pady=10)
        start_date_entry = tk.Entry(d_start_f, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, borderwidth=0, insertbackground=self.fg_text)
        start_date_entry.pack(side="left", fill="x", expand=True, ipady=5)
        start_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(d_start_f, text="Data", command=lambda: self.open_calendar(start_date_entry), width=50, height=42, bg=self.accent, fg=self.fg_text).pack(side="left", padx=(10, 0))

        add_row("Data Fim*:", 2)
        d_end_f = tk.Frame(fields_frame, bg=self.bg_secondary)
        d_end_f.grid(row=2, column=1, sticky="ew", pady=10)
        end_date_entry = tk.Entry(d_end_f, font=self.font_entry, bg=self.bg_button, fg=self.fg_text, borderwidth=0, insertbackground=self.fg_text)
        end_date_entry.pack(side="left", fill="x", expand=True, ipady=5)
        end_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(d_end_f, text="Data", command=lambda: self.open_calendar(end_date_entry), width=50, height=42, bg=self.accent, fg=self.fg_text).pack(side="left", padx=(10, 0))

        add_row("Descrição:", 3)
        description_entry = ttk.Entry(fields_frame, validate="key", validatecommand=(v_input, "%P", "desc", 255))
        description_entry.grid(row=3, column=1, sticky="ew", pady=10)
        add_placeholder(description_entry, "Ex.: Troca de óleo e filtros")

        add_row("Valor (R$)*:", 4)
        amount_entry = ttk.Entry(fields_frame, validate="key", validatecommand=(v_decimal, "%P"))
        amount_entry.grid(row=4, column=1, sticky="ew", pady=10)
        add_placeholder(amount_entry, "0.00")

        add_row("Quilometragem*:", 5)
        km_traveled_entry = ttk.Entry(fields_frame, validate="key", validatecommand=(v_num, "%P"))
        km_traveled_entry.grid(row=5, column=1, sticky="ew", pady=10)
        add_placeholder(km_traveled_entry, "Ex.: 45000")

        add_row("Comprovante:", 6)
        rcp_f = tk.Frame(fields_frame, bg=self.bg_secondary)
        rcp_f.grid(row=6, column=1, sticky="ew", pady=10)
        receipt_path_entry = ttk.Entry(rcp_f, state="readonly")
        receipt_path_entry.pack(side="left", fill="x", expand=True)
        ListRoundedButton(rcp_f, text="Anexar", command=lambda: self.select_file(receipt_path_entry), width=80, height=32, bg=self.bg_button, fg=self.fg_text).pack(side="left", padx=(10, 0))

        add_row("Tipo:", 7)
        preventive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fields_frame, text="Manutenção Preventiva", variable=preventive_var).grid(row=7, column=1, sticky="w", pady=10)

        btns_f = tk.Frame(scrollable_frame, bg=self.bg_main)
        btns_f.pack(pady=40)

        ListRoundedButton(btns_f, text="Salvar", command=lambda: self.save_maintenance(
            service_provider_entry, start_date_entry, end_date_entry, description_entry,
            amount_entry, km_traveled_entry, receipt_path_entry, preventive_var
        ), width=180, height=45, bg=self.accent, fg=self.fg_text, font=self.font_button).pack(side="left", padx=10)

        ListRoundedButton(btns_f, text="Voltar", command=self.back, width=180, height=45, bg=self.bg_secondary, fg=self.fg_text, font=self.font_button).pack(side="left", padx=10)

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))
        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self, receipt_path_entry):
        file_path = askopenfilename(filetypes=[("Arquivos de Imagem/PDF", "*.pdf *.jpg *.jpeg *.png")])
        if file_path:
            receipt_path_entry.config(state="normal")
            receipt_path_entry.delete(0, tk.END)
            receipt_path_entry.insert(0, file_path)
            receipt_path_entry.config(state="readonly")

    def save_maintenance(self, service_provider_entry, start_date_entry, end_date_entry, description_entry,
                         amount_entry, km_traveled_entry, receipt_path_entry, preventive_var):
        service_provider = get_entry_value(service_provider_entry)
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        description = get_entry_value(description_entry)
        amount = get_entry_value(amount_entry).replace(',', '.')
        km_traveled = get_entry_value(km_traveled_entry)
        receipt_path = receipt_path_entry.get().strip()
        preventive = preventive_var.get()

        if not all([service_provider, start_date, end_date, amount, km_traveled]):
            messagebox.showerror("Atenção", "Por favor, preencha todos os campos obrigatórios (*).")
            return

        try:
            start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
            end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
            if end_date_obj < start_date_obj:
                messagebox.showerror("Erro", "A data de término não pode ser anterior ao início.")
                return

            receipt = None
            if receipt_path:
                with open(receipt_path, 'rb') as f:
                    receipt = sqlite3.Binary(f.read())

            maintenance = Maintenance(
                None, self.vehicle_id, service_provider, start_date_obj.strftime('%Y-%m-%d'),
                end_date_obj.strftime('%Y-%m-%d'), description, receipt, float(amount),
                int(preventive), int(km_traveled)
            )
            self.maintenance_repo.add(maintenance)
            messagebox.showinfo("Sucesso", "Manutenção registrada com sucesso!")
            self.back()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        InterfaceListVehicles(self.parent, self.db_path).show()