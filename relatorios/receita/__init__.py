"""
Módulo de relatórios de receita
Exporta todas as funções de geração de relatórios de receita
"""

from .balanco_orcamentario import gerar_balanco_orcamentario
from .receita_estimada import gerar_relatorio_receita_estimada
from .receita_por_adm import gerar_relatorio_por_adm
from .receita_atualizada import gerar_relatorio_receita_atualizada_vs_inicial
from .grafico_pizza import gerar_grafico_receita_liquida
from .receita_conta_corrente import gerar_relatorio_receita_conta_corrente

# Aliases para compatibilidade
from .receita_estimada import gerar_relatorio_receita_estimada as gerar_relatorio_estimada

__all__ = [
    'gerar_balanco_orcamentario',
    'gerar_relatorio_receita_estimada',
    'gerar_relatorio_por_adm', 
    'gerar_relatorio_receita_atualizada_vs_inicial',
    'gerar_grafico_receita_liquida',
    'gerar_relatorio_receita_conta_corrente',
    'gerar_relatorio_estimada'  # Alias para compatibilidade
]