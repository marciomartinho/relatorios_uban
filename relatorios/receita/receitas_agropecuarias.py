"""
Relatório: Receitas Agropecuárias Líquidas Realizada
Analisa receitas das origens 14 e 74 com desdobramentos por alínea
REGRAS:
- ORIGEM = 14 e 74 (receitas agropecuárias)
- Desdobramento por ALINEA e NOALINEA
- Valores de RECEITA LÍQUIDA
- Comparativo 2024 vs 2025 com variações absoluta e percentual
- Comparativo mensal acumulado
- Estrutura sempre expandida (sem botões de expansão)
"""
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receitas_agropecuarias(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receitas agropecuárias líquidas com comparativo 2024 vs 2025
    
    REGRAS DE NEGÓCIO:
    - Filtra apenas ORIGEM = 14 e 74 (receitas agropecuárias)
    - Agrupa por ESPÉCIE primeiro
    - Desdobra por ALINEA e NOALINEA
    - Compara 2024 vs 2025 com variações absoluta e percentual
    - Estrutura hierárquica: espécie → alíneas (sempre expandida)
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
    
    # Filtra apenas origens agropecuárias (14 e 74) para 2025 e 2024
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['ORIGEM'].isin(['14', '74']))
    ]
    df_2024 = df_processar[
        (df_processar['COEXERCICIO'] == 2024) & 
        (df_processar['ORIGEM'].isin(['14', '74']))
    ]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}, [], []
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}, [], []
    
    # Verifica se as colunas ALINEA e NOALINEA existem
    if 'ALINEA' not in df_2025.columns or 'NOALINEA' not in df_2025.columns:
        print("⚠️ Colunas 'ALINEA' ou 'NOALINEA' não encontradas na planilha")
        return [], obter_mes_numero(df_processar), [], {}, [], []
    
    print("🔍 Processando receitas agropecuárias (ORIGEM 14 e 74)...")
    
    # Debug: Verificar estrutura dos dados
    print(f"📊 Dados 2025 - Total de registros: {len(df_2025)}")
    print(f"📊 Dados 2024 - Total de registros: {len(df_2024)}")
    
    if not df_2025.empty:
        print(f"📊 Colunas disponíveis: {list(df_2025.columns)}")
        print(f"📊 Espécies em 2025: {sorted(df_2025['ESPECIE'].dropna().unique())}")
        if 'ALINEA' in df_2025.columns:
            print(f"📊 Alíneas em 2025: {sorted(df_2025['ALINEA'].dropna().unique())}")
    
    if not df_2024.empty:
        print(f"📊 Espécies em 2024: {sorted(df_2024['ESPECIE'].dropna().unique())}")
        if 'ALINEA' in df_2024.columns:
            print(f"📊 Alíneas em 2024: {sorted(df_2024['ALINEA'].dropna().unique())}")
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada espécie encontrada - CORREÇÃO: considerar espécies de AMBOS os anos
    especies_2025 = set(df_2025['ESPECIE'].dropna().unique())
    especies_2024 = set(df_2024['ESPECIE'].dropna().unique()) if not df_2024.empty else set()
    todas_especies = sorted(especies_2025.union(especies_2024))
    
    print(f"📊 Espécies combinadas (2024+2025): {todas_especies}")
    
    for especie in todas_especies:
        print(f"\n🏛️ Processando espécie: {especie}")
        
        # Busca nome da espécie - priorizar 2025, depois 2024
        nome_especie = _obter_nome_especie(df_2025, especie)
        if not nome_especie and not df_2024.empty:
            nome_especie = _obter_nome_especie(df_2024, especie)
        if not nome_especie:
            print(f"   ❌ Nome da espécie não encontrado")
            continue
            
        print(f"   📝 Nome: {nome_especie}")
            
        # Filtra dados desta espécie
        df_especie_2025 = df_2025[df_2025['ESPECIE'] == especie]
        df_especie_2024 = df_2024[df_2024['ESPECIE'] == especie] if not df_2024.empty else pd.DataFrame()
        
        print(f"   📊 Registros 2025: {len(df_especie_2025)}")
        print(f"   📊 Registros 2024: {len(df_especie_2024)}")
        
        # Calcula valores da espécie (totais)
        valor_2025_especie = float(df_especie_2025['RECEITA LIQUIDA'].sum())
        valor_2024_especie = float(df_especie_2024['RECEITA LIQUIDA'].sum()) if not df_especie_2024.empty else 0.0
        
        print(f"   💰 Total 2025: R$ {valor_2025_especie:,.2f}")
        print(f"   💰 Total 2024: R$ {valor_2024_especie:,.2f}")
        
        if valor_2025_especie == 0 and valor_2024_especie == 0:
            print(f"   ⚠️ Valores zerados - pulando espécie")
            continue
            
        # Calcula variações da espécie
        variacao_abs_especie = valor_2025_especie - valor_2024_especie
        variacao_perc_especie = ((valor_2025_especie - valor_2024_especie) / valor_2024_especie * 100) if valor_2024_especie > 0 else (100 if valor_2025_especie > 0 else 0)
        
        # CORREÇÃO: Obtém alíneas de AMBOS os anos
        alineas_2025 = _obter_alineas_especie(df_especie_2025)
        alineas_2024 = _obter_alineas_especie(df_especie_2024) if not df_especie_2024.empty else []
        
        # Combinar alíneas de ambos os anos para garantir que todas apareçam
        todas_alineas = {}
        
        # Adicionar alíneas de 2025
        for alinea in alineas_2025:
            todas_alineas[alinea['ALINEA']] = alinea
            
        # Adicionar alíneas de 2024 que não estão em 2025
        for alinea in alineas_2024:
            if alinea['ALINEA'] not in todas_alineas:
                todas_alineas[alinea['ALINEA']] = alinea
        
        # Converter de volta para lista ordenada
        alineas = [todas_alineas[codigo] for codigo in sorted(todas_alineas.keys())]
        tem_alineas = len(alineas) > 0
        
        print(f"   🔖 Alíneas combinadas (2024+2025): {[a['ALINEA'] for a in alineas]}")
        print(f"   📊 Total de alíneas: {len(alineas)}")
        
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
            
            print(f"      🔖 Processando alínea: {codigo_alinea} - {nome_alinea}")
                
            # Filtra dados desta alínea
            df_alinea_2025 = df_especie_2025[df_especie_2025['ALINEA'] == codigo_alinea]
            df_alinea_2024 = df_especie_2024[df_especie_2024['ALINEA'] == codigo_alinea] if not df_especie_2024.empty else pd.DataFrame()
            
            valor_2025_alinea = float(df_alinea_2025['RECEITA LIQUIDA'].sum())
            valor_2024_alinea = float(df_alinea_2024['RECEITA LIQUIDA'].sum()) if not df_alinea_2024.empty else 0.0
            
            print(f"         💰 Alínea 2025: R$ {valor_2025_alinea:,.2f}")
            print(f"         💰 Alínea 2024: R$ {valor_2024_alinea:,.2f}")
            
            if valor_2025_alinea == 0 and valor_2024_alinea == 0:
                print(f"         ⚠️ Valores zerados - pulando alínea")
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
                'especie_codigo_fmt': f"{codigo_alinea}YY",  # ADICIONADO: YY no final para alíneas
                'nome_especie_fmt': nome_alinea,
                'receita_2024_fmt': motor.formatar_numero(valor_2024_alinea),
                'receita_2025_fmt': motor.formatar_numero(valor_2025_alinea),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs_alinea),
                'variacao_perc_fmt': formatar_percentual(variacao_perc_alinea),
                'tem_alineas': False,
                'qtd_alineas': 0
            }
            dados_numericos.append(linha_alinea)
            print(f"         ✅ Alínea adicionada ao relatório")
    
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
    
    # NOVO: Gerar comparativo mensal acumulado
    comparativo_mensal = _gerar_comparativo_mensal_acumulado(df_processar, motor, mes_referencia)
    
    print(f"✅ Relatório de receitas agropecuárias gerado: {len(dados_numericos)} linhas (espécies + alíneas + total)")
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
        # Debug: mostrar dados disponíveis
        print(f"🔍 DEBUG: Analisando alíneas da espécie...")
        print(f"   Total de registros: {len(df_especie)}")
        
        # Filtrar apenas registros válidos (com valores não nulos)
        df_valido = df_especie[
            (pd.notna(df_especie['ALINEA'])) & 
            (pd.notna(df_especie['NOALINEA'])) &
            (df_especie['ALINEA'] != '') &
            (df_especie['NOALINEA'] != '')
        ].copy()
        
        print(f"   Registros válidos: {len(df_valido)}")
        
        if not df_valido.empty:
            # Verificar valores únicos de ALINEA
            alineas_disponiveis = df_valido['ALINEA'].unique()
            print(f"   Alíneas encontradas: {sorted(alineas_disponiveis)}")
            
            # Agrupar por ALINEA e pegar o primeiro NOALINEA de cada grupo
            alineas_unicas = df_valido.groupby('ALINEA').agg({
                'NOALINEA': 'first'
            }).reset_index()
            
            print(f"   Alíneas únicas após agrupamento: {len(alineas_unicas)}")
            
            for _, row in alineas_unicas.iterrows():
                codigo_alinea = str(row['ALINEA']).strip()
                nome_alinea = str(row['NOALINEA']).strip()
                
                # Validar se não são strings vazias
                if codigo_alinea and nome_alinea and codigo_alinea != 'nan' and nome_alinea != 'nan':
                    alineas.append({
                        'ALINEA': codigo_alinea,
                        'NOALINEA': nome_alinea
                    })
                    print(f"   ✅ Adicionada: {codigo_alinea} - {nome_alinea}")
                else:
                    print(f"   ❌ Ignorada (inválida): {codigo_alinea} - {nome_alinea}")
        else:
            print("   ⚠️ Nenhum registro válido encontrado")
    else:
        print("   ❌ Colunas ALINEA ou NOALINEA não encontradas")
    
    print(f"   🎯 Total de alíneas retornadas: {len(alineas)}")
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
        # Filtra apenas origens agropecuárias (14 e 74)
        df_agropecuarias = df_completo[df_completo['ORIGEM'].isin(['14', '74'])].copy()
        
        if df_agropecuarias.empty or 'INMES' not in df_agropecuarias.columns:
            print("⚠️ Dados insuficientes para comparativo mensal")
            return []
        
        # Obtém meses disponíveis em 2025
        meses_2025 = sorted(df_agropecuarias[df_agropecuarias['COEXERCICIO'] == 2025]['INMES'].dropna().unique())
        meses_2024 = sorted(df_agropecuarias[df_agropecuarias['COEXERCICIO'] == 2024]['INMES'].dropna().unique())
        
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
            df_2025_acum = df_agropecuarias[
                (df_agropecuarias['COEXERCICIO'] == 2025) &
                (df_agropecuarias['INMES'] <= mes_atual)
            ]
            saldo_2025 = float(df_2025_acum['RECEITA LIQUIDA'].sum()) if 'RECEITA LIQUIDA' in df_2025_acum.columns else 0.0
            
            # 2024: soma de INMES 1 até mes_atual
            df_2024_acum = df_agropecuarias[
                (df_agropecuarias['COEXERCICIO'] == 2024) &
                (df_agropecuarias['INMES'] <= mes_atual)
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