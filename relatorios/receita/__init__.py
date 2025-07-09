"""
Módulo de relatórios de receita
Exporta todas as funções de geração de relatórios de receita
"""

from .balanco_orcamentario import gerar_balanco_orcamentario
from .receita_estimada import gerar_relatorio_receita_estimada
from .receita_por_adm import gerar_relatorio_por_adm
from .receita_atualizada import gerar_relatorio_receita_atualizada_vs_inicial
from .grafico_pizza import gerar_grafico_receita_liquida
from .grafico_receita_capital import gerar_grafico_receita_capital
from .receita_conta_corrente import gerar_relatorio_receita_conta_corrente
from .receita_fonte_recursos import gerar_relatorio_receita_fonte_recursos
from .receitas_tributarias import gerar_relatorio_receitas_tributarias
from .receitas_contribuicoes import gerar_relatorio_receitas_contribuicoes
from .receitas_patrimoniais import gerar_relatorio_receitas_patrimoniais
from .receitas_agropecuarias import gerar_relatorio_receitas_agropecuarias
from .receitas_industriais import gerar_relatorio_receitas_industriais
from .receitas_servicos import gerar_relatorio_receitas_servicos
from .receitas_transferencias import gerar_relatorio_receitas_transferencias
from .receitas_outras_correntes import gerar_relatorio_outras_receitas_correntes
from .receitas_alienacao_bens import gerar_relatorio_receitas_alienacao_bens
from .receitas_amortizacao_emprestimo import gerar_relatorio_receitas_amortizacao_emprestimo
from .receitas_transferencia_capital import gerar_relatorio_receitas_transferencia_capital

# Aliases para compatibilidade
from .receita_estimada import gerar_relatorio_receita_estimada as gerar_relatorio_estimada

__all__ = [
    'gerar_balanco_orcamentario',
    'gerar_relatorio_receita_estimada',
    'gerar_relatorio_por_adm', 
    'gerar_relatorio_receita_atualizada_vs_inicial',
    'gerar_grafico_receita_liquida',
    'gerar_grafico_receita_capital',
    'gerar_relatorio_receita_conta_corrente',
    'gerar_relatorio_receita_fonte_recursos',
    'gerar_relatorio_receitas_tributarias',
    'gerar_relatorio_receitas_contribuicoes',
    'gerar_relatorio_receitas_patrimoniais',
    'gerar_relatorio_receitas_agropecuarias',
    'gerar_relatorio_receitas_industriais',
    'gerar_relatorio_receitas_servicos',
    'gerar_relatorio_receitas_transferencias',
    'gerar_relatorio_outras_receitas_correntes',
    'gerar_relatorio_receitas_alienacao_bens',
    'gerar_relatorio_receitas_amortizacao_emprestimo',
    'gerar_relatorio_receitas_transferencia_capital',
    'gerar_relatorio_estimada'  # Alias para compatibilidade
]