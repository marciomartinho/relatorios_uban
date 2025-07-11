"""
Processador para arquivos PDF do SISGEPAT com cache
"""
import pdfplumber
import re
import pandas as pd
from typing import Dict, Tuple
from cache_service import cache_service

class SisgepatProcessor:
    """Processa arquivos PDF do relatório SISGEPAT"""
    
    # Local especial do DFTRANS
    LOCAL_DFTRANS = '1130000000000'
    NOME_DFTRANS = 'TRANSPORTE URBANO DO DISTRITO FEDERAL - DFTRANS'
    
    @staticmethod
    def processar_pdf(caminho_pdf: str, df_depara: pd.DataFrame) -> Dict[Tuple[str, str], float]:
        """
        Processa PDF do relatório SISGEPAT com cache
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            df_depara: DataFrame com correspondência Local -> COUG
            
        Returns:
            dict: Dicionário com chave (COUG, SUBITEM) e valor do SISGEPAT
        """
        # Tenta pegar do cache primeiro
        dados_cache = cache_service.get_cached_pdf_sisgepat(caminho_pdf)
        if dados_cache is not None:
            return dados_cache
        
        print("🔄 Processando PDF SISGEPAT (isso pode demorar um pouco na primeira vez)...")
        
        dados_sisgepat = {}
        
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                local_atual = None
                coug_atual = None
                
                total_paginas = len(pdf.pages)
                print(f"📄 Total de páginas para processar: {total_paginas}")
                
                for idx, pagina in enumerate(pdf.pages):
                    if idx % 10 == 0:  # Mostra progresso a cada 10 páginas
                        print(f"  Processando página {idx + 1} de {total_paginas}...")
                    
                    texto = pagina.extract_text()
                    if not texto:
                        continue
                        
                    linhas = texto.split('\n')
                    
                    for linha in linhas:
                        linha = linha.strip()
                        
                        # Verifica se é uma linha de Local
                        if linha.startswith('Local:'):
                            # Extrai o número do local (13 dígitos)
                            match = re.search(r'Local:\s*(\d{13})', linha)
                            if match:
                                local = match.group(1)
                                # Remove zeros à esquerda para fazer o match
                                local_sem_zeros = local.lstrip('0') or '0'
                                
                                # Busca a COUG correspondente no DE-PARA
                                coug_match = df_depara[
                                    (df_depara['Local'] == local) | 
                                    (df_depara['Local'] == local_sem_zeros) |
                                    (df_depara['Local'].str.lstrip('0') == local_sem_zeros)
                                ]
                                
                                if not coug_match.empty:
                                    coug_atual = str(coug_match.iloc[0]['COUG']).strip()
                                    local_atual = local
                                else:
                                    coug_atual = None
                                    local_atual = None
                        
                        # Se temos uma COUG válida, processa as linhas de dados
                        elif coug_atual and not linha.startswith('Subitem') and not linha.startswith('TOTAL:'):
                            # Tenta extrair subitem e valor da linha
                            partes = linha.split()
                            
                            if len(partes) >= 2:
                                # Verifica se o primeiro elemento é um número (subitem)
                                try:
                                    subitem = int(partes[0])
                                    if 1 <= subitem <= 99:  # Subitens válidos
                                        subitem_str = str(subitem).zfill(2)
                                        
                                        # Procura o último valor numérico da linha
                                        valor = 0
                                        valores_encontrados = []
                                        
                                        # Coleta TODOS os valores numéricos da linha
                                        for parte in partes[1:]:  # Pula o primeiro elemento (subitem)
                                            # Remove pontos de milhares e troca vírgula por ponto
                                            valor_str = parte.replace('.', '').replace(',', '.')
                                            try:
                                                valor_temp = float(valor_str)
                                                # Se for um número válido (incluindo 0), adiciona à lista
                                                if ',' in parte or parte == '0' or parte == '0,00':
                                                    valores_encontrados.append(valor_temp)
                                            except:
                                                continue
                                        
                                        # Pega o ÚLTIMO valor encontrado (Saldo Atual)
                                        if valores_encontrados:
                                            valor = valores_encontrados[-1]
                                            dados_sisgepat[(coug_atual, subitem_str)] = valor
                                except:
                                    # Não é uma linha de subitem
                                    pass
            
            print(f"\n✅ Total de registros SISGEPAT processados: {len(dados_sisgepat)}")
            
            # Salva no cache para próximas execuções
            cache_service.cache_pdf_sisgepat(dados_sisgepat, caminho_pdf)
            
            return dados_sisgepat
            
        except Exception as e:
            print(f"❌ Erro ao processar PDF SISGEPAT: {str(e)}")
            return {}
    
    @staticmethod
    def identificar_coug_dftrans(df_depara: pd.DataFrame) -> str:
        """Identifica a COUG do DFTRANS no DE-PARA"""
        if df_depara is None:
            return None
            
        dftrans_match = df_depara[
            (df_depara['Local'] == SisgepatProcessor.LOCAL_DFTRANS) | 
            (df_depara['Local'].str.lstrip('0') == SisgepatProcessor.LOCAL_DFTRANS.lstrip('0'))
        ]
        
        if not dftrans_match.empty:
            coug_dftrans = str(dftrans_match.iloc[0]['COUG']).strip()
            print(f"DFTRANS identificado: Local {SisgepatProcessor.LOCAL_DFTRANS} -> COUG {coug_dftrans}")
            return coug_dftrans
        
        return None