import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import StrMethodFormatter
from typing import Sequence


class ReportGraphics:
    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self._apply_theme()

    def _apply_theme(self):
        if self.theme.lower() == "dark":
            plt.style.use("dark_background")
            self.bg_figure = "#1c1c1e"
            self.color_primary = "#ff7f32"
            self.color_success = "#8adf8a"
            self.color_danger = "#ff8a8a"
            self.color_info = "#74b9ff"
            self.text_color = "white"
            self.pie_text_color = "black"
        else:
            plt.style.use("default")
            self.bg_figure = "white"
            self.color_primary = "#ff7f32"
            self.color_success = "#2ecc71"
            self.color_danger = "#e74c3c"
            self.color_info = "#3498db"
            self.text_color = "black"
            self.pie_text_color = "black"

    def _apply_currency_formatter(self, ax, decimal_places: int = 0):
        if decimal_places == 0:
            formatter = StrMethodFormatter("R$ {x:,.0f}")
        else:
            formatter = StrMethodFormatter("R$ {x:,.2f}")
        ax.yaxis.set_major_formatter(formatter)

    def _style_axis(self, ax):
        ax.set_facecolor(self.bg_figure)
        ax.title.set_color(self.text_color)
        ax.xaxis.label.set_color(self.text_color)
        ax.yaxis.label.set_color(self.text_color)
        ax.tick_params(colors=self.text_color)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.text_color)

    def bar_monthly_profit(self, lucros_por_mes: dict[str, float]):
        if not lucros_por_mes:
            print("Nenhum lucro recebido.")
            return None

        import numpy as np
        import matplotlib.pyplot as plt

        meses = []
        profits = []

        for mes, valor in lucros_por_mes.items():
            try:
                v = float(valor)
                if np.isnan(v):
                    v = 0
            except:
                v = 0

            meses.append(mes)
            profits.append(v)

        meses, profits = zip(*sorted(zip(meses, profits), key=lambda x: x[0]))
        profits = list(profits)

        cores = ["green" if p >= 0 else "red" for p in profits]

        if len(meses) == 1:
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor(self.bg_figure)
            ax.set_facecolor(self.bg_figure)

            ax.bar([0], [profits[0]], width=0.25, color=cores)

            ax.set_xticks([0])
            ax.set_xticklabels([meses[0]], color=self.text_color)
            ax.set_xlim(-0.7, 0.7)

            ax.axhline(0, color=self.text_color, linewidth=1.6)

            ax.set_title(f"Lucro — {meses[0]}", color=self.text_color)
            ax.set_ylabel("Lucro (R$)", color=self.text_color)

            self._apply_currency_formatter(ax, decimal_places=2)
            ax.tick_params(colors=self.text_color)

            for spine in ax.spines.values():
                spine.set_edgecolor(self.text_color)

            plt.tight_layout()
            return fig

        n = len(meses)
        fig_width = max(6, min(18, n * 0.75))
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        x = np.arange(n)
        bar_width = 0.35

        ax.bar(x, profits, width=bar_width, color=cores, edgecolor="black", linewidth=0.6)

        ax.set_xticks(x)
        ax.set_xticklabels(
            meses,
            rotation=45,
            ha="right",
            color=self.text_color
        )

        ax.axhline(0, color=self.text_color, linewidth=1.8)

        ax.set_title("Lucro Mensal", color=self.text_color)
        ax.set_ylabel("Lucro (R$)", color=self.text_color)
        ax.set_xlabel("Mês", color=self.text_color)

        self._apply_currency_formatter(ax, decimal_places=2)

        ax.tick_params(colors=self.text_color)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.text_color)

        ax.grid(axis="y", linestyle="--", alpha=0.35)

        plt.tight_layout()
        return fig

    def plot_revenue_by_route_pie(self, receita_por_linha: dict[str, float]) -> Figure | None:
        if not receita_por_linha:
            return None

        dados = [(k, v) for k, v in receita_por_linha.items() if v and v > 0]
        if not dados:
            return None

        labels, valores = zip(*dados)
        fig = Figure(figsize=(6, 6), facecolor=self.bg_figure)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            textprops={"color": self.text_color},
            startangle=90,
            wedgeprops={"edgecolor": self.bg_figure},
        )

        for autotext in autotexts:
            autotext.set_color(self.pie_text_color)

        ax.set_title("Participação da Receita por Linha", color=self.text_color)
        ax.axis("equal")
        fig.tight_layout()
        return fig

    def bar_consumo_combustivel(self, veiculos: Sequence[str], km_por_litro: Sequence[float]) -> Figure | None:
        if not veiculos or not km_por_litro:
            return None

        if len(veiculos) == 1:
            fig, ax = plt.subplots(figsize=(4, 4))
            width = 0.35
        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            width = 0.6 if len(veiculos) < 6 else 0.45

        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)
        ax.bar(veiculos, km_por_litro, width=width, color=self.color_primary)

        ax.set_title("Consumo de Combustível (Km/L por Veículo)", color=self.text_color)
        ax.set_ylabel("Km/L", color=self.text_color)
        ax.set_xlabel("Veículos", color=self.text_color)

        ax.tick_params(axis='x', rotation=45 if len(veiculos) > 3 else 0, colors=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color)
        self._style_axis(ax)
        plt.tight_layout()
        return fig

    def bar_custo_por_km(self, veiculos: Sequence[str], custo_por_km: Sequence[float]) -> Figure | None:
        if not veiculos or not custo_por_km:
            return None

        if len(veiculos) == 1:
            fig, ax = plt.subplots(figsize=(4, 4))
            width = 0.35
        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            width = 0.6 if len(veiculos) < 6 else 0.45

        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)
        ax.bar(veiculos, custo_por_km, width=width, color=self.color_danger)

        ax.set_title("Custo Total por KM (Combustível + Manutenção)", color=self.text_color)
        ax.set_ylabel("R$ por KM", color=self.text_color)
        ax.set_xlabel("Veículos", color=self.text_color)
        ax.tick_params(axis='x', rotation=45 if len(veiculos) > 3 else 0, colors=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color)

        ax.yaxis.set_major_formatter(StrMethodFormatter("R$ {x:,.2f}"))
        self._style_axis(ax)
        plt.tight_layout()
        return fig

    def bar_lucro_por_veiculo(self, vehicle_names: Sequence[str], valores: Sequence[float]) -> Figure | None:
        if not vehicle_names or not valores:
            return None

        if len(vehicle_names) == 1:
            fig, ax = plt.subplots(figsize=(5, 4))
            width = 0.4
        else:
            fig, ax = plt.subplots(figsize=(10, 5))
            width = 0.6 if len(vehicle_names) < 8 else 0.45

        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        cores = [self.color_success if v >= 0 else self.color_danger for v in valores]
        ax.bar(vehicle_names, valores, width=width, color=cores)

        ax.set_title("Lucro por Veículo", color=self.text_color)
        ax.set_xlabel("Veículo", color=self.text_color)
        ax.set_ylabel("Lucro (R$)", color=self.text_color)

        ax.tick_params(axis='x', rotation=45 if len(vehicle_names) > 5 else 0, colors=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color)
        self._apply_currency_formatter(ax, decimal_places=2)
        self._style_axis(ax)
        plt.tight_layout()
        return fig

    def bar_lucro_por_motorista(self, motoristas: Sequence[str], lucro: Sequence[float]) -> Figure | None:
        if not motoristas or not lucro:
            return None

        if len(motoristas) == 1:
            fig, ax = plt.subplots(figsize=(5, 4))
            width = 0.4
        else:
            fig, ax = plt.subplots(figsize=(9, 5))
            width = 0.6 if len(motoristas) < 8 else 0.45

        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        cores = [self.color_success if v >= 0 else self.color_danger for v in lucro]
        ax.bar(motoristas, lucro, width=width, color=cores)

        ax.set_title("Lucro por Motorista", color=self.text_color)
        ax.set_ylabel("R$", color=self.text_color)
        ax.set_xlabel("Motoristas", color=self.text_color)

        ax.tick_params(axis='x', rotation=45 if len(motoristas) > 5 else 0, colors=self.text_color)
        ax.tick_params(axis='y', colors=self.text_color)
        self._apply_currency_formatter(ax, decimal_places=2)
        self._style_axis(ax)
        plt.tight_layout()
        return fig

    def pie_lucro_por_veiculo(self, lucro_por_veiculo: dict[str, float]) -> Figure | None:
        if not lucro_por_veiculo:
            return None

        dados = [(k, v) for k, v in lucro_por_veiculo.items() if v and v > 0]
        if not dados:
            return None

        labels, valores = zip(*dados)
        fig = Figure(figsize=(6, 6), facecolor=self.bg_figure)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            textprops={"color": self.text_color},
            startangle=90,
            wedgeprops={"edgecolor": self.bg_figure},
        )

        for autotext in autotexts:
            autotext.set_color(self.pie_text_color)

        ax.set_title("Participação no Lucro Total por Veículo", color=self.text_color)
        ax.axis("equal")
        fig.tight_layout()
        return fig
