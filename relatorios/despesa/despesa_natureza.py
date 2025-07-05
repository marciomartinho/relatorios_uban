"""
Relatório: Despesa por Natureza
Agrupa despesas por natureza de gasto (pessoal, material, serviços, etc.)
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_relatorio_despesa_por_natureza(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa agrupada por natureza de gasto
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado para despesa (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    mes_referencia = obter_mes_numero(df_2025)
    dados_numericos = []
    dados_para_ia = []
    
    # Verifica se existe coluna ELEMENTO (que pode representar natureza)
    if 'ELEMENTO' in df_2025.columns and 'NOELEMENTO' in df_2025.columns:
        # Agrupa por elemento (natureza)
        elementos = df_2025.groupby('ELEMENTO', observed=True).agg({
            'NOELEMENTO': 'first',
            'DOTACAO INICIAL': 'sum',
            'DOTACAO ADICIONAL': 'sum',
            'CANCELAMENTO DE DOTACAO': 'sum',
            'CANCEL-REMANEJA DOTACAO': 'sum',
            'DESPESA EMPENHADA': 'sum',
            'DESPESA LIQUIDADA': 'sum',
            'DESPESA PAGA': 'sum'
        }).reset_index()
        
        for _, elemento in elementos.iterrows():
            dotacao_inicial = float(elemento['DOTACAO INICIAL'])
            dotacao_adicional = float(elemento['DOTACAO ADICIONAL'])
            cancelamento = float(elemento['CANCELAMENTO DE DOTACAO'])
            cancel_remaneja = float(elemento['CANCEL-REMANEJA DOTACAO'])
            
            dotacao_atualizada = dotacao_inicial + dotacao_adicional + cancelamento + cancel_remaneja
            despesa_empenhada = float(elemento['DESPESA EMPENHADA'])
            saldo = dotacao_atualizada - despesa_empenhada
            
            linha_elemento = {
                'tipo': 'principal',
                'especificacao': elemento['NOELEMENTO'],
                'dotacao_inicial': dotacao_inicial,
                'dotacao_atualizada': dotacao_atualizada,
                'despesa_empenhada': despesa_empenhada,
                'saldo': saldo,
                'dotacao_inicial_fmt': motor.formatar_numero(dotacao_inicial),
                'dotacao_atualizada_fmt': motor.formatar_numero(dotacao_atualizada),
                'despesa_empenhada_fmt': motor.formatar_numero(despesa_empenhada),
                'saldo_fmt': motor.formatar_numero(saldo)
            }
            dados_numericos.append(linha_elemento)
            dados_para_ia.append(linha_elemento)
        
        # Calcula total
        if dados_numericos:
            total_inicial = sum(l['dotacao_inicial'] for l in dados_numericos)
            total_atualizada = sum(l['dotacao_atualizada'] for l in dados_numericos)
            total_empenhada = sum(l['despesa_empenhada'] for l in dados_numericos)
            total_saldo = sum(l['saldo'] for l in dados_numericos)
            
            linha_total = {
                'tipo': 'total',
                'especificacao': 'TOTAL GERAL',
                'dotacao_inicial_fmt': motor.formatar_numero(total_inicial),
                'dotacao_atualizada_fmt': motor.formatar_numero(total_atualizada),
                'despesa_empenhada_fmt': motor.formatar_numero(total_empenhada),
                'saldo_fmt': motor.formatar_numero(total_saldo)
            }
            dados_numericos.append(linha_total)
    
    # Dados para PDF
    dados_pdf = {
        "head": [['NATUREZA DA DESPESA', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 'DESPESA EMPENHADA', 'SALDO']],
        "body": [
            [linha['especificacao'], linha.get('dotacao_inicial_fmt', 'R$ 0,00'),
             linha.get('dotacao_atualizada_fmt', 'R$ 0,00'), linha.get('despesa_empenhada_fmt', 'R$ 0,00'),
             linha.get('saldo_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf