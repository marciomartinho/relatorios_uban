"""
Relatório: Despesa por Modalidade de Aplicação
Agrupa despesas por modalidade (direta, transferências, etc.)
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_relatorio_despesa_por_modalidade(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa agrupada por modalidade de aplicação
    
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
    
    # Usa a coluna MODALIDADE que já existe na planilha
    if 'MODALIDADE' in df_2025.columns and 'NOMODALIDADE' in df_2025.columns:
        # Agrupa por modalidade
        modalidades = df_2025.groupby('MODALIDADE', observed=True).agg({
            'NOMODALIDADE': 'first',
            'DOTACAO INICIAL': 'sum',
            'DOTACAO ADICIONAL': 'sum',
            'CANCELAMENTO DE DOTACAO': 'sum',
            'CANCEL-REMANEJA DOTACAO': 'sum',
            'DESPESA EMPENHADA': 'sum',
            'DESPESA LIQUIDADA': 'sum',
            'DESPESA PAGA': 'sum'
        }).reset_index()
        
        for _, modalidade in modalidades.iterrows():
            dotacao_inicial = float(modalidade['DOTACAO INICIAL'])
            dotacao_adicional = float(modalidade['DOTACAO ADICIONAL'])
            cancelamento = float(modalidade['CANCELAMENTO DE DOTACAO'])
            cancel_remaneja = float(modalidade['CANCEL-REMANEJA DOTACAO'])
            
            dotacao_atualizada = dotacao_inicial + dotacao_adicional + cancelamento + cancel_remaneja
            despesa_empenhada = float(modalidade['DESPESA EMPENHADA'])
            despesa_liquidada = float(modalidade['DESPESA LIQUIDADA'])
            despesa_paga = float(modalidade['DESPESA PAGA'])
            saldo = dotacao_atualizada - despesa_empenhada
            
            linha_modalidade = {
                'tipo': 'principal',
                'especificacao': modalidade['NOMODALIDADE'],
                'dotacao_inicial': dotacao_inicial,
                'dotacao_atualizada': dotacao_atualizada,
                'despesa_empenhada': despesa_empenhada,
                'despesa_liquidada': despesa_liquidada,
                'despesa_paga': despesa_paga,
                'saldo': saldo,
                'dotacao_inicial_fmt': motor.formatar_numero(dotacao_inicial),
                'dotacao_atualizada_fmt': motor.formatar_numero(dotacao_atualizada),
                'despesa_empenhada_fmt': motor.formatar_numero(despesa_empenhada),
                'despesa_liquidada_fmt': motor.formatar_numero(despesa_liquidada),
                'despesa_paga_fmt': motor.formatar_numero(despesa_paga),
                'saldo_fmt': motor.formatar_numero(saldo)
            }
            dados_numericos.append(linha_modalidade)
            dados_para_ia.append(linha_modalidade)
        
        # Calcula totais
        if dados_numericos:
            totais = {
                'dotacao_inicial': sum(l['dotacao_inicial'] for l in dados_numericos),
                'dotacao_atualizada': sum(l['dotacao_atualizada'] for l in dados_numericos),
                'despesa_empenhada': sum(l['despesa_empenhada'] for l in dados_numericos),
                'despesa_liquidada': sum(l['despesa_liquidada'] for l in dados_numericos),
                'despesa_paga': sum(l['despesa_paga'] for l in dados_numericos),
                'saldo': sum(l['saldo'] for l in dados_numericos)
            }
            
            linha_total = {
                'tipo': 'total',
                'especificacao': 'TOTAL GERAL',
                **{f'{k}_fmt': motor.formatar_numero(v) for k, v in totais.items()}
            }
            dados_numericos.append(linha_total)
            dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF
    dados_pdf = {
        "head": [['MODALIDADE DE APLICAÇÃO', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 
                 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', 'SALDO']],
        "body": [
            [linha['especificacao'], linha.get('dotacao_inicial_fmt', 'R$ 0,00'),
             linha.get('dotacao_atualizada_fmt', 'R$ 0,00'), linha.get('despesa_empenhada_fmt', 'R$ 0,00'),
             linha.get('despesa_liquidada_fmt', 'R$ 0,00'), linha.get('despesa_paga_fmt', 'R$ 0,00'),
             linha.get('saldo_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf