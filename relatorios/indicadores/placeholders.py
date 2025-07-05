"""
Placeholders para relatórios de indicadores
Funções temporárias que retornam estruturas vazias até serem implementadas
"""
from ..utils import obter_mes_numero

def gerar_dashboard_executivo_placeholder(df_completo=None, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Placeholder para Dashboard Executivo
    
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("⚠️ Dashboard Executivo ainda não implementado")
    
    return [], "12", [], {
        "head": [['INDICADOR', 'VALOR', 'META', 'STATUS']],
        "body": []
    }

def gerar_indicadores_orcamentarios_placeholder(df_completo=None, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Placeholder para Indicadores Orçamentários
    
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("⚠️ Indicadores Orçamentários ainda não implementados")
    
    return [], "12", [], {
        "head": [['INDICADOR', 'VALOR ATUAL', 'VALOR ANTERIOR', 'VARIAÇÃO']],
        "body": []
    }

def gerar_analise_variacoes_placeholder(df_completo=None, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Placeholder para Análise de Variações
    
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("⚠️ Análise de Variações ainda não implementada")
    
    return [], "12", [], {
        "head": [['ITEM', 'VALOR BASE', 'VALOR ATUAL', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": []
    }

def gerar_relatorio_por_noug_placeholder(df_completo=None, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Placeholder para Relatório por Unidade Gestora
    
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("⚠️ Relatório por Unidade Gestora ainda não implementado")
    
    return [], "12", [], {
        "head": [['UNIDADE GESTORA', 'RECEITA', 'DESPESA', 'SALDO']],
        "body": []
    }