"""
Relatório: Despesa por Função com Tipo de Despesa e Programa de Trabalho
Analisa despesa agrupando por FUNÇÃO → TIPO DE DESPESA → PROGRAMA DE TRABALHO
HIERARQUIA: Função → Tipo (Discricionária/Condicionada) → Programa de Trabalho
"""
import os
import pandas as pd
from motor_relatorios import MotorRelatorios, obter_mes_numero

def gerar_relatorio_despesa_funcao_tipo_programa(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera relatório de despesa por função/tipo de despesa/programa de trabalho
    
    REGRAS DE NEGÓCIO:
    - Agrupa primeiro por COFUNCAO (código da função)
    - Separa por tipo de despesa (Discricionária TD=5 / Obrigatória TD≠5)
    - Detalha por Programa de Trabalho
    - Calcula % empenhado em relação à dotação atualizada
    - Calcula % de despesas discricionárias vs obrigatórias
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    print("🚀 Iniciando gerar_relatorio_despesa_funcao_tipo_programa")
    
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
    df_programa_trabalho = _carregar_programa_trabalho()
    
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
    
    # Aplica classificação de programa de trabalho e TD
    if df_programa_trabalho.empty:
        df_trabalho['NOME_PROGRAMA'] = 'Nome não encontrado'
        df_trabalho['TD_PROGRAMA'] = ''
        df_trabalho['TIPO_DESPESA'] = 'Obrigatória'
    else:
        df_trabalho = df_trabalho.merge(
            df_programa_trabalho,
            left_on='CODIGO_PROGRAMA_TRABALHO',
            right_on='Código',
            how='left'
        )
        df_trabalho['NOME_PROGRAMA'] = df_trabalho['Nome'].fillna('Programa não encontrado')
        df_trabalho['TD_PROGRAMA'] = df_trabalho['TD'].fillna('')
        
        # Classifica tipo de despesa baseado no TD
        # TD deve ser comparado como string de 2 dígitos
        def classificar_tipo_despesa(td):
            # Converte TD para string e padroniza para 2 dígitos
            if pd.isna(td) or str(td).strip() == '':
                return 'Obrigatória'
            
            # Remove espaços e converte para string
            td_str = str(td).strip()
            
            # Se for número, formata com 2 dígitos
            try:
                td_num = int(float(td_str))
                td_formatado = f"{td_num:02d}"
            except:
                # Se não conseguir converter, usa como está
                td_formatado = td_str
            
            # TD = "05" é Discricionária, qualquer outro é Obrigatória
            return 'Discricionária' if td_formatado == '05' else 'Obrigatória'
        
        df_trabalho['TIPO_DESPESA'] = df_trabalho['TD'].apply(classificar_tipo_despesa)
        
        # Debug: mostra distribuição de TDs
        print("\n📊 Distribuição de TDs encontrados:")
        td_counts = df_trabalho.groupby(['TD', 'TIPO_DESPESA']).size().reset_index(name='count')
        for _, row in td_counts.iterrows():
            print(f"   TD: {row['TD']} -> {row['TIPO_DESPESA']} ({row['count']} registros)")
    
    # Calcula dotação atualizada
    df_trabalho['DOTACAO_ATUALIZADA'] = (
        df_trabalho['DOTACAO INICIAL'] + 
        df_trabalho['DOTACAO ADICIONAL'] + 
        df_trabalho['CANCELAMENTO DE DOTACAO'] + 
        df_trabalho['CANCEL-REMANEJA DOTACAO']
    )
    
    # Calcula % empenhado
    df_trabalho['PERCENTUAL_EMPENHADO'] = (
        (df_trabalho['DESPESA EMPENHADA'] / df_trabalho['DOTACAO_ATUALIZADA'] * 100)
        .fillna(0)
        .round(2)
    )
    
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
    
    # Calcula dotação atualizada e percentual para funções
    resultado_funcoes['DOTACAO_ATUALIZADA'] = (
        resultado_funcoes['DOTACAO INICIAL'] + 
        resultado_funcoes['DOTACAO ADICIONAL'] + 
        resultado_funcoes['CANCELAMENTO DE DOTACAO'] + 
        resultado_funcoes['CANCEL-REMANEJA DOTACAO']
    )
    resultado_funcoes['PERCENTUAL_EMPENHADO'] = (
        (resultado_funcoes['DESPESA EMPENHADA'] / resultado_funcoes['DOTACAO_ATUALIZADA'] * 100)
        .fillna(0)
        .round(2)
    )
    
    # Ordena por despesa empenhada (maior para menor)
    resultado_funcoes = resultado_funcoes.sort_values('DESPESA EMPENHADA', ascending=False)
    
    # Agrupa dados por FUNÇÃO + TIPO DE DESPESA
    resultado_tipos = df_trabalho.groupby(['COFUNCAO', 'TIPO_DESPESA']).agg({
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Calcula dotação atualizada e percentual para tipos
    resultado_tipos['DOTACAO_ATUALIZADA'] = (
        resultado_tipos['DOTACAO INICIAL'] + 
        resultado_tipos['DOTACAO ADICIONAL'] + 
        resultado_tipos['CANCELAMENTO DE DOTACAO'] + 
        resultado_tipos['CANCEL-REMANEJA DOTACAO']
    )
    resultado_tipos['PERCENTUAL_EMPENHADO'] = (
        (resultado_tipos['DESPESA EMPENHADA'] / resultado_tipos['DOTACAO_ATUALIZADA'] * 100)
        .fillna(0)
        .round(2)
    )
    
    # Agrupa dados por PROGRAMA DE TRABALHO
    resultado_programas = df_trabalho.groupby(['COFUNCAO', 'TIPO_DESPESA', 'CODIGO_PROGRAMA_TRABALHO', 
                                              'NOME_PROGRAMA', 'TD_PROGRAMA']).agg({
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    # Calcula dotação atualizada e percentual para programas
    resultado_programas['DOTACAO_ATUALIZADA'] = (
        resultado_programas['DOTACAO INICIAL'] + 
        resultado_programas['DOTACAO ADICIONAL'] + 
        resultado_programas['CANCELAMENTO DE DOTACAO'] + 
        resultado_programas['CANCEL-REMANEJA DOTACAO']
    )
    resultado_programas['PERCENTUAL_EMPENHADO'] = (
        (resultado_programas['DESPESA EMPENHADA'] / resultado_programas['DOTACAO_ATUALIZADA'] * 100)
        .fillna(0)
        .round(2)
    )
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Calcula totais gerais para análise percentual
    total_empenhado_discr = resultado_tipos[resultado_tipos['TIPO_DESPESA'] == 'Discricionária']['DESPESA EMPENHADA'].sum()
    total_empenhado_obrig = resultado_tipos[resultado_tipos['TIPO_DESPESA'] == 'Obrigatória']['DESPESA EMPENHADA'].sum()
    total_empenhado_geral = total_empenhado_discr + total_empenhado_obrig
    
    perc_discr = (total_empenhado_discr / total_empenhado_geral * 100) if total_empenhado_geral > 0 else 0
    perc_obrig = (total_empenhado_obrig / total_empenhado_geral * 100) if total_empenhado_geral > 0 else 0
    
    # Adiciona informação de percentuais gerais
    info_percentuais = {
        'tipo': 'info_percentuais',
        'total_empenhado_discr': total_empenhado_discr,
        'total_empenhado_obrig': total_empenhado_obrig,
        'perc_discr': round(perc_discr, 2),
        'perc_obrig': round(perc_obrig, 2),
        'total_empenhado_discr_fmt': motor._formatar_numero(total_empenhado_discr),
        'total_empenhado_obrig_fmt': motor._formatar_numero(total_empenhado_obrig),
        'perc_discr_fmt': f"{perc_discr:.2f}%",
        'perc_obrig_fmt': f"{perc_obrig:.2f}%"
    }
    dados_numericos.append(info_percentuais)
    
    # Processa cada função principal
    for _, funcao in resultado_funcoes.iterrows():
        codigo_funcao = funcao['COFUNCAO']
        nome_funcao = funcao['NOME_FUNCAO']
        dotacao_inicial = float(funcao['DOTACAO INICIAL'])
        dotacao_atualizada = float(funcao['DOTACAO_ATUALIZADA'])
        despesa_empenhada = float(funcao['DESPESA EMPENHADA'])
        despesa_liquidada = float(funcao['DESPESA LIQUIDADA'])
        despesa_paga = float(funcao['DESPESA PAGA'])
        percentual_empenhado = float(funcao['PERCENTUAL_EMPENHADO'])
        
        # Verifica se tem tipos de despesa
        tipos_desta_funcao = resultado_tipos[resultado_tipos['COFUNCAO'] == codigo_funcao]
        tem_tipos = len(tipos_desta_funcao) > 0
        
        linha_funcao = {
            'tipo': 'funcao',
            'funcao_codigo': str(codigo_funcao).zfill(2),
            'nome_funcao': nome_funcao,
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'percentual_empenhado': percentual_empenhado,
            'funcao_codigo_fmt': str(codigo_funcao).zfill(2),
            'nome_funcao_fmt': nome_funcao,
            'dotacao_inicial_fmt': motor._formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor._formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor._formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor._formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor._formatar_numero(despesa_paga),
            'percentual_empenhado_fmt': f"{percentual_empenhado:.2f}%",
            'tem_tipos': tem_tipos
        }
        dados_numericos.append(linha_funcao)
        dados_para_ia.append(linha_funcao)
        
        # Adiciona os tipos de despesa desta função
        for tipo_despesa in ['Discricionária', 'Obrigatória']:
            tipo_dados = tipos_desta_funcao[tipos_desta_funcao['TIPO_DESPESA'] == tipo_despesa]
            
            if len(tipo_dados) > 0:
                tipo_row = tipo_dados.iloc[0]
                dot_inicial_tipo = float(tipo_row['DOTACAO INICIAL'])
                dot_atualizada_tipo = float(tipo_row['DOTACAO_ATUALIZADA'])
                desp_emp_tipo = float(tipo_row['DESPESA EMPENHADA'])
                desp_liq_tipo = float(tipo_row['DESPESA LIQUIDADA'])
                desp_paga_tipo = float(tipo_row['DESPESA PAGA'])
                
                # Para tipos de despesa, calcula % em relação ao total empenhado da função
                perc_tipo_sobre_funcao = (desp_emp_tipo / despesa_empenhada * 100) if despesa_empenhada > 0 else 0
                
                # Conta quantos programas este tipo tem
                programas_deste_tipo = resultado_programas[
                    (resultado_programas['COFUNCAO'] == codigo_funcao) & 
                    (resultado_programas['TIPO_DESPESA'] == tipo_despesa)
                ]
                tem_programas = len(programas_deste_tipo) > 0
                
                linha_tipo = {
                    'tipo': 'tipo_despesa',
                    'funcao_pai': str(codigo_funcao).zfill(2),
                    'tipo_despesa': tipo_despesa,
                    'dotacao_inicial': dot_inicial_tipo,
                    'dotacao_atualizada': dot_atualizada_tipo,
                    'despesa_empenhada': desp_emp_tipo,
                    'despesa_liquidada': desp_liq_tipo,
                    'despesa_paga': desp_paga_tipo,
                    'percentual_empenhado': perc_tipo_sobre_funcao,  # Agora é % sobre o total da função
                    'tipo_despesa_fmt': f"Despesas {tipo_despesa}s",
                    'dotacao_inicial_fmt': motor._formatar_numero(dot_inicial_tipo),
                    'dotacao_atualizada_fmt': motor._formatar_numero(dot_atualizada_tipo),
                    'despesa_empenhada_fmt': motor._formatar_numero(desp_emp_tipo),
                    'despesa_liquidada_fmt': motor._formatar_numero(desp_liq_tipo),
                    'despesa_paga_fmt': motor._formatar_numero(desp_paga_tipo),
                    'percentual_empenhado_fmt': f"{perc_tipo_sobre_funcao:.2f}%",
                    'tem_programas': tem_programas,
                    'qtd_programas': len(programas_deste_tipo)
                }
                dados_numericos.append(linha_tipo)
                
                # Adiciona os programas deste tipo
                for _, programa in programas_deste_tipo.iterrows():
                    codigo_programa = programa['CODIGO_PROGRAMA_TRABALHO']
                    nome_programa = programa['NOME_PROGRAMA']
                    td_programa = programa['TD_PROGRAMA']
                    dot_inicial_prog = float(programa['DOTACAO INICIAL'])
                    dot_atualizada_prog = float(programa['DOTACAO_ATUALIZADA'])
                    desp_emp_prog = float(programa['DESPESA EMPENHADA'])
                    desp_liq_prog = float(programa['DESPESA LIQUIDADA'])
                    desp_paga_prog = float(programa['DESPESA PAGA'])
                    perc_emp_prog = float(programa['PERCENTUAL_EMPENHADO'])
                    
                    linha_programa = {
                        'tipo': 'programa',
                        'funcao_pai': str(codigo_funcao).zfill(2),
                        'tipo_pai': tipo_despesa,
                        'programa_codigo': codigo_programa,
                        'nome_programa': nome_programa,
                        'td_programa': td_programa,
                        'dotacao_inicial': dot_inicial_prog,
                        'dotacao_atualizada': dot_atualizada_prog,
                        'despesa_empenhada': desp_emp_prog,
                        'despesa_liquidada': desp_liq_prog,
                        'despesa_paga': desp_paga_prog,
                        'percentual_empenhado': perc_emp_prog,
                        'programa_codigo_fmt': codigo_programa,
                        'nome_programa_fmt': nome_programa,
                        'td_programa_fmt': f"TD: {td_programa}" if td_programa else "",
                        'dotacao_inicial_fmt': motor._formatar_numero(dot_inicial_prog),
                        'dotacao_atualizada_fmt': motor._formatar_numero(dot_atualizada_prog),
                        'despesa_empenhada_fmt': motor._formatar_numero(desp_emp_prog),
                        'despesa_liquidada_fmt': motor._formatar_numero(desp_liq_prog),
                        'despesa_paga_fmt': motor._formatar_numero(desp_paga_prog),
                        'percentual_empenhado_fmt': f"{perc_emp_prog:.2f}%"
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
            'despesa_paga': sum(l['despesa_paga'] for l in funcoes_principais)
        }
        
        perc_total = (totais['despesa_empenhada'] / totais['dotacao_atualizada'] * 100) if totais['dotacao_atualizada'] > 0 else 0
        
        linha_total = {
            'tipo': 'total',
            'funcao_codigo': 'TOTAL',
            'nome_funcao': 'TOTAL GERAL',
            'dotacao_inicial': totais['dotacao_inicial'],
            'dotacao_atualizada': totais['dotacao_atualizada'],
            'despesa_empenhada': totais['despesa_empenhada'],
            'despesa_liquidada': totais['despesa_liquidada'],
            'despesa_paga': totais['despesa_paga'],
            'percentual_empenhado': round(perc_total, 2),
            'funcao_codigo_fmt': 'TOTAL',
            'nome_funcao_fmt': 'TOTAL GERAL',
            'dotacao_inicial_fmt': motor._formatar_numero(totais['dotacao_inicial']),
            'dotacao_atualizada_fmt': motor._formatar_numero(totais['dotacao_atualizada']),
            'despesa_empenhada_fmt': motor._formatar_numero(totais['despesa_empenhada']),
            'despesa_liquidada_fmt': motor._formatar_numero(totais['despesa_liquidada']),
            'despesa_paga_fmt': motor._formatar_numero(totais['despesa_paga']),
            'percentual_empenhado_fmt': f"{perc_total:.2f}%",
            'tem_tipos': False
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'nome_funcao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF (apenas funções principais)
    dados_pdf = {
        "head": [['CÓD. FUNÇÃO', 'NOME DA FUNÇÃO', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 
                 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', '% EMPENHADO']],
        "body": [
            [linha.get('funcao_codigo_fmt', ''), linha.get('nome_funcao_fmt', ''), 
             linha.get('dotacao_inicial_fmt', 'R$ 0,00'), linha.get('dotacao_atualizada_fmt', 'R$ 0,00'),
             linha.get('despesa_empenhada_fmt', 'R$ 0,00'), linha.get('despesa_liquidada_fmt', 'R$ 0,00'),
             linha.get('despesa_paga_fmt', 'R$ 0,00'), linha.get('percentual_empenhado_fmt', '0,00%')]
            for linha in dados_numericos if linha['tipo'] in ['funcao', 'total']
        ]
    }
    
    print(f"✅ Relatório por função/tipo/programa gerado: {len(dados_numericos)} linhas")
    
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
            # TD deve ser tratado como string de 2 dígitos
            def formatar_td(td):
                if pd.isna(td) or str(td).strip() == '':
                    return ''
                try:
                    # Converte para número e formata com 2 dígitos
                    td_num = int(float(str(td).strip()))
                    return f"{td_num:02d}"
                except:
                    # Se falhar, retorna como string
                    return str(td).strip()
            
            result_df['TD'] = df[td_col].apply(formatar_td)
        else:
            result_df['TD'] = ''
        
        result_df = result_df.drop_duplicates()
        result_df = result_df.dropna(subset=['Código', 'Nome'])
        
        print(f"✅ Programas de Trabalho carregados: {len(result_df)} registros")
        
        # Log dos primeiros registros para debug
        if len(result_df) > 0:
            print("📋 Primeiros programas:")
            for i, row in result_df.head(5).iterrows():
                print(f"   {row['Código']} -> {row['Nome']} (TD: '{row.get('TD', '')}')")
        
        # Mostra estatísticas de TD
        td_stats = result_df['TD'].value_counts()
        print("\n📊 Estatísticas de TD:")
        for td, count in td_stats.items():
            tipo = 'Discricionária' if td == '05' else 'Obrigatória'
            print(f"   TD '{td}' -> {tipo}: {count} programas")
        
        return result_df
        
    except Exception as e:
        print(f"❌ Erro ao carregar programa de trabalho: {e}")
        return pd.DataFrame()