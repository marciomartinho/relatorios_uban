"""
Relatório: Receita por Conta Corrente APRIMORADO
Analisa receita usando substring do COCONTACORRENTE e busca nomes na classificação orçamentária
NOVO: Inclui dados de 2024, variação absoluta e percentual
"""
import os
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receita_conta_corrente(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receita por conta corrente com comparativo 2024 vs 2025
    
    REGRAS DE NEGÓCIO:
    - COCONTACORRENTE tem 17 caracteres
    - Posições 1-8: RECEITA (código da receita)
    - Posições 9-17: FONTE (código da fonte)
    - Busca nome da receita na planilha CLASSIFICACAO_ORCAMENTARIA
    - NOVO: Compara 2024 vs 2025 com variações absoluta e percentual
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
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
    
    # Processa 2024 (se disponível)
    df_2024_trabalho = pd.DataFrame()
    if not df_2024.empty and 'COCONTACORRENTE' in df_2024.columns:
        df_2024_trabalho = df_2024.copy()
        df_2024_trabalho['RECEITA_CODIGO'] = df_2024_trabalho['COCONTACORRENTE'].astype(str).str[:8]
        df_2024_trabalho['FONTE_CODIGO'] = df_2024_trabalho['COCONTACORRENTE'].astype(str).str[8:]
    
    # Carrega planilha de classificação orçamentária
    df_classificacao = _carregar_classificacao_orcamentaria()
    
    # Aplica classificação aos dados de 2025
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
    
    # Aplica classificação aos dados de 2024
    if not df_2024_trabalho.empty and not df_classificacao.empty:
        df_2024_trabalho = df_2024_trabalho.merge(
            df_classificacao[['COCLASSEORC', 'NOCLASSIFICACAO']], 
            left_on='RECEITA_CODIGO', 
            right_on='COCLASSEORC', 
            how='left'
        )
        df_2024_trabalho['NOME_RECEITA'] = df_2024_trabalho['NOCLASSIFICACAO'].fillna('Classificação não encontrada')
    
    # Agrupa dados de 2025 por RECEITA_CODIGO
    resultado_2025 = df_2025_trabalho.groupby(['RECEITA_CODIGO', 'NOME_RECEITA']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    resultado_2025.columns = ['RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2025']
    
    # Agrupa dados de 2024 por RECEITA_CODIGO (se disponível)
    resultado_2024 = pd.DataFrame()
    if not df_2024_trabalho.empty:
        resultado_2024 = df_2024_trabalho.groupby(['RECEITA_CODIGO', 'NOME_RECEITA']).agg({
            'RECEITA LIQUIDA': 'sum'
        }).reset_index()
        resultado_2024.columns = ['RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2024']
    
    # Combina dados de 2025 e 2024
    if not resultado_2024.empty:
        resultado_combinado = resultado_2025.merge(
            resultado_2024[['RECEITA_CODIGO', 'RECEITA_2024']], 
            on='RECEITA_CODIGO', 
            how='left'
        )
        resultado_combinado['RECEITA_2024'] = resultado_combinado['RECEITA_2024'].fillna(0)
    else:
        resultado_combinado = resultado_2025.copy()
        resultado_combinado['RECEITA_2024'] = 0
    
    # Calcula variações
    resultado_combinado['VARIACAO_ABSOLUTA'] = resultado_combinado['RECEITA_2025'] - resultado_combinado['RECEITA_2024']
    resultado_combinado['VARIACAO_PERCENTUAL'] = resultado_combinado.apply(
        lambda row: ((row['RECEITA_2025'] - row['RECEITA_2024']) / row['RECEITA_2024'] * 100) 
        if row['RECEITA_2024'] > 0 else (100 if row['RECEITA_2025'] > 0 else 0), 
        axis=1
    )
    
    # Ordena por receita de 2025 (maior para menor)
    resultado_combinado = resultado_combinado.sort_values('RECEITA_2025', ascending=False)
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada linha do resultado
    for _, linha in resultado_combinado.iterrows():
        codigo_receita = linha['RECEITA_CODIGO']
        nome_receita = linha['NOME_RECEITA']
        valor_2025 = float(linha['RECEITA_2025'])
        valor_2024 = float(linha['RECEITA_2024'])
        variacao_abs = float(linha['VARIACAO_ABSOLUTA'])
        variacao_perc = float(linha['VARIACAO_PERCENTUAL'])
        
        # Só inclui se pelo menos um dos valores for maior que zero
        if valor_2025 > 0 or valor_2024 > 0:
            linha_dados = {
                'tipo': 'principal',
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
                'variacao_perc_fmt': formatar_percentual(variacao_perc)
            }
            dados_numericos.append(linha_dados)
            dados_para_ia.append(linha_dados)
    
    # Adiciona totais gerais
    if dados_numericos:
        total_2025 = sum(l['receita_2025'] for l in dados_numericos)
        total_2024 = sum(l['receita_2024'] for l in dados_numericos)
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
            'variacao_perc_fmt': formatar_percentual(total_variacao_perc)
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
    
    # Dados para PDF
    dados_pdf = {
        "head": [['CÓDIGO RECEITA', 'NOME DA RECEITA', f'RECEITA {mes_referencia}/2025', f'RECEITA {mes_referencia}/2024', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": [
            [linha.get('receita_codigo_fmt', ''), linha.get('nome_receita_fmt', ''), 
             linha.get('receita_2025_fmt', 'R$ 0,00'), linha.get('receita_2024_fmt', 'R$ 0,00'),
             linha.get('variacao_abs_fmt', 'R$ 0,00'), linha.get('variacao_perc_fmt', '0,00%')]
            for linha in dados_numericos
        ]
    }
    
    print(f"✅ Relatório aprimorado gerado: {len(dados_numericos)} linhas (incluindo total)")
    
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
        
        # Carrega apenas as colunas necessárias
        df = pd.read_excel(
            caminho_arquivo,
            usecols=['COCLASSEORC', 'NOCLASSIFICACAO'],
            dtype={
                'COCLASSEORC': str,
                'NOCLASSIFICACAO': str
            }
        )
        
        # Remove duplicatas e valores nulos
        df = df.drop_duplicates(subset=['COCLASSEORC'])
        df = df.dropna(subset=['COCLASSEORC', 'NOCLASSIFICACAO'])
        
        print(f"✅ Classificação carregada: {len(df)} registros únicos")
        
        # Log dos primeiros registros para debug
        if len(df) > 0:
            print("📋 Primeiros registros da classificação:")
            for i, row in df.head(3).iterrows():
                print(f"   {row['COCLASSEORC']} -> {row['NOCLASSIFICACAO']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar classificação orçamentária: {e}")
        return pd.DataFrame()