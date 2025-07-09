"""
Relatório: Receita por Conta Corrente APRIMORADO COM EXPANSÃO DE FONTES E FILTRO DE CATEGORIAS
Analisa receita usando substring do COCONTACORRENTE e busca nomes na classificação orçamentária
NOVO: Inclui dados de 2024, variação absoluta e percentual + expansão de fontes + filtro de categorias
"""
import os
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receita_conta_corrente(df_completo, estrutura_hierarquica=None, noug_selecionada=None, categorias_selecionadas=None):
    """
    Gera relatório de receita por conta corrente com comparativo 2024 vs 2025 + expansão de fontes
    
    REGRAS DE NEGÓCIO:
    - COCONTACORRENTE tem 17 caracteres
    - Posições 1-8: RECEITA (código da receita)
    - Posições 9-17: FONTE (código da fonte)
    - Busca nome da receita na planilha CLASSIFICACAO_ORCAMENTARIA
    - Busca nome da fonte na planilha FONTE.xlsx
    - NOVO: Compara 2024 vs 2025 com variações absoluta e percentual
    - NOVO: Estrutura hierárquica receita → fontes com botão de expansão
    - NOVO: Filtro por categorias de receitas
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        categorias_selecionadas: Lista de prefixos de categorias selecionadas (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Define mapeamento de categorias se não fornecido
    if categorias_selecionadas is None:
        # Por padrão, todas as categorias estão selecionadas
        categorias_selecionadas = ['11', '71', '12', '72', '13', '73', '14', '74', 
                                 '15', '75', '16', '76', '17', '77', '19', '79',
                                 '21', '22', '23', '24']
    
    # Filtra dados de 2025 e 2024
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    df_2024 = df_processar[df_processar['COEXERCICIO'] == 2024]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    # Verifica se a coluna COCONTACORRENTE existe
    if 'COCONTACORRENTE' not in df_2025.columns:
        print("⚠️ Coluna 'COCONTACORRENTE' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}
    
    print("🔍 Processando substrings do COCONTACORRENTE para 2025 e 2024...")
    
    # Processa 2025
    df_2025_trabalho = df_2025.copy()
    df_2025_trabalho['RECEITA_CODIGO'] = df_2025_trabalho['COCONTACORRENTE'].astype(str).str[:8]
    df_2025_trabalho['FONTE_CODIGO'] = df_2025_trabalho['COCONTACORRENTE'].astype(str).str[8:]
    
    # NOVO: Aplica filtro de categorias
    if categorias_selecionadas:
        print(f"🔍 Aplicando filtro de categorias: {categorias_selecionadas}")
        # Cria máscara para filtrar apenas receitas das categorias selecionadas
        mascara = df_2025_trabalho['RECEITA_CODIGO'].str[:2].isin(categorias_selecionadas)
        df_2025_trabalho = df_2025_trabalho[mascara]
        print(f"✅ Receitas após filtro: {len(df_2025_trabalho)} registros")
    
    # Processa 2024 (se disponível)
    df_2024_trabalho = pd.DataFrame()
    if not df_2024.empty and 'COCONTACORRENTE' in df_2024.columns:
        df_2024_trabalho = df_2024.copy()
        df_2024_trabalho['RECEITA_CODIGO'] = df_2024_trabalho['COCONTACORRENTE'].astype(str).str[:8]
        df_2024_trabalho['FONTE_CODIGO'] = df_2024_trabalho['COCONTACORRENTE'].astype(str).str[8:]
        
        # NOVO: Aplica mesmo filtro de categorias em 2024
        if categorias_selecionadas:
            mascara = df_2024_trabalho['RECEITA_CODIGO'].str[:2].isin(categorias_selecionadas)
            df_2024_trabalho = df_2024_trabalho[mascara]
    
    # Carrega planilhas de classificação
    df_classificacao = _carregar_classificacao_orcamentaria()
    df_fontes = _carregar_fontes()
    
    # Aplica classificação de receitas aos dados de 2025
    if df_classificacao.empty:
        print("⚠️ Planilha de classificação orçamentária não encontrada ou vazia")
        df_2025_trabalho['NOME_RECEITA'] = 'Nome não encontrado'
    else:
        print(f"✅ Classificação orçamentária carregada: {len(df_classificacao)} registros")
        df_2025_trabalho = df_2025_trabalho.merge(
            df_classificacao[['COCLASSEORC', 'NOCLASSIFICACAO']], 
            left_on='RECEITA_CODIGO', 
            right_on='COCLASSEORC', 
            how='left'
        )
        df_2025_trabalho['NOME_RECEITA'] = df_2025_trabalho['NOCLASSIFICACAO'].fillna('Classificação não encontrada')
    
    # Aplica classificação de fontes aos dados de 2025
    if df_fontes.empty:
        print("⚠️ Planilha de fontes não encontrada ou vazia")
        df_2025_trabalho['NOME_FONTE'] = 'Nome da fonte não encontrado'
    else:
        print(f"✅ Classificação de fontes carregada: {len(df_fontes)} registros")
        df_2025_trabalho = df_2025_trabalho.merge(
            df_fontes[['COFONTE', 'NOFONTE']], 
            left_on='FONTE_CODIGO', 
            right_on='COFONTE', 
            how='left'
        )
        df_2025_trabalho['NOME_FONTE'] = df_2025_trabalho['NOFONTE'].fillna('Fonte não encontrada')
    
    # Aplica classificação aos dados de 2024
    if not df_2024_trabalho.empty:
        if not df_classificacao.empty:
            df_2024_trabalho = df_2024_trabalho.merge(
                df_classificacao[['COCLASSEORC', 'NOCLASSIFICACAO']], 
                left_on='RECEITA_CODIGO', 
                right_on='COCLASSEORC', 
                how='left'
            )
            df_2024_trabalho['NOME_RECEITA'] = df_2024_trabalho['NOCLASSIFICACAO'].fillna('Classificação não encontrada')
        
        if not df_fontes.empty:
            df_2024_trabalho = df_2024_trabalho.merge(
                df_fontes[['COFONTE', 'NOFONTE']], 
                left_on='FONTE_CODIGO', 
                right_on='COFONTE', 
                how='left'
            )
            df_2024_trabalho['NOME_FONTE'] = df_2024_trabalho['NOFONTE'].fillna('Fonte não encontrada')
    
    # Agrupa dados por RECEITA_CODIGO (receitas principais)
    resultado_receitas_2025 = df_2025_trabalho.groupby(['RECEITA_CODIGO', 'NOME_RECEITA']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    resultado_receitas_2025.columns = ['RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2025']
    
    resultado_receitas_2024 = pd.DataFrame()
    if not df_2024_trabalho.empty:
        resultado_receitas_2024 = df_2024_trabalho.groupby(['RECEITA_CODIGO', 'NOME_RECEITA']).agg({
            'RECEITA LIQUIDA': 'sum'
        }).reset_index()
        resultado_receitas_2024.columns = ['RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2024']
    
    # Combina dados de receitas de 2025 e 2024
    if not resultado_receitas_2024.empty:
        resultado_receitas = resultado_receitas_2025.merge(
            resultado_receitas_2024[['RECEITA_CODIGO', 'RECEITA_2024']], 
            on='RECEITA_CODIGO', 
            how='left'
        )
        resultado_receitas['RECEITA_2024'] = resultado_receitas['RECEITA_2024'].fillna(0)
    else:
        resultado_receitas = resultado_receitas_2025.copy()
        resultado_receitas['RECEITA_2024'] = 0
    
    # Calcula variações das receitas
    resultado_receitas['VARIACAO_ABSOLUTA'] = resultado_receitas['RECEITA_2025'] - resultado_receitas['RECEITA_2024']
    resultado_receitas['VARIACAO_PERCENTUAL'] = resultado_receitas.apply(
        lambda row: ((row['RECEITA_2025'] - row['RECEITA_2024']) / row['RECEITA_2024'] * 100) 
        if row['RECEITA_2024'] > 0 else (100 if row['RECEITA_2025'] > 0 else 0), 
        axis=1
    )
    
    # Ordena por receita de 2025 (maior para menor)
    resultado_receitas = resultado_receitas.sort_values('RECEITA_2025', ascending=False)
    
    # Agrupa dados por RECEITA_CODIGO + FONTE_CODIGO (fontes por receita)
    resultado_fontes_2025 = df_2025_trabalho.groupby(['RECEITA_CODIGO', 'FONTE_CODIGO', 'NOME_FONTE']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    resultado_fontes_2025.columns = ['RECEITA_CODIGO', 'FONTE_CODIGO', 'NOME_FONTE', 'RECEITA_2025']
    
    resultado_fontes_2024 = pd.DataFrame()
    if not df_2024_trabalho.empty:
        resultado_fontes_2024 = df_2024_trabalho.groupby(['RECEITA_CODIGO', 'FONTE_CODIGO', 'NOME_FONTE']).agg({
            'RECEITA LIQUIDA': 'sum'
        }).reset_index()
        resultado_fontes_2024.columns = ['RECEITA_CODIGO', 'FONTE_CODIGO', 'NOME_FONTE', 'RECEITA_2024']
    
    # Combina dados de fontes de 2025 e 2024
    if not resultado_fontes_2024.empty:
        resultado_fontes = resultado_fontes_2025.merge(
            resultado_fontes_2024[['RECEITA_CODIGO', 'FONTE_CODIGO', 'RECEITA_2024']], 
            on=['RECEITA_CODIGO', 'FONTE_CODIGO'], 
            how='left'
        )
        resultado_fontes['RECEITA_2024'] = resultado_fontes['RECEITA_2024'].fillna(0)
    else:
        resultado_fontes = resultado_fontes_2025.copy()
        resultado_fontes['RECEITA_2024'] = 0
    
    # Calcula variações das fontes
    resultado_fontes['VARIACAO_ABSOLUTA'] = resultado_fontes['RECEITA_2025'] - resultado_fontes['RECEITA_2024']
    resultado_fontes['VARIACAO_PERCENTUAL'] = resultado_fontes.apply(
        lambda row: ((row['RECEITA_2025'] - row['RECEITA_2024']) / row['RECEITA_2024'] * 100) 
        if row['RECEITA_2024'] > 0 else (100 if row['RECEITA_2025'] > 0 else 0), 
        axis=1
    )
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada receita principal
    for _, receita in resultado_receitas.iterrows():
        codigo_receita = receita['RECEITA_CODIGO']
        nome_receita = receita['NOME_RECEITA']
        valor_2025 = float(receita['RECEITA_2025'])
        valor_2024 = float(receita['RECEITA_2024'])
        variacao_abs = float(receita['VARIACAO_ABSOLUTA'])
        variacao_perc = float(receita['VARIACAO_PERCENTUAL'])
        
        # Só inclui se pelo menos um dos valores for maior que zero
        if valor_2025 > 0 or valor_2024 > 0:
            # Conta quantas fontes esta receita tem
            fontes_desta_receita = resultado_fontes[resultado_fontes['RECEITA_CODIGO'] == codigo_receita]
            tem_fontes = len(fontes_desta_receita) > 0
            
            linha_receita = {
                'tipo': 'receita',
                'receita_codigo': codigo_receita,
                'nome_receita': nome_receita,
                'receita_2025': valor_2025,
                'receita_2024': valor_2024,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'receita_codigo_fmt': codigo_receita,
                'nome_receita_fmt': nome_receita,
                'receita_2025_fmt': motor.formatar_numero(valor_2025),
                'receita_2024_fmt': motor.formatar_numero(valor_2024),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc),
                'tem_fontes': tem_fontes,
                'qtd_fontes': len(fontes_desta_receita)
            }
            dados_numericos.append(linha_receita)
            dados_para_ia.append(linha_receita)
            
            # Adiciona as fontes desta receita (inicialmente ocultas)
            for _, fonte in fontes_desta_receita.iterrows():
                fonte_codigo = fonte['FONTE_CODIGO']
                nome_fonte = fonte['NOME_FONTE']
                valor_2025_fonte = float(fonte['RECEITA_2025'])
                valor_2024_fonte = float(fonte['RECEITA_2024'])
                variacao_abs_fonte = float(fonte['VARIACAO_ABSOLUTA'])
                variacao_perc_fonte = float(fonte['VARIACAO_PERCENTUAL'])
                
                linha_fonte = {
                    'tipo': 'fonte',
                    'receita_pai': codigo_receita,
                    'fonte_codigo': fonte_codigo,
                    'nome_fonte': nome_fonte,
                    'receita_2025': valor_2025_fonte,
                    'receita_2024': valor_2024_fonte,
                    'variacao_abs': variacao_abs_fonte,
                    'variacao_perc': variacao_perc_fonte,
                    'receita_codigo_fmt': fonte_codigo,
                    'nome_receita_fmt': nome_fonte,
                    'receita_2025_fmt': motor.formatar_numero(valor_2025_fonte),
                    'receita_2024_fmt': motor.formatar_numero(valor_2024_fonte),
                    'variacao_abs_fmt': motor.formatar_numero(variacao_abs_fonte),
                    'variacao_perc_fmt': formatar_percentual(variacao_perc_fonte),
                    'tem_fontes': False,
                    'qtd_fontes': 0
                }
                dados_numericos.append(linha_fonte)
    
    # Adiciona totais gerais (apenas das receitas principais)
    receitas_principais = [d for d in dados_numericos if d['tipo'] == 'receita']
    if receitas_principais:
        total_2025 = sum(l['receita_2025'] for l in receitas_principais)
        total_2024 = sum(l['receita_2024'] for l in receitas_principais)
        total_variacao_abs = total_2025 - total_2024
        total_variacao_perc = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else (100 if total_2025 > 0 else 0)
        
        linha_total = {
            'tipo': 'total',
            'receita_codigo': 'TOTAL',
            'nome_receita': 'TOTAL GERAL',
            'receita_2025': total_2025,
            'receita_2024': total_2024,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc,
            'receita_codigo_fmt': 'TOTAL',
            'nome_receita_fmt': 'TOTAL GERAL',
            'receita_2025_fmt': motor.formatar_numero(total_2025),
            'receita_2024_fmt': motor.formatar_numero(total_2024),
            'variacao_abs_fmt': motor.formatar_numero(total_variacao_abs),
            'variacao_perc_fmt': formatar_percentual(total_variacao_perc),
            'tem_fontes': False,
            'qtd_fontes': 0
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({
            'receita_codigo': 'TOTAL', 
            'nome_receita': 'TOTAL GERAL', 
            'receita_2025': total_2025,
            'receita_2024': total_2024,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc
        })
    
    # Dados para PDF (apenas receitas principais para não ficar muito extenso)
    dados_pdf = {
        "head": [['CÓDIGO RECEITA', 'NOME DA RECEITA', f'RECEITA {mes_referencia}/2024', f'RECEITA {mes_referencia}/2025', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": [
            [linha.get('receita_codigo_fmt', ''), linha.get('nome_receita_fmt', ''), 
             linha.get('receita_2024_fmt', 'R$ 0,00'), linha.get('receita_2025_fmt', 'R$ 0,00'),
             linha.get('variacao_abs_fmt', 'R$ 0,00'), linha.get('variacao_perc_fmt', '0,00%')]
            for linha in dados_numericos if linha['tipo'] in ['receita', 'total']
        ]
    }
    
    print(f"✅ Relatório hierárquico gerado: {len(dados_numericos)} linhas (receitas + fontes + total)")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

def _carregar_classificacao_orcamentaria():
    """
    Carrega a planilha de classificação orçamentária
    
    Returns:
        DataFrame com COCLASSEORC e NOCLASSIFICACAO
    """
    caminho_arquivo = os.path.join('dados', 'CLASSIFICACAO_ORCAMENTARIA.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        print(f"🔄 Carregando classificação orçamentária de {caminho_arquivo}")
        
        df = pd.read_excel(
            caminho_arquivo,
            usecols=['COCLASSEORC', 'NOCLASSIFICACAO'],
            dtype={
                'COCLASSEORC': str,
                'NOCLASSIFICACAO': str
            }
        )
        
        df = df.drop_duplicates(subset=['COCLASSEORC'])
        df = df.dropna(subset=['COCLASSEORC', 'NOCLASSIFICACAO'])
        
        print(f"✅ Classificação carregada: {len(df)} registros únicos")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar classificação orçamentária: {e}")
        return pd.DataFrame()

def _carregar_fontes():
    """
    Carrega a planilha de fontes
    
    Returns:
        DataFrame com COFONTE e NOFONTE
    """
    caminho_arquivo = os.path.join('dados', 'FONTE.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        print(f"🔄 Carregando fontes de {caminho_arquivo}")
        
        df = pd.read_excel(
            caminho_arquivo,
            usecols=['COFONTE', 'NOFONTE'],
            dtype={
                'COFONTE': str,
                'NOFONTE': str
            }
        )
        
        df = df.drop_duplicates(subset=['COFONTE'])
        df = df.dropna(subset=['COFONTE', 'NOFONTE'])
        
        print(f"✅ Fontes carregadas: {len(df)} registros únicos")
        
        # Log dos primeiros registros para debug
        if len(df) > 0:
            print("📋 Primeiros registros das fontes:")
            for i, row in df.head(3).iterrows():
                print(f"   {row['COFONTE']} -> {row['NOFONTE']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar fontes: {e}")
        return pd.DataFrame()