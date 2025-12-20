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

        print("\n========== DEBUG ENTRADA DE DADOS ==========")
        print("lucros_por_mes:", lucros_por_mes)
        print("receita_por_linha:", receita_por_linha)
        print("consumo_por_veiculo:", consumo_por_veiculo)
        print("custo_por_km:", custo_por_km)
        print("lucro_por_veiculo:", lucro_por_veiculo)
        print("lucro_por_motorista:", lucro_por_motorista)
        print("gastos_por_veiculo:", gastos_por_veiculo)
        print("despesa_por_categoria:", despesa_por_categoria)
        print("============================================\n")

        def add(label, description, fig):
            if fig is not None:
                figs.append(fig)
                descriptions.append(description)
                print(f"-> {label}: OK")
            else:
                print(f"-> {label}: ERRO (fig None)")

        add(
            "Gráfico Fluxo Mensal",
            "Apresenta o lucro mensal ao longo do período analisado, "
            "permitindo identificar meses com melhor e pior desempenho.",
            self.graphics.bar_monthly_profit(lucros_por_mes)
        )

        add(
            "Pizza Receita por Linha",
            "Distribuição percentual da receita total entre as linhas/rotas.",
            self.graphics.plot_revenue_by_route_pie(receita_por_linha)
        )

        add(
            "Consumo Combustível",
            "Consumo médio de combustível por veículo, útil para análise de eficiência.",
            self.graphics.bar_consumo_combustivel(
                list(consumo_por_veiculo.keys()) if consumo_por_veiculo else [],
                [float(consumo_por_veiculo[k]) for k in consumo_por_veiculo] if consumo_por_veiculo else []
            )
        )

        add(
            "Custo por KM",
            "Custo médio por quilômetro rodado, considerando despesas operacionais.",
            self.graphics.bar_custo_por_km(
                list(custo_por_km.keys()) if custo_por_km else [],
                [float(custo_por_km[k]) for k in custo_por_km] if custo_por_km else []
            )
        )

        add(
            "Lucro por Veículo",
            "Comparação do lucro gerado por cada veículo da frota.",
            self.graphics.bar_lucro_por_veiculo(
                list(lucro_por_veiculo.keys()) if lucro_por_veiculo else [],
                [float(lucro_por_veiculo[k]) for k in lucro_por_veiculo] if lucro_por_veiculo else []
            )
        )

        add(
            "Lucro por Motorista",
            "Lucro total associado a cada motorista no período analisado.",
            self.graphics.bar_lucro_por_motorista(
                list(lucro_por_motorista.keys()) if lucro_por_motorista else [],
                [float(lucro_por_motorista[k]) for k in lucro_por_motorista] if lucro_por_motorista else []
            )
        )

        add(
            "Pizza Lucro por Veículo",
            "Participação percentual de cada veículo no lucro total.",
            self.graphics.pie_lucro_por_veiculo(lucro_por_veiculo)
        )

        print(f"\n========== TOTAL GERADO: {len(figs)} gráficos ==========\n")

        return figs, descriptions




