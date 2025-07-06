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
from .receitas_tributarias import gerar_relatorio_receitas_tributarias
from .receitas_contribuicoes import gerar_relatorio_receitas_contribuicoes
from .receitas_patrimoniais import gerar_relatorio_receitas_patrimoniais
from .receitas_servicos import gerar_relatorio_receitas_servicos
from .receitas_transferencias import gerar_relatorio_receitas_transferencias

# Aliases para compatibilidade
from .receita_estimada import gerar_relatorio_receita_estimada as gerar_relatorio_estimada

__all__ = [
    'gerar_balanco_orcamentario',
    'gerar_relatorio_receita_estimada',
    'gerar_relatorio_por_adm', 
    'gerar_relatorio_receita_atualizada_vs_inicial',
    'gerar_grafico_receita_liquida',
    'gerar_relatorio_receita_conta_corrente',
    'gerar_relatorio_receitas_tributarias',
    'gerar_relatorio_receitas_contribuicoes',
    'gerar_relatorio_receitas_patrimoniais',
    'gerar_relatorio_receitas_servicos',
    'gerar_relatorio_receitas_transferencias',
    'gerar_relatorio_estimada'  # Alias para compatibilidade
]