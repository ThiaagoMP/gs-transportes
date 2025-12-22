import tkinter as tk
from tkinter import ttk

class GetGraphics:
    def __init__(self, graphics):
        self.graphics = graphics

    def get_figs(
            self,
            despesa_por_categoria,
            despesas_por_mes,
            extras_linha_mes,
            gastos_por_veiculo,
            lucro_por_veiculo,
            lucros_por_mes,
            pagamentos_alunos_mes,
            recebimentos_por_aluno,
            receita_por_linha,
            consumo_por_veiculo=None,
            custo_por_km=None,
            lucro_por_motorista=None
    ):

        figs = []
        descriptions = []

        def add(label, description, fig):
            if fig is not None:
                figs.append(fig)
                descriptions.append(description)

        def safe_extract(data_dict):
            if not data_dict or not isinstance(data_dict, dict):
                return [], []
            keys = list(data_dict.keys())
            values = []
            for k in keys:
                try:
                    values.append(float(data_dict[k]))
                except (ValueError, TypeError):
                    values.append(0.0)
            return keys, values

        add(
            "Fluxo mensal",
            "Apresenta o lucro mensal ao longo do período analisado, "
            "permitindo identificar meses com melhor e pior desempenho.",
            self.graphics.bar_monthly_profit(lucros_por_mes)
        )

        add(
            "Receita por linha",
            "Distribuição percentual da receita total entre as linhas e rotas.",
            self.graphics.plot_revenue_by_route_pie(receita_por_linha)
        )

        c_keys, c_values = safe_extract(consumo_por_veiculo)
        add(
            "Consumo de combustível",
            "Consumo médio de combustível por veículo, útil para análise de eficiência.",
            self.graphics.bar_consumo_combustivel(c_keys, c_values)
        )

        ckm_keys, ckm_values = safe_extract(custo_por_km)
        add(
            "Custo por quilômetro",
            "Custo médio por quilômetro rodado, considerando despesas operacionais.",
            self.graphics.bar_custo_por_km(ckm_keys, ckm_values)
        )

        lv_keys, lv_values = safe_extract(lucro_por_veiculo)
        add(
            "Lucro por veículo",
            "Comparação do lucro gerado por cada veículo da frota no período.",
            self.graphics.bar_lucro_por_veiculo(lv_keys, lv_values)
        )

        lm_keys, lm_values = safe_extract(lucro_por_motorista)
        add(
            "Lucro por motorista",
            "Lucro total associado a cada motorista no período analisado.",
            self.graphics.bar_lucro_por_motorista(lm_keys, lm_values)
        )

        add(
            "Participação no lucro",
            "Participação percentual de cada veículo no lucro total acumulado.",
            self.graphics.pie_lucro_por_veiculo(lucro_por_veiculo)
        )

        return figs, descriptions