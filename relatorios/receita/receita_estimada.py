"""
Relatório: Receita Estimada (Comparativo Anual)
Compara receita prevista entre 2024 e 2025 com percentuais e variações
"""
from ..utils import MotorRelatorios, formatar_percentual

def gerar_relatorio_receita_estimada(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera relatório comparativo de receita estimada entre 2024 e 2025
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Calcula totais gerais por exercício
    totais = {
        2024: float(df_processar[df_processar['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum()),
        2025: float(df_processar[df_processar['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
    }
    
    # Processa cada categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria:
            continue
            
        df_categoria = df_processar[df_processar['CATEGORIA'] == cod_cat]
        
        # Valores por exercício
        valor_2024_cat = float(df_categoria[df_categoria['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum())
        valor_2025_cat = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
        
        if valor_2024_cat == 0 and valor_2025_cat == 0:
            continue
        
        # Calcula percentuais
        perc_2024_cat = (valor_2024_cat / totais[2024] * 100) if totais[2024] > 0 else 0
        perc_2025_cat = (valor_2025_cat / totais[2025] * 100) if totais[2025] > 0 else 0
        
        # Calcula variação percentual
        delta_perc_cat = ((valor_2025_cat - valor_2024_cat) / valor_2024_cat) * 100 if valor_2024_cat > 0 else (100 if valor_2025_cat > 0 else 0)
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': nome_categoria,
            'valor_2024': valor_2024_cat,
            'valor_2025': valor_2025_cat,
            'perc_2024': perc_2024_cat,
            'perc_2025': perc_2025_cat,
            'delta': delta_perc_cat,
            'valor_2024_fmt': motor.formatar_numero(valor_2024_cat),
            'valor_2025_fmt': motor.formatar_numero(valor_2025_cat),
            'perc_2024_fmt': f"{perc_2024_cat:.2f}%",
            'perc_2025_fmt': f"{perc_2025_cat:.2f}%",
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
            
            valor_2024_orig = float(df_origem[df_origem['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum())
            valor_2025_orig = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
            
            if valor_2024_orig == 0 and valor_2025_orig == 0:
                continue
            
            perc_2024_orig = (valor_2024_orig / totais[2024] * 100) if totais[2024] > 0 else 0
            perc_2025_orig = (valor_2025_orig / totais[2025] * 100) if totais[2025] > 0 else 0
            delta_perc_orig = ((valor_2025_orig - valor_2024_orig) / valor_2024_orig) * 100 if valor_2024_orig > 0 else (100 if valor_2025_orig > 0 else 0)
            
            linha_origem = {
                'tipo': 'filha',
                'especificacao': f"  {nome_origem}",
                'valor_2024': valor_2024_orig,
                'valor_2025': valor_2025_orig,
                'perc_2024': perc_2024_orig,
                'perc_2025': perc_2025_orig,
                'delta': delta_perc_orig,
                'valor_2024_fmt': motor.formatar_numero(valor_2024_orig),
                'valor_2025_fmt': motor.formatar_numero(valor_2025_orig),
                'perc_2024_fmt': f"{perc_2024_orig:.2f}%",
                'perc_2025_fmt': f"{perc_2025_orig:.2f}%",
                'delta_fmt': formatar_percentual(delta_perc_orig)
            }
            dados_numericos.append(linha_origem)
            dados_para_ia.append(linha_origem)
    
    # Adiciona totais gerais
    if totais[2024] > 0 or totais[2025] > 0:
        delta_total = ((totais[2025] - totais[2024]) / totais[2024] * 100) if totais[2024] > 0 else 100
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            'valor_2024': totais[2024],
            'valor_2025': totais[2025],
            'perc_2024': 100.0,
            'perc_2025': 100.0,
            'delta': delta_total,
            'valor_2024_fmt': motor.formatar_numero(totais[2024]),
            'valor_2025_fmt': motor.formatar_numero(totais[2025]),
            'perc_2024_fmt': "100,00%",
            'perc_2025_fmt': "100,00%",
            'delta_fmt': formatar_percentual(delta_total)
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append(linha_total)
    
    # Dados para PDF
    dados_pdf = {
        "head": [['ESPECIFICAÇÃO', 'RECEITA PREVISTA 2024', '% 2024', 'RECEITA PREVISTA 2025', '% 2025', 'Δ%']],
        "body": [
            [linha['especificacao'], linha['valor_2024_fmt'], linha['perc_2024_fmt'], 
             linha['valor_2025_fmt'], linha['perc_2025_fmt'], linha['delta_fmt']]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, dados_para_ia, dados_pdf