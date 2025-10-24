import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from app.repositories.refueling_repository import RefuelingRepository
from app.models.refueling import Refueling
from tkinter.filedialog import askopenfilename
import sqlite3
from app.components.custom_calendar import CustomCalendar
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.vehicle_repository import VehicleRepository


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


class InterfaceAddRefueling:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.refueling_repo = RefuelingRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

    @staticmethod
    def validate_input(P, field, max_length):
        if not P:
            return True
        max_length = int(max_length)
        clean_text = ''.join(c for c in P if c.isalnum() or c.isspace())
        return len(clean_text) <= max_length

    @staticmethod
    def validate_decimal(P):
        if not P:
            return True
        for c in P:
            if not (c.isdigit() or c in ".,"):
                return False
        P = P.replace(',', '.')
        if P.count('.') > 1:
            return False
        return True

    @staticmethod
    def validate_number(P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(
            self.parent,
            text="Cadastrar Abastecimento",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=25)

        main_frame = tk.Frame(self.parent, bg=self.bg_main, width=800)
        main_frame.pack(padx=30, pady=10, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=self.font_label, background=self.bg_main, foreground=self.fg_text)
        style.configure("TEntry", font=self.font_entry, padding=6, fieldbackground=self.bg_button,
                        foreground=self.fg_text)
        style.configure("TButton", font=self.font_button, padding=10,
                        background=self.bg_button, foreground=self.fg_text)
        style.map("TButton",
                  background=[("active", self.accent)],
                  foreground=[("active", self.fg_text)])
        style.configure("Placeholder.TEntry", foreground="#7a7a7a")

        validate_cmd = self.parent.register(InterfaceAddRefueling.validate_input)
        validate_decimal = self.parent.register(InterfaceAddRefueling.validate_decimal)
        validate_number = self.parent.register(InterfaceAddRefueling.validate_number)

        ttk.Label(main_frame, text="Preço por Litro (R$)*:").grid(row=0, column=0, sticky="e", padx=(0, 10), pady=10)
        price_per_liter_entry = ttk.Entry(main_frame, width=64, validate="key",
                                          validatecommand=(validate_decimal, "%P"))
        price_per_liter_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(price_per_liter_entry, "Ex.: 5.50")

        ttk.Label(main_frame, text="Litros*:").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=10)
        liters_entry = ttk.Entry(main_frame, width=64, validate="key",
                                 validatecommand=(validate_number, "%P"))
        liters_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(liters_entry, "Ex.: 50")

        ttk.Label(main_frame, text="Km rodado*:").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=10)
        km_traveled_entry = ttk.Entry(main_frame, width=64, validate="key",
                                      validatecommand=(validate_number, "%P"))
        km_traveled_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(km_traveled_entry, "Ex.: 10000")

        ttk.Label(main_frame, text="Posto:").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=10)
        posto_entry = ttk.Entry(main_frame, width=64, validate="key",
                                validatecommand=(validate_cmd, "%P", "posto", 100))
        posto_entry.grid(row=3, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(posto_entry, "Ex.: Posto XYZ")

        ttk.Label(main_frame, text="Tipo de Combustível*:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=10)
        fuel_type_var = tk.StringVar(value="Diesel")
        fuel_type_combobox = ttk.Combobox(main_frame, textvariable=fuel_type_var, values=[
            "Diesel",
            "Diesel S10",
            "Gasolina comum",
            "Gasolina aditivada",
            "GNV",
            "Biodiesel",
            "Elétrico",
            "Híbridos"
        ], state="readonly", width=55, font=self.font_entry)
        fuel_type_combobox.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=10)

        ttk.Label(main_frame, text="Descrição:").grid(row=5, column=0, sticky="e", padx=(0, 10), pady=10)
        description_entry = ttk.Entry(main_frame, width=64, validate="key",
                                      validatecommand=(validate_cmd, "%P", "description", 255))
        description_entry.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=10)
        add_placeholder(description_entry, "Ex.: Abastecimento noturno")

        ttk.Label(main_frame, text="Data de Abastecimento*:").grid(row=6, column=0, sticky="e", padx=(0, 10), pady=10)
        date_frame = tk.Frame(main_frame, bg=self.bg_main)
        date_frame.grid(row=6, column=1, sticky="w", padx=(0, 10), pady=10)
        refueling_date_entry = tk.Entry(date_frame, width=55, font=self.font_entry, bg=self.bg_button, fg=self.fg_text,
                                        insertbackground=self.fg_text)
        refueling_date_entry.pack(side="left", padx=5)
        refueling_date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        ListRoundedButton(date_frame, text="Selecionar Data", command=lambda: self.open_calendar(refueling_date_entry),
                          bg=self.bg_button, fg=self.fg_text, font=self.font_button).pack(side="left", padx=5)

        ttk.Label(main_frame, text="Comprovante:").grid(row=7, column=0, sticky="e", padx=(0, 10), pady=10)
        receipt_frame = tk.Frame(main_frame, bg=self.bg_main)
        receipt_frame.grid(row=7, column=1, sticky="w", padx=(0, 10), pady=10)
        receipt_path_entry = ttk.Entry(receipt_frame, width=55, state="readonly", font=self.font_entry)
        receipt_path_entry.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ListRoundedButton(receipt_frame, text="Selecionar", command=lambda: self.select_file(receipt_path_entry),
                          bg=self.bg_button, fg=self.fg_text, font=self.font_button).grid(row=0, column=1, padx=5,
                                                                                          pady=5)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ListRoundedButton(
            button_frame,
            text="Salvar",
            command=lambda: self.save_refueling(
                price_per_liter_entry, liters_entry, km_traveled_entry, posto_entry, fuel_type_combobox,
                description_entry, refueling_date_entry, receipt_path_entry
            ),
            bg=self.bg_button, fg=self.fg_text, font=self.font_button
        ).pack(side="left", padx=5)

        ListRoundedButton(
            button_frame,
            text="Voltar",
            command=self.back,
            bg=self.bg_button, fg=self.fg_text, font=self.font_button
        ).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"),
                  foreground=self.fg_text).grid(row=9, column=0, columnspan=2, pady=15)

    def open_calendar(self, date_entry):
        def callback(selected_date):
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date.strftime('%d/%m/%Y'))

        CustomCalendar(self.parent, callback=callback, initial_date=datetime.now().date())

    def select_file(self, receipt_path_entry):
        file_path = askopenfilename(filetypes=[("PDF", "*.pdf"), ("JPEG", "*.jpg"), ("PNG", "*.png")], )
        if file_path:
            receipt_path_entry.config(state="normal")
            receipt_path_entry.delete(0, tk.END)
            receipt_path_entry.insert(0, file_path)
            receipt_path_entry.config(state="readonly")

    def save_refueling(self, price_per_liter_entry, liters_entry, km_traveled_entry, posto_entry, fuel_type_combobox,
                       description_entry, refueling_date_entry, receipt_path_entry):
        price_per_liter = get_entry_value(price_per_liter_entry).replace(',', '.')
        liters = get_entry_value(liters_entry)
        km_traveled = get_entry_value(km_traveled_entry)
        posto = get_entry_value(posto_entry)
        fuel_type = fuel_type_combobox.get()
        description = get_entry_value(description_entry)
        refueling_date = refueling_date_entry.get().strip()
        receipt_path = receipt_path_entry.get().strip()

        if not all([price_per_liter, liters, km_traveled, refueling_date, fuel_type]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if len(posto) > 100:
            messagebox.showerror("Erro", "Posto deve ter no máximo 100 caracteres.")
            return
        if len(description) > 255:
            messagebox.showerror("Erro", "Descrição deve ter no máximo 255 caracteres.")
            return
        if not liters.isdigit():
            messagebox.showerror("Erro", "Litros deve ser um número válido.")
            return
        if not km_traveled.isdigit():
            messagebox.showerror("Erro", "Quilometragem deve ser um número válido.")
            return

        try:
            price_per_liter = float(price_per_liter)
            liters = int(liters)
            km_traveled = int(km_traveled)
            refueling_date_obj = datetime.strptime(refueling_date, '%d/%m/%Y')
            refueling_date_sql = refueling_date_obj.strftime('%Y-%m-%d')

            receipt = None
            if receipt_path:
                try:
                    with open(receipt_path, 'rb') as f:
                        receipt = sqlite3.Binary(f.read())
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao ler o comprovante: {str(e)}")
                    return

                refueling = Refueling(
                    None, self.vehicle_id, price_per_liter, liters, km_traveled, description, refueling_date_sql,
                    fuel_type,
                    receipt, posto
                )
                self.refueling_repo.add(refueling)
                messagebox.showinfo("Sucesso", "Abastecimento cadastrado com sucesso!")
            self.back()
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar abastecimento: {str(e)}")

    def back(self):
        from app.interface.vehicle.interface_abastecimento import InterfaceFueling
        repo = VehicleRepository(self.db_path)
        interface = InterfaceFueling(self.parent, self.db_path, self.vehicle_id, repo.get_by_id(self.vehicle_id))
        interface.show()
