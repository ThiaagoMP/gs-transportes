import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
from app.components.list_rounded_button import ListRoundedButton

class InterfaceRelatorio:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_options = self.load_vehicle_options()
        self.route_options = self.load_route_options()
        self.driver_options = self.load_driver_options()

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_label = ("Segoe UI", 18, "bold")
        self.font_button = ("Segoe UI", 18, "bold")
        self.font_title = ("Segoe UI", 36, "bold")
        self.font_tree = ("Segoe UI", 14)

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(fill="both", expand=True, padx=50, pady=40)

        title_label = tk.Label(main_frame, text="Relatórios", font=self.font_title,
                               bg=self.bg_main, fg=self.accent, anchor="w")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky="w")

        filter_frame = tk.Frame(main_frame, bg=self.bg_main, bd=2, relief="solid")
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        label_style = {"bg": self.bg_main, "fg": self.fg_text, "font": self.font_label}

        tk.Label(filter_frame, text="Selecione o Veículo:", **label_style).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.vehicle_combobox = ttk.Combobox(filter_frame, values=self.vehicle_options, width=50, state="readonly",
                                             font=("Segoe UI", 14))
        self.vehicle_combobox.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        self.vehicle_combobox.set("Todos" if self.vehicle_options else "")

        tk.Label(filter_frame, text="Selecione a Linha:", **label_style).grid(row=1, column=0, padx=15, pady=15, sticky="w")
        self.route_combobox = ttk.Combobox(filter_frame, values=self.route_options, width=50, state="readonly",
                                           font=("Segoe UI", 14))
        self.route_combobox.grid(row=1, column=1, padx=15, pady=15, sticky="w")
        self.route_combobox.set("Todos" if self.route_options else "")

        tk.Label(filter_frame, text="Selecione o Motorista:", **label_style).grid(row=2, column=0, padx=15, pady=15, sticky="w")
        self.driver_combobox = ttk.Combobox(filter_frame, values=self.driver_options, width=50, state="readonly",
                                            font=("Segoe UI", 14))
        self.driver_combobox.grid(row=2, column=1, padx=15, pady=15, sticky="w")
        self.driver_combobox.set("Todos" if self.driver_options else "")

        date_frame = tk.Frame(filter_frame, bg=self.bg_main)
        date_frame.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky="w")
        tk.Label(date_frame, text="De:", **label_style).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.start_date = DateEntry(date_frame, width=25, background=self.accent, foreground=self.fg_text,
                                    borderwidth=2, date_pattern="dd/mm/yyyy", font=("Segoe UI", 14))
        self.start_date.grid(row=0, column=1, padx=15, pady=10, sticky="w")
        self.start_date.set_date(datetime.now().strftime('%d/%m/%Y'))

        tk.Label(date_frame, text="Até:", **label_style).grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.end_date = DateEntry(date_frame, width=25, background=self.accent, foreground=self.fg_text,
                                  borderwidth=2, date_pattern="dd/mm/yyyy", font=("Segoe UI", 14))
        self.end_date.grid(row=0, column=3, padx=15, pady=10, sticky="w")
        self.end_date.set_date(datetime.now().strftime('%d/%m/%Y'))

        ListRoundedButton(filter_frame, text="Gerar Relatório", command=self.generate_report,
                          bg=self.bg_button, fg=self.fg_text, hover_bg=self.accent,
                          width=350, height=65, font=self.font_button).grid(row=4, column=0, columnspan=2, padx=20, pady=25)

        self.result_frame = tk.Frame(main_frame, bg=self.bg_main, bd=2, relief="solid")
        self.result_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=self.font_tree, rowheight=35, background=self.bg_button,
                        fieldbackground=self.bg_button, foreground=self.fg_text)
        style.configure("Treeview.Heading", font=("Segoe UI", 16, "bold"),
                        background=self.accent, foreground=self.fg_text)

    def load_vehicle_options(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT license_plate FROM Vehicle")
                plates = [row[0] for row in cursor.fetchall()]
                return ["Todos"] + plates if plates else ["Nenhum veículo cadastrado"]
        except sqlite3.Error as e:
            print(f"Erro ao carregar veículos: {str(e)}")
            return ["Erro ao carregar veículos"]

    def load_route_options(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Name FROM Route")
                routes = [row[0] for row in cursor.fetchall()]
                return ["Todos"] + routes if routes else ["Nenhuma linha cadastrada"]
        except sqlite3.Error as e:
            print(f"Erro ao carregar linhas: {str(e)}")
            return ["Erro ao carregar linhas"]

    def load_driver_options(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Name FROM Driver")
                drivers = [row[0] for row in cursor.fetchall()]
                return ["Todos"] + drivers if drivers else ["Nenhum motorista cadastrado"]
        except sqlite3.Error as e:
            print(f"Erro ao carregar motoristas: {str(e)}")
            return ["Erro ao carregar motoristas"]

    def generate_report(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                start_date = self.start_date.get().replace('/', '-')
                end_date = self.end_date.get().replace('/', '-')

                vehicle_plate = self.vehicle_combobox.get()
                route_name = self.route_combobox.get()
                driver_name = self.driver_combobox.get()

                query = """
                    SELECT m.StartDate, v.LicensePlate, m.Description, m.Amount, m.Preventive
                    FROM Maintenance m
                    JOIN Vehicle v ON m.VehicleID = v.VehicleID
                    LEFT JOIN Route r ON r.VehicleID = v.VehicleID
                    LEFT JOIN TripDriver td ON td.TripID IN (SELECT TripID FROM Trip WHERE VehicleID = v.VehicleID)
                    LEFT JOIN Driver d ON d.DriverID = td.DriverID
                    WHERE m.StartDate BETWEEN ? AND ?
                """
                params = [start_date, end_date]

                if vehicle_plate != "Todos":
                    query += " AND v.LicensePlate = ?"
                    params.append(vehicle_plate)
                if route_name != "Todos":
                    query += " AND r.Name = ?"
                    params.append(route_name)
                if driver_name != "Todos":
                    query += " AND d.Name = ?"
                    params.append(driver_name)

                cursor.execute(query, params)
                maintenances = cursor.fetchall()

                if not maintenances:
                    tk.Label(self.result_frame, text="Nenhum registro encontrado.", font=("Segoe UI", 12),
                             bg=self.bg_main, fg=self.fg_text).pack(pady=10)
                    return

                tree = ttk.Treeview(self.result_frame,
                                    columns=("Data", "Placa", "Descrição", "Valor (R$)", "Preventiva"),
                                    show="headings", height=10)
                tree.heading("Data", text="Data")
                tree.heading("Placa", text="Placa")
                tree.heading("Descrição", text="Descrição")
                tree.heading("Valor (R$)", text="Valor (R$)")
                tree.heading("Preventiva", text="Preventiva")
                tree.column("Data", width=120)
                tree.column("Placa", width=120)
                tree.column("Descrição", width=250)
                tree.column("Valor (R$)", width=120)
                tree.column("Preventiva", width=100)
                tree.pack(fill="both", expand=True)

                total_cost = 0
                for maint in maintenances:
                    date, plate, desc, amount, preventive = maint
                    tree.insert("", "end", values=(date, plate, desc, f"{amount:.2f}", "Sim" if preventive else "Não"))
                    total_cost += amount

                tk.Label(self.result_frame, text=f"Total de Custos: R$ {total_cost:.2f}",
                         font=("Segoe UI", 12, "bold"), bg=self.bg_main, fg=self.fg_text).pack(pady=15)

        except sqlite3.Error as e:
            tk.Label(self.result_frame, text=f"Erro ao gerar relatório: {str(e)}",
                     font=("Segoe UI", 12), fg="red", bg=self.bg_main).pack(pady=10)
        except Exception as e:
            tk.Label(self.result_frame, text=f"Erro inesperado: {str(e)}",
                     font=("Segoe UI", 12), fg="red", bg=self.bg_main).pack(pady=10)
