"""
Relatório: Receita por Conta Corrente
Analisa receita usando substring do COCONTACORRENTE e busca nomes na classificação orçamentária
"""
import os
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_relatorio_receita_conta_corrente(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receita por conta corrente
    
    REGRAS DE NEGÓCIO:
    - COCONTACORRENTE tem 17 caracteres
    - Posições 1-8: RECEITA (código da receita)
    - Posições 9-17: FONTE (código da fonte)
    - Busca nome da receita na planilha CLASSIFICACAO_ORCAMENTARIA
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025 e verifica se tem dados
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
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
    
    print("🔍 Processando substrings do COCONTACORRENTE...")
    
    # Cria cópias para não modificar o DataFrame original
    df_trabalho = df_2025.copy()
    
    # Aplica substring no COCONTACORRENTE
    # Posições 1-8 = RECEITA, Posições 9-17 = FONTE
    df_trabalho['RECEITA_CODIGO'] = df_trabalho['COCONTACORRENTE'].astype(str).str[:8]
    df_trabalho['FONTE_CODIGO'] = df_trabalho['COCONTACORRENTE'].astype(str).str[8:]
    
    print(f"✅ Substrings aplicados. Encontrados {df_trabalho['RECEITA_CODIGO'].nunique()} códigos de receita únicos")
    
    # Carrega planilha de classificação orçamentária
    df_classificacao = _carregar_classificacao_orcamentaria()
    
    if df_classificacao.empty:
        print("⚠️ Planilha de classificação orçamentária não encontrada ou vazia")
        # Continua sem os nomes (só com códigos)
        df_trabalho['NOME_RECEITA'] = 'Nome não encontrado'
    else:
        print(f"✅ Classificação orçamentária carregada: {len(df_classificacao)} registros")
        
        # Faz merge para buscar os nomes
        # RECEITA_CODIGO = COCLASSEORC -> pega NOCLASSIFICACAO
        df_trabalho = df_trabalho.merge(
            df_classificacao[['COCLASSEORC', 'NOCLASSIFICACAO']], 
            left_on='RECEITA_CODIGO', 
            right_on='COCLASSEORC', 
            how='left'
        )
        
        # Se não encontrou nome, usa um padrão
        df_trabalho['NOME_RECEITA'] = df_trabalho['NOCLASSIFICACAO'].fillna('Classificação não encontrada')
    
    # Agrupa por RECEITA_CODIGO e soma a RECEITA LIQUIDA
    resultado_agrupado = df_trabalho.groupby(['RECEITA_CODIGO', 'NOME_RECEITA']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Ordena por valor (maior para menor)
    resultado_agrupado = resultado_agrupado.sort_values('RECEITA LIQUIDA', ascending=False)
    
    total_geral = 0
    
    # Processa cada linha do resultado
    for _, linha in resultado_agrupado.iterrows():
        codigo_receita = linha['RECEITA_CODIGO']
        nome_receita = linha['NOME_RECEITA']
        valor_receita = float(linha['RECEITA LIQUIDA'])
        
        total_geral += valor_receita
        
        # Só inclui se o valor for maior que zero
        if valor_receita > 0:
            linha_dados = {
                'tipo': 'principal',
                'receita_codigo': codigo_receita,
                'nome_receita': nome_receita,
                'receita_realizada': valor_receita,
                'receita_codigo_fmt': codigo_receita,
                'nome_receita_fmt': nome_receita,
                'receita_realizada_fmt': motor.formatar_numero(valor_receita)
            }
            dados_numericos.append(linha_dados)
            dados_para_ia.append(linha_dados)
    
    # Adiciona total geral
    if dados_numericos:
        linha_total = {
            'tipo': 'total',
            'receita_codigo': 'TOTAL',
            'nome_receita': 'TOTAL GERAL',
            'receita_realizada': total_geral,
            'receita_codigo_fmt': 'TOTAL',
            'nome_receita_fmt': 'TOTAL GERAL',
            'receita_realizada_fmt': motor.formatar_numero(total_geral)
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'receita_codigo': 'TOTAL', 'nome_receita': 'TOTAL GERAL', 'receita_realizada': total_geral})
    
    # Dados para PDF
    dados_pdf = {
        "head": [['CÓDIGO RECEITA', 'NOME DA RECEITA', 'RECEITA REALIZADA']],
        "body": [
            [linha.get('receita_codigo_fmt', ''), linha.get('nome_receita_fmt', ''), linha.get('receita_realizada_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    print(f"✅ Relatório gerado: {len(dados_numericos)} linhas (incluindo total)")
    
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