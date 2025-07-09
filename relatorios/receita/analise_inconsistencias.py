"""
Relatório: Análise de Inconsistências na Receita
Identifica receitas negativas e receitas em UGs inválidas (INTIPOADM = 1)
"""
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual
from utils.data_loaders import carregar_classificacao_orcamentaria, carregar_fontes

def gerar_relatorio_analise_inconsistencias(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de análise de inconsistências na receita
    
    REGRAS DE NEGÓCIO CORRIGIDAS:
    1. Receitas Negativas: Agrupa por COCONTACORRENTE e soma RECEITA LIQUIDA de todos os meses
       - Se soma total < 0, mostra inconsistência
       - Quebra COCONTACORRENTE: 8 primeiros = receita, resto = fonte
    
    2. Receitas em UGs Inválidas: INTIPOADM = 1 não pode ter RECEITA LIQUIDA (exceto 130101)
       - Agrupa por COCONTACORRENTE e verifica se existe em UG com INTIPOADM = 1
    
    3. Receitas com Fontes de Superávit: Identifica receitas com fontes começando com 3, 4 ou 8
       - Essas fontes indicam superávit e não deveriam ter arrecadação
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_receitas_negativas, dados_ugs_invalidas, mes_referencia, 
                analise_mensal_negativas, analise_mensal_ugs, resumo_geral, 
                dados_fontes_superavit, analise_mensal_superavit)
    """
    try:
        motor = MotorRelatorios(df_completo, tipo_dados='receita')
        df_processar = motor.filtrar_por_noug(noug_selecionada)
        
        print("🔍 Iniciando análise de inconsistências...")
        
        # Verifica colunas necessárias - CORREÇÃO: usar INTIPOADM
        colunas_necessarias = ['COCONTACORRENTE', 'RECEITA LIQUIDA', 'INTIPOADM', 'COEXERCICIO', 'INMES', 'NOUG']
        for coluna in colunas_necessarias:
            if coluna not in df_processar.columns:
                print(f"⚠️ Coluna '{coluna}' não encontrada")
                return [], [], "05/2025", [], [], {}, [], []
        
        # Calcula mês de referência de forma mais robusta
        try:
            mes_referencia = obter_mes_numero(df_processar)
            
            # Converte para int se for string
            if isinstance(mes_referencia, str):
                mes_referencia = int(mes_referencia)
            
            # Validação do mês (deve estar entre 1 e 12)
            if not isinstance(mes_referencia, int) or mes_referencia < 1 or mes_referencia > 12:
                mes_referencia = df_processar['INMES'].max() if 'INMES' in df_processar.columns else 5
                
        except (ValueError, TypeError, KeyError):
            # Fallback: pega o maior mês disponível ou default 5
            try:
                mes_referencia = int(df_processar['INMES'].max()) if 'INMES' in df_processar.columns else 5
            except:
                mes_referencia = 5
        
        mes_referencia_str = f"{mes_referencia:02d}/2025"
        
        # Carrega dados auxiliares para nomes
        classificacao_orcamentaria = carregar_classificacao_orcamentaria()
        fontes = carregar_fontes()
        
        print(f"📊 Classificações carregadas: {len(classificacao_orcamentaria)} receitas, {len(fontes)} fontes")
        
        # 1. ANÁLISE DE RECEITAS NEGATIVAS - CORRIGIDA
        print("\n1️⃣ Analisando receitas negativas (agrupado por COCONTACORRENTE)...")
        dados_receitas_negativas = _analisar_receitas_negativas_corrigido(
            df_processar, classificacao_orcamentaria, fontes, motor
        )
        
        # 2. ANÁLISE DE UGS INVÁLIDAS - CORRIGIDA  
        print("\n2️⃣ Analisando receitas em UGs inválidas (INTIPOADM = 1, exceto 130101)...")
        dados_ugs_invalidas = _analisar_ugs_invalidas_corrigido(
            df_processar, classificacao_orcamentaria, fontes, motor
        )
        
        # 3. ANÁLISE DE FONTES DE SUPERÁVIT - NOVA
        print("\n3️⃣ Analisando receitas com fontes de superávit (3xx, 4xx, 8xx)...")
        dados_fontes_superavit = _analisar_fontes_superavit(
            df_processar, classificacao_orcamentaria, fontes, motor
        )
        
        # 4. ANÁLISE MENSAL - BASEADA NOS DADOS CORRIGIDOS
        print("\n📅 Gerando análise mensal...")
        analise_mensal_negativas = _gerar_analise_mensal_corrigida(
            df_processar, 'receitas_negativas', dados_receitas_negativas
        )
        analise_mensal_ugs = _gerar_analise_mensal_corrigida(
            df_processar, 'ugs_invalidas', dados_ugs_invalidas
        )
        analise_mensal_superavit = _gerar_analise_mensal_corrigida(
            df_processar, 'fontes_superavit', dados_fontes_superavit
        )
        
        # 5. RESUMO GERAL - VERSÃO MAIS ROBUSTA
        print("\n📊 Calculando resumo geral...")
        
        # Calcula valores sem formatação primeiro
        total_receitas_negativas_2024 = len([r for r in dados_receitas_negativas if 2024 in r.get('exercicios', [])])
        total_receitas_negativas_2025 = len([r for r in dados_receitas_negativas if 2025 in r.get('exercicios', [])])
        total_ugs_invalidas_2024 = len([r for r in dados_ugs_invalidas if 2024 in r.get('exercicios', [])])
        total_ugs_invalidas_2025 = len([r for r in dados_ugs_invalidas if 2025 in r.get('exercicios', [])])
        total_fontes_superavit_2024 = len([r for r in dados_fontes_superavit if 2024 in r.get('exercicios', [])])
        total_fontes_superavit_2025 = len([r for r in dados_fontes_superavit if 2025 in r.get('exercicios', [])])
        
        valor_total_negativo_2024 = sum([r.get('valor_2024', 0) for r in dados_receitas_negativas])
        valor_total_negativo_2025 = sum([r.get('valor_2025', 0) for r in dados_receitas_negativas])
        valor_total_ug_invalida_2024 = sum([r.get('valor_2024', 0) for r in dados_ugs_invalidas])
        valor_total_ug_invalida_2025 = sum([r.get('valor_2025', 0) for r in dados_ugs_invalidas])
        valor_total_superavit_2024 = sum([r.get('valor_2024', 0) for r in dados_fontes_superavit])
        valor_total_superavit_2025 = sum([r.get('valor_2025', 0) for r in dados_fontes_superavit])
        
        # Monta o dicionário completo de uma vez
        resumo_geral = {
            # Contadores
            'total_receitas_negativas_2024': total_receitas_negativas_2024,
            'total_receitas_negativas_2025': total_receitas_negativas_2025,
            'total_ugs_invalidas_2024': total_ugs_invalidas_2024,
            'total_ugs_invalidas_2025': total_ugs_invalidas_2025,
            'total_fontes_superavit_2024': total_fontes_superavit_2024,
            'total_fontes_superavit_2025': total_fontes_superavit_2025,
            
            # Valores numéricos
            'valor_total_negativo_2024': valor_total_negativo_2024,
            'valor_total_negativo_2025': valor_total_negativo_2025,
            'valor_total_ug_invalida_2024': valor_total_ug_invalida_2024,
            'valor_total_ug_invalida_2025': valor_total_ug_invalida_2025,
            'valor_total_superavit_2024': valor_total_superavit_2024,
            'valor_total_superavit_2025': valor_total_superavit_2025,
            
            # Valores formatados (adicionados diretamente)
            'valor_total_negativo_2024_fmt': motor.formatar_numero(valor_total_negativo_2024),
            'valor_total_negativo_2025_fmt': motor.formatar_numero(valor_total_negativo_2025),
            'valor_total_ug_invalida_2024_fmt': motor.formatar_numero(valor_total_ug_invalida_2024),
            'valor_total_ug_invalida_2025_fmt': motor.formatar_numero(valor_total_ug_invalida_2025),
            'valor_total_superavit_2024_fmt': motor.formatar_numero(valor_total_superavit_2024),
            'valor_total_superavit_2025_fmt': motor.formatar_numero(valor_total_superavit_2025)
        }
        
        print(f"✅ Análise concluída:")
        print(f"   📍 Receitas negativas: {len(dados_receitas_negativas)} contas correntes")
        print(f"   📍 UGs inválidas: {len(dados_ugs_invalidas)} contas correntes")
        print(f"   📍 Fontes de superávit: {len(dados_fontes_superavit)} contas correntes")
        
        return (dados_receitas_negativas, dados_ugs_invalidas, mes_referencia_str, 
                analise_mensal_negativas, analise_mensal_ugs, resumo_geral,
                dados_fontes_superavit, analise_mensal_superavit)
    
    except Exception as e:
        print(f"❌ Erro na análise de inconsistências: {e}")
        import traceback
        traceback.print_exc()
        return [], [], "05/2025", [], [], {}, [], []

def _analisar_fontes_superavit(df_processar, classificacao_orcamentaria, fontes, motor):
    """
    Analisa receitas com fontes de superávit (começando com 3, 4 ou 8)
    Essas fontes não deveriam ter arrecadação
    """
    dados = []
    
    # Cria uma cópia para processar
    df_fontes = df_processar.copy()
    
    # Extrai o código da fonte (parte depois dos 8 primeiros dígitos)
    df_fontes['codigo_fonte'] = df_fontes['COCONTACORRENTE'].astype(str).str[8:]
    
    # Identifica se a fonte começa com 3, 4 ou 8
    df_fontes['eh_fonte_superavit'] = df_fontes['codigo_fonte'].str.match(r'^[348]', na=False)
    
    # Filtra apenas registros com fontes de superávit
    df_superavit = df_fontes[df_fontes['eh_fonte_superavit']].copy()
    
    if len(df_superavit) == 0:
        print("   ✅ Nenhuma receita com fonte de superávit (3xx, 4xx, 8xx) encontrada")
        return dados
    
    # Agrupa por COCONTACORRENTE e COEXERCICIO
    df_agrupado = df_superavit.groupby(['COCONTACORRENTE', 'COEXERCICIO']).agg({
        'RECEITA LIQUIDA': 'sum',
        'NOUG': 'first',
        'INMES': 'max',
        'codigo_fonte': 'first'
    }).reset_index()
    
    print(f"   📊 {len(df_agrupado)} combinações COCONTACORRENTE x EXERCICIO com fontes de superávit analisadas")
    
    # Identifica contas correntes com receita em fontes de superávit
    contas_superavit = {}
    
    for _, linha in df_agrupado.iterrows():
        conta_corrente = str(linha['COCONTACORRENTE']).strip()
        exercicio = int(linha['COEXERCICIO'])
        valor_total = float(linha['RECEITA LIQUIDA'])
        
        # Só considera se tem valor de receita (positivo ou negativo)
        if valor_total != 0:
            if conta_corrente not in contas_superavit:
                contas_superavit[conta_corrente] = {
                    'conta_corrente': conta_corrente,
                    'exercicios': [],
                    'valores': {},
                    'nougs': set(),
                    'meses': set(),
                    'codigo_fonte': str(linha['codigo_fonte'])
                }
            
            contas_superavit[conta_corrente]['exercicios'].append(exercicio)
            contas_superavit[conta_corrente]['valores'][f'valor_{exercicio}'] = valor_total
            contas_superavit[conta_corrente]['nougs'].add(str(linha['NOUG']))
            contas_superavit[conta_corrente]['meses'].add(int(linha['INMES']))
    
    print(f"   💰 {len(contas_superavit)} contas correntes com arrecadação em fontes de superávit encontradas")
    
    # Processa cada conta corrente com fonte de superávit
    for conta_corrente, info in contas_superavit.items():
        # Quebra COCONTACORRENTE
        if len(conta_corrente) >= 8:
            codigo_receita = conta_corrente[:8]
            codigo_fonte = info['codigo_fonte']
            
            # Busca nomes
            nome_receita = _buscar_nome_receita(codigo_receita, classificacao_orcamentaria)
            nome_fonte = _buscar_nome_fonte(codigo_fonte, fontes) if codigo_fonte else 'Sem Fonte'
            
            # Calcula valores para cada exercício
            valor_2024 = info['valores'].get('valor_2024', 0)
            valor_2025 = info['valores'].get('valor_2025', 0)
            
            # Identifica o tipo de fonte de superávit
            if codigo_fonte.startswith('3'):
                tipo_superavit = 'Recursos Próprios'
            elif codigo_fonte.startswith('4'):
                tipo_superavit = 'Recursos Destinados'
            elif codigo_fonte.startswith('8'):
                tipo_superavit = 'Recursos de Exercícios Anteriores'
            else:
                tipo_superavit = 'Superávit'
            
            dados.append({
                'conta_corrente': conta_corrente,
                'codigo_receita': codigo_receita,
                'nome_receita': nome_receita,
                'codigo_fonte': codigo_fonte,
                'nome_fonte': nome_fonte,
                'tipo_superavit': tipo_superavit,
                'exercicios': info['exercicios'],
                'valor_2024': valor_2024,
                'valor_2025': valor_2025,
                'valor_2024_fmt': motor.formatar_numero(valor_2024),
                'valor_2025_fmt': motor.formatar_numero(valor_2025),
                'nougs': ', '.join(sorted(info['nougs'])),
                'meses': ', '.join([f"{m:02d}" for m in sorted(info['meses'])]),
                'tipo': 'fonte_superavit'
            })
    
    # Ordena por código da fonte e depois por valor
    return sorted(dados, key=lambda x: (x['codigo_fonte'], -abs(max(x['valor_2024'], x['valor_2025']))))

def _analisar_receitas_negativas_corrigido(df_processar, classificacao_orcamentaria, fontes, motor):
    """
    Analisa receitas com valor líquido negativo - VERSÃO CORRIGIDA
    Agrupa por COCONTACORRENTE e soma todos os valores por exercício
    """
    dados = []
    
    # Agrupa por COCONTACORRENTE e COEXERCICIO, somando RECEITA LIQUIDA
    df_agrupado = df_processar.groupby(['COCONTACORRENTE', 'COEXERCICIO']).agg({
        'RECEITA LIQUIDA': 'sum',
        'NOUG': 'first',  # Pega a primeira NOUG encontrada
        'INMES': 'max'    # Pega o último mês para referência
    }).reset_index()
    
    print(f"   📊 {len(df_agrupado)} combinações COCONTACORRENTE x EXERCICIO analisadas")
    
    # Identifica contas correntes que ficaram negativas em algum exercício
    contas_negativas = {}
    
    for _, linha in df_agrupado.iterrows():
        conta_corrente = str(linha['COCONTACORRENTE']).strip()
        exercicio = int(linha['COEXERCICIO'])
        valor_total = float(linha['RECEITA LIQUIDA'])
        
        if valor_total < 0:  # Só considera se ficou negativo
            if conta_corrente not in contas_negativas:
                contas_negativas[conta_corrente] = {
                    'conta_corrente': conta_corrente,
                    'exercicios': [],
                    'valores': {},
                    'nougs': set(),
                    'meses': set()
                }
            
            contas_negativas[conta_corrente]['exercicios'].append(exercicio)
            contas_negativas[conta_corrente]['valores'][f'valor_{exercicio}'] = valor_total
            contas_negativas[conta_corrente]['nougs'].add(str(linha['NOUG']))
            contas_negativas[conta_corrente]['meses'].add(int(linha['INMES']))
    
    print(f"   🚨 {len(contas_negativas)} contas correntes com saldo negativo encontradas")
    
    # Processa cada conta corrente negativa
    for conta_corrente, info in contas_negativas.items():
        # Quebra COCONTACORRENTE: 8 primeiros = receita, resto = fonte
        if len(conta_corrente) >= 8:
            codigo_receita = conta_corrente[:8]
            codigo_fonte = conta_corrente[8:] if len(conta_corrente) > 8 else ''
            
            # Busca nomes
            nome_receita = _buscar_nome_receita(codigo_receita, classificacao_orcamentaria)
            nome_fonte = _buscar_nome_fonte(codigo_fonte, fontes) if codigo_fonte else 'Sem Fonte'
            
            # Calcula valores para cada exercício
            valor_2024 = info['valores'].get('valor_2024', 0)
            valor_2025 = info['valores'].get('valor_2025', 0)
            
            dados.append({
                'conta_corrente': conta_corrente,
                'codigo_receita': codigo_receita,
                'nome_receita': nome_receita,
                'codigo_fonte': codigo_fonte,
                'nome_fonte': nome_fonte,
                'exercicios': info['exercicios'],
                'valor_2024': valor_2024,
                'valor_2025': valor_2025,
                'valor_2024_fmt': motor.formatar_numero(valor_2024),
                'valor_2025_fmt': motor.formatar_numero(valor_2025),
                'nougs': ', '.join(sorted(info['nougs'])),
                'meses': ', '.join([f"{m:02d}" for m in sorted(info['meses'])]),
                'tipo': 'receita_negativa'
            })
    
    # Ordena por maior valor negativo (valor absoluto)
    return sorted(dados, key=lambda x: min(x['valor_2024'], x['valor_2025']))

def _analisar_ugs_invalidas_corrigido(df_processar, classificacao_orcamentaria, fontes, motor):
    """
    Analisa receitas em UGs com INTIPOADM = 1 - VERSÃO CORRIGIDA
    Agrupa por COCONTACORRENTE e verifica se existe em UG inválida (exceto COUG 130101)
    """
    dados = []
    
    # Filtra apenas registros com INTIPOADM = 1 (com tratamento de string/espaços)
    # E EXCLUI COUG = 130101 (que é permitido ter receita)
    df_intipoadm_1 = df_processar[
        (df_processar['INTIPOADM'].astype(str).str.strip() == '1') &
        (df_processar['COUG'] != 130101)  # CORREÇÃO: Exclui COUG 130101
    ].copy()
    
    if len(df_intipoadm_1) == 0:
        print("   ✅ Nenhuma UG com INTIPOADM = 1 encontrada (excluindo COUG 130101)")
        return dados
    
    # Agrupa por COCONTACORRENTE e COEXERCICIO para UGs com INTIPOADM = 1 (exceto 130101)
    df_agrupado = df_intipoadm_1.groupby(['COCONTACORRENTE', 'COEXERCICIO']).agg({
        'RECEITA LIQUIDA': 'sum',
        'NOUG': 'first',
        'INMES': 'max',
        'INTIPOADM': 'first',
        'COUG': 'first'  # Adiciona COUG para debug
    }).reset_index()
    
    print(f"   📊 {len(df_agrupado)} combinações COCONTACORRENTE x EXERCICIO em UGs INTIPOADM=1 analisadas (excluindo COUG 130101)")
    
    # Identifica contas correntes com receita em UGs inválidas
    contas_invalidas = {}
    
    for _, linha in df_agrupado.iterrows():
        conta_corrente = str(linha['COCONTACORRENTE']).strip()
        exercicio = int(linha['COEXERCICIO'])
        valor_total = float(linha['RECEITA LIQUIDA'])
        coug = linha['COUG']
        
        # DUPLA VERIFICAÇÃO: Se por algum motivo ainda chegou COUG 130101, pula
        if coug == 130101:
            continue
            
        # Se tem qualquer valor de receita (positivo ou negativo), é inconsistência
        if valor_total != 0:
            if conta_corrente not in contas_invalidas:
                contas_invalidas[conta_corrente] = {
                    'conta_corrente': conta_corrente,
                    'exercicios': [],
                    'valores': {},
                    'nougs': set(),
                    'meses': set(),
                    'intipoadm': str(linha['INTIPOADM']).strip(),
                    'coug': coug  # Para debug
                }
            
            contas_invalidas[conta_corrente]['exercicios'].append(exercicio)
            contas_invalidas[conta_corrente]['valores'][f'valor_{exercicio}'] = valor_total
            contas_invalidas[conta_corrente]['nougs'].add(str(linha['NOUG']))
            contas_invalidas[conta_corrente]['meses'].add(int(linha['INMES']))
    
    print(f"   ⚠️ {len(contas_invalidas)} contas correntes em UGs inválidas encontradas (excluindo COUG 130101)")
    
    # Processa cada conta corrente inválida
    for conta_corrente, info in contas_invalidas.items():
        # Quebra COCONTACORRENTE
        if len(conta_corrente) >= 8:
            codigo_receita = conta_corrente[:8]
            codigo_fonte = conta_corrente[8:] if len(conta_corrente) > 8 else ''
            
            # Busca nomes
            nome_receita = _buscar_nome_receita(codigo_receita, classificacao_orcamentaria)
            nome_fonte = _buscar_nome_fonte(codigo_fonte, fontes) if codigo_fonte else 'Sem Fonte'
            
            # Calcula valores para cada exercício
            valor_2024 = info['valores'].get('valor_2024', 0)
            valor_2025 = info['valores'].get('valor_2025', 0)
            
            dados.append({
                'conta_corrente': conta_corrente,
                'codigo_receita': codigo_receita,
                'nome_receita': nome_receita,
                'codigo_fonte': codigo_fonte,
                'nome_fonte': nome_fonte,
                'intipoadm': info['intipoadm'],
                'exercicios': info['exercicios'],
                'valor_2024': valor_2024,
                'valor_2025': valor_2025,
                'valor_2024_fmt': motor.formatar_numero(valor_2024),
                'valor_2025_fmt': motor.formatar_numero(valor_2025),
                'nougs': ', '.join(sorted(info['nougs'])),
                'meses': ', '.join([f"{m:02d}" for m in sorted(info['meses'])]),
                'tipo': 'ug_invalida',
                'coug': info['coug']  # Para debug
            })
    
    # Debug: verifica se ainda tem COUG 130101
    coug_130101_encontrados = [item for item in dados if item['coug'] == 130101]
    if coug_130101_encontrados:
        print(f"⚠️ ATENÇÃO: Ainda encontrados {len(coug_130101_encontrados)} registros com COUG 130101!")
        for item in coug_130101_encontrados:
            print(f"   Debug: {item['conta_corrente']} - COUG: {item['coug']} - NOUG: {item['nougs']}")
    
    # Ordena por maior valor absoluto
    return sorted(dados, key=lambda x: abs(max(x['valor_2024'], x['valor_2025'])), reverse=True)

def _gerar_analise_mensal_corrigida(df_processar, tipo_analise, dados_inconsistencias):
    """
    Gera análise mensal baseada nos dados de inconsistências já processados
    """
    analise = []
    
    if not dados_inconsistencias:
        return analise
    
    # Obtém todas as contas correntes problemáticas
    contas_problematicas = [item['conta_corrente'] for item in dados_inconsistencias]
    
    if not contas_problematicas:
        return analise
    
    # Filtra dados apenas das contas problemáticas
    df_filtrado = df_processar[df_processar['COCONTACORRENTE'].isin(contas_problematicas)]
    
    if tipo_analise == 'ugs_invalidas':
        # Para UGs inválidas, filtra também por INTIPOADM = 1 E exclui COUG 130101
        df_filtrado = df_filtrado[
            (df_filtrado['INTIPOADM'].astype(str).str.strip() == '1') &
            (df_filtrado['COUG'] != 130101)  # CORREÇÃO: Exclui COUG 130101
        ]
    elif tipo_analise == 'fontes_superavit':
        # Para fontes de superávit, filtra apenas as que começam com 3, 4 ou 8
        df_filtrado['codigo_fonte'] = df_filtrado['COCONTACORRENTE'].astype(str).str[8:]
        df_filtrado = df_filtrado[df_filtrado['codigo_fonte'].str.match(r'^[348]', na=False)]
    
    # Agrupa por mês e exercício
    df_mensal = df_filtrado.groupby(['COEXERCICIO', 'INMES']).agg({
        'COCONTACORRENTE': 'count',  # Conta registros únicos
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    
    # Obtém range de meses
    if len(df_mensal) > 0:
        max_mes = df_mensal['INMES'].max()
        
        for mes in range(1, max_mes + 1):
            dados_2024 = df_mensal[(df_mensal['COEXERCICIO'] == 2024) & (df_mensal['INMES'] == mes)]
            dados_2025 = df_mensal[(df_mensal['COEXERCICIO'] == 2025) & (df_mensal['INMES'] == mes)]
            
            count_2024 = dados_2024['COCONTACORRENTE'].sum() if len(dados_2024) > 0 else 0
            count_2025 = dados_2025['COCONTACORRENTE'].sum() if len(dados_2025) > 0 else 0
            valor_2024 = dados_2024['RECEITA LIQUIDA'].sum() if len(dados_2024) > 0 else 0.0
            valor_2025 = dados_2025['RECEITA LIQUIDA'].sum() if len(dados_2025) > 0 else 0.0
            
            if count_2024 > 0 or count_2025 > 0:
                analise.append({
                    'mes': mes,
                    'mes_fmt': f"{mes:02d}",
                    'count_2024': int(count_2024),
                    'count_2025': int(count_2025),
                    'valor_2024': float(valor_2024),
                    'valor_2025': float(valor_2025),
                    'valor_2024_fmt': f"R$ {valor_2024:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'valor_2025_fmt': f"R$ {valor_2025:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'variacao_count': int(count_2025) - int(count_2024),
                    'variacao_valor': float(valor_2025) - float(valor_2024),
                    'variacao_valor_fmt': f"R$ {(valor_2025 - valor_2024):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                })
    
    return analise

def _buscar_nome_receita(codigo_receita, classificacao_orcamentaria):
    """Busca nome da receita na classificação orçamentária"""
    return classificacao_orcamentaria.get(codigo_receita, f'Receita {codigo_receita}')

def _buscar_nome_fonte(codigo_fonte, fontes):
    """Busca nome da fonte"""
    return fontes.get(codigo_fonte, f'Fonte {codigo_fonte}')