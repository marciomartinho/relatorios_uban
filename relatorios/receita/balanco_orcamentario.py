"""
Relatório: Balanço Orçamentário da Receita
Compara previsão inicial, atualizada e receita realizada
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_balanco_orcamentario(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera o balanço orçamentário da receita comparando previsão com realização
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra dados de 2025 e 2024
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    df_2024 = df_processar[df_processar['COEXERCICIO'] == 2024]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria: 
            continue
            
        df_cat_2025 = df_2025[df_2025['CATEGORIA'] == cod_cat]
        df_cat_2024 = df_2024[df_2024['CATEGORIA'] == cod_cat]
        
        if df_cat_2025.empty: 
            continue
        
        # Calcula valores da categoria
        pi_2025 = float(df_cat_2025['PREVISAO INICIAL LIQUIDA'].sum())
        
        # Verifica se a coluna PREVISAO ATUALIZADA LIQUIDA existe
        if 'PREVISAO ATUALIZADA LIQUIDA' in df_cat_2025.columns:
            pa_2025 = float(df_cat_2025['PREVISAO ATUALIZADA LIQUIDA'].sum())
        else:
            pa_2025 = pi_2025
        
        # Verifica se a coluna RECEITA LIQUIDA existe
        if 'RECEITA LIQUIDA' in df_cat_2025.columns:
            rr_2025 = float(df_cat_2025['RECEITA LIQUIDA'].sum())
        else:
            rr_2025 = 0.0
            
        if 'RECEITA LIQUIDA' in df_cat_2024.columns and not df_cat_2024.empty:
            rr_2024 = float(df_cat_2024['RECEITA LIQUIDA'].sum())
        else:
            rr_2024 = 0.0
            
        saldo = rr_2025 - rr_2024
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': nome_categoria,
            'pi_2025': pi_2025,
            'pa_2025': pa_2025,
            'rr_2025': rr_2025,
            'rr_2024': rr_2024,
            'saldo': saldo,
            'pi_2025_fmt': motor.formatar_numero(pi_2025),
            'pa_2025_fmt': motor.formatar_numero(pa_2025),
            'rr_2025_fmt': motor.formatar_numero(rr_2025),
            'rr_2024_fmt': motor.formatar_numero(rr_2024),
            'saldo_fmt': motor.formatar_numero(saldo)
        }
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Processa origens dentro da categoria
        for cod_orig in origens.keys():
            nome_origem = motor.obter_nome_origem(cod_orig)
            if not nome_origem: 
                continue
            
            df_orig_2025 = df_cat_2025[df_cat_2025['ORIGEM'] == cod_orig]
            df_orig_2024 = df_cat_2024[df_cat_2024['ORIGEM'] == cod_orig]
            
            if df_orig_2025.empty: 
                continue
            
            pi_2025_orig = float(df_orig_2025['PREVISAO INICIAL LIQUIDA'].sum())
            
            if 'PREVISAO ATUALIZADA LIQUIDA' in df_orig_2025.columns:
                pa_2025_orig = float(df_orig_2025['PREVISAO ATUALIZADA LIQUIDA'].sum())
            else:
                pa_2025_orig = pi_2025_orig
                
            if 'RECEITA LIQUIDA' in df_orig_2025.columns:
                rr_2025_orig = float(df_orig_2025['RECEITA LIQUIDA'].sum())
            else:
                rr_2025_orig = 0.0
                
            if 'RECEITA LIQUIDA' in df_orig_2024.columns and not df_orig_2024.empty:
                rr_2024_orig = float(df_orig_2024['RECEITA LIQUIDA'].sum())
            else:
                rr_2024_orig = 0.0
                
            saldo_orig = rr_2025_orig - rr_2024_orig
            
            linha_origem = {
                'tipo': 'filha',
                'especificacao': f"  {nome_origem}",
                'pi_2025': pi_2025_orig,
                'pa_2025': pa_2025_orig,
                'rr_2025': rr_2025_orig,
                'rr_2024': rr_2024_orig,
                'saldo': saldo_orig,
                'pi_2025_fmt': motor.formatar_numero(pi_2025_orig),
                'pa_2025_fmt': motor.formatar_numero(pa_2025_orig),
                'rr_2025_fmt': motor.formatar_numero(rr_2025_orig),
                'rr_2024_fmt': motor.formatar_numero(rr_2024_orig),
                'saldo_fmt': motor.formatar_numero(saldo_orig)
            }
            dados_numericos.append(linha_origem)
    
    # Calcula totais gerais
    linhas_principais = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_principais:
        totais = {
            'pi_2025': sum(l['pi_2025'] for l in linhas_principais),
            'pa_2025': sum(l['pa_2025'] for l in linhas_principais),
            'rr_2025': sum(l['rr_2025'] for l in linhas_principais),
            'rr_2024': sum(l['rr_2024'] for l in linhas_principais),
        }
        totais['saldo'] = totais['rr_2025'] - totais['rr_2024']
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            **{f'{k}_fmt': motor.formatar_numero(v) for k, v in totais.items()}
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF
    dados_pdf = {
        "head": [['RECEITAS', 'PREVISÃO INICIAL 2025', 'PREVISÃO ATUALIZADA 2025', 
                 f'RECEITA REALIZADA {mes_referencia}/2025', f'RECEITA REALIZADA {mes_referencia}/2024', 
                 'VARIAÇÃO 2025 x 2024']],
        "body": [
            [linha['especificacao'], linha.get('pi_2025_fmt', 'R$ 0,00'), linha.get('pa_2025_fmt', 'R$ 0,00'), 
             linha.get('rr_2025_fmt', 'R$ 0,00'), linha.get('rr_2024_fmt', 'R$ 0,00'), linha.get('saldo_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf