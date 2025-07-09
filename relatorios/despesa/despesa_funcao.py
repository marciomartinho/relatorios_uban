"""
Relatório: Despesa por Função de Governo
Analisa despesa agrupando por FUNÇÃO e depois por SUBFUNÇÃO
HIERARQUIA: Função → Subfunção (com expansão/recolhimento)
"""
import os
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero

# Debug inicial
print(f"🔍 [despesa_funcao.py] Diretório atual: {os.getcwd()}")
print(f"🔍 [despesa_funcao.py] Pasta dados existe? {os.path.exists('dados')}")
if os.path.exists('dados'):
    arquivos = os.listdir('dados')
    print(f"🔍 [despesa_funcao.py] Total de arquivos em dados: {len(arquivos)}")
    # Procura por arquivos de função
    funcao_files = [f for f in arquivos if 'funcao' in f.lower() or 'FUNCAO' in f]
    print(f"🔍 [despesa_funcao.py] Arquivos com 'funcao': {funcao_files}")

def gerar_relatorio_despesa_funcao(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa por função de governo com detalhamento por subfunção
    
    REGRAS DE NEGÓCIO:
    - Agrupa primeiro por COFUNCAO (código da função)
    - Detalha por COSUBFUNCAO (código da subfunção)
    - Busca nome da função na planilha funcao.xlsx (NOFUNCAO)
    - Busca nome da subfunção na planilha subfuncao.xlsx (NOSUBFUNCAO)
    - Calcula dotação atualizada: INICIAL + ADICIONAL + CANCELAMENTO + CANCEL-REMANEJA
    - Calcula saldo: DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
    - Permite expandir/recolher subfunções de cada função
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("🚀 Iniciando gerar_relatorio_despesa_funcao")
    
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        print("⚠️ DataFrame 2025 está vazio")
        return [], obter_mes_numero(df_processar), [], {}
    
    print(f"✅ DataFrame 2025: {len(df_2025)} registros")
    
    # Verifica se as colunas necessárias existem
    colunas_necessarias = ['COFUNCAO', 'COSUBFUNCAO', 'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 
                          'CANCELAMENTO DE DOTACAO', 'CANCEL-REMANEJA DOTACAO', 
                          'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA']
    
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_2025.columns]
    if colunas_faltantes:
        print(f"⚠️ Colunas faltantes: {', '.join(colunas_faltantes)}")
        return [], obter_mes_numero(df_processar), [], {}
    
    print("🔍 Processando dados por função de governo...")
    
    # Cria cópia de trabalho
    df_trabalho = df_2025.copy()
    
    # Carrega planilhas de classificação
    print("📁 Carregando planilhas auxiliares...")
    df_funcoes = _carregar_funcoes()
    df_subfuncoes = _carregar_subfuncoes()
    
    print(f"📊 Funções carregadas: {len(df_funcoes)} registros")
    print(f"📊 Subfunções carregadas: {len(df_subfuncoes)} registros")
    
    # Aplica classificação de funções
    if df_funcoes.empty:
        print("⚠️ Planilha de funções não encontrada ou vazia")
        df_trabalho['NOME_FUNCAO'] = 'Nome não encontrado'
    else:
        print(f"✅ Classificação de funções carregada: {len(df_funcoes)} registros")
        df_trabalho = df_trabalho.merge(
            df_funcoes[['COFUNCAO', 'NOFUNCAO']], 
            on='COFUNCAO', 
            how='left'
        )
        df_trabalho['NOME_FUNCAO'] = df_trabalho['NOFUNCAO'].fillna('Função não encontrada')
    
    # Aplica classificação de subfunções
    if df_subfuncoes.empty:
        print("⚠️ Planilha de subfunções não encontrada ou vazia")
        df_trabalho['NOME_SUBFUNCAO'] = 'Nome não encontrado'
    else:
        print(f"✅ Classificação de subfunções carregada: {len(df_subfuncoes)} registros")
        df_trabalho = df_trabalho.merge(
            df_subfuncoes[['COSUBFUNCAO', 'NOSUBFUNCAO']], 
            on='COSUBFUNCAO', 
            how='left'
        )
        df_trabalho['NOME_SUBFUNCAO'] = df_trabalho['NOSUBFUNCAO'].fillna('Subfunção não encontrada')
    
    # Agrupa dados por FUNÇÃO
    resultado_funcoes = df_trabalho.groupby(['COFUNCAO', 'NOME_FUNCAO']).agg({
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Calcula dotação atualizada e saldo para funções
    resultado_funcoes['DOTACAO_ATUALIZADA'] = (
        resultado_funcoes['DOTACAO INICIAL'] + 
        resultado_funcoes['DOTACAO ADICIONAL'] + 
        resultado_funcoes['CANCELAMENTO DE DOTACAO'] + 
        resultado_funcoes['CANCEL-REMANEJA DOTACAO']
    )
    resultado_funcoes['SALDO_DOTACAO'] = (
        resultado_funcoes['DOTACAO_ATUALIZADA'] - 
        resultado_funcoes['DESPESA EMPENHADA']
    )
    
    # Ordena por despesa empenhada (maior para menor)
    resultado_funcoes = resultado_funcoes.sort_values('DESPESA EMPENHADA', ascending=False)
    
    # Agrupa dados por FUNÇÃO + SUBFUNÇÃO
    resultado_subfuncoes = df_trabalho.groupby(['COFUNCAO', 'COSUBFUNCAO', 'NOME_SUBFUNCAO']).agg({
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Calcula dotação atualizada e saldo para subfunções
    resultado_subfuncoes['DOTACAO_ATUALIZADA'] = (
        resultado_subfuncoes['DOTACAO INICIAL'] + 
        resultado_subfuncoes['DOTACAO ADICIONAL'] + 
        resultado_subfuncoes['CANCELAMENTO DE DOTACAO'] + 
        resultado_subfuncoes['CANCEL-REMANEJA DOTACAO']
    )
    resultado_subfuncoes['SALDO_DOTACAO'] = (
        resultado_subfuncoes['DOTACAO_ATUALIZADA'] - 
        resultado_subfuncoes['DESPESA EMPENHADA']
    )
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada função principal
    for _, funcao in resultado_funcoes.iterrows():
        codigo_funcao = funcao['COFUNCAO']
        nome_funcao = funcao['NOME_FUNCAO']
        dotacao_inicial = float(funcao['DOTACAO INICIAL'])
        dotacao_atualizada = float(funcao['DOTACAO_ATUALIZADA'])
        despesa_empenhada = float(funcao['DESPESA EMPENHADA'])
        despesa_liquidada = float(funcao['DESPESA LIQUIDADA'])
        despesa_paga = float(funcao['DESPESA PAGA'])
        saldo_dotacao = float(funcao['SALDO_DOTACAO'])
        
        # Conta quantas subfunções esta função tem
        subfuncoes_desta_funcao = resultado_subfuncoes[resultado_subfuncoes['COFUNCAO'] == codigo_funcao]
        tem_subfuncoes = len(subfuncoes_desta_funcao) > 0
        
        linha_funcao = {
            'tipo': 'funcao',
            'funcao_codigo': str(codigo_funcao).zfill(2),  # Formata com 2 dígitos
            'nome_funcao': nome_funcao,
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'saldo_dotacao': saldo_dotacao,
            'funcao_codigo_fmt': str(codigo_funcao).zfill(2),
            'nome_funcao_fmt': nome_funcao,
            'dotacao_inicial_fmt': motor.formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor.formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor.formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor.formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor.formatar_numero(despesa_paga),
            'saldo_dotacao_fmt': motor.formatar_numero(saldo_dotacao),
            'tem_subfuncoes': tem_subfuncoes,
            'qtd_subfuncoes': len(subfuncoes_desta_funcao)
        }
        dados_numericos.append(linha_funcao)
        dados_para_ia.append(linha_funcao)
        
        # Adiciona as subfunções desta função (inicialmente ocultas)
        for _, subfuncao in subfuncoes_desta_funcao.iterrows():
            codigo_subfuncao = subfuncao['COSUBFUNCAO']
            nome_subfuncao = subfuncao['NOME_SUBFUNCAO']
            dot_inicial_sub = float(subfuncao['DOTACAO INICIAL'])
            dot_atualizada_sub = float(subfuncao['DOTACAO_ATUALIZADA'])
            desp_emp_sub = float(subfuncao['DESPESA EMPENHADA'])
            desp_liq_sub = float(subfuncao['DESPESA LIQUIDADA'])
            desp_paga_sub = float(subfuncao['DESPESA PAGA'])
            saldo_sub = float(subfuncao['SALDO_DOTACAO'])
            
            linha_subfuncao = {
                'tipo': 'subfuncao',
                'funcao_pai': str(codigo_funcao).zfill(2),
                'subfuncao_codigo': str(codigo_subfuncao).zfill(3),  # Formata com 3 dígitos
                'nome_subfuncao': nome_subfuncao,
                'dotacao_inicial': dot_inicial_sub,
                'dotacao_atualizada': dot_atualizada_sub,
                'despesa_empenhada': desp_emp_sub,
                'despesa_liquidada': desp_liq_sub,
                'despesa_paga': desp_paga_sub,
                'saldo_dotacao': saldo_sub,
                'subfuncao_codigo_fmt': str(codigo_subfuncao).zfill(3),
                'nome_subfuncao_fmt': nome_subfuncao,
                'dotacao_inicial_fmt': motor.formatar_numero(dot_inicial_sub),
                'dotacao_atualizada_fmt': motor.formatar_numero(dot_atualizada_sub),
                'despesa_empenhada_fmt': motor.formatar_numero(desp_emp_sub),
                'despesa_liquidada_fmt': motor.formatar_numero(desp_liq_sub),
                'despesa_paga_fmt': motor.formatar_numero(desp_paga_sub),
                'saldo_dotacao_fmt': motor.formatar_numero(saldo_sub),
                'tem_subfuncoes': False,
                'qtd_subfuncoes': 0
            }
            dados_numericos.append(linha_subfuncao)
    
    # Adiciona totais gerais (apenas das funções principais)
    funcoes_principais = [d for d in dados_numericos if d['tipo'] == 'funcao']
    if funcoes_principais:
        totais = {
            'dotacao_inicial': sum(l['dotacao_inicial'] for l in funcoes_principais),
            'dotacao_atualizada': sum(l['dotacao_atualizada'] for l in funcoes_principais),
            'despesa_empenhada': sum(l['despesa_empenhada'] for l in funcoes_principais),
            'despesa_liquidada': sum(l['despesa_liquidada'] for l in funcoes_principais),
            'despesa_paga': sum(l['despesa_paga'] for l in funcoes_principais),
            'saldo_dotacao': sum(l['saldo_dotacao'] for l in funcoes_principais)
        }
        
        linha_total = {
            'tipo': 'total',
            'funcao_codigo': 'TOTAL',
            'nome_funcao': 'TOTAL GERAL',
            'dotacao_inicial': totais['dotacao_inicial'],
            'dotacao_atualizada': totais['dotacao_atualizada'],
            'despesa_empenhada': totais['despesa_empenhada'],
            'despesa_liquidada': totais['despesa_liquidada'],
            'despesa_paga': totais['despesa_paga'],
            'saldo_dotacao': totais['saldo_dotacao'],
            'funcao_codigo_fmt': 'TOTAL',
            'nome_funcao_fmt': 'TOTAL GERAL',
            'dotacao_inicial_fmt': motor.formatar_numero(totais['dotacao_inicial']),
            'dotacao_atualizada_fmt': motor.formatar_numero(totais['dotacao_atualizada']),
            'despesa_empenhada_fmt': motor.formatar_numero(totais['despesa_empenhada']),
            'despesa_liquidada_fmt': motor.formatar_numero(totais['despesa_liquidada']),
            'despesa_paga_fmt': motor.formatar_numero(totais['despesa_paga']),
            'saldo_dotacao_fmt': motor.formatar_numero(totais['saldo_dotacao']),
            'tem_subfuncoes': False,
            'qtd_subfuncoes': 0
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'nome_funcao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF (apenas funções principais para não ficar muito extenso)
    dados_pdf = {
        "head": [['CÓD. FUNÇÃO', 'NOME DA FUNÇÃO', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 
                 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', 'SALDO DA DOTAÇÃO']],
        "body": [
            [linha.get('funcao_codigo_fmt', ''), linha.get('nome_funcao_fmt', ''), 
             linha.get('dotacao_inicial_fmt', 'R$ 0,00'), linha.get('dotacao_atualizada_fmt', 'R$ 0,00'),
             linha.get('despesa_empenhada_fmt', 'R$ 0,00'), linha.get('despesa_liquidada_fmt', 'R$ 0,00'),
             linha.get('despesa_paga_fmt', 'R$ 0,00'), linha.get('saldo_dotacao_fmt', 'R$ 0,00')]
            for linha in dados_numericos if linha['tipo'] in ['funcao', 'total']
        ]
    }
    
    print(f"✅ Relatório por função gerado: {len(dados_numericos)} linhas (funções + subfunções + total)")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

def _carregar_funcoes():
    """
    Carrega a planilha de funções
    
    Returns:
        DataFrame com COFUNCAO e NOFUNCAO
    """
    caminho_arquivo = os.path.join('dados', 'FUNCAO.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        print(f"🔄 Carregando funções de {caminho_arquivo}")
        
        # Verifica se o arquivo existe antes de tentar ler
        if not os.path.exists(caminho_arquivo):
            print(f"❌ Arquivo não existe: {caminho_arquivo}")
            print(f"📁 Diretório atual: {os.getcwd()}")
            print(f"📁 Arquivos na pasta dados: {os.listdir('dados') if os.path.exists('dados') else 'Pasta dados não existe'}")
        
        df = pd.read_excel(
            caminho_arquivo,
            dtype={
                'COFUNCAO': 'int64',
                'NOFUNCAO': str
            }
        )
        
        # Verifica se as colunas necessárias existem
        if 'COFUNCAO' not in df.columns or 'NOFUNCAO' not in df.columns:
            print(f"❌ Colunas COFUNCAO ou NOFUNCAO não encontradas")
            return pd.DataFrame()
        
        df = df[['COFUNCAO', 'NOFUNCAO']].drop_duplicates()
        df = df.dropna(subset=['COFUNCAO', 'NOFUNCAO'])
        
        print(f"✅ Funções carregadas: {len(df)} registros únicos")
        
        # Log dos primeiros registros para debug
        if len(df) > 0:
            print("📋 Primeiras funções:")
            for i, row in df.head(3).iterrows():
                print(f"   {row['COFUNCAO']:02d} -> {row['NOFUNCAO']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar funções: {e}")
        return pd.DataFrame()

def _carregar_subfuncoes():
    """
    Carrega a planilha de subfunções
    
    Returns:
        DataFrame com COSUBFUNCAO e NOSUBFUNCAO
    """
    caminho_arquivo = os.path.join('dados', 'SUBFUNCAO.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        print(f"🔄 Carregando subfunções de {caminho_arquivo}")
        
        # Verifica se o arquivo existe antes de tentar ler
        if not os.path.exists(caminho_arquivo):
            print(f"❌ Arquivo não existe: {caminho_arquivo}")
            print(f"📁 Diretório atual: {os.getcwd()}")
            print(f"📁 Arquivos na pasta dados: {os.listdir('dados') if os.path.exists('dados') else 'Pasta dados não existe'}")
        
        df = pd.read_excel(
            caminho_arquivo,
            dtype={
                'COSUBFUNCAO': 'int64',
                'NOSUBFUNCAO': str
            }
        )
        
        # Verifica se as colunas necessárias existem
        if 'COSUBFUNCAO' not in df.columns or 'NOSUBFUNCAO' not in df.columns:
            print(f"❌ Colunas COSUBFUNCAO ou NOSUBFUNCAO não encontradas")
            return pd.DataFrame()
        
        df = df[['COSUBFUNCAO', 'NOSUBFUNCAO']].drop_duplicates()
        df = df.dropna(subset=['COSUBFUNCAO', 'NOSUBFUNCAO'])
        
        print(f"✅ Subfunções carregadas: {len(df)} registros únicos")
        
        # Log dos primeiros registros para debug
        if len(df) > 0:
            print("📋 Primeiras subfunções:")
            for i, row in df.head(3).iterrows():
                print(f"   {row['COSUBFUNCAO']:03d} -> {row['NOSUBFUNCAO']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar subfunções: {e}")
        return pd.DataFrame()