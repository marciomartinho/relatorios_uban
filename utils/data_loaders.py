"""
Funções centralizadas para carregamento de dados
Extraídas do app.py para reutilização em diferentes blueprints
"""
import os
import time
import pandas as pd
from pathlib import Path

# Tenta importar o cache service, mas funciona sem ele se não estiver disponível
try:
    from cache_service import cache_service
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_service = None

def carregar_dataframe_receita():
    """Carrega dados de receita com cache"""
    caminho_arquivo = os.path.join('dados', 'RECEITA.xlsx')

    # Tenta carregar do cache primeiro se disponível
    if CACHE_AVAILABLE and cache_service:
        try:
            df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'receita')
            if df_cached is not None:
                return df_cached
        except:
            pass  # Continua sem cache se houver erro

    print("🔄 Carregando dados de receita do Excel...")
    inicio = time.time()

    # Carrega do Excel - COLUNAS ATUALIZADAS
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIARECEITA': str,
        'ORIGEM': str, 'NOFONTERECEITA': str,
        'ESPECIE': str, 'NOSUBFONTERECEITA': str,
        'ALINEA': str, 'NOALINEA': str,
        'INTIPOADM': str,  # Mudança: agora é string para tratar espaços
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

    # Salva no cache se disponível
    if CACHE_AVAILABLE and cache_service:
        try:
            cache_service.cache_dataframe(df, caminho_arquivo, 'receita')
        except:
            pass  # Continua sem salvar cache se houver erro

    fim = time.time()
    print(f"⏱️ Dados de receita carregados em {fim - inicio:.2f} segundos")

    return df

def carregar_dataframe_despesa():
    """Carrega dados de despesa com cache e precisão monetária corrigida"""
    caminho_arquivo = os.path.join('dados', 'DESPESA.xlsx')

    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()

    # Tenta carregar do cache primeiro se disponível
    if CACHE_AVAILABLE and cache_service:
        try:
            df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'despesa')
            if df_cached is not None:
                return df_cached
        except:
            pass

    print("🔄 Carregando dados de despesa do Excel...")
    inicio = time.time()

    # Colunas necessárias - ATUALIZADO COM TODAS AS COLUNAS
    colunas_necessarias = [
        'COCONTACORRENTE', 'CONATUREZA', 'CATEGORIA', 'NOCATEGORIA', 
        'GRUPO', 'NOGRUPO', 'MODALIDADE', 'NOMODALIDADE', 
        'ELEMENTO', 'NOELEMENTO', 'COEXERCICIO', 'INMES',
        'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 'CANCELAMENTO DE DOTACAO',
        'CANCEL-REMANEJA DOTACAO', 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA',
        'DESPESA PAGA', 'SALDO DOTACAO', 'COFUNCAO', 'COSUBFUNCAO',
        'COPROGRAMA', 'COPROJETO', 'COSUBTITULO', 'NOPT', 'INESFERA',
        'COFONTE', 'COUG', 'COGESTAO', 'INTIPOADM', 'NOUG'
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
                'INTIPOADM': str,  # Mudança: string para tratar espaços
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

        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_service.cache_dataframe(df, caminho_arquivo, 'despesa')
            except:
                pass

        fim = time.time()
        print(f"⏱️ Dados de despesa carregados em {fim - inicio:.2f} segundos")
        print(f"📊 {len(df):,} registros carregados (apenas 2025)")
        print(f"💰 Precisão monetária: float64 aplicada para evitar perda de precisão")

        return df

    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def carregar_classificacao_orcamentaria():
    """
    Carrega dados da planilha classificacao_orcamentaria.xlsx
    Mapeia COCLASSEORC → NOCLASSIFICACAO
    
    Returns:
        dict: Dicionário com código da classificação como chave e nome como valor
    """
    try:
        caminho_dados = Path("dados/classificacao_orcamentaria.xlsx")
        
        if not caminho_dados.exists():
            print(f"⚠️ Arquivo não encontrado: {caminho_dados}")
            return {}
        
        # Tenta carregar do cache primeiro se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"classificacao_orcamentaria_{os.path.getmtime(caminho_dados)}"
                # Usa um método mais simples se get() não existir
                if hasattr(cache_service, 'get'):
                    classificacao_cached = cache_service.get(cache_key)
                else:
                    classificacao_cached = None
                    
                if classificacao_cached is not None:
                    print(f"✅ Classificação orçamentária carregada do cache: {len(classificacao_cached)} registros")
                    return classificacao_cached
            except Exception as e:
                print(f"⚠️ Erro no cache, carregando do arquivo: {e}")
        
        df = pd.read_excel(caminho_dados)
        
        # Verifica se as colunas existem
        if 'COCLASSEORC' not in df.columns or 'NOCLASSIFICACAO' not in df.columns:
            print("⚠️ Colunas COCLASSEORC ou NOCLASSIFICACAO não encontradas")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return {}
        
        # Cria dicionário de mapeamento
        classificacao_dict = {}
        for _, row in df.iterrows():
            codigo = str(row['COCLASSEORC']).strip()
            nome = str(row['NOCLASSIFICACAO']).strip()
            
            if codigo and nome and codigo != 'nan' and nome != 'nan':
                classificacao_dict[codigo] = nome
        
        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"classificacao_orcamentaria_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'set'):
                    cache_service.set(cache_key, classificacao_dict, ttl=3600)
            except:
                pass
        
        print(f"✅ Classificação orçamentária carregada: {len(classificacao_dict)} registros")
        return classificacao_dict
        
    except Exception as e:
        print(f"❌ Erro ao carregar classificação orçamentária: {e}")
        return {}

def carregar_fontes():
    """
    Carrega dados da planilha fonte.xlsx
    Mapeia COFONTE → NOFONTE
    
    Returns:
        dict: Dicionário com código da fonte como chave e nome como valor
    """
    try:
        caminho_dados = Path("dados/fonte.xlsx")
        
        if not caminho_dados.exists():
            print(f"⚠️ Arquivo não encontrado: {caminho_dados}")
            return {}
        
        # Tenta carregar do cache primeiro se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"fontes_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'get'):
                    fontes_cached = cache_service.get(cache_key)
                else:
                    fontes_cached = None
                    
                if fontes_cached is not None:
                    print(f"✅ Fontes carregadas do cache: {len(fontes_cached)} registros")
                    return fontes_cached
            except Exception as e:
                print(f"⚠️ Erro no cache, carregando do arquivo: {e}")
        
        df = pd.read_excel(caminho_dados)
        
        # Verifica se as colunas existem
        if 'COFONTE' not in df.columns or 'NOFONTE' not in df.columns:
            print("⚠️ Colunas COFONTE ou NOFONTE não encontradas")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return {}
        
        # Cria dicionário de mapeamento
        fontes_dict = {}
        for _, row in df.iterrows():
            codigo = str(row['COFONTE']).strip()
            nome = str(row['NOFONTE']).strip()
            
            if codigo and nome and codigo != 'nan' and nome != 'nan':
                fontes_dict[codigo] = nome
        
        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"fontes_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'set'):
                    cache_service.set(cache_key, fontes_dict, ttl=3600)
            except:
                pass
        
        print(f"✅ Fontes carregadas: {len(fontes_dict)} registros")
        return fontes_dict
        
    except Exception as e:
        print(f"❌ Erro ao carregar fontes: {e}")
        return {}

def carregar_unidades_gestoras():
    """
    Carrega dados das unidades gestoras
    Pode ser usado para validar INTIPOADM e outras informações
    
    Returns:
        dict: Dicionário com informações das UGs
    """
    try:
        caminho_dados = Path("dados/unidades_gestoras.xlsx")
        
        if not caminho_dados.exists():
            print(f"⚠️ Arquivo de unidades gestoras não encontrado: {caminho_dados}")
            return {}
        
        # Tenta carregar do cache primeiro se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"unidades_gestoras_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'get'):
                    ugs_cached = cache_service.get(cache_key)
                else:
                    ugs_cached = None
                    
                if ugs_cached is not None:
                    print(f"✅ Unidades gestoras carregadas do cache: {len(ugs_cached)} registros")
                    return ugs_cached
            except:
                pass
        
        df = pd.read_excel(caminho_dados)
        
        # Cria dicionário de mapeamento (adapte conforme estrutura real)
        ugs_dict = {}
        for _, row in df.iterrows():
            # Adapte estas colunas conforme a estrutura real da planilha
            codigo_ug = str(row.get('COUG', row.get('NOUG', ''))).strip()
            if codigo_ug:
                ugs_dict[codigo_ug] = {
                    'nome': str(row.get('NOME', row.get('NOMEUG', ''))).strip(),
                    'intipoadm': str(row.get('INTIPOADM', row.get('INTIPO', ''))).strip(),
                    'tipo': str(row.get('TIPO', '')).strip()
                }
        
        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"unidades_gestoras_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'set'):
                    cache_service.set(cache_key, ugs_dict, ttl=3600)
            except:
                pass
        
        print(f"✅ Unidades gestoras carregadas: {len(ugs_dict)} registros")
        return ugs_dict
        
    except Exception as e:
        print(f"❌ Erro ao carregar unidades gestoras: {e}")
        return {}

def carregar_conta_contabil():
    """
    Carrega dados da planilha CONTACONTABIL.xlsx
    Mapeia COCONTACONTABIL → NOCONTACONTABIL
    
    Returns:
        dict: Dicionário com código da conta como chave e nome como valor
    """
    try:
        caminho_dados = Path("dados/CONTACONTABIL.xlsx")
        
        if not caminho_dados.exists():
            print(f"⚠️ Arquivo não encontrado: {caminho_dados}")
            return {}
        
        # Tenta carregar do cache primeiro se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"conta_contabil_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'get'):
                    contas_cached = cache_service.get(cache_key)
                else:
                    contas_cached = None
                    
                if contas_cached is not None:
                    print(f"✅ Contas contábeis carregadas do cache: {len(contas_cached)} registros")
                    return contas_cached
            except Exception as e:
                print(f"⚠️ Erro no cache, carregando do arquivo: {e}")
        
        df = pd.read_excel(caminho_dados)
        
        # Remove espaços dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Verifica se as colunas existem
        if 'COCONTACONTABIL' not in df.columns or 'NOCONTACONTABIL' not in df.columns:
            print("⚠️ Colunas COCONTACONTABIL ou NOCONTACONTABIL não encontradas")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            return {}
        
        # Cria dicionário de mapeamento
        contas_dict = {}
        for _, row in df.iterrows():
            codigo = str(row['COCONTACONTABIL']).strip()
            nome = str(row['NOCONTACONTABIL']).strip()
            
            if codigo and nome and codigo != 'nan' and nome != 'nan':
                # Remove .0 se existir no código
                if codigo.endswith('.0'):
                    codigo = codigo[:-2]
                contas_dict[codigo] = nome
        
        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_key = f"conta_contabil_{os.path.getmtime(caminho_dados)}"
                if hasattr(cache_service, 'set'):
                    cache_service.set(cache_key, contas_dict, ttl=3600)
            except:
                pass
        
        print(f"✅ Contas contábeis carregadas: {len(contas_dict)} registros")
        return contas_dict
        
    except Exception as e:
        print(f"❌ Erro ao carregar contas contábeis: {e}")
        return {}
    """
    Lista todos os arquivos disponíveis na pasta dados
    Útil para debug e verificação
    """
    try:
        pasta_dados = Path("dados")
        if pasta_dados.exists():
            arquivos = [f.name for f in pasta_dados.glob("*.xlsx")]
            print(f"📁 Arquivos Excel encontrados em dados/: {arquivos}")
            return arquivos
        else:
            print("📁 Pasta 'dados' não encontrada")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        return []

def carregar_dataframe_bens_moveis():
    """Carrega dados de bens móveis com cache"""
    # Lista de possíveis nomes e extensões
    possiveis_arquivos = [
        os.path.join('dados', 'BENSMOVEIS.xlsx'),
        os.path.join('dados', 'BENSMOVEIS.xls'),
        os.path.join('dados', 'BensMoveis.xlsx'),
        os.path.join('dados', 'BensMoveis.xls')
    ]
    
    caminho_arquivo = None
    for arquivo in possiveis_arquivos:
        if os.path.exists(arquivo):
            caminho_arquivo = arquivo
            break
    
    if not caminho_arquivo:
        print(f"❌ Arquivo de bens móveis não encontrado. Tentativas:")
        for arquivo in possiveis_arquivos:
            print(f"   - {arquivo}")
        return pd.DataFrame()

    # Tenta carregar do cache primeiro se disponível
    if CACHE_AVAILABLE and cache_service:
        try:
            df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'bens_moveis')
            if df_cached is not None:
                return df_cached
        except:
            pass

    print(f"🔄 Carregando dados de bens móveis do arquivo: {caminho_arquivo}")
    inicio = time.time()

    try:
        df = pd.read_excel(caminho_arquivo)
        
        # Remove espaços dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        print(f"📊 Colunas carregadas: {df.columns.tolist()}")
        print(f"📊 {len(df):,} registros carregados")
        
        # Mapeia os nomes das colunas para os esperados pelo sistema
        mapeamento_colunas = {
            'BENS_MOVEIS': 'BENS_MOVEIS',
            'BENS_MOVEIS_ALMOX': 'BENS_MOVEIS_ALMOX', 
            'BENS_MOVEIS_IMPORT': 'BENS_MOVEIS_IMPORT',
            'BENS_MOVEIS_TOTAL': 'BENS_MOVEIS_TOTAL'
        }
        
        # Verifica se as colunas já existem ou precisam ser criadas
        if 'BENS_MOVEIS' not in df.columns:
            print("⚠️ Coluna BENS_MOVEIS não encontrada diretamente")
            # Procura por variações do nome
            for col in df.columns:
                if 'BENS' in col and 'MOVEIS' in col and 'ALMOX' not in col and 'IMPORT' not in col and 'TOTAL' not in col:
                    print(f"✅ Mapeando '{col}' para BENS_MOVEIS")
                    df['BENS_MOVEIS'] = df[col]
                    break
        
        if 'BENS_MOVEIS_ALMOX' not in df.columns:
            print("⚠️ Coluna BENS_MOVEIS_ALMOX não encontrada diretamente")
            # Procura por variações do nome
            for col in df.columns:
                if 'ALMOX' in col:
                    print(f"✅ Mapeando '{col}' para BENS_MOVEIS_ALMOX")
                    df['BENS_MOVEIS_ALMOX'] = df[col]
                    break
        
        if 'BENS_MOVEIS_IMPORT' not in df.columns:
            print("⚠️ Coluna BENS_MOVEIS_IMPORT não encontrada diretamente")
            # Procura por variações do nome
            for col in df.columns:
                if 'IMPORT' in col:
                    print(f"✅ Mapeando '{col}' para BENS_MOVEIS_IMPORT")
                    df['BENS_MOVEIS_IMPORT'] = df[col]
                    break
        
        # Garante que todas as colunas necessárias existam (cria com zeros se não existirem)
        colunas_necessarias = ['COUG', 'NOUG', 'SUBITEM', 'BENS_MOVEIS', 'BENS_MOVEIS_ALMOX', 'BENS_MOVEIS_IMPORT']
        for col in colunas_necessarias:
            if col not in df.columns:
                print(f"⚠️ Criando coluna {col} com valores zero")
                df[col] = 0
        
        # Converte valores para numérico e preenche NaN com 0
        for col in ['BENS_MOVEIS', 'BENS_MOVEIS_ALMOX', 'BENS_MOVEIS_IMPORT']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Mostra algumas linhas com valores para debug
        print("\n📊 Amostra de dados carregados (linhas com valores > 0):")
        df_com_valores = df[(df['BENS_MOVEIS'] > 0) | (df['BENS_MOVEIS_ALMOX'] > 0) | (df['BENS_MOVEIS_IMPORT'] > 0)]
        if not df_com_valores.empty:
            print(df_com_valores[['COUG', 'SUBITEM', 'BENS_MOVEIS', 'BENS_MOVEIS_ALMOX', 'BENS_MOVEIS_IMPORT']].head(10))
        else:
            print("⚠️ Nenhuma linha com valores > 0 encontrada!")
        
        # Garante que SUBITEM seja string com 2 dígitos
        if 'SUBITEM' in df.columns:
            df['SUBITEM'] = df['SUBITEM'].apply(lambda x: str(int(x)).zfill(2) if pd.notna(x) else '00')
        
        if 'NOUG' in df.columns:
            print(f"🏛️ NOUGs encontradas: {df['NOUG'].nunique()} unidades")

        # Salva no cache se disponível
        if CACHE_AVAILABLE and cache_service:
            try:
                cache_service.cache_dataframe(df, caminho_arquivo, 'bens_moveis')
            except:
                pass

        fim = time.time()
        print(f"⏱️ Dados de bens móveis carregados em {fim - inicio:.2f} segundos")

        return df

    except Exception as e:
        print(f"❌ Erro ao carregar dados de bens móveis: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def carregar_saldos_contabeis():
    """
    Carrega especificamente a planilha 19-SaldoBensMoveis.xlsx
    para exibir a tabela de saldos contábeis no início do relatório
    
    Returns:
        DataFrame com códigos e saldos
    """
    # Lista de possíveis nomes para o arquivo
    possiveis_arquivos = [
        os.path.join('dados', '19-SaldoBensMoveis.xlsx'),
        os.path.join('dados', '19SaldoBensMoveis.xlsx'),
        os.path.join('dados', '19-Saldo Bens Móveis.xlsx'),
        os.path.join('dados', '19 Saldo Bens Móveis.xlsx')
    ]
    
    caminho_arquivo = None
    for arquivo in possiveis_arquivos:
        if os.path.exists(arquivo):
            caminho_arquivo = arquivo
            break
    
    if not caminho_arquivo:
        print(f"❌ Arquivo de saldos contábeis não encontrado")
        return None
    
    try:
        print(f"🔄 Carregando saldos contábeis de: {caminho_arquivo}")
        df = pd.read_excel(caminho_arquivo)
        
        # Remove espaços dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        print(f"📊 Colunas encontradas: {df.columns.tolist()}")
        print(f"📊 Número de linhas: {len(df)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar saldos contábeis: {e}")
        return None

def carregar_dataframe_sisgepat():
    """
    Carrega o DataFrame com dados do relatório SISGEPAT
    
    Returns:
        DataFrame com dados do SISGEPAT
    """
    try:
        # Ajuste o caminho conforme necessário
        df = pd.read_excel('dados/Relatorio_Demonstrativos_Bem_Moveis.xlsx', 
                          header=None,  # Sem cabeçalho, pois os dados começam direto
                          dtype=str)    # Tudo como string para facilitar processamento
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar dados SISGEPAT: {str(e)}")
        raise

def carregar_dataframe_depara():
    """
    Carrega o DataFrame com DE-PARA entre Local e COUG
    
    Returns:
        DataFrame com correspondência Local -> COUG
    """
    try:
        # Ajuste o caminho e nomes das colunas conforme necessário
        df = pd.read_excel('dados/DEPARAUG.xlsx')
        
        # Garante que as colunas estejam no formato esperado
        # Ajuste os nomes reais das colunas aqui
        if 'LOCAL' in df.columns:
            df.rename(columns={'LOCAL': 'Local'}, inplace=True)
        
        # Remove zeros à esquerda do Local se necessário
        df['Local'] = df['Local'].astype(str).str.strip()
        df['COUG'] = df['COUG'].astype(str).str.strip()
        
        print(f"✅ DE-PARA carregado: {len(df)} registros")
        
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar dados DE-PARA: {str(e)}")
        raise