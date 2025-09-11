import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from app.repositories.trip_repository import TripRepository
from app.models.trip import Trip

class InterfaceCadastrarViagem:
    def __init__(self, parent, db_path, vehicle_id):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.trip_repo = TripRepository(self.db_path)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        tk.Label(self.parent, text="Cadastrar Viagem", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#1976d2").pack(pady=25)

        main_frame = tk.Frame(self.parent, bg="#ffffff")
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 14), background="#ffffff")
        style.configure("TEntry", font=("Segoe UI", 12), padding=6)
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")], foreground=[("active", "#ffffff")])
        style.configure("my.DateEntry", fieldbackground="#e0e0e0", background="#1976d2", foreground="#ffffff")

        # Campos
        ttk.Label(main_frame, text="Despesas Adicionais (R$)*:").grid(row=0, column=0, sticky="e", padx=15, pady=15)
        additional_expenses_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        additional_expenses_entry.grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Quilometragem Total (km)*:").grid(row=1, column=0, sticky="e", padx=15, pady=15)
        total_km_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_number), "%P"))
        total_km_entry.grid(row=1, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Tarifa por Passageiro (R$)*:").grid(row=2, column=0, sticky="e", padx=15, pady=15)
        passenger_fare_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_decimal), "%P"))
        passenger_fare_entry.grid(row=2, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Quantidade de Passageiros*:").grid(row=3, column=0, sticky="e", padx=15, pady=15)
        passenger_count_entry = ttk.Entry(main_frame, width=45, validate="key", validatecommand=(self.parent.register(self.validate_number), "%P"))
        passenger_count_entry.grid(row=3, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Data de Início*:").grid(row=4, column=0, sticky="e", padx=15, pady=15)
        start_date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        start_date_entry.grid(row=4, column=1, padx=15, pady=15)
        start_date_entry.set_date(datetime.now().strftime('%d/%m/%Y'))  # 09/09/2025

        ttk.Label(main_frame, text="Data de Fim*:").grid(row=5, column=0, sticky="e", padx=15, pady=15)
        end_date_entry = DateEntry(main_frame, width=43, date_pattern="dd/mm/yyyy", style="my.DateEntry")
        end_date_entry.grid(row=5, column=1, padx=15, pady=15)

        ttk.Label(main_frame, text="Descrição:").grid(row=6, column=0, sticky="e", padx=15, pady=15)
        description_entry = ttk.Entry(main_frame, width=45)
        description_entry.grid(row=6, column=1, padx=15, pady=15)

        # Botões
        button_frame = tk.Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Salvar", style="TButton", command=lambda: self.save_trip(
            additional_expenses_entry, total_km_entry, passenger_fare_entry, passenger_count_entry,
            start_date_entry, end_date_entry, description_entry
        )).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Voltar", style="TButton", command=self.back).pack(side="left", padx=5)

    def validate_number(self, P):
        if not P:
            return True
        return all(c.isdigit() for c in P)

    def validate_decimal(self, P):
        if not P:
            return True
        for c in P:
            if not (c.isdigit() or c in ".,"):
                return False
        P = P.replace(',', '.')
        if P.count('.') > 1:
            return False
        return True

    def save_trip(self, additional_expenses_entry, total_km_entry, passenger_fare_entry, passenger_count_entry,
                  start_date_entry, end_date_entry, description_entry):
        additional_expenses = float(additional_expenses_entry.get().replace(',', '.') or 0.0)
        total_km = float(total_km_entry.get() or 0.0)
        passenger_fare = float(passenger_fare_entry.get().replace(',', '.') or 0.0)
        passenger_count = int(passenger_count_entry.get() or 0)
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        description = description_entry.get().strip()

        if not all([total_km, passenger_fare, passenger_count, start_date, end_date]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
            end_date_obj = datetime.strptime(end_date, '%d/%m/%Y')
            start_date_sql = start_date_obj.strftime('%Y-%m-%d')
            end_date_sql = end_date_obj.strftime('%Y-%m-%d')

            trip = Trip(None, self.vehicle_id, additional_expenses, total_km, passenger_fare, passenger_count, start_date_sql, end_date_sql, description)
            trip_id = self.trip_repo.add(trip)
            if trip_id:
                messagebox.showinfo("Sucesso", f"Viagem cadastrada com ID {trip_id}!")
                self.back()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar a viagem.")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceVeiculo
        interface = InterfaceVeiculo(self.parent, self.db_path)
        interface.show()