import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime
import numpy as np
from matplotlib.ticker import StrMethodFormatter
from collections import defaultdict  # Garantindo importação para auxiliar, se necessário


class ReportGraphics:
    def __init__(self, theme="dark"):
        self.theme = theme
        self._apply_theme()

    def _apply_theme(self):
        if self.theme.lower() == "dark":
            plt.style.use("dark_background")
            self.bg_figure = "#1c1c1e"
            self.color_primary = "#ff7f32"
            self.color_secondary = "#ffffff"
            self.text_color_dark_bg = "white"
            self.text_color_pie = "black"
        else:
            plt.style.use("default")
            self.bg_figure = "white"
            self.color_primary = "#ff7f32"
            self.color_secondary = "#000000"
            self.text_color_dark_bg = "black"
            self.text_color_pie = "black"

    # Função auxiliar para aplicar formatação R$ no eixo Y
    def _apply_currency_formatter(self, ax, decimal_places=0):
        if decimal_places == 0:
            formatter = StrMethodFormatter("R$ {x:,.0f}")
        else:
            formatter = StrMethodFormatter("R$ {x:,.2f}")
        ax.yaxis.set_major_formatter(formatter)

    # ======================================================
    # NOVO: Fluxo Financeiro Mensal (Barras Agrupadas)
    # ======================================================
    def bar_financial_flow_monthly(self, pagamentos_alunos, extras_linha, despesas, lucros):
        """
        Gráfico de barras agrupadas: Faturamento, Despesas e Lucro Líquido por mês.
        O faturamento é a soma de Pagamentos Alunos + Extras Linha.
        """
        # 1. Obter e ordenar todos os meses únicos
        meses_set = set(pagamentos_alunos.keys()) | set(extras_linha.keys()) | set(despesas.keys()) | set(lucros.keys())
        meses = sorted(list(meses_set))
        if not meses: return None

        # 2. Mapear valores e calcular Faturamento Total
        faturamento_total = []
        despesas_vals = []
        lucros_vals = []

        for mes in meses:
            fat_aluno = pagamentos_alunos.get(mes, 0)
            fat_extra = extras_linha.get(mes, 0)
            faturamento_total.append(fat_aluno + fat_extra)
            despesas_vals.append(despesas.get(mes, 0))
            lucros_vals.append(lucros.get(mes, 0))

        # 3. Preparar gráfico
        x = np.arange(len(meses))  # Localizações para as barras
        width = 0.25  # Largura de cada barra

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor(self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        # Plotar as barras
        rects1 = ax.bar(x - width, faturamento_total, width, label='Faturamento Total', color='#8adf8a')  # Verde
        rects2 = ax.bar(x, despesas_vals, width, label='Despesas', color='#ff8a8a')  # Vermelho
        rects3 = ax.bar(x + width, lucros_vals, width, label='Lucro Líquido', color='#74b9ff')  # Azul

        # Configurações do eixo
        ax.set_title("Fluxo Financeiro Mensal: Faturamento vs. Despesas vs. Lucro", color=self.text_color_dark_bg)
        ax.set_ylabel("Valor (R$)", color=self.text_color_dark_bg)
        ax.set_xlabel("Mês", color=self.text_color_dark_bg)
        ax.set_xticks(x)
        ax.set_xticklabels(meses, rotation=45, ha="right")

        # Estilização
        ax.legend(facecolor=self.bg_figure, edgecolor=self.text_color_dark_bg, labelcolor=self.text_color_dark_bg)
        ax.tick_params(colors=self.text_color_dark_bg)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.text_color_dark_bg)

        self._apply_currency_formatter(ax)

        plt.tight_layout()
        return fig

    # ======================================================
    # Gráficos Antigos REMOVIDOS (plot_expenses_monthly, plot_profit_monthly, plot_revenue_monthly)
    # ======================================================

    def plot_revenue_by_route_pie(self, receita_por_linha: dict):
        """
        Gráfico de pizza: Participação de cada linha na receita total.
        """
        if not receita_por_linha:
            return None

        labels = list(receita_por_linha.keys())
        valores = list(receita_por_linha.values())

        dados = [(l, v) for l, v in zip(labels, valores) if v > 0]
        if not dados: return None
        labels, valores = zip(*dados)

        fig = Figure(figsize=(6, 6), facecolor=self.bg_figure)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(valores, labels=labels, autopct="%1.1f%%",
                                          textprops={"color": self.text_color_dark_bg},
                                          startangle=90, wedgeprops={"edgecolor": self.bg_figure})

        # Cor das porcentagens como preto
        for autotext in autotexts:
            autotext.set_color(self.text_color_pie)

        ax.set_title("Participação da Receita por Linha", color=self.text_color_dark_bg)
        ax.axis('equal')
        fig.tight_layout()
        return fig

    # ======================================================
    # 1) Consumo de Combustível (Km/L por Veículo)
    # ======================================================
    def bar_consumo_combustivel(self, veiculos, km_por_litro):
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=self.bg_figure)
        ax.set_facecolor(self.bg_figure)
        ax.bar(veiculos, km_por_litro, color=self.color_primary)
        ax.set_title("Consumo de Combustível (Km/L por Veículo)", color=self.color_secondary)
        ax.set_ylabel("Km/L", color=self.color_secondary)
        ax.set_xlabel("Veículos", color=self.color_secondary)
        ax.tick_params(axis='x', colors=self.color_secondary)
        ax.tick_params(axis='y', colors=self.color_secondary)
        plt.tight_layout()
        return fig

    # ======================================================
    # 2) Custo por KM (Combustível + Manutenção)
    # ======================================================
    def bar_custo_por_km(self, veiculos, custo_por_km):
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=self.bg_figure)
        ax.set_facecolor(self.bg_figure)
        ax.bar(veiculos, custo_por_km, color='#ff8a8a')
        ax.set_title("Custo Total por KM (Combustível + Manutenção)", color=self.color_secondary)
        ax.set_ylabel("R$ por KM", color=self.color_secondary)
        ax.set_xlabel("Veículos", color=self.color_secondary)
        ax.tick_params(axis='x', colors=self.color_secondary)
        ax.tick_params(axis='y', colors=self.color_secondary)
        formatter = StrMethodFormatter("R$ {x:,.2f}")
        ax.yaxis.set_major_formatter(formatter)
        plt.tight_layout()
        return fig

    # ======================================================
    # 3) Lucro por Veículo (Barra)
    # ======================================================
    def bar_lucro_por_veiculo(self, vehicle_names, valores):
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        cores = ['#8adf8a' if v >= 0 else '#ff8a8a' for v in valores]
        ax.bar(vehicle_names, valores, color=cores)

        ax.set_title("Lucro por Veículo", fontsize=14, color=self.text_color_dark_bg)
        ax.set_xlabel("Veículo", color=self.text_color_dark_bg)
        ax.set_ylabel("Lucro (R$)", color=self.text_color_dark_bg)

        ax.tick_params(colors=self.text_color_dark_bg)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.text_color_dark_bg)

        self._apply_currency_formatter(ax)

        plt.tight_layout()
        return fig

    # ======================================================
    # 4) Lucro por Motorista (Barra)
    # ======================================================
    def bar_lucro_por_motorista(self, motoristas, lucro):
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=self.bg_figure)
        ax.set_facecolor(self.bg_figure)

        cores = ['#8adf8a' if v >= 0 else '#ff8a8a' for v in lucro]
        ax.bar(motoristas, lucro, color=cores)

        ax.set_title("Lucro por Motorista", color=self.color_secondary)
        ax.set_ylabel("R$", color=self.color_secondary)
        ax.set_xlabel("Motoristas", color=self.color_secondary)
        ax.tick_params(axis='x', colors=self.color_secondary)
        ax.tick_params(axis='y', colors=self.color_secondary)
        self._apply_currency_formatter(ax)

        plt.tight_layout()
        return fig

    # ======================================================
    # 5) Recebimento Total por Aluno (Barra)
    # ======================================================
    def bar_recebimentos_por_aluno(self, alunos, valores):
        fig, ax = plt.subplots(figsize=(9, 5), facecolor=self.bg_figure)
        ax.set_facecolor(self.bg_figure)
        ax.bar(alunos, valores, color=self.color_primary)

        ax.set_title("Recebimentos por Aluno", color=self.color_secondary)
        ax.set_ylabel("R$", color=self.color_secondary)
        ax.set_xlabel("Alunos", color=self.color_secondary)
        ax.tick_params(axis='x', colors=self.color_secondary, rotation=30)
        ax.tick_params(axis='y', colors=self.color_secondary)
        self._apply_currency_formatter(ax)

        plt.tight_layout()
        return fig

    # ======================================================
    # 6) Gastos (Manutenção + Abastecimento) por Veículo (Pizza)
    # ======================================================
    def pie_gastos_por_veiculo(self, gastos_por_veiculo: dict):
        if not gastos_por_veiculo:
            return None

        labels = list(gastos_por_veiculo.keys())
        valores = list(gastos_por_veiculo.values())

        dados = [(l, v) for l, v in zip(labels, valores) if v > 0]
        if not dados: return None
        labels, valores = zip(*dados)

        fig = Figure(figsize=(6, 6), facecolor=self.bg_figure)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(valores, labels=labels, autopct="%1.1f%%",
                                          textprops={"color": self.text_color_dark_bg},
                                          startangle=90, wedgeprops={"edgecolor": self.bg_figure})

        for autotext in autotexts:
            autotext.set_color(self.text_color_pie)

        ax.set_title("Participação nos Gastos por Veículo", color=self.text_color_dark_bg)
        ax.axis('equal')
        fig.tight_layout()
        return fig

    # ======================================================
    # 7) Lucro Total por Veículo (Pizza)
    # ======================================================
    def pie_lucro_por_veiculo(self, lucro_por_veiculo: dict):
        lucro_positivo = {k: v for k, v in lucro_por_veiculo.items() if v > 0}

        if not lucro_positivo:
            return None

        labels = list(lucro_positivo.keys())
        valores = list(lucro_positivo.values())

        fig = Figure(figsize=(6, 6), facecolor=self.bg_figure)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(valores, labels=labels, autopct="%1.1f%%",
                                          textprops={"color": self.text_color_dark_bg},
                                          startangle=90, wedgeprops={"edgecolor": self.bg_figure})

        for autotext in autotexts:
            autotext.set_color(self.text_color_pie)

        ax.set_title("Participação no Lucro Total por Veículo", color=self.text_color_dark_bg)
        ax.axis('equal')
        fig.tight_layout()
        return fig

