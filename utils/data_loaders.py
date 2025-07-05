"""
Funções centralizadas para carregamento de dados
Extraídas do app.py para reutilização em diferentes blueprints
"""
import os
import time
import pandas as pd
from cache_service import cache_service

def carregar_dataframe_receita():
    """Carrega dados de receita com cache"""
    caminho_arquivo = os.path.join('dados', 'RECEITA.xlsx')

    # Tenta carregar do cache primeiro
    df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'receita')
    if df_cached is not None:
        return df_cached

    print("🔄 Carregando dados de receita do Excel...")
    inicio = time.time()

    # Carrega do Excel - COLUNAS ATUALIZADAS
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIARECEITA': str,
        'ORIGEM': str, 'NOFONTERECEITA': str,
        'ESPECIE': str, 'NOSUBFONTERECEITA': str,
        'ALINEA': str, 'NOALINEA': str,
        'INTIPOADM': int,
        'NOUG': str,
        'COEXERCICIO': int,
        'INMES': int
    }
    
    # Tenta ler todas as colunas primeiro para ver o que está disponível
    df_temp = pd.read_excel(caminho_arquivo, nrows=5)  # Lê só as primeiras linhas para ver colunas
    colunas_disponiveis = df_temp.columns.tolist()
    
    print(f"📋 Colunas disponíveis na planilha: {colunas_disponiveis}")
    
    # Lê o arquivo completo
    df = pd.read_excel(caminho_arquivo, dtype=dtype_map)
    
    print(f"📊 Colunas carregadas: {df.columns.tolist()}")
    print(f"📅 Exercícios encontrados: {df['COEXERCICIO'].unique() if 'COEXERCICIO' in df.columns else 'COEXERCICIO não encontrado'}")
    
    if 'INMES' in df.columns:
        print(f"📅 Meses disponíveis: {sorted(df['INMES'].unique())}")
        max_mes = df['INMES'].max()
        print(f"📅 Mês de referência: {max_mes}")

    # Salva no cache
    cache_service.cache_dataframe(df, caminho_arquivo, 'receita')

    fim = time.time()
    print(f"⏱️ Dados de receita carregados em {fim - inicio:.2f} segundos")

    return df

def carregar_dataframe_despesa():
    """Carrega dados de despesa com cache e precisão monetária corrigida"""
    caminho_arquivo = os.path.join('dados', 'DESPESA.xlsx')

    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()

    # Tenta carregar do cache primeiro
    df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'despesa')
    if df_cached is not None:
        return df_cached

    print("🔄 Carregando dados de despesa do Excel...")
    inicio = time.time()

    # Colunas necessárias
    colunas_necessarias = [
        'CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO',
        'MODALIDADE', 'NOMODALIDADE', 'ELEMENTO', 'NOELEMENTO',
        'COEXERCICIO', 'INMES', 'INTIPOADM', 'NOUG',
        'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 'CANCELAMENTO DE DOTACAO',
        'CANCEL-REMANEJA DOTACAO', 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA',
        'DESPESA PAGA', 'SALDO DOTACAO'
    ]

    try:
        # CORREÇÃO: Usar float64 para precisão monetária
        df = pd.read_excel(
            caminho_arquivo,
            sheet_name=0,
            usecols=lambda x: x in colunas_necessarias,
            dtype={
                'CATEGORIA': str, 'NOCATEGORIA': str,
                'GRUPO': str, 'NOGRUPO': str,
                'MODALIDADE': str, 'NOMODALIDADE': str,
                'ELEMENTO': str, 'NOELEMENTO': str,
                'COEXERCICIO': 'int32',
                'INMES': 'int32',
                'INTIPOADM': 'int32',
                'NOUG': str,
                # CORREÇÃO: Mudança de float32 para float64 para precisão monetária
                'DOTACAO INICIAL': 'float64',
                'DOTACAO ADICIONAL': 'float64',
                'CANCELAMENTO DE DOTACAO': 'float64',
                'CANCEL-REMANEJA DOTACAO': 'float64',
                'DESPESA EMPENHADA': 'float64',
                'DESPESA LIQUIDADA': 'float64',
                'DESPESA PAGA': 'float64'
            }
        )
        
        df = df[df['COEXERCICIO'] == 2025].copy()

        for col in ['CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO', 'NOUG']:
            if col in df.columns:
                df[col] = df[col].astype('category')

        cache_service.cache_dataframe(df, caminho_arquivo, 'despesa')

        fim = time.time()
        print(f"⏱️ Dados de despesa carregados em {fim - inicio:.2f} segundos")
        print(f"📊 {len(df):,} registros carregados (apenas 2025)")
        print(f"💰 Precisão monetária: float64 aplicada para evitar perda de precisão")

        return df

    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()