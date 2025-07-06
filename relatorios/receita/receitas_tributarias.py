"""
Relatório: Receitas Tributárias Líquidas Realizada
Analisa receitas das origens 11 e 71 com desdobramentos por espécie
REGRAS:
- ORIGEM = 11 e 71 apenas
- Desdobramento por ESPÉCIE  
- Se ESPÉCIE = 111 ou 711 → exibir NOALINEA
- Se ESPÉCIE = 112 ou 712 → exibir NORUBRICA
- Valores de RECEITA LÍQUIDA
- Comparativo 2024 vs 2025 com variações absoluta e percentual
- Comparativo mensal acumulado
"""
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receitas_tributarias(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receitas tributárias líquidas com comparativo 2024 vs 2025
    
    REGRAS DE NEGÓCIO:
    - Filtra apenas ORIGEM = 11 e 71 (receitas tributárias)
    - Agrupa por ESPÉCIE primeiro
    - Se ESPÉCIE = 111 ou 711 → desdobra por NOALINEA
    - Se ESPÉCIE = 112 ou 712 → desdobra por NORUBRICA
    - Compara 2024 vs 2025 com variações absoluta e percentual
    - Estrutura hierárquica: espécie → detalhamento (alínea ou rubrica)
    - Comparativo mensal acumulado
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs, comparativo_mensal)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas origens tributárias (11 e 71) para 2025 e 2024
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['ORIGEM'].isin(['11', '71']))
    ]
    df_2024 = df_processar[
        (df_processar['COEXERCICIO'] == 2024) & 
        (df_processar['ORIGEM'].isin(['11', '71']))
    ]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}, [], []
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}, [], []
    
    print("🔍 Processando receitas tributárias (ORIGEM 11 e 71)...")
    
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
        
        # Conta quantos detalhamentos esta espécie tem
        detalhamentos = _obter_detalhamentos_especie(df_especie_2025, especie)
        tem_detalhamentos = len(detalhamentos) > 0
        
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
            'tem_detalhamentos': tem_detalhamentos,
            'qtd_detalhamentos': len(detalhamentos)
        }
        dados_numericos.append(linha_especie)
        dados_para_ia.append(linha_especie)
        
        # Adiciona detalhamentos desta espécie (alíneas ou rubricas)
        for detalhamento in detalhamentos:
            if especie in ['111', '711']:
                # Usar NOALINEA
                codigo_det = detalhamento['ALINEA']
                nome_det = detalhamento['NOALINEA']
                campo_filtro = 'ALINEA'
            elif especie in ['112', '712']:
                # Usar NORUBRICA (ou NOALINEA como fallback)
                codigo_det = detalhamento['RUBRICA']
                nome_det = detalhamento['NORUBRICA']
                # Verifica se realmente existe coluna RUBRICA ou se está usando fallback
                campo_filtro = 'RUBRICA' if 'RUBRICA' in df_especie_2025.columns else 'ALINEA'
            else:
                continue  # Pula espécies que não se encaixam nas regras
                
            # Filtra dados deste detalhamento
            df_det_2025 = df_especie_2025[df_especie_2025[campo_filtro] == codigo_det]
            df_det_2024 = df_especie_2024[df_especie_2024[campo_filtro] == codigo_det] if not df_especie_2024.empty else pd.DataFrame()
            
            valor_2025_det = float(df_det_2025['RECEITA LIQUIDA'].sum())
            valor_2024_det = float(df_det_2024['RECEITA LIQUIDA'].sum()) if not df_det_2024.empty else 0.0
            
            if valor_2025_det == 0 and valor_2024_det == 0:
                continue
                
            variacao_abs_det = valor_2025_det - valor_2024_det
            variacao_perc_det = ((valor_2025_det - valor_2024_det) / valor_2024_det * 100) if valor_2024_det > 0 else (100 if valor_2025_det > 0 else 0)
            
            linha_detalhamento = {
                'tipo': 'detalhamento',
                'especie_pai': especie,
                'detalhamento_codigo': codigo_det,
                'nome_detalhamento': nome_det,
                'receita_2024': valor_2024_det,
                'receita_2025': valor_2025_det,
                'variacao_abs': variacao_abs_det,
                'variacao_perc': variacao_perc_det,
                'especie_codigo_fmt': codigo_det,
                'nome_especie_fmt': nome_det,
                'receita_2024_fmt': motor.formatar_numero(valor_2024_det),
                'receita_2025_fmt': motor.formatar_numero(valor_2025_det),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs_det),
                'variacao_perc_fmt': formatar_percentual(variacao_perc_det),
                'tem_detalhamentos': False,
                'qtd_detalhamentos': 0
            }
            dados_numericos.append(linha_detalhamento)
    
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
            'tem_detalhamentos': False,
            'qtd_detalhamentos': 0
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
    
    # NOVO: Gerar comparativo mensal acumulado
    comparativo_mensal = _gerar_comparativo_mensal_acumulado(df_processar, motor, mes_referencia)
    
    print(f"✅ Relatório de receitas tributárias gerado: {len(dados_numericos)} linhas (espécies + detalhamentos + total)")
    print(f"📋 NOUGs com saldo: {len(resumo_nougs)} unidades")
    print(f"📅 Comparativo mensal: {len(comparativo_mensal)} meses")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs, comparativo_mensal

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

def _obter_detalhamentos_especie(df_especie, codigo_especie):
    """
    Obtém os detalhamentos de uma espécie (alíneas ou rubricas)
    
    Args:
        df_especie: DataFrame filtrado da espécie
        codigo_especie: Código da espécie
        
    Returns:
        Lista de detalhamentos únicos
    """
    detalhamentos = []
    
    if codigo_especie in ['111', '711']:
        # Usar ALINEA/NOALINEA
        if 'ALINEA' in df_especie.columns and 'NOALINEA' in df_especie.columns:
            alineas_unicas = df_especie[['ALINEA', 'NOALINEA']].drop_duplicates()
            for _, row in alineas_unicas.iterrows():
                if pd.notna(row['ALINEA']) and pd.notna(row['NOALINEA']):
                    detalhamentos.append({
                        'ALINEA': str(row['ALINEA']),
                        'NOALINEA': str(row['NOALINEA'])
                    })
                    
    elif codigo_especie in ['112', '712']:
        # Verificar se colunas RUBRICA existem, senão usar ALINEA como fallback
        if 'RUBRICA' in df_especie.columns and 'NORUBRICA' in df_especie.columns:
            rubricas_unicas = df_especie[['RUBRICA', 'NORUBRICA']].drop_duplicates()
            for _, row in rubricas_unicas.iterrows():
                if pd.notna(row['RUBRICA']) and pd.notna(row['NORUBRICA']):
                    detalhamentos.append({
                        'RUBRICA': str(row['RUBRICA']),
                        'NORUBRICA': str(row['NORUBRICA'])
                    })
        else:
            # Fallback: usar ALINEA se RUBRICA não existir
            print(f"⚠️ Colunas RUBRICA/NORUBRICA não encontradas para espécie {codigo_especie}. Usando ALINEA como fallback.")
            if 'ALINEA' in df_especie.columns and 'NOALINEA' in df_especie.columns:
                alineas_unicas = df_especie[['ALINEA', 'NOALINEA']].drop_duplicates()
                for _, row in alineas_unicas.iterrows():
                    if pd.notna(row['ALINEA']) and pd.notna(row['NOALINEA']):
                        detalhamentos.append({
                            'RUBRICA': str(row['ALINEA']),  # Usando ALINEA como RUBRICA
                            'NORUBRICA': str(row['NOALINEA'])  # Usando NOALINEA como NORUBRICA
                        })
    
    return detalhamentos

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

def _gerar_comparativo_mensal_acumulado(df_completo, motor, mes_referencia):
    """
    Gera comparativo mensal acumulado 2024 vs 2025
    
    REGRA: 
    - Mês 1: soma INMES=1
    - Mês 2: soma INMES=1+2 (acumulado)
    - Mês 3: soma INMES=1+2+3 (acumulado)
    - etc.
    
    Args:
        df_completo: DataFrame completo
        motor: Instância do MotorRelatorios
        mes_referencia: Mês de referência atual
        
    Returns:
        Lista com comparativos mensais
    """
    try:
        # Filtra apenas origens tributárias
        df_tributarias = df_completo[df_completo['ORIGEM'].isin(['11', '71'])].copy()
        
        if df_tributarias.empty or 'INMES' not in df_tributarias.columns:
            print("⚠️ Dados insuficientes para comparativo mensal")
            return []
        
        # Obtém meses disponíveis em 2025
        meses_2025 = sorted(df_tributarias[df_tributarias['COEXERCICIO'] == 2025]['INMES'].dropna().unique())
        meses_2024 = sorted(df_tributarias[df_tributarias['COEXERCICIO'] == 2024]['INMES'].dropna().unique())
        
        if not meses_2025:
            return []
        
        max_mes = max(meses_2025)
        print(f"📅 Gerando comparativo mensal até mês {max_mes-1} (referência: {max_mes})")
        
        comparativo = []
        
        # Gera comparativo para cada mês (exceto o último)
        for mes_atual in range(1, max_mes):  # Para até max_mes-1
            if mes_atual not in meses_2025:
                continue
                
            # Calcula saldo acumulado até o mês atual
            # 2025: soma de INMES 1 até mes_atual
            df_2025_acum = df_tributarias[
                (df_tributarias['COEXERCICIO'] == 2025) &
                (df_tributarias['INMES'] <= mes_atual)
            ]
            saldo_2025 = float(df_2025_acum['RECEITA LIQUIDA'].sum()) if 'RECEITA LIQUIDA' in df_2025_acum.columns else 0.0
            
            # 2024: soma de INMES 1 até mes_atual
            df_2024_acum = df_tributarias[
                (df_tributarias['COEXERCICIO'] == 2024) &
                (df_tributarias['INMES'] <= mes_atual)
            ]
            saldo_2024 = float(df_2024_acum['RECEITA LIQUIDA'].sum()) if 'RECEITA LIQUIDA' in df_2024_acum.columns else 0.0
            
            # Calcula variação
            variacao_abs = saldo_2025 - saldo_2024
            variacao_perc = ((saldo_2025 - saldo_2024) / saldo_2024 * 100) if saldo_2024 > 0 else (100 if saldo_2025 > 0 else 0)
            
            comparativo.append({
                'mes': mes_atual,
                'mes_fmt': f"{mes_atual:02d}",
                'saldo_2024': saldo_2024,
                'saldo_2025': saldo_2025,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'saldo_2024_fmt': motor.formatar_numero(saldo_2024),
                'saldo_2025_fmt': motor.formatar_numero(saldo_2025),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc)
            })
        
        print(f"✅ Comparativo mensal gerado: {len(comparativo)} períodos")
        return comparativo
        
    except Exception as e:
        print(f"❌ Erro ao gerar comparativo mensal: {e}")
        return []