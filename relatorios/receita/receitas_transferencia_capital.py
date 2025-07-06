"""
Relatório: Receita de Transferências de Capital Líquida Realizada
Analisa receitas da origem 24 com desdobramentos por alínea
REGRAS:
- ORIGEM = 24 (receitas de transferências de capital)
- Desdobramento por ALINEA e NOALINEA
- Valores de RECEITA LÍQUIDA
- Comparativo 2024 vs 2025 com variações absoluta e percentual
- Estrutura sempre expandida (sem botões de expansão)
"""
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receitas_transferencia_capital(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receitas de transferências de capital líquidas com comparativo 2024 vs 2025
    
    REGRAS DE NEGÓCIO:
    - Filtra apenas ORIGEM = 24 (receitas de transferências de capital)
    - Agrupa por ESPÉCIE primeiro
    - Desdobra por ALINEA e NOALINEA
    - Compara 2024 vs 2025 com variações absoluta e percentual
    - Estrutura hierárquica: espécie → alíneas (sempre expandida)
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas origem de transferências de capital (24) para 2025 e 2024
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['ORIGEM'] == '24')
    ]
    df_2024 = df_processar[
        (df_processar['COEXERCICIO'] == 2024) & 
        (df_processar['ORIGEM'] == '24')
    ]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}, []
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}, []
    
    # Verifica se as colunas ALINEA e NOALINEA existem
    if 'ALINEA' not in df_2025.columns or 'NOALINEA' not in df_2025.columns:
        print("⚠️ Colunas 'ALINEA' ou 'NOALINEA' não encontradas na planilha")
        return [], obter_mes_numero(df_processar), [], {}, []
    
    print("🔍 Processando receitas de transferências de capital (ORIGEM 24)...")
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada espécie encontrada
    especies_disponiveis = sorted(df_2025['ESPECIE'].dropna().unique())
    print(f"📊 Espécies encontradas: {especies_disponiveis}")
    
    for especie in especies_disponiveis:
        # Busca nome da espécie
        nome_especie = _obter_nome_especie(df_2025, especie)
        if not nome_especie:
            continue
            
        # Filtra dados desta espécie
        df_especie_2025 = df_2025[df_2025['ESPECIE'] == especie]
        df_especie_2024 = df_2024[df_2024['ESPECIE'] == especie] if not df_2024.empty else pd.DataFrame()
        
        # Calcula valores da espécie (totais)
        valor_2025_especie = float(df_especie_2025['RECEITA LIQUIDA'].sum())
        valor_2024_especie = float(df_especie_2024['RECEITA LIQUIDA'].sum()) if not df_especie_2024.empty else 0.0
        
        if valor_2025_especie == 0 and valor_2024_especie == 0:
            continue
            
        # Calcula variações da espécie
        variacao_abs_especie = valor_2025_especie - valor_2024_especie
        variacao_perc_especie = ((valor_2025_especie - valor_2024_especie) / valor_2024_especie * 100) if valor_2024_especie > 0 else (100 if valor_2025_especie > 0 else 0)
        
        # Obtém alíneas desta espécie
        alineas = _obter_alineas_especie(df_especie_2025)
        tem_alineas = len(alineas) > 0
        
        # Adiciona linha da espécie (principal)
        linha_especie = {
            'tipo': 'especie',
            'especie_codigo': especie,
            'nome_especie': nome_especie,
            'receita_2024': valor_2024_especie,
            'receita_2025': valor_2025_especie,
            'variacao_abs': variacao_abs_especie,
            'variacao_perc': variacao_perc_especie,
            'especie_codigo_fmt': especie,
            'nome_especie_fmt': nome_especie,
            'receita_2024_fmt': motor.formatar_numero(valor_2024_especie),
            'receita_2025_fmt': motor.formatar_numero(valor_2025_especie),
            'variacao_abs_fmt': motor.formatar_numero(variacao_abs_especie),
            'variacao_perc_fmt': formatar_percentual(variacao_perc_especie),
            'tem_alineas': tem_alineas,
            'qtd_alineas': len(alineas)
        }
        dados_numericos.append(linha_especie)
        dados_para_ia.append(linha_especie)
        
        # Adiciona alíneas desta espécie
        for alinea in alineas:
            codigo_alinea = alinea['ALINEA']
            nome_alinea = alinea['NOALINEA']
                
            # Filtra dados desta alínea
            df_alinea_2025 = df_especie_2025[df_especie_2025['ALINEA'] == codigo_alinea]
            df_alinea_2024 = df_especie_2024[df_especie_2024['ALINEA'] == codigo_alinea] if not df_especie_2024.empty else pd.DataFrame()
            
            valor_2025_alinea = float(df_alinea_2025['RECEITA LIQUIDA'].sum())
            valor_2024_alinea = float(df_alinea_2024['RECEITA LIQUIDA'].sum()) if not df_alinea_2024.empty else 0.0
            
            if valor_2025_alinea == 0 and valor_2024_alinea == 0:
                continue
                
            variacao_abs_alinea = valor_2025_alinea - valor_2024_alinea
            variacao_perc_alinea = ((valor_2025_alinea - valor_2024_alinea) / valor_2024_alinea * 100) if valor_2024_alinea > 0 else (100 if valor_2025_alinea > 0 else 0)
            
            linha_alinea = {
                'tipo': 'alinea',
                'especie_pai': especie,
                'alinea_codigo': codigo_alinea,
                'nome_alinea': nome_alinea,
                'receita_2024': valor_2024_alinea,
                'receita_2025': valor_2025_alinea,
                'variacao_abs': variacao_abs_alinea,
                'variacao_perc': variacao_perc_alinea,
                'especie_codigo_fmt': codigo_alinea,
                'nome_especie_fmt': nome_alinea,
                'receita_2024_fmt': motor.formatar_numero(valor_2024_alinea),
                'receita_2025_fmt': motor.formatar_numero(valor_2025_alinea),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs_alinea),
                'variacao_perc_fmt': formatar_percentual(variacao_perc_alinea),
                'tem_alineas': False,
                'qtd_alineas': 0
            }
            dados_numericos.append(linha_alinea)
    
    # Adiciona totais gerais (apenas das espécies principais)
    especies_principais = [d for d in dados_numericos if d['tipo'] == 'especie']
    if especies_principais:
        total_2025 = sum(l['receita_2025'] for l in especies_principais)
        total_2024 = sum(l['receita_2024'] for l in especies_principais)
        total_variacao_abs = total_2025 - total_2024
        total_variacao_perc = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else (100 if total_2025 > 0 else 0)
        
        linha_total = {
            'tipo': 'total',
            'especie_codigo': 'TOTAL',
            'nome_especie': 'TOTAL GERAL',
            'receita_2024': total_2024,
            'receita_2025': total_2025,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc,
            'especie_codigo_fmt': 'TOTAL',
            'nome_especie_fmt': 'TOTAL GERAL',
            'receita_2024_fmt': motor.formatar_numero(total_2024),
            'receita_2025_fmt': motor.formatar_numero(total_2025),
            'variacao_abs_fmt': motor.formatar_numero(total_variacao_abs),
            'variacao_perc_fmt': formatar_percentual(total_variacao_perc),
            'tem_alineas': False,
            'qtd_alineas': 0
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({
            'especie_codigo': 'TOTAL', 
            'nome_especie': 'TOTAL GERAL', 
            'receita_2024': total_2024,
            'receita_2025': total_2025,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc
        })
    
    # Dados para PDF (apenas espécies principais para não ficar muito extenso)
    dados_pdf = {
        "head": [['CÓDIGO ESPÉCIE', 'NOME DA ESPÉCIE', f'RECEITA {mes_referencia}/2024', f'RECEITA {mes_referencia}/2025', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": [
            [linha.get('especie_codigo_fmt', ''), linha.get('nome_especie_fmt', ''), 
             linha.get('receita_2024_fmt', 'R$ 0,00'), linha.get('receita_2025_fmt', 'R$ 0,00'),
             linha.get('variacao_abs_fmt', 'R$ 0,00'), linha.get('variacao_perc_fmt', '0,00%')]
            for linha in dados_numericos if linha['tipo'] in ['especie', 'total']
        ]
    }
    
    # NOVO: Gerar resumo das NOUGs com saldos
    resumo_nougs = _gerar_resumo_nougs_com_saldo(df_2025, motor)
    
    print(f"✅ Relatório de receitas de transferências de capital gerado: {len(dados_numericos)} linhas (espécies + alíneas + total)")
    print(f"📋 NOUGs com saldo: {len(resumo_nougs)} unidades")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs

def _obter_nome_especie(df, codigo_especie):
    """
    Obtém o nome da espécie pelo código
    
    Args:
        df: DataFrame com dados
        codigo_especie: Código da espécie
        
    Returns:
        Nome da espécie ou string vazia se não encontrado
    """
    linha_especie = df[df['ESPECIE'] == codigo_especie].first_valid_index()
    if linha_especie is not None:
        nome = df.loc[linha_especie, 'NOSUBFONTERECEITA']
        return str(nome) if pd.notna(nome) else f'Espécie {codigo_especie}'
    return f'Espécie {codigo_especie}'

def _obter_alineas_especie(df_especie):
    """
    Obtém as alíneas de uma espécie
    
    Args:
        df_especie: DataFrame filtrado da espécie
        
    Returns:
        Lista de alíneas únicas
    """
    alineas = []
    
    if 'ALINEA' in df_especie.columns and 'NOALINEA' in df_especie.columns:
        alineas_unicas = df_especie[['ALINEA', 'NOALINEA']].drop_duplicates()
        for _, row in alineas_unicas.iterrows():
            if pd.notna(row['ALINEA']) and pd.notna(row['NOALINEA']):
                alineas.append({
                    'ALINEA': str(row['ALINEA']),
                    'NOALINEA': str(row['NOALINEA'])
                })
    
    return alineas

def _gerar_resumo_nougs_com_saldo(df_2025, motor):
    """
    Gera resumo das NOUGs que possuem saldo de receita líquida em 2025
    
    Args:
        df_2025: DataFrame filtrado para 2025
        motor: Instância do MotorRelatorios
        
    Returns:
        Lista ordenada de NOUGs com seus respectivos saldos
    """
    if 'NOUG' not in df_2025.columns:
        print("⚠️ Coluna 'NOUG' não encontrada")
        return []
    
    # Agrupa por NOUG e soma a receita líquida
    resumo_nougs = df_2025.groupby('NOUG').agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    
    # Filtra apenas NOUGs com saldo positivo
    resumo_nougs = resumo_nougs[resumo_nougs['RECEITA LIQUIDA'] > 0].copy()
    
    if resumo_nougs.empty:
        return []
    
    # Formata os dados
    nougs_com_saldo = []
    for _, row in resumo_nougs.iterrows():
        noug = str(row['NOUG'])
        saldo = float(row['RECEITA LIQUIDA'])
        
        nougs_com_saldo.append({
            'noug': noug,
            'saldo': saldo,
            'saldo_fmt': motor.formatar_numero(saldo)
        })
    
    # Ordena por saldo (maior para menor)
    nougs_com_saldo.sort(key=lambda x: x['saldo'], reverse=True)
    
    return nougs_com_saldo