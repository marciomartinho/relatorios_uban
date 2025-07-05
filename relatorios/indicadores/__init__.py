"""
Módulo de relatórios de indicadores e análises
Exporta todas as funções de geração de indicadores orçamentários e análises avançadas
"""

# TODO: Quando implementados, adicionar:
# from .dashboard_executivo import gerar_dashboard_executivo
# from .indicadores_orcamentarios import gerar_relatorio_indicadores
# from .analise_variacoes import gerar_relatorio_analise_variacoes
# from .relatorio_por_noug import gerar_relatorio_por_noug
# from .receita_vs_despesa import gerar_relatorio_receita_vs_despesa
# from .evolucao_temporal import gerar_relatorio_evolucao_temporal

# Por enquanto, placeholders que retornam estruturas vazias
from .placeholders import (
    gerar_dashboard_executivo_placeholder,
    gerar_indicadores_orcamentarios_placeholder,
    gerar_analise_variacoes_placeholder,
    gerar_relatorio_por_noug_placeholder
)

__all__ = [
    # Placeholders temporários
    'gerar_dashboard_executivo_placeholder',
    'gerar_indicadores_orcamentarios_placeholder', 
    'gerar_analise_variacoes_placeholder',
    'gerar_relatorio_por_noug_placeholder'
    
    # TODO: Quando implementados, substituir pelos reais:
    # 'gerar_dashboard_executivo',
    # 'gerar_relatorio_indicadores',
    # 'gerar_relatorio_analise_variacoes',
    # 'gerar_relatorio_por_noug',
    # 'gerar_relatorio_receita_vs_despesa',
    # 'gerar_relatorio_evolucao_temporal'
]