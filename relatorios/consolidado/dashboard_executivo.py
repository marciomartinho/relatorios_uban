"""
Dashboard Executivo para o Relatório Consolidado
Gera KPIs e resumos executivos dos dados consolidados
"""
from typing import Dict, Any, List
import pandas as pd

class DashboardExecutivo:
    """
    Classe responsável por gerar dashboard executivo com KPIs principais
    """
    
    def __init__(self, dados_consolidados: Dict[str, Any]):
        """
        Inicializa o dashboard executivo
        
        Args:
            dados_consolidados: Dados consolidados de todos os relatórios
        """
        self.dados = dados_consolidados
    
    def gerar_kpis_principais(self) -> Dict[str, Any]:
        """
        Gera os 4 KPIs principais do dashboard
        
        Returns:
            Dicionário com KPIs formatados
        """
        totais = self.dados.get('metadados', {}).get('totais_consolidados', {})
        
        # KPI 1: Receita Total 2025
        receita_total_2025 = totais.get('total_geral_2025', 0)
        
        # KPI 2: Variação vs 2024
        receita_total_2024 = totais.get('total_geral_2024', 0)
        variacao_perc = ((receita_total_2025 - receita_total_2024) / receita_total_2024 * 100) if receita_total_2024 > 0 else 0
        
        # KPI 3: Maior Fonte
        resumo = self.dados.get('resumo_executivo', {})
        maior_receita = resumo.get('maior_receita', 'Não identificada')
        
        # KPI 4: Meta Cumprida (placeholder - será calculado quando houver dados de meta)
        meta_cumprida = 0  # TODO: Implementar cálculo real da meta
        
        return {
            'receita_total_2025': {
                'valor': receita_total_2025,
                'valor_fmt': self._formatar_valor(receita_total_2025),
                'titulo': 'Receita Total 2025'
            },
            'variacao_vs_2024': {
                'valor': variacao_perc,
                'valor_fmt': f"{variacao_perc:+.1f}%",
                'titulo': 'Variação vs 2024',
                'classe_css': 'positivo' if variacao_perc > 0 else 'negativo' if variacao_perc < 0 else 'neutro'
            },
            'maior_fonte': {
                'valor': maior_receita,
                'valor_fmt': maior_receita,
                'titulo': 'Maior Fonte'
            },
            'meta_cumprida': {
                'valor': meta_cumprida,
                'valor_fmt': f"{meta_cumprida:.1f}%",
                'titulo': 'Meta Cumprida',
                'classe_css': 'alto' if meta_cumprida >= 80 else 'medio' if meta_cumprida >= 60 else 'baixo'
            }
        }
    
    def gerar_alertas_visuais(self) -> List[Dict[str, Any]]:
        """
        Gera alertas visuais baseados nos dados
        
        Returns:
            Lista de alertas com cores e mensagens
        """
        alertas = []
        
        # Analisa inconsistências
        inconsistencias = self.dados.get('analises_especiais', {}).get('inconsistencias', {})
        if inconsistencias and inconsistencias.get('totais', {}).get('total_2025', 0) > 0:
            alertas.append({
                'tipo': 'warning',
                'cor': 'amarelo',
                'emoji': '🟡',
                'titulo': 'Inconsistências Detectadas',
                'mensagem': 'Foram encontradas inconsistências nos dados que requerem atenção'
            })
        
        # Analisa variação geral
        totais = self.dados.get('metadados', {}).get('totais_consolidados', {})
        receita_2025 = totais.get('total_geral_2025', 0)
        receita_2024 = totais.get('total_geral_2024', 0)
        
        if receita_2024 > 0:
            variacao = ((receita_2025 - receita_2024) / receita_2024) * 100
            
            if variacao > 10:
                alertas.append({
                    'tipo': 'success',
                    'cor': 'verde',
                    'emoji': '🟢',
                    'titulo': 'Crescimento Acima da Meta',
                    'mensagem': f'Receita cresceu {variacao:.1f}% em relação ao ano anterior'
                })
            elif variacao < -5:
                alertas.append({
                    'tipo': 'error',
                    'cor': 'vermelho',
                    'emoji': '🔴',
                    'titulo': 'Queda Significativa',
                    'mensagem': f'Receita caiu {abs(variacao):.1f}% em relação ao ano anterior'
                })
            else:
                alertas.append({
                    'tipo': 'info',
                    'cor': 'amarelo',
                    'emoji': '🟡',
                    'titulo': 'Dentro da Normalidade',
                    'mensagem': f'Variação de {variacao:.1f}% está dentro do esperado'
                })
        
        return alertas
    
    def gerar_mini_graficos(self) -> Dict[str, Any]:
        """
        Gera dados para mini-gráficos (sparklines, gauges, barras de progresso)
        
        Returns:
            Dados para renderização de mini-gráficos
        """
        # Placeholder para dados de mini-gráficos
        # Será expandido nas próximas fases
        return {
            'sparklines_evolucao': [],
            'gauges_performance': [],
            'barras_progresso': []
        }
    
    def _formatar_valor(self, valor: float) -> str:
        """
        Formata valor monetário para exibição
        
        Args:
            valor: Valor a ser formatado
            
        Returns:
            String formatada
        """
        if valor == 0:
            return "R$ 0,00"
        
        # Formata em milhões para valores grandes
        if abs(valor) >= 1_000_000:
            valor_milhoes = valor / 1_000_000
            return f"R$ {valor_milhoes:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")