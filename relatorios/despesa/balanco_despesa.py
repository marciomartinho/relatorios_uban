"""
Relatório: Balanço Orçamentário da Despesa
Compara dotação inicial, atualizada com despesas empenhadas, liquidadas e pagas
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_balanco_despesa(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera o balanço orçamentário da despesa comparando dotação com execução
    
    FÓRMULAS APLICADAS:
    - DOTAÇÃO INICIAL = DOTACAO INICIAL
    - DOTAÇÃO ATUALIZADA = DOTACAO INICIAL + DOTACAO ADICIONAL + CANCELAMENTO DE DOTACAO + CANCEL-REMANEJA DOTACAO
    - SALDO DA DOTAÇÃO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado para despesa (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Agrupa por categoria com observed=True para evitar warning
    categorias = df_2025.groupby('CATEGORIA', observed=True).agg({
        'NOCATEGORIA': 'first',
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Processa cada categoria
    for _, categoria in categorias.iterrows():
        dotacao_inicial = float(categoria['DOTACAO INICIAL'])
        dotacao_adicional = float(categoria['DOTACAO ADICIONAL'])
        cancelamento_dotacao = float(categoria['CANCELAMENTO DE DOTACAO'])
        cancel_remaneja = float(categoria['CANCEL-REMANEJA DOTACAO'])
        
        # FÓRMULA: DOTAÇÃO ATUALIZADA = INICIAL + ADICIONAL + CANCELAMENTO + CANCEL-REMANEJA
        dotacao_atualizada = dotacao_inicial + dotacao_adicional + cancelamento_dotacao + cancel_remaneja
        
        despesa_empenhada = float(categoria['DESPESA EMPENHADA'])
        despesa_liquidada = float(categoria['DESPESA LIQUIDADA'])
        despesa_paga = float(categoria['DESPESA PAGA'])
        
        # FÓRMULA: SALDO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
        saldo_dotacao = dotacao_atualizada - despesa_empenhada
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': categoria['NOCATEGORIA'],
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'saldo_dotacao': saldo_dotacao,
            'dotacao_inicial_fmt': motor.formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor.formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor.formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor.formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor.formatar_numero(despesa_paga),
            'saldo_dotacao_fmt': motor.formatar_numero(saldo_dotacao)
        }
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Processa grupos dentro da categoria
        grupos = df_2025[df_2025['CATEGORIA'] == categoria['CATEGORIA']].groupby('GRUPO', observed=True).agg({
            'NOGRUPO': 'first',
            'DOTACAO INICIAL': 'sum',
            'DOTACAO ADICIONAL': 'sum',
            'CANCELAMENTO DE DOTACAO': 'sum',
            'CANCEL-REMANEJA DOTACAO': 'sum',
            'DESPESA EMPENHADA': 'sum',
            'DESPESA LIQUIDADA': 'sum',
            'DESPESA PAGA': 'sum'
        }).reset_index()
        
        for _, grupo in grupos.iterrows():
            dot_inicial_grupo = float(grupo['DOTACAO INICIAL'])
            dot_adicional_grupo = float(grupo['DOTACAO ADICIONAL'])
            cancel_dotacao_grupo = float(grupo['CANCELAMENTO DE DOTACAO'])
            cancel_remaneja_grupo = float(grupo['CANCEL-REMANEJA DOTACAO'])
            
            # FÓRMULA PARA GRUPO
            dot_atualizada_grupo = dot_inicial_grupo + dot_adicional_grupo + cancel_dotacao_grupo + cancel_remaneja_grupo
            
            desp_emp_grupo = float(grupo['DESPESA EMPENHADA'])
            desp_liq_grupo = float(grupo['DESPESA LIQUIDADA'])
            desp_paga_grupo = float(grupo['DESPESA PAGA'])
            
            # FÓRMULA PARA SALDO DO GRUPO
            saldo_grupo = dot_atualizada_grupo - desp_emp_grupo
            
            linha_grupo = {
                'tipo': 'filha',
                'especificacao': f"  {grupo['NOGRUPO']}",
                'dotacao_inicial': dot_inicial_grupo,
                'dotacao_atualizada': dot_atualizada_grupo,
                'despesa_empenhada': desp_emp_grupo,
                'despesa_liquidada': desp_liq_grupo,
                'despesa_paga': desp_paga_grupo,
                'saldo_dotacao': saldo_grupo,
                'dotacao_inicial_fmt': motor.formatar_numero(dot_inicial_grupo),
                'dotacao_atualizada_fmt': motor.formatar_numero(dot_atualizada_grupo),
                'despesa_empenhada_fmt': motor.formatar_numero(desp_emp_grupo),
                'despesa_liquidada_fmt': motor.formatar_numero(desp_liq_grupo),
                'despesa_paga_fmt': motor.formatar_numero(desp_paga_grupo),
                'saldo_dotacao_fmt': motor.formatar_numero(saldo_grupo)
            }
            dados_numericos.append(linha_grupo)
    
    # Calcula totais gerais
    linhas_principais = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_principais:
        totais = {
            'dotacao_inicial': sum(l['dotacao_inicial'] for l in linhas_principais),
            'dotacao_atualizada': sum(l['dotacao_atualizada'] for l in linhas_principais),
            'despesa_empenhada': sum(l['despesa_empenhada'] for l in linhas_principais),
            'despesa_liquidada': sum(l['despesa_liquidada'] for l in linhas_principais),
            'despesa_paga': sum(l['despesa_paga'] for l in linhas_principais),
            'saldo_dotacao': sum(l['saldo_dotacao'] for l in linhas_principais)
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
        "head": [['DESPESAS ORÇAMENTÁRIAS', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 
                 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', 'SALDO DA DOTAÇÃO']],
        "body": [
            [linha['especificacao'], linha.get('dotacao_inicial_fmt', 'R$ 0,00'), 
             linha.get('dotacao_atualizada_fmt', 'R$ 0,00'), linha.get('despesa_empenhada_fmt', 'R$ 0,00'),
             linha.get('despesa_liquidada_fmt', 'R$ 0,00'), linha.get('despesa_paga_fmt', 'R$ 0,00'), 
             linha.get('saldo_dotacao_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf