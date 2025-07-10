"""
Relatório: Bens Móveis
Demonstrativo de saldos de bens móveis por UG com integração SISGEPAT
"""
import pandas as pd
from utils.formatacao import formatar_numero
import pdfplumber
import re

# COUGs a serem excluídas da apresentação consolidada
COUGS_EXCLUIDAS = [
    '10101',    # CÂMARA LEGISLATIVA DO DISTRITO FEDERAL
    '150206',   # AGÊNCIA REGULADORA DE ÁGUAS E SANEAMENTO BÁSICO DO DF – ADASA
    '170202',   # FUNDAÇÃO HEMOCENTRO DE BRASÍLIA – FHB
    '190201',   # COMPANHIA URBANIZADORA DA NOVA CAPITAL DO BRASIL – NOVACAP
    '200201',   # SOCIEDADE DE TRANSPORTES COLETIVOS DE BRASÍLIA – TCB
    '200202',   # DEPARTAMENTO DE ESTRADAS DE RODAGEM DO DF – DER/DF
    '200204',   # COMPANHIA DO METROPOLITANO DO DF – METRÔ-DF
    '210203',   # EMPRESA DE ASSISTÊNCIA TÉCNICA E EXTENSÃO RURAL DO DF – EMATER
    '220201',   # DEPARTAMENTO DE TRÂNSITO DO DF – DETRAN-DF
    '280208',   # INSTITUTO DE MEIO AMBIENTE E RECURSOS HÍDRICOS DO DF
    '280209',   # COMPANHIA DE DESENVOLVIMENTO DA HABITAÇÃO DO DF – CODHAB
    '320205',   # SOCIEDADE DE ABASTECIMENTO DE BRASÍLIA – SAB
    '180902',   # FUNDO DE ASSISTÊNCIA SOCIAL DO DISTRITO FEDERAL
    '110903',   # FUNDO DE MANUTENÇÃO E DESENVOLVIMENTO DA EDUCAÇÃO BÁSICA
    '130911',   # FUNDO DE DEFESA DOS DIREITOS DO CONSUMIDOR
    '150901',   # FUNDO DA RECEITA TRIBUTÁRIA DO DF – PRÓ-RECEITA
    '160903',   # FUNDO ÚNICO DE MEIO AMBIENTE DO DISTRITO FEDERAL
    '220904',   # FUNDO DE MODERNIZAÇÃO, MANUTENÇÃO E REEQUIPAMENTO DA PMDF – FUNPM
    '280901',   # FUNDO PENITENCIÁRIO DO DF – FUNPDF
    '220908',   # FUNDO DE SEGURANÇA PÚBLICA DO DISTRITO FEDERAL
    '220909',   # FUNDO DE DESENVOLVIMENTO URBANO DO DISTRITO FEDERAL
    '120901',   # Fundos adicionais
    '180904',   # Fundos adicionais
    '150203',   # INSTITUTO DE ECOLOGIA E MEIO AMBIENTE
    '230201',   # FUNDAÇÃO CULTURAL DO DF
    '530101',   # SEC. DE EST. DE MICRO E PEQ. EMP. E ECON. SOL. DF
    '550101'    # SECRETARIA DE EST. DE REGUL. DE CONDOMÍNIOS DO DF
]

# Local especial do DFTRANS
LOCAL_DFTRANS = '1130000000000'
NOME_DFTRANS = 'TRANSPORTE URBANO DO DISTRITO FEDERAL - DFTRANS'

def processar_pdf_sisgepat(caminho_pdf, df_depara):
    """
    Processa PDF do relatório SISGEPAT para extrair valores por COUG e subitem
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF (dados/Relatorio_Demonstrativos_Bem_Moveis.pdf)
        df_depara: DataFrame com correspondência Local -> COUG
        
    Returns:
        dict: Dicionário com chave (COUG, SUBITEM) e valor do SISGEPAT
    """
    dados_sisgepat = {}
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            local_atual = None
            coug_atual = None
            
            for pagina in pdf.pages:
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
                                print(f"Processando Local {local} -> COUG {coug_atual}")
                            else:
                                coug_atual = None
                                local_atual = None
                    
                    # Se temos uma COUG válida, processa as linhas de dados
                    elif coug_atual and not linha.startswith('Subitem') and not linha.startswith('TOTAL:'):
                        # Tenta extrair subitem e valor da linha
                        # Padrão: número (subitem) no início da linha e valores numéricos
                        partes = linha.split()
                        
                        if len(partes) >= 2:
                            # Verifica se o primeiro elemento é um número (subitem)
                            try:
                                subitem = int(partes[0])
                                if 1 <= subitem <= 99:  # Subitens válidos
                                    subitem_str = str(subitem).zfill(2)
                                    
                                    # Procura o último valor numérico da linha (Saldo Atual - Valor)
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
                                        valor = valores_encontrados[-1]  # Último valor da lista
                                        dados_sisgepat[(coug_atual, subitem_str)] = valor
                                        if valor > 0:
                                            print(f"  -> COUG {coug_atual}, Subitem {subitem_str}: R$ {valor:,.2f}")
                                        else:
                                            print(f"  -> COUG {coug_atual}, Subitem {subitem_str}: R$ 0,00")
                            except:
                                # Não é uma linha de subitem
                                pass
        
        print(f"\nTotal de registros SISGEPAT processados: {len(dados_sisgepat)}")
        return dados_sisgepat
        
    except Exception as e:
        print(f"❌ Erro ao processar PDF SISGEPAT: {str(e)}")
        return {}

def processar_saldos_contabeis(df_saldos, dict_contas=None):
    """
    Processa os saldos contábeis da planilha 19-SaldoBensMoveis.xlsx
    
    Args:
        df_saldos: DataFrame carregado da planilha 19-SaldoBensMoveis.xlsx
        dict_contas: Dicionário com mapeamento COCONTACONTABIL -> NOCONTACONTABIL (opcional)
        
    Returns:
        dict: Dados dos saldos contábeis formatados ou None se não houver dados
    """
    if df_saldos is None or df_saldos.empty:
        return None
        
    dados_saldos = []
    
    try:
        print(f"📊 Processando saldos contábeis...")
        
        # Pega a primeira coluna (códigos) e a última coluna (saldos)
        primeira_coluna = df_saldos.columns[0]
        ultima_coluna = df_saldos.columns[-1]
        
        print(f"📊 Coluna de códigos: {primeira_coluna}")
        print(f"📊 Coluna de saldos: {ultima_coluna}")
        
        # Identifica colunas numéricas para determinar o mês
        colunas_numericas = []
        for col in df_saldos.columns:
            try:
                num = int(str(col))
                if 1 <= num <= 12:  # Apenas meses válidos
                    colunas_numericas.append(num)
            except:
                pass
        
        # Determina o mês de referência
        if colunas_numericas:
            mes_numero = max(colunas_numericas)
            meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_referencia = f"{meses[mes_numero]}/2025"
        else:
            mes_referencia = "Junho/2025"
        
        print(f"📊 Mês de referência: {mes_referencia}")
        
        # Processa cada linha
        for idx, row in df_saldos.iterrows():
            try:
                # Pega o código da primeira coluna
                codigo = str(row[primeira_coluna]).strip()
                
                # Verifica se é um código válido (começa com números)
                if not codigo or not codigo[0].isdigit():
                    continue
                
                # Remove possível .0 no final se existir
                if codigo.endswith('.0'):
                    codigo = codigo[:-2]
                
                # Adiciona '00' ao final do código
                codigo_formatado = codigo + '00'
                
                # Busca o nome da conta se o dicionário foi fornecido
                nome_conta = ""
                if dict_contas and codigo_formatado in dict_contas:
                    nome_conta = dict_contas[codigo_formatado]
                
                # Pega o saldo da última coluna
                saldo = row[ultima_coluna]
                
                # Converte para float
                if pd.isna(saldo) or saldo == '':
                    saldo = 0
                else:
                    saldo = float(saldo)
                
                # Adiciona apenas se tiver saldo positivo
                if saldo > 0:
                    dados_saldos.append({
                        'codigo': codigo_formatado,
                        'nome': nome_conta,
                        'saldo': saldo,
                        'saldo_fmt': formatar_numero(saldo)
                    })
                    
            except Exception as e:
                continue
        
        # Calcula o total
        total_saldos = sum(item['saldo'] for item in dados_saldos)
        
        print(f"✅ Total de contas com saldo: {len(dados_saldos)}")
        print(f"💰 Total geral: {formatar_numero(total_saldos)}")
        
        if not dados_saldos:
            return None
        
        return {
            'itens': sorted(dados_saldos, key=lambda x: x['codigo']),
            'total': total_saldos,
            'total_fmt': formatar_numero(total_saldos),
            'mes_referencia': mes_referencia
        }
        
    except Exception as e:
        print(f"❌ Erro ao processar saldos contábeis: {str(e)}")
        return None

def gerar_relatorio_bens_moveis(df_completo, dados_sisgepat=None, df_depara=None, noug_selecionada=None, df_saldos_contabeis=None):
    """
    Gera o relatório de bens móveis por UG com integração SISGEPAT
    
    Args:
        df_completo: DataFrame com dados de bens móveis (BENSMOVEIS.xlsx)
        dados_sisgepat: Dicionário com dados do SISGEPAT (opcional)
        df_depara: DataFrame com DE-PARA Local -> COUG (opcional)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        df_saldos_contabeis: DataFrame com saldos contábeis (19-SaldoBensMoveis.xlsx) (opcional)
        
    Returns:
        Tuple: (dados_relatorio, dados_pdf, dados_saldos_contabeis)
    """
    # Processar saldos contábeis apenas se não houver filtro de NOUG
    dados_saldos_contabeis = None
    if (not noug_selecionada or noug_selecionada == 'todos') and df_saldos_contabeis is not None:
        # Carrega dicionário de contas contábeis se disponível
        try:
            from utils.data_loaders import carregar_conta_contabil
            dict_contas = carregar_conta_contabil()
        except:
            dict_contas = None
            print("⚠️ Não foi possível carregar nomes das contas contábeis")
            
        dados_saldos_contabeis = processar_saldos_contabeis(df_saldos_contabeis, dict_contas)
    
    # O resto do código permanece EXATAMENTE igual
    # Inicializa estruturas de dados
    dados_relatorio = []
    dados_pdf_body = []
    
    # Se não temos dados SISGEPAT, cria dicionário vazio
    if dados_sisgepat is None:
        dados_sisgepat = {}
    
    # Filtra as COUGs excluídas da planilha base
    df_filtrado = df_completo[~df_completo['COUG'].astype(str).isin(COUGS_EXCLUIDAS)].copy()
    
    # Aplica filtro de NOUG se especificado
    if noug_selecionada and noug_selecionada != 'todos':
        df_filtrado = df_filtrado[df_filtrado['NOUG'] == noug_selecionada].copy()
    
    # Identifica COUG do DFTRANS
    coug_dftrans = None
    if df_depara is not None:
        dftrans_match = df_depara[
            (df_depara['Local'] == LOCAL_DFTRANS) | 
            (df_depara['Local'].str.lstrip('0') == LOCAL_DFTRANS.lstrip('0'))
        ]
        if not dftrans_match.empty:
            coug_dftrans = str(dftrans_match.iloc[0]['COUG']).strip()
            print(f"DFTRANS identificado: Local {LOCAL_DFTRANS} -> COUG {coug_dftrans}")
    
    # Cria estrutura completa de dados combinando planilha base e SISGEPAT
    dados_combinados = {}
    
    # 1. Adiciona dados da planilha base
    print(f"\n📊 Processando {len(df_filtrado)} linhas da planilha base...")
    linhas_com_valor = 0
    
    for _, row in df_filtrado.iterrows():
        coug = str(row['COUG']).strip()
        # Garante que SUBITEM seja formatado corretamente
        try:
            subitem = str(int(float(row['SUBITEM']))).zfill(2) if pd.notna(row['SUBITEM']) else '00'
        except:
            subitem = str(row['SUBITEM']).strip().zfill(2) if pd.notna(row['SUBITEM']) else '00'
            
        noug = row['NOUG']
        
        if noug not in dados_combinados:
            dados_combinados[noug] = {}
        
        chave = (coug, subitem)
        
        # Captura os valores com mais cuidado
        bens_moveis = float(row['BENS_MOVEIS']) if pd.notna(row['BENS_MOVEIS']) else 0.0
        bens_moveis_almox = float(row['BENS_MOVEIS_ALMOX']) if pd.notna(row['BENS_MOVEIS_ALMOX']) else 0.0
        bens_moveis_import = float(row['BENS_MOVEIS_IMPORT']) if pd.notna(row['BENS_MOVEIS_IMPORT']) else 0.0
        
        # Debug para valores que deveriam aparecer
        total_linha = bens_moveis + bens_moveis_almox + bens_moveis_import
        if total_linha > 0:
            linhas_com_valor += 1
            if linhas_com_valor <= 10:  # Mostra as primeiras 10 para debug
                print(f"  ✅ COUG {coug}, Subitem {subitem}: BM={bens_moveis:,.2f}, ALMOX={bens_moveis_almox:,.2f}, IMPORT={bens_moveis_import:,.2f}")
        
        # CORREÇÃO: Se a chave já existe, SOMA os valores ao invés de sobrescrever
        if chave in dados_combinados[noug]:
            # Soma aos valores existentes
            dados_combinados[noug][chave]['BENS_MOVEIS'] += bens_moveis
            dados_combinados[noug][chave]['BENS_MOVEIS_ALMOX'] += bens_moveis_almox
            dados_combinados[noug][chave]['BENS_MOVEIS_IMPORT'] += bens_moveis_import
            print(f"  ➕ Somando valores para COUG {coug}, Subitem {subitem} (linha duplicada)")
        else:
            # Cria novo registro
            dados_combinados[noug][chave] = {
                'COUG': coug,
                'SUBITEM': subitem,
                'BENS_MOVEIS': bens_moveis,
                'BENS_MOVEIS_ALMOX': bens_moveis_almox,
                'BENS_MOVEIS_IMPORT': bens_moveis_import,
                'SISGEPAT': dados_sisgepat.get(chave, 0)
            }
    
    print(f"📊 Total de linhas com valores > 0: {linhas_com_valor}")
    
    # 2. Adiciona dados que existem apenas no SISGEPAT (exceto DFTRANS e COUGs excluídas)
    for (coug, subitem), valor in dados_sisgepat.items():
        if coug in COUGS_EXCLUIDAS or coug == coug_dftrans:
            continue
            
        # Busca NOUG da COUG
        noug_match = df_completo[df_completo['COUG'] == coug]['NOUG'].values
        if len(noug_match) > 0:
            noug = noug_match[0]
            
            # Verifica se deve incluir baseado no filtro
            if noug_selecionada and noug_selecionada != 'todos' and noug != noug_selecionada:
                continue
                
            if noug not in dados_combinados:
                dados_combinados[noug] = {}
                
            chave = (coug, subitem)
            if chave not in dados_combinados[noug]:
                dados_combinados[noug][chave] = {
                    'COUG': coug,
                    'SUBITEM': subitem,
                    'BENS_MOVEIS': 0,
                    'BENS_MOVEIS_ALMOX': 0,
                    'BENS_MOVEIS_IMPORT': 0,
                    'SISGEPAT': valor
                }
    
    # 3. Processa dados do DFTRANS separadamente
    dados_dftrans = {}
    if coug_dftrans and (not noug_selecionada or noug_selecionada == 'todos'):
        for (coug, subitem), valor in dados_sisgepat.items():
            if coug == coug_dftrans:
                dados_dftrans[(coug, subitem)] = {
                    'COUG': coug,
                    'SUBITEM': subitem,
                    'BENS_MOVEIS': 0,
                    'BENS_MOVEIS_ALMOX': 0,
                    'BENS_MOVEIS_IMPORT': 0,
                    'SISGEPAT': valor
                }
    
    # Processa dados por NOUG (exceto DFTRANS)
    for noug in sorted(dados_combinados.keys()):
        # Adiciona cabeçalho da NOUG
        dados_relatorio.append({
            'tipo': 'header_noug',
            'noug': noug,
            'colspan': 8
        })
        
        # Processa cada combinação COUG/SUBITEM
        subtotal_noug = {
            'BENS_MOVEIS': 0,
            'BENS_MOVEIS_ALMOX': 0,
            'BENS_MOVEIS_IMPORT': 0,
            'SISGEPAT': 0
        }
        
        for chave in sorted(dados_combinados[noug].keys()):
            dados = dados_combinados[noug][chave]
            
            # Calcula totais
            saldo_siggo = dados['BENS_MOVEIS'] + dados['BENS_MOVEIS_ALMOX'] + dados['BENS_MOVEIS_IMPORT']
            saldo_sisgepat = dados['SISGEPAT']
            diferenca = saldo_siggo - saldo_sisgepat
            
            # Adiciona linha de dados
            linha_dados = {
                'tipo': 'dados',
                'coug': dados['COUG'],
                'subitem': dados['SUBITEM'],
                'bens_moveis': dados['BENS_MOVEIS'],
                'bens_moveis_almox': dados['BENS_MOVEIS_ALMOX'],
                'bens_moveis_import': dados['BENS_MOVEIS_IMPORT'],
                'saldo_total': saldo_siggo,
                'saldo_sisgepat': saldo_sisgepat,
                'diferenca': diferenca,
                'bens_moveis_fmt': formatar_numero(dados['BENS_MOVEIS']),
                'bens_moveis_almox_fmt': formatar_numero(dados['BENS_MOVEIS_ALMOX']),
                'bens_moveis_import_fmt': formatar_numero(dados['BENS_MOVEIS_IMPORT']),
                'saldo_total_fmt': formatar_numero(saldo_siggo),
                'saldo_sisgepat_fmt': formatar_numero(saldo_sisgepat),
                'diferenca_fmt': formatar_numero(diferenca)
            }
            dados_relatorio.append(linha_dados)
            
            # Adiciona ao PDF
            dados_pdf_body.append([
                noug,
                dados['COUG'],
                dados['SUBITEM'],
                linha_dados['bens_moveis_fmt'],
                linha_dados['bens_moveis_almox_fmt'],
                linha_dados['bens_moveis_import_fmt'],
                linha_dados['saldo_total_fmt'],
                linha_dados['saldo_sisgepat_fmt'],
                linha_dados['diferenca_fmt']
            ])
            
            # Acumula subtotais
            subtotal_noug['BENS_MOVEIS'] += dados['BENS_MOVEIS']
            subtotal_noug['BENS_MOVEIS_ALMOX'] += dados['BENS_MOVEIS_ALMOX']
            subtotal_noug['BENS_MOVEIS_IMPORT'] += dados['BENS_MOVEIS_IMPORT']
            subtotal_noug['SISGEPAT'] += dados['SISGEPAT']
        
        # Adiciona subtotal da NOUG
        total_siggo_noug = subtotal_noug['BENS_MOVEIS'] + subtotal_noug['BENS_MOVEIS_ALMOX'] + subtotal_noug['BENS_MOVEIS_IMPORT']
        diferenca_noug = total_siggo_noug - subtotal_noug['SISGEPAT']
        
        linha_subtotal = {
            'tipo': 'subtotal',
            'noug': noug,
            'bens_moveis': subtotal_noug['BENS_MOVEIS'],
            'bens_moveis_almox': subtotal_noug['BENS_MOVEIS_ALMOX'],
            'bens_moveis_import': subtotal_noug['BENS_MOVEIS_IMPORT'],
            'saldo_total': total_siggo_noug,
            'saldo_sisgepat': subtotal_noug['SISGEPAT'],
            'diferenca': diferenca_noug,
            'bens_moveis_fmt': formatar_numero(subtotal_noug['BENS_MOVEIS']),
            'bens_moveis_almox_fmt': formatar_numero(subtotal_noug['BENS_MOVEIS_ALMOX']),
            'bens_moveis_import_fmt': formatar_numero(subtotal_noug['BENS_MOVEIS_IMPORT']),
            'saldo_total_fmt': formatar_numero(total_siggo_noug),
            'saldo_sisgepat_fmt': formatar_numero(subtotal_noug['SISGEPAT']),
            'diferenca_fmt': formatar_numero(diferenca_noug)
        }
        dados_relatorio.append(linha_subtotal)
        
        # Adiciona subtotal ao PDF
        dados_pdf_body.append([
            'SUBTOTAL',
            '',
            '',
            linha_subtotal['bens_moveis_fmt'],
            linha_subtotal['bens_moveis_almox_fmt'],
            linha_subtotal['bens_moveis_import_fmt'],
            linha_subtotal['saldo_total_fmt'],
            linha_subtotal['saldo_sisgepat_fmt'],
            linha_subtotal['diferenca_fmt']
        ])
        
        # Adiciona separador
        if list(dados_combinados.keys())[-1] != noug or dados_dftrans:
            dados_relatorio.append({'tipo': 'separador'})
    
    # Processa DFTRANS por último
    if dados_dftrans:
        # Adiciona cabeçalho do DFTRANS
        dados_relatorio.append({
            'tipo': 'header_noug',
            'noug': NOME_DFTRANS,
            'colspan': 8
        })
        
        # Processa dados do DFTRANS
        subtotal_dftrans = {
            'BENS_MOVEIS': 0,
            'BENS_MOVEIS_ALMOX': 0,
            'BENS_MOVEIS_IMPORT': 0,
            'SISGEPAT': 0
        }
        
        for chave in sorted(dados_dftrans.keys()):
            dados = dados_dftrans[chave]
            
            # Para DFTRANS, saldo SIGGO é sempre 0
            saldo_siggo = 0
            saldo_sisgepat = dados['SISGEPAT']
            diferenca = saldo_siggo - saldo_sisgepat
            
            # Adiciona linha de dados
            linha_dados = {
                'tipo': 'dados',
                'coug': dados['COUG'],
                'subitem': dados['SUBITEM'],
                'bens_moveis': 0,
                'bens_moveis_almox': 0,
                'bens_moveis_import': 0,
                'saldo_total': 0,
                'saldo_sisgepat': saldo_sisgepat,
                'diferenca': diferenca,
                'bens_moveis_fmt': formatar_numero(0),
                'bens_moveis_almox_fmt': formatar_numero(0),
                'bens_moveis_import_fmt': formatar_numero(0),
                'saldo_total_fmt': formatar_numero(0),
                'saldo_sisgepat_fmt': formatar_numero(saldo_sisgepat),
                'diferenca_fmt': formatar_numero(diferenca)
            }
            dados_relatorio.append(linha_dados)
            
            # Adiciona ao PDF
            dados_pdf_body.append([
                NOME_DFTRANS,
                dados['COUG'],
                dados['SUBITEM'],
                linha_dados['bens_moveis_fmt'],
                linha_dados['bens_moveis_almox_fmt'],
                linha_dados['bens_moveis_import_fmt'],
                linha_dados['saldo_total_fmt'],
                linha_dados['saldo_sisgepat_fmt'],
                linha_dados['diferenca_fmt']
            ])
            
            # Acumula subtotais
            subtotal_dftrans['SISGEPAT'] += dados['SISGEPAT']
        
        # Adiciona subtotal do DFTRANS
        diferenca_dftrans = 0 - subtotal_dftrans['SISGEPAT']
        
        linha_subtotal = {
            'tipo': 'subtotal',
            'noug': NOME_DFTRANS,
            'bens_moveis': 0,
            'bens_moveis_almox': 0,
            'bens_moveis_import': 0,
            'saldo_total': 0,
            'saldo_sisgepat': subtotal_dftrans['SISGEPAT'],
            'diferenca': diferenca_dftrans,
            'bens_moveis_fmt': formatar_numero(0),
            'bens_moveis_almox_fmt': formatar_numero(0),
            'bens_moveis_import_fmt': formatar_numero(0),
            'saldo_total_fmt': formatar_numero(0),
            'saldo_sisgepat_fmt': formatar_numero(subtotal_dftrans['SISGEPAT']),
            'diferenca_fmt': formatar_numero(diferenca_dftrans)
        }
        dados_relatorio.append(linha_subtotal)
        
        # Adiciona subtotal ao PDF
        dados_pdf_body.append([
            'SUBTOTAL',
            '',
            '',
            linha_subtotal['bens_moveis_fmt'],
            linha_subtotal['bens_moveis_almox_fmt'],
            linha_subtotal['bens_moveis_import_fmt'],
            linha_subtotal['saldo_total_fmt'],
            linha_subtotal['saldo_sisgepat_fmt'],
            linha_subtotal['diferenca_fmt']
        ])
    
    # Calcula total geral
    total_geral = {
        'BENS_MOVEIS': 0,
        'BENS_MOVEIS_ALMOX': 0,
        'BENS_MOVEIS_IMPORT': 0,
        'SISGEPAT': 0
    }
    
    # Soma todos os dados (incluindo DFTRANS)
    for noug_dados in dados_combinados.values():
        for dados in noug_dados.values():
            total_geral['BENS_MOVEIS'] += dados['BENS_MOVEIS']
            total_geral['BENS_MOVEIS_ALMOX'] += dados['BENS_MOVEIS_ALMOX']
            total_geral['BENS_MOVEIS_IMPORT'] += dados['BENS_MOVEIS_IMPORT']
            total_geral['SISGEPAT'] += dados['SISGEPAT']
    
    # Adiciona DFTRANS ao total geral
    for dados in dados_dftrans.values():
        total_geral['SISGEPAT'] += dados['SISGEPAT']
    
    # Calcula totais finais
    total_siggo_geral = total_geral['BENS_MOVEIS'] + total_geral['BENS_MOVEIS_ALMOX'] + total_geral['BENS_MOVEIS_IMPORT']
    diferenca_geral = total_siggo_geral - total_geral['SISGEPAT']
    
    # Adiciona linha de total geral
    linha_total_geral = {
        'tipo': 'total',
        'bens_moveis': total_geral['BENS_MOVEIS'],
        'bens_moveis_almox': total_geral['BENS_MOVEIS_ALMOX'],
        'bens_moveis_import': total_geral['BENS_MOVEIS_IMPORT'],
        'saldo_total': total_siggo_geral,
        'saldo_sisgepat': total_geral['SISGEPAT'],
        'diferenca': diferenca_geral,
        'bens_moveis_fmt': formatar_numero(total_geral['BENS_MOVEIS']),
        'bens_moveis_almox_fmt': formatar_numero(total_geral['BENS_MOVEIS_ALMOX']),
        'bens_moveis_import_fmt': formatar_numero(total_geral['BENS_MOVEIS_IMPORT']),
        'saldo_total_fmt': formatar_numero(total_siggo_geral),
        'saldo_sisgepat_fmt': formatar_numero(total_geral['SISGEPAT']),
        'diferenca_fmt': formatar_numero(diferenca_geral)
    }
    dados_relatorio.append(linha_total_geral)
    
    # Adiciona total geral ao PDF
    dados_pdf_body.append([
        'TOTAL GERAL',
        '',
        '',
        linha_total_geral['bens_moveis_fmt'],
        linha_total_geral['bens_moveis_almox_fmt'],
        linha_total_geral['bens_moveis_import_fmt'],
        linha_total_geral['saldo_total_fmt'],
        linha_total_geral['saldo_sisgepat_fmt'],
        linha_total_geral['diferenca_fmt']
    ])
    
    # Prepara dados para PDF
    dados_pdf = {
        "head": [[
            'NOUG',
            'Código\nda UG',
            'Subitem',
            'Saldo\nBens Móveis',
            'Saldo Bens\nMóveis em\nAlmoxarifado',
            'Saldo Bens\nMóveis em\nImportação',
            'Saldo Total\nBens Móveis\nno SIGGO',
            'Saldo Total\nBens Móveis\nno SISGEPAT',
            'Diferença'
        ]],
        "body": dados_pdf_body
    }
    
    return dados_relatorio, dados_pdf, dados_saldos_contabeis