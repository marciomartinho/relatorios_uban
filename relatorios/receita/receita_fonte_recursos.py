"""
Relatório: Receita por Fonte de Recursos
Analisa receita agrupando primeiro por FONTE e depois mostrando as RECEITAS
HIERARQUIA INVERTIDA: Fonte → Receitas (ao contrário do relatório conta corrente)
"""
import os
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_receita_fonte_recursos(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de receita por fonte de recursos com comparativo 2024 vs 2025
    
    REGRAS DE NEGÓCIO:
    - COCONTACORRENTE tem 17 caracteres
    - Posições 1-8: RECEITA (código da receita)
    - Posições 9-17: FONTE (código da fonte)
    - Busca nome da receita na planilha CLASSIFICACAO_ORCAMENTARIA
    - Busca nome da fonte na planilha FONTE.xlsx
    - HIERARQUIA INVERTIDA: Agrupa primeiro por FONTE, depois mostra RECEITAS
    - Compara 2024 vs 2025 com variações absoluta e percentual
    
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
    
    # Carrega planilhas de classificação
    df_classificacao = _carregar_classificacao_orcamentaria()
    df_fontes = _carregar_fontes()
    
    # Aplica classificação de receitas aos dados de 2025
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
    
    # Aplica classificação de fontes aos dados de 2025
    if df_fontes.empty:
        print("⚠️ Planilha de fontes não encontrada ou vazia")
        df_2025_trabalho['NOME_FONTE'] = 'Nome da fonte não encontrado'
    else:
        print(f"✅ Classificação de fontes carregada: {len(df_fontes)} registros")
        df_2025_trabalho = df_2025_trabalho.merge(
            df_fontes[['COFONTE', 'NOFONTE']], 
            left_on='FONTE_CODIGO', 
            right_on='COFONTE', 
            how='left'
        )
        df_2025_trabalho['NOME_FONTE'] = df_2025_trabalho['NOFONTE'].fillna('Fonte não encontrada')
    
    # Aplica classificação aos dados de 2024
    if not df_2024_trabalho.empty:
        if not df_classificacao.empty:
            df_2024_trabalho = df_2024_trabalho.merge(
                df_classificacao[['COCLASSEORC', 'NOCLASSIFICACAO']], 
                left_on='RECEITA_CODIGO', 
                right_on='COCLASSEORC', 
                how='left'
            )
            df_2024_trabalho['NOME_RECEITA'] = df_2024_trabalho['NOCLASSIFICACAO'].fillna('Classificação não encontrada')
        
        if not df_fontes.empty:
            df_2024_trabalho = df_2024_trabalho.merge(
                df_fontes[['COFONTE', 'NOFONTE']], 
                left_on='FONTE_CODIGO', 
                right_on='COFONTE', 
                how='left'
            )
            df_2024_trabalho['NOME_FONTE'] = df_2024_trabalho['NOFONTE'].fillna('Fonte não encontrada')
    
    # HIERARQUIA INVERTIDA: Agrupa dados por FONTE_CODIGO (fontes principais)
    resultado_fontes_2025 = df_2025_trabalho.groupby(['FONTE_CODIGO', 'NOME_FONTE']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    resultado_fontes_2025.columns = ['FONTE_CODIGO', 'NOME_FONTE', 'RECEITA_2025']
    
    resultado_fontes_2024 = pd.DataFrame()
    if not df_2024_trabalho.empty:
        resultado_fontes_2024 = df_2024_trabalho.groupby(['FONTE_CODIGO', 'NOME_FONTE']).agg({
            'RECEITA LIQUIDA': 'sum'
        }).reset_index()
        resultado_fontes_2024.columns = ['FONTE_CODIGO', 'NOME_FONTE', 'RECEITA_2024']
    
    # Combina dados de fontes de 2025 e 2024
    if not resultado_fontes_2024.empty:
        resultado_fontes = resultado_fontes_2025.merge(
            resultado_fontes_2024[['FONTE_CODIGO', 'RECEITA_2024']], 
            on='FONTE_CODIGO', 
            how='left'
        )
        resultado_fontes['RECEITA_2024'] = resultado_fontes['RECEITA_2024'].fillna(0)
    else:
        resultado_fontes = resultado_fontes_2025.copy()
        resultado_fontes['RECEITA_2024'] = 0
    
    # Calcula variações das fontes
    resultado_fontes['VARIACAO_ABSOLUTA'] = resultado_fontes['RECEITA_2025'] - resultado_fontes['RECEITA_2024']
    resultado_fontes['VARIACAO_PERCENTUAL'] = resultado_fontes.apply(
        lambda row: ((row['RECEITA_2025'] - row['RECEITA_2024']) / row['RECEITA_2024'] * 100) 
        if row['RECEITA_2024'] > 0 else (100 if row['RECEITA_2025'] > 0 else 0), 
        axis=1
    )
    
    # Ordena por receita de 2025 (maior para menor)
    resultado_fontes = resultado_fontes.sort_values('RECEITA_2025', ascending=False)
    
    # Agrupa dados por FONTE_CODIGO + RECEITA_CODIGO (receitas por fonte)
    resultado_receitas_2025 = df_2025_trabalho.groupby(['FONTE_CODIGO', 'RECEITA_CODIGO', 'NOME_RECEITA']).agg({
        'RECEITA LIQUIDA': 'sum'
    }).reset_index()
    resultado_receitas_2025.columns = ['FONTE_CODIGO', 'RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2025']
    
    resultado_receitas_2024 = pd.DataFrame()
    if not df_2024_trabalho.empty:
        resultado_receitas_2024 = df_2024_trabalho.groupby(['FONTE_CODIGO', 'RECEITA_CODIGO', 'NOME_RECEITA']).agg({
            'RECEITA LIQUIDA': 'sum'
        }).reset_index()
        resultado_receitas_2024.columns = ['FONTE_CODIGO', 'RECEITA_CODIGO', 'NOME_RECEITA', 'RECEITA_2024']
    
    # Combina dados de receitas de 2025 e 2024
    if not resultado_receitas_2024.empty:
        resultado_receitas = resultado_receitas_2025.merge(
            resultado_receitas_2024[['FONTE_CODIGO', 'RECEITA_CODIGO', 'RECEITA_2024']], 
            on=['FONTE_CODIGO', 'RECEITA_CODIGO'], 
            how='left'
        )
        resultado_receitas['RECEITA_2024'] = resultado_receitas['RECEITA_2024'].fillna(0)
    else:
        resultado_receitas = resultado_receitas_2025.copy()
        resultado_receitas['RECEITA_2024'] = 0
    
    # Calcula variações das receitas
    resultado_receitas['VARIACAO_ABSOLUTA'] = resultado_receitas['RECEITA_2025'] - resultado_receitas['RECEITA_2024']
    resultado_receitas['VARIACAO_PERCENTUAL'] = resultado_receitas.apply(
        lambda row: ((row['RECEITA_2025'] - row['RECEITA_2024']) / row['RECEITA_2024'] * 100) 
        if row['RECEITA_2024'] > 0 else (100 if row['RECEITA_2025'] > 0 else 0), 
        axis=1
    )
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada fonte principal
    for _, fonte in resultado_fontes.iterrows():
        codigo_fonte = fonte['FONTE_CODIGO']
        nome_fonte = fonte['NOME_FONTE']
        valor_2025 = float(fonte['RECEITA_2025'])
        valor_2024 = float(fonte['RECEITA_2024'])
        variacao_abs = float(fonte['VARIACAO_ABSOLUTA'])
        variacao_perc = float(fonte['VARIACAO_PERCENTUAL'])
        
        # Só inclui se pelo menos um dos valores for maior que zero
        if valor_2025 > 0 or valor_2024 > 0:
            # Conta quantas receitas esta fonte tem
            receitas_desta_fonte = resultado_receitas[resultado_receitas['FONTE_CODIGO'] == codigo_fonte]
            tem_receitas = len(receitas_desta_fonte) > 0
            
            linha_fonte = {
                'tipo': 'fonte',
                'fonte_codigo': codigo_fonte,
                'nome_fonte': nome_fonte,
                'receita_2025': valor_2025,
                'receita_2024': valor_2024,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'fonte_codigo_fmt': codigo_fonte,
                'nome_fonte_fmt': nome_fonte,
                'receita_2025_fmt': motor.formatar_numero(valor_2025),
                'receita_2024_fmt': motor.formatar_numero(valor_2024),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc),
                'tem_receitas': tem_receitas,
                'qtd_receitas': len(receitas_desta_fonte)
            }
            dados_numericos.append(linha_fonte)
            dados_para_ia.append(linha_fonte)
            
            # Adiciona as receitas desta fonte (inicialmente ocultas)
            for _, receita in receitas_desta_fonte.iterrows():
                receita_codigo = receita['RECEITA_CODIGO']
                nome_receita = receita['NOME_RECEITA']
                valor_2025_receita = float(receita['RECEITA_2025'])
                valor_2024_receita = float(receita['RECEITA_2024'])
                variacao_abs_receita = float(receita['VARIACAO_ABSOLUTA'])
                variacao_perc_receita = float(receita['VARIACAO_PERCENTUAL'])
                
                linha_receita = {
                    'tipo': 'receita',
                    'fonte_pai': codigo_fonte,
                    'receita_codigo': receita_codigo,
                    'nome_receita': nome_receita,
                    'receita_2025': valor_2025_receita,
                    'receita_2024': valor_2024_receita,
                    'variacao_abs': variacao_abs_receita,
                    'variacao_perc': variacao_perc_receita,
                    'receita_codigo_fmt': receita_codigo,
                    'nome_receita_fmt': nome_receita,
                    'receita_2025_fmt': motor.formatar_numero(valor_2025_receita),
                    'receita_2024_fmt': motor.formatar_numero(valor_2024_receita),
                    'variacao_abs_fmt': motor.formatar_numero(variacao_abs_receita),
                    'variacao_perc_fmt': formatar_percentual(variacao_perc_receita),
                    'tem_receitas': False,
                    'qtd_receitas': 0
                }
                dados_numericos.append(linha_receita)
    
    # Adiciona totais gerais (apenas das fontes principais)
    fontes_principais = [d for d in dados_numericos if d['tipo'] == 'fonte']
    if fontes_principais:
        total_2025 = sum(l['receita_2025'] for l in fontes_principais)
        total_2024 = sum(l['receita_2024'] for l in fontes_principais)
        total_variacao_abs = total_2025 - total_2024
        total_variacao_perc = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else (100 if total_2025 > 0 else 0)
        
        linha_total = {
            'tipo': 'total',
            'fonte_codigo': 'TOTAL',
            'nome_fonte': 'TOTAL GERAL',
            'receita_2025': total_2025,
            'receita_2024': total_2024,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc,
            'fonte_codigo_fmt': 'TOTAL',
            'nome_fonte_fmt': 'TOTAL GERAL',
            'receita_2025_fmt': motor.formatar_numero(total_2025),
            'receita_2024_fmt': motor.formatar_numero(total_2024),
            'variacao_abs_fmt': motor.formatar_numero(total_variacao_abs),
            'variacao_perc_fmt': formatar_percentual(total_variacao_perc),
            'tem_receitas': False,
            'qtd_receitas': 0
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({
            'fonte_codigo': 'TOTAL', 
            'nome_fonte': 'TOTAL GERAL', 
            'receita_2025': total_2025,
            'receita_2024': total_2024,
            'variacao_abs': total_variacao_abs,
            'variacao_perc': total_variacao_perc
        })
    
    # Dados para PDF (apenas fontes principais para não ficar muito extenso)
    dados_pdf = {
        "head": [['CÓDIGO FONTE', 'NOME DA FONTE', f'RECEITA {mes_referencia}/2024', f'RECEITA {mes_referencia}/2025', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": [
            [linha.get('fonte_codigo_fmt', ''), linha.get('nome_fonte_fmt', ''), 
             linha.get('receita_2024_fmt', 'R$ 0,00'), linha.get('receita_2025_fmt', 'R$ 0,00'),
             linha.get('variacao_abs_fmt', 'R$ 0,00'), linha.get('variacao_perc_fmt', '0,00%')]
            for linha in dados_numericos if linha['tipo'] in ['fonte', 'total']
        ]
    }
    
    print(f"✅ Relatório hierárquico gerado: {len(dados_numericos)} linhas (fontes + receitas + total)")
    
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
        
        df = pd.read_excel(
            caminho_arquivo,
            usecols=['COCLASSEORC', 'NOCLASSIFICACAO'],
            dtype={
                'COCLASSEORC': str,
                'NOCLASSIFICACAO': str
            }
        )
        
        df = df.drop_duplicates(subset=['COCLASSEORC'])
        df = df.dropna(subset=['COCLASSEORC', 'NOCLASSIFICACAO'])
        
        print(f"✅ Classificação carregada: {len(df)} registros únicos")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar classificação orçamentária: {e}")
        return pd.DataFrame()

def _carregar_fontes():
    """
    Carrega a planilha de fontes
    
    Returns:
        DataFrame com COFONTE e NOFONTE
    """
    caminho_arquivo = os.path.join('dados', 'FONTE.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        print(f"🔄 Carregando fontes de {caminho_arquivo}")
        
        df = pd.read_excel(
            caminho_arquivo,
            usecols=['COFONTE', 'NOFONTE'],
            dtype={
                'COFONTE': str,
                'NOFONTE': str
            }
        )
        
        df = df.drop_duplicates(subset=['COFONTE'])
        df = df.dropna(subset=['COFONTE', 'NOFONTE'])
        
        print(f"✅ Fontes carregadas: {len(df)} registros únicos")
        
        # Log dos primeiros registros para debug
        if len(df) > 0:
            print("📋 Primeiros registros das fontes:")
            for i, row in df.head(3).iterrows():
                print(f"   {row['COFONTE']} -> {row['NOFONTE']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar fontes: {e}")
        return pd.DataFrame()