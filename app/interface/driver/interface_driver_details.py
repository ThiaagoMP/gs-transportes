import tkinter as tk
from datetime import datetime
from app.components.list_rounded_button import ListRoundedButton
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_driver_repository import RouteDriverRepository
from app.repositories.trip_driver_repository import TripDriverRepository
from app.repositories.driver_bonus_repository import DriverBonusRepository

class InterfaceDriverDetails:
    def __init__(self, parent, db_path, driver_id):
        self.parent = parent
        self.db_path = db_path
        self.driver_repo = DriverRepository(self.db_path)
        self.route_repo = RouteDriverRepository(self.db_path)
        self.trip_repo = TripDriverRepository(self.db_path)
        self.bonus_repo = DriverBonusRepository(self.db_path)
        self.driver = self.driver_repo.get_by_id(driver_id)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Detalhes do Motorista",
            font=("Segoe UI", 26, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(20, 10))

        frame = tk.Frame(self.parent, bg=self.bg_main)
        frame.pack(padx=40, pady=10, fill="both", expand=True)

        start_date = self.format_date(self.driver.start_date)
        end_date = self.format_date(self.driver.end_date) if self.driver.end_date else "-"

        qtd_rotas = self.route_repo.count_routes_by_driver(self.driver.driver_id)
        qtd_viagens_total = self.trip_repo.count_trips(self.driver.driver_id, period="total")
        qtd_viagens_ano = self.trip_repo.count_trips(self.driver.driver_id, period="year")
        qtd_viagens_mes = self.trip_repo.count_trips(self.driver.driver_id, period="month")
        bonus_total = self.bonus_repo.sum_bonus(self.driver.driver_id, period="total")
        bonus_ano = self.bonus_repo.sum_bonus(self.driver.driver_id, period="year")
        bonus_mes = self.bonus_repo.sum_bonus(self.driver.driver_id, period="month")

        detalhes = {
            "Nome": self.driver.name,
            "Salário (R$)": f"{self.driver.salary:.2f}",
            "Contato": self.driver.contact,
            "Data Contratado": start_date,
            "Data Demitido": end_date,
            "CPF": self.driver.cpf,
            "RG": self.driver.rg,
            "CNH": self.driver.cnh,
            "Informações Extras": self.driver.extra_info or "-",
            "Quantidade de linhas trabalhadas": str(qtd_rotas),
            "Quantidade de viagens feitas (Total)": str(qtd_viagens_total),
            "Quantidade de viagens feitas (Ano)": str(qtd_viagens_ano),
            "Quantidade de viagens feitas (Mês)": str(qtd_viagens_mes),
            "Bonificações recebidas (Total)": str(bonus_total),
            "Bonificações recebidas (Ano)": str(bonus_ano),
            "Bonificações recebidas (Mês)": str(bonus_mes),
        }

        for i, (label_text, value_text) in enumerate(detalhes.items()):
            tk.Label(
                frame,
                text=label_text + ":",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_main,
                fg=self.fg_text
            ).grid(row=i, column=0, sticky="e", padx=(10, 10), pady=5)

            if label_text == "Informações Extras":
                txt = tk.Text(frame, height=5, width=50, bg=self.bg_button, fg=self.fg_text, wrap="word")
                txt.insert("1.0", value_text)
                txt.config(state="disabled")
                txt.grid(row=i, column=1, sticky="w", pady=5, padx=5)
            else:
                tk.Label(
                    frame,
                    text=value_text,
                    font=("Segoe UI", 12),
                    bg=self.bg_button,
                    fg=self.fg_text,
                    anchor="w",
                    width=40,
                    padx=8,
                    pady=4
                ).grid(row=i, column=1, sticky="w", pady=5)

        btn_voltar = ListRoundedButton(
            self.parent,
            text="Voltar",
            command=self.voltar,
            width=200,
            height=50,
            bg=self.bg_button,
            fg=self.fg_text,
            hover_bg=self.accent,
            font=("Segoe UI", 11, "bold")
        )
        btn_voltar.pack(pady=20)

    def format_date(self, date_value):
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                return date_value
        return str(date_value)

    def voltar(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        interface = InterfaceListDrivers(self.parent, self.db_path)
        interface.show()
