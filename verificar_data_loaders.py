"""
Verifica como os dados estão sendo carregados
"""
import pandas as pd
import os

# Caminho do arquivo
arquivo = os.path.join('dados', 'DESPESA.xlsx')

print(f"📁 Carregando arquivo: {arquivo}")

# Carrega SEM limitar colunas
df_completo = pd.read_excel(arquivo, nrows=5)
print(f"\n✅ Carregamento completo: {df_completo.shape[1]} colunas")
print(f"📋 Todas as colunas: {list(df_completo.columns)}")

# Verifica se COFUNCAO e COSUBFUNCAO estão presentes
if 'COFUNCAO' in df_completo.columns:
    print("\n✅ COFUNCAO encontrada!")
else:
    print("\n❌ COFUNCAO NÃO encontrada!")
    
if 'COSUBFUNCAO' in df_completo.columns:
    print("✅ COSUBFUNCAO encontrada!")
else:
    print("❌ COSUBFUNCAO NÃO encontrada!")

# Procura a posição das colunas
for i, col in enumerate(df_completo.columns):
    if 'FUNCAO' in col:
        print(f"\n📍 {col} está na posição {i+1} (coluna {chr(65+i)})")