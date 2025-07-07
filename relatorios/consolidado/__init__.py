# relatorios/consolidado/__init__.py
"""
Módulo de Relatório Consolidado de Receitas PDF
Fase 1: Estrutura Base + Consolidador de Dados
"""

from .relatorio_consolidado import RelatorioConsolidado, gerar_relatorio_consolidado_completo
from .gerador_pdf import GeradorPDF
from .dashboard_executivo import DashboardExecutivo

__all__ = [
    'RelatorioConsolidado',
    'GeradorPDF', 
    'DashboardExecutivo',
    'gerar_relatorio_consolidado_completo'
]