"""
Relatório: Despesa por Função com Programa de Trabalho
Analisa despesa agrupando por FUNÇÃO → SUBFUNÇÃO → PROGRAMA DE TRABALHO
HIERARQUIA: Função → Subfunção → Programa de Trabalho (com dupla expansão/recolhimento)
"""
import os
import pandas as pd
from motor_relatorios import MotorRelatorios, obter_mes_numero

# Debug inicial
print(f"🔍 [despesa_funcao_programa.py] Diretório atual: {os.getcwd()}")
print(f"🔍 [despesa_funcao_programa.py] Pasta dados existe? {os.path.exists('dados')}")

def gerar_relatorio_despesa_funcao_programa(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa por função/subfunção/programa de trabalho
    
    REGRAS DE NEGÓCIO:
    - Agrupa primeiro por COFUNCAO (código da função)
    - Detalha por COSUBFUNCAO (código da subfunção)
    - Detalha por Programa de Trabalho (COFUNCAO.COSUBFUNCAO.COPROGRAMA.COPROJETO.COSUBTITULO)
    - Busca nome da função na planilha funcao.xlsx
    - Busca nome da subfunção na planilha subfuncao.xlsx
    - Busca nome do programa na planilha Programa de Trabalho.xlsx
    - Permite expandir/recolher com dois níveis de hierarquia
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("🚀 Iniciando gerar_relatorio_despesa_funcao_programa")
    
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        print("⚠️ DataFrame 2025 está vazio")
        return [], obter_mes_numero(df_processar), [], {}
    
    print(f"✅ DataFrame 2025: {len(df_2025)} registros")
    
    # Verifica se as colunas necessárias existem
    colunas_necessarias = ['COFUNCAO', 'COSUBFUNCAO', 'COPROGRAMA', 'COPROJETO', 'COSUBTITULO',
                          'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 
                          'CANCELAMENTO DE DOTACAO', 'CANCEL-REMANEJA DOTACAO', 
                          'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA']
    
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_2025.columns]
    if colunas_faltantes:
        print(f"⚠️ Colunas faltantes: {', '.join(colunas_faltantes)}")
        return [], obter_mes_numero(df_processar), [], {}
    
    print("🔍 Processando dados por função/subfunção/programa...")
    
    # Cria cópia de trabalho
    df_trabalho = df_2025.copy()
    
    # Cria código do programa de trabalho formatado
    df_trabalho['CODIGO_PROGRAMA_TRABALHO'] = (
        df_trabalho['COFUNCAO'].astype(str).str.zfill(2) + '.' +
        df_trabalho['COSUBFUNCAO'].astype(str).str.zfill(3) + '.' +
        df_trabalho['COPROGRAMA'].astype(str).str.zfill(4) + '.' +
        df_trabalho['COPROJETO'].astype(str).str.zfill(4) + '.' +
        df_trabalho['COSUBTITULO'].astype(str).str.zfill(4)
    )
    
    # Carrega planilhas de classificação
    print("📁 Carregando planilhas auxiliares...")
    df_funcoes = _carregar_funcoes()
    df_subfuncoes = _carregar_subfuncoes()
    df_programa_trabalho = _carregar_programa_trabalho()
    
    print(f"📊 Funções carregadas: {len(df_funcoes)} registros")
    print(f"📊 Subfunções carregadas: {len(df_subfuncoes)} registros")
    print(f"📊 Programas de Trabalho carregados: {len(df_programa_trabalho)} registros")
    
    # Aplica classificação de funções
    if df_funcoes.empty:
        df_trabalho['NOME_FUNCAO'] = 'Nome não encontrado'
    else:
        df_trabalho = df_trabalho.merge(
            df_funcoes[['COFUNCAO', 'NOFUNCAO']], 
            on='COFUNCAO', 
            how='left'
        )
        df_trabalho['NOME_FUNCAO'] = df_trabalho['NOFUNCAO'].fillna('Função não encontrada')
    
    # Aplica classificação de subfunções
    if df_subfuncoes.empty:
        df_trabalho['NOME_SUBFUNCAO'] = 'Nome não encontrado'
    else:
        df_trabalho = df_trabalho.merge(
            df_subfuncoes[['COSUBFUNCAO', 'NOSUBFUNCAO']], 
            on='COSUBFUNCAO', 
            how='left'
        )
        df_trabalho['NOME_SUBFUNCAO'] = df_trabalho['NOSUBFUNCAO'].fillna('Subfunção não encontrada')
    
    # Aplica classificação de programa de trabalho
    if df_programa_trabalho.empty:
        df_trabalho['NOME_PROGRAMA'] = 'Nome não encontrado'
        df_trabalho['TD_PROGRAMA'] = ''
    else:
        df_trabalho = df_trabalho.merge(
            df_programa_trabalho,
            left_on='CODIGO_PROGRAMA_TRABALHO',
            right_on='Código',
            how='left'
        )
        df_trabalho['NOME_PROGRAMA'] = df_trabalho['Nome'].fillna('Programa não encontrado')
        df_trabalho['TD_PROGRAMA'] = df_trabalho['TD'].fillna('')
    
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
    
    # Agrupa dados por PROGRAMA DE TRABALHO
    resultado_programas = df_trabalho.groupby(['COFUNCAO', 'COSUBFUNCAO', 'CODIGO_PROGRAMA_TRABALHO', 
                                              'NOME_PROGRAMA', 'TD_PROGRAMA']).agg({
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Calcula dotação atualizada e saldo para programas
    resultado_programas['DOTACAO_ATUALIZADA'] = (
        resultado_programas['DOTACAO INICIAL'] + 
        resultado_programas['DOTACAO ADICIONAL'] + 
        resultado_programas['CANCELAMENTO DE DOTACAO'] + 
        resultado_programas['CANCEL-REMANEJA DOTACAO']
    )
    resultado_programas['SALDO_DOTACAO'] = (
        resultado_programas['DOTACAO_ATUALIZADA'] - 
        resultado_programas['DESPESA EMPENHADA']
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
            'funcao_codigo': str(codigo_funcao).zfill(2),
            'nome_funcao': nome_funcao,
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'saldo_dotacao': saldo_dotacao,
            'funcao_codigo_fmt': str(codigo_funcao).zfill(2),
            'nome_funcao_fmt': nome_funcao,
            'dotacao_inicial_fmt': motor._formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor._formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor._formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor._formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor._formatar_numero(despesa_paga),
            'saldo_dotacao_fmt': motor._formatar_numero(saldo_dotacao),
            'tem_subfuncoes': tem_subfuncoes,
            'qtd_subfuncoes': len(subfuncoes_desta_funcao)
        }
        dados_numericos.append(linha_funcao)
        dados_para_ia.append(linha_funcao)
        
        # Adiciona as subfunções desta função
        for _, subfuncao in subfuncoes_desta_funcao.iterrows():
            codigo_subfuncao = subfuncao['COSUBFUNCAO']
            nome_subfuncao = subfuncao['NOME_SUBFUNCAO']
            dot_inicial_sub = float(subfuncao['DOTACAO INICIAL'])
            dot_atualizada_sub = float(subfuncao['DOTACAO_ATUALIZADA'])
            desp_emp_sub = float(subfuncao['DESPESA EMPENHADA'])
            desp_liq_sub = float(subfuncao['DESPESA LIQUIDADA'])
            desp_paga_sub = float(subfuncao['DESPESA PAGA'])
            saldo_sub = float(subfuncao['SALDO_DOTACAO'])
            
            # Conta quantos programas esta subfunção tem
            programas_desta_subfuncao = resultado_programas[
                (resultado_programas['COFUNCAO'] == codigo_funcao) & 
                (resultado_programas['COSUBFUNCAO'] == codigo_subfuncao)
            ]
            tem_programas = len(programas_desta_subfuncao) > 0
            
            linha_subfuncao = {
                'tipo': 'subfuncao',
                'funcao_pai': str(codigo_funcao).zfill(2),
                'subfuncao_codigo': str(codigo_subfuncao).zfill(3),
                'nome_subfuncao': nome_subfuncao,
                'dotacao_inicial': dot_inicial_sub,
                'dotacao_atualizada': dot_atualizada_sub,
                'despesa_empenhada': desp_emp_sub,
                'despesa_liquidada': desp_liq_sub,
                'despesa_paga': desp_paga_sub,
                'saldo_dotacao': saldo_sub,
                'subfuncao_codigo_fmt': str(codigo_subfuncao).zfill(3),
                'nome_subfuncao_fmt': nome_subfuncao,
                'dotacao_inicial_fmt': motor._formatar_numero(dot_inicial_sub),
                'dotacao_atualizada_fmt': motor._formatar_numero(dot_atualizada_sub),
                'despesa_empenhada_fmt': motor._formatar_numero(desp_emp_sub),
                'despesa_liquidada_fmt': motor._formatar_numero(desp_liq_sub),
                'despesa_paga_fmt': motor._formatar_numero(desp_paga_sub),
                'saldo_dotacao_fmt': motor._formatar_numero(saldo_sub),
                'tem_programas': tem_programas,
                'qtd_programas': len(programas_desta_subfuncao)
            }
            dados_numericos.append(linha_subfuncao)
            
            # Adiciona os programas desta subfunção
            for _, programa in programas_desta_subfuncao.iterrows():
                codigo_programa = programa['CODIGO_PROGRAMA_TRABALHO']
                nome_programa = programa['NOME_PROGRAMA']
                td_programa = programa['TD_PROGRAMA']
                dot_inicial_prog = float(programa['DOTACAO INICIAL'])
                dot_atualizada_prog = float(programa['DOTACAO_ATUALIZADA'])
                desp_emp_prog = float(programa['DESPESA EMPENHADA'])
                desp_liq_prog = float(programa['DESPESA LIQUIDADA'])
                desp_paga_prog = float(programa['DESPESA PAGA'])
                saldo_prog = float(programa['SALDO_DOTACAO'])
                
                linha_programa = {
                    'tipo': 'programa',
                    'funcao_pai': str(codigo_funcao).zfill(2),
                    'subfuncao_pai': str(codigo_subfuncao).zfill(3),
                    'programa_codigo': codigo_programa,
                    'nome_programa': nome_programa,
                    'td_programa': td_programa,
                    'dotacao_inicial': dot_inicial_prog,
                    'dotacao_atualizada': dot_atualizada_prog,
                    'despesa_empenhada': desp_emp_prog,
                    'despesa_liquidada': desp_liq_prog,
                    'despesa_paga': desp_paga_prog,
                    'saldo_dotacao': saldo_prog,
                    'programa_codigo_fmt': codigo_programa,
                    'nome_programa_fmt': nome_programa,
                    'td_programa_fmt': f"TD: {td_programa}" if td_programa else "",
                    'dotacao_inicial_fmt': motor._formatar_numero(dot_inicial_prog),
                    'dotacao_atualizada_fmt': motor._formatar_numero(dot_atualizada_prog),
                    'despesa_empenhada_fmt': motor._formatar_numero(desp_emp_prog),
                    'despesa_liquidada_fmt': motor._formatar_numero(desp_liq_prog),
                    'despesa_paga_fmt': motor._formatar_numero(desp_paga_prog),
                    'saldo_dotacao_fmt': motor._formatar_numero(saldo_prog)
                }
                dados_numericos.append(linha_programa)
    
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
            'dotacao_inicial_fmt': motor._formatar_numero(totais['dotacao_inicial']),
            'dotacao_atualizada_fmt': motor._formatar_numero(totais['dotacao_atualizada']),
            'despesa_empenhada_fmt': motor._formatar_numero(totais['despesa_empenhada']),
            'despesa_liquidada_fmt': motor._formatar_numero(totais['despesa_liquidada']),
            'despesa_paga_fmt': motor._formatar_numero(totais['despesa_paga']),
            'saldo_dotacao_fmt': motor._formatar_numero(totais['saldo_dotacao']),
            'tem_subfuncoes': False,
            'qtd_subfuncoes': 0
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'nome_funcao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF (apenas funções principais)
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
    
    print(f"✅ Relatório por função/programa gerado: {len(dados_numericos)} linhas")
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

def _carregar_funcoes():
    """Carrega a planilha de funções"""
    caminho_arquivo = os.path.join('dados', 'FUNCAO.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(
            caminho_arquivo,
            dtype={
                'COFUNCAO': 'int64',
                'NOFUNCAO': str
            }
        )
        
        if 'COFUNCAO' not in df.columns or 'NOFUNCAO' not in df.columns:
            return pd.DataFrame()
        
        df = df[['COFUNCAO', 'NOFUNCAO']].drop_duplicates()
        df = df.dropna(subset=['COFUNCAO', 'NOFUNCAO'])
        
        print(f"✅ Funções carregadas: {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar funções: {e}")
        return pd.DataFrame()

def _carregar_subfuncoes():
    """Carrega a planilha de subfunções"""
    caminho_arquivo = os.path.join('dados', 'SUBFUNCAO.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(
            caminho_arquivo,
            dtype={
                'COSUBFUNCAO': 'int64',
                'NOSUBFUNCAO': str
            }
        )
        
        if 'COSUBFUNCAO' not in df.columns or 'NOSUBFUNCAO' not in df.columns:
            return pd.DataFrame()
        
        df = df[['COSUBFUNCAO', 'NOSUBFUNCAO']].drop_duplicates()
        df = df.dropna(subset=['COSUBFUNCAO', 'NOSUBFUNCAO'])
        
        print(f"✅ Subfunções carregadas: {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar subfunções: {e}")
        return pd.DataFrame()

def _carregar_programa_trabalho():
    """Carrega a planilha de programa de trabalho"""
    caminho_arquivo = os.path.join('dados', 'Programa de Trabalho.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(caminho_arquivo)
        
        print(f"📋 Colunas encontradas em Programa de Trabalho: {df.columns.tolist()}")
        
        # Tenta identificar as colunas corretas (case insensitive)
        codigo_col = None
        nome_col = None
        td_col = None
        
        for col in df.columns:
            col_upper = col.upper()
            if 'CÓDIGO' in col_upper or 'CODIGO' in col_upper:
                codigo_col = col
            elif 'NOME' in col_upper:
                nome_col = col
            elif 'TD' in col_upper:
                td_col = col
        
        if not codigo_col or not nome_col:
            print(f"❌ Colunas necessárias não encontradas. Procurando por 'Código/CODIGO' e 'Nome/NOME'")
            print(f"   Colunas disponíveis: {df.columns.tolist()}")
            return pd.DataFrame()
        
        # Cria DataFrame padronizado
        result_df = pd.DataFrame()
        result_df['Código'] = df[codigo_col].astype(str)
        result_df['Nome'] = df[nome_col].astype(str)
        
        if td_col:
            result_df['TD'] = df[td_col].astype(str)
        else:
            result_df['TD'] = ''
        
        result_df = result_df.drop_duplicates()
        result_df = result_df.dropna(subset=['Código', 'Nome'])
        
        print(f"✅ Programas de Trabalho carregados: {len(result_df)} registros")
        
        # Log dos primeiros registros para debug
        if len(result_df) > 0:
            print("📋 Primeiros programas:")
            for i, row in result_df.head(3).iterrows():
                print(f"   {row['Código']} -> {row['Nome']} (TD: {row.get('TD', '')})")
        
        return result_df
        
    except Exception as e:
        print(f"❌ Erro ao carregar programa de trabalho: {e}")
        return pd.DataFrame()