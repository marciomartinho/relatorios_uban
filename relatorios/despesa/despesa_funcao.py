"""
Relatório: Despesa por Função de Governo
Agrupa despesas por função governamental (educação, saúde, segurança, etc.)
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_relatorio_despesa_por_funcao(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa agrupada por função de governo
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado para despesa (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    # TODO: Implementar quando houver dados de função governamental
    # Este relatório precisa da coluna FUNÇÃO ou similar na planilha de despesa
    
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    mes_referencia = obter_mes_numero(df_2025)
    
    # Por enquanto retorna estrutura vazia
    # Implementar quando tiver a coluna de função na planilha
    dados_numericos = []
    dados_para_ia = []
    dados_pdf = {
        "head": [['FUNÇÃO', 'DOTAÇÃO INICIAL', 'DESPESA EMPENHADA', 'SALDO']],
        "body": []
    }
    
    print("⚠️ Relatório de Despesa por Função ainda não implementado")
    print("   Aguardando colunas de função governamental na planilha")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf