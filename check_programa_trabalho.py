import pandas as pd
import os

# Verifica se o arquivo existe
arquivo = 'dados/Programa de Trabalho.xlsx'
if os.path.exists(arquivo):
    print(f"✅ Arquivo encontrado: {arquivo}")
    
    # Lê a planilha
    df = pd.read_excel(arquivo)
    
    # Mostra informações sobre a planilha
    print(f"\n📊 Número de linhas: {len(df)}")
    print(f"📊 Número de colunas: {len(df.columns)}")
    
    print("\n📋 Colunas encontradas:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    # Mostra as primeiras linhas
    print("\n📄 Primeiras 5 linhas:")
    print(df.head())
    
    # Mostra tipos de dados
    print("\n📈 Tipos de dados:")
    print(df.dtypes)
else:
    print(f"❌ Arquivo não encontrado: {arquivo}")