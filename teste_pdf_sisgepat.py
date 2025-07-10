"""
Script de teste para verificar leitura do PDF SISGEPAT
Execute este arquivo diretamente para testar
"""
import pdfplumber
import pandas as pd
import re

def testar_pdf():
    """Testa a leitura do PDF e mostra o que está sendo extraído"""
    
    caminho_pdf = 'dados/Relatorio_Demonstrativos_Bem_Moveis.pdf'
    
    print("=== TESTE DE LEITURA DO PDF ===\n")
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"PDF aberto com sucesso! Total de páginas: {len(pdf.pages)}\n")
            
            # Testa as primeiras 3 páginas
            for num_pagina in range(min(3, len(pdf.pages))):
                print(f"\n--- PÁGINA {num_pagina + 1} ---")
                pagina = pdf.pages[num_pagina]
                texto = pagina.extract_text()
                
                if texto:
                    linhas = texto.split('\n')
                    print(f"Total de linhas na página: {len(linhas)}")
                    
                    # Procura por linhas com "Local:"
                    for i, linha in enumerate(linhas):
                        if 'Local:' in linha:
                            print(f"\nLinha {i}: {linha[:100]}...")  # Primeiros 100 caracteres
                            
                            # Tenta extrair o número do local
                            match = re.search(r'Local:\s*(\d{13})', linha)
                            if match:
                                print(f"  -> Local encontrado: {match.group(1)}")
                            else:
                                print("  -> Não conseguiu extrair o número do local")
                                # Tenta outro padrão
                                match2 = re.search(r'Local:\s*(\d+)', linha)
                                if match2:
                                    print(f"  -> Número encontrado (outro padrão): {match2.group(1)}")
                            
                            # Mostra as próximas 10 linhas após o Local
                            print("\n  Próximas linhas após o Local:")
                            for j in range(i+1, min(i+11, len(linhas))):
                                print(f"    {j}: {linhas[j][:80]}...")
                else:
                    print("Não foi possível extrair texto desta página")
                    
    except Exception as e:
        print(f"ERRO ao abrir PDF: {str(e)}")
        return
    
    # Testa o DE-PARA
    print("\n\n=== TESTE DO DE-PARA ===\n")
    try:
        df_depara = pd.read_excel('dados/DEPARAUG.xlsx')
        print(f"DE-PARA carregado! Shape: {df_depara.shape}")
        print(f"Colunas: {list(df_depara.columns)}")
        print("\nPrimeiras 5 linhas:")
        print(df_depara.head())
        
        # Verifica se tem a coluna Local
        if 'Local' in df_depara.columns:
            print(f"\nExemplos de valores na coluna 'Local':")
            print(df_depara['Local'].head(10).tolist())
        else:
            print("\nATENÇÃO: Coluna 'Local' não encontrada!")
            print("Procurando por colunas que possam conter o local...")
            for col in df_depara.columns:
                if 'local' in col.lower() or 'loc' in col.lower():
                    print(f"\nPossível coluna de local: '{col}'")
                    print(df_depara[col].head(5).tolist())
                    
    except Exception as e:
        print(f"ERRO ao carregar DE-PARA: {str(e)}")

if __name__ == "__main__":
    testar_pdf()