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
        self.bg_card = "#2c2c2e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        canvas = tk.Canvas(self.parent, bg=self.bg_main, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_main)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.parent.winfo_width())

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.parent.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(
            scrollable_frame,
            text="RELATORIO DO MOTORISTA",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(15, 10))

        content_container = tk.Frame(scrollable_frame, bg=self.bg_main)
        content_container.pack(fill="both", expand=True, padx=30)

        left_column = tk.Frame(content_container, bg=self.bg_main)
        left_column.pack(side="left", fill="both", expand=True, padx=10)

        right_column = tk.Frame(content_container, bg=self.bg_main)
        right_column.pack(side="left", fill="both", expand=True, padx=10)

        start_date = self.format_date(self.driver.start_date)
        end_date = self.format_date(self.driver.end_date) if self.driver.end_date else "ATIVO"

        qtd_rotas = self.route_repo.count_routes_by_driver(self.driver.driver_id)
        qtd_viagens_total = self.trip_repo.count_trips(self.driver.driver_id, period="total")
        qtd_viagens_ano = self.trip_repo.count_trips(self.driver.driver_id, period="year")
        qtd_viagens_mes = self.trip_repo.count_trips(self.driver.driver_id, period="month")

        bonus_total = self.bonus_repo.sum_bonus(self.driver.driver_id, period="total")
        bonus_ano = self.bonus_repo.sum_bonus(self.driver.driver_id, period="year")
        bonus_mes = self.bonus_repo.sum_bonus(self.driver.driver_id, period="month")

        dados_pessoais = {
            "Nome": self.driver.name,
            "CPF": self.driver.cpf,
            "RG": self.driver.rg,
            "CNH": self.driver.cnh,
            "Contato": self.driver.contact,
            "Salário (R$)": f"{self.driver.salary:.2f}",
            "Admissão": start_date,
            "Status": end_date
        }

        estatisticas = {
            "ROTAS": str(qtd_rotas),
            "TOTAL VIAGENS": str(qtd_viagens_total),
            "VIAGENS (ANO)": str(qtd_viagens_ano),
            "VIAGENS (MES)": str(qtd_viagens_mes),
            "BONUS (TOTAL)": f"R$ {float(bonus_total or 0):.2f}",
            "BONUS (ANO)": f"R$ {float(bonus_ano or 0):.2f}",
            "BONUS (MES)": f"R$ {float(bonus_mes or 0):.2f}"
        }

        self._render_section(left_column, "DADOS CADASTRAIS", dados_pessoais)
        self._render_section(right_column, "DESEMPENHO", estatisticas)

        extra_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        extra_frame.pack(fill="x", padx=40, pady=10)

        tk.Label(
            extra_frame, text="OBSERVACOES:",
            font=("Segoe UI", 10, "bold"), bg=self.bg_main, fg="#aaaaaa"
        ).pack(anchor="w")

        txt_extra = tk.Text(
            extra_frame, height=3, font=("Segoe UI", 10),
            bg=self.bg_card, fg=self.fg_text, relief="flat", padx=10, pady=10
        )
        txt_extra.insert("1.0", self.driver.extra_info or "SEM OBSERVACOES")
        txt_extra.config(state="disabled")
        txt_extra.pack(fill="x", pady=5)

        btn_frame = tk.Frame(scrollable_frame, bg=self.bg_main)
        btn_frame.pack(pady=(10, 20))

        ListRoundedButton(
            btn_frame,
            text="Voltar para lista",
            command=self.voltar,
            width=200,
            height=40,
            bg=self.bg_button,
            fg=self.fg_text
        ).pack()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _render_section(self, parent_frame, title, data_dict):
        tk.Label(
            parent_frame, text=title, font=("Segoe UI", 11, "bold"),
            bg=self.bg_main, fg=self.accent
        ).pack(anchor="w", pady=(5, 10))

        for label, value in data_dict.items():
            row = tk.Frame(parent_frame, bg=self.bg_main)
            row.pack(fill="x", pady=2)

            tk.Label(
                row, text=f"{label}:", font=("Segoe UI", 9, "bold"),
                bg=self.bg_main, fg="#aaaaaa", width=15, anchor="w"
            ).pack(side="left")

            tk.Label(
                row, text=value, font=("Segoe UI", 9),
                bg=self.bg_main, fg=self.fg_text, anchor="w"
            ).pack(side="left", fill="x")

    def format_date(self, date_value):
        if isinstance(date_value, str) and "-" in date_value:
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                return date_value
        return str(date_value)

    def voltar(self):
        self.parent.unbind_all("<MouseWheel>")
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        InterfaceListDrivers(self.parent, self.db_path).show()