"""
Relatório: Receita Atualizada X Inicial
Compara previsão inicial com previsão atualizada para 2025
"""
from ..utils import MotorRelatorios, formatar_percentual

def gerar_relatorio_receita_atualizada_vs_inicial(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera relatório comparativo entre previsão inicial e previsão atualizada para 2025
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], [], {}
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria:
            continue
            
        df_categoria = df_2025[df_2025['CATEGORIA'] == cod_cat]
        if df_categoria.empty:
            continue
        
        # Calcula valores da categoria
        inicial_cat = float(df_categoria['PREVISAO INICIAL LIQUIDA'].sum())
        
        if 'PREVISAO ATUALIZADA LIQUIDA' in df_categoria.columns:
            atualizada_cat = float(df_categoria['PREVISAO ATUALIZADA LIQUIDA'].sum())
        else:
            atualizada_cat = inicial_cat
        
        if inicial_cat == 0 and atualizada_cat == 0:
            continue
        
        # Calcula variação percentual
        delta_perc_cat = ((atualizada_cat - inicial_cat) / inicial_cat) * 100 if inicial_cat > 0 else (100 if atualizada_cat > 0 else 0)
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': nome_categoria,
            'inicial': inicial_cat,
            'atualizada': atualizada_cat,
            'delta': delta_perc_cat,
            'inicial_fmt': motor.formatar_numero(inicial_cat),
            'atualizada_fmt': motor.formatar_numero(atualizada_cat),
            'delta_fmt': formatar_percentual(delta_perc_cat)
        }
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Processa origens dentro da categoria
        for cod_orig in origens.keys():
            nome_origem = motor.obter_nome_origem(cod_orig)
            if not nome_origem:
                continue
            
            df_origem = df_categoria[df_categoria['ORIGEM'] == cod_orig]
            if df_origem.empty:
                continue
            
            inicial_orig = float(df_origem['PREVISAO INICIAL LIQUIDA'].sum())
            
            if 'PREVISAO ATUALIZADA LIQUIDA' in df_origem.columns:
                atualizada_orig = float(df_origem['PREVISAO ATUALIZADA LIQUIDA'].sum())
            else:
                atualizada_orig = inicial_orig
            
            if inicial_orig == 0 and atualizada_orig == 0:
                continue
            
            delta_perc_orig = ((atualizada_orig - inicial_orig) / inicial_orig) * 100 if inicial_orig > 0 else (100 if atualizada_orig > 0 else 0)
            
            linha_origem = {
                'tipo': 'filha',
                'especificacao': f"  {nome_origem}",
                'inicial': inicial_orig,
                'atualizada': atualizada_orig,
                'delta': delta_perc_orig,
                'inicial_fmt': motor.formatar_numero(inicial_orig),
                'atualizada_fmt': motor.formatar_numero(atualizada_orig),
                'delta_fmt': formatar_percentual(delta_perc_orig)
            }
            dados_numericos.append(linha_origem)
            dados_para_ia.append(linha_origem)
    
    # Calcula totais gerais
    linhas_principais = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_principais:
        totais_inicial = sum(l['inicial'] for l in linhas_principais)
        totais_atualizada = sum(l['atualizada'] for l in linhas_principais)
        delta_total = ((totais_atualizada - totais_inicial) / totais_inicial * 100) if totais_inicial > 0 else 100
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            'inicial': totais_inicial,
            'atualizada': totais_atualizada,
            'delta': delta_total,
            'inicial_fmt': motor.formatar_numero(totais_inicial),
            'atualizada_fmt': motor.formatar_numero(totais_atualizada),
            'delta_fmt': formatar_percentual(delta_total)
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append(linha_total)
    
    # Dados para PDF
    dados_pdf = {
        "head": [['ESPECIFICAÇÃO', 'PREVISÃO INICIAL', 'PREVISÃO ATUALIZADA', 'Δ%']],
        "body": [
            [linha['especificacao'], linha['inicial_fmt'], linha['atualizada_fmt'], linha['delta_fmt']]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, dados_para_ia, dados_pdf