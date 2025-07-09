"""
Script para verificar as colunas disponíveis na planilha DESPESA.xlsx
"""
import pandas as pd
import os

# Caminho do arquivo
arquivo = os.path.join('dados', 'DESPESA.xlsx')

print(f"📁 Verificando arquivo: {arquivo}")
print(f"📁 Arquivo existe? {os.path.exists(arquivo)}")

if os.path.exists(arquivo):
    # Carrega apenas as primeiras linhas para ser rápido
    df = pd.read_excel(arquivo, nrows=5)
    
    print(f"\n📊 Total de colunas: {len(df.columns)}")
    print("\n📋 Lista de TODAS as colunas:\n")
    
    # Lista todas as colunas
    for i, col in enumerate(df.columns, 1):
        print(f"{i:3d}. {col}")
    
    print("\n🔍 Procurando colunas relacionadas a FUNÇÃO:")
    funcao_cols = [col for col in df.columns if 'FUNC' in col.upper()]
    if funcao_cols:
        print(f"   Encontradas: {funcao_cols}")
    else:
        print("   ❌ Nenhuma coluna com 'FUNC' encontrada")
    
    print("\n🔍 Procurando colunas relacionadas a SUBFUNÇÃO:")
    subfuncao_cols = [col for col in df.columns if 'SUBFUNC' in col.upper() or 'SUB FUNC' in col.upper()]
    if subfuncao_cols:
        print(f"   Encontradas: {subfuncao_cols}")
    else:
        print("   ❌ Nenhuma coluna com 'SUBFUNC' encontrada")
    
    # Procura outras possibilidades
    print("\n🔍 Outras colunas que podem ser relevantes:")
    for col in df.columns:
        if any(termo in col.upper() for termo in ['CODIGO', 'COD', 'FUNÇÃO', 'FUNCAO']):
            print(f"   - {col}")
else:
    print("❌ Arquivo não encontrado!")