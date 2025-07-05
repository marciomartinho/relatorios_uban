import os
import time
import pandas as pd
from flask import Flask, render_template, request, jsonify
import traceback

# Importações das configurações
from config_relatorios import HIERARQUIA_RECEITAS, MENU_PRINCIPAL

# Importações do motor unificado
from motor_relatorios import (
    gerar_balanco_orcamentario,
    gerar_balanco_despesa,
    gerar_relatorio_estimada,
    gerar_relatorio_por_adm,
    gerar_relatorio_previsao_atualizada,
    gerar_relatorio_receita_estimada
)

# Importa o serviço de cache
from cache_service import cache_service

app = Flask(__name__)

def carregar_dataframe_receita():
    """Carrega dados de receita com cache"""
    caminho_arquivo = os.path.join('dados', 'RECEITA.xlsx')

    # Tenta carregar do cache primeiro
    df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'receita')
    if df_cached is not None:
        return df_cached

    print("🔄 Carregando dados de receita do Excel...")
    inicio = time.time()

    # Carrega do Excel - COLUNAS ATUALIZADAS
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIARECEITA': str,
        'ORIGEM': str, 'NOFONTERECEITA': str,
        'ESPECIE': str, 'NOSUBFONTERECEITA': str,
        'ALINEA': str, 'NOALINEA': str,
        'INTIPOADM': int,
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

    # Salva no cache
    cache_service.cache_dataframe(df, caminho_arquivo, 'receita')

    fim = time.time()
    print(f"⏱️ Dados de receita carregados em {fim - inicio:.2f} segundos")

    return df

def carregar_dataframe_despesa():
    """Carrega dados de despesa com cache e precisão monetária corrigida"""
    caminho_arquivo = os.path.join('dados', 'DESPESA.xlsx')

    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()

    # Tenta carregar do cache primeiro
    df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'despesa')
    if df_cached is not None:
        return df_cached

    print("🔄 Carregando dados de despesa do Excel...")
    inicio = time.time()

    # Colunas necessárias
    colunas_necessarias = [
        'CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO',
        'MODALIDADE', 'NOMODALIDADE', 'ELEMENTO', 'NOELEMENTO',
        'COEXERCICIO', 'INMES', 'INTIPOADM', 'NOUG',
        'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 'CANCELAMENTO DE DOTACAO',
        'CANCEL-REMANEJA DOTACAO', 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA',
        'DESPESA PAGA', 'SALDO DOTACAO'
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
                'INTIPOADM': 'int32',
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

        cache_service.cache_dataframe(df, caminho_arquivo, 'despesa')

        fim = time.time()
        print(f"⏱️ Dados de despesa carregados em {fim - inicio:.2f} segundos")
        print(f"📊 {len(df):,} registros carregados (apenas 2025)")
        print(f"💰 Precisão monetária: float64 aplicada para evitar perda de precisão")

        return df

    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html', menu=MENU_PRINCIPAL)

# ===================== ROTAS DE RECEITA =====================

@app.route('/relatorio/balanco-orcamentario')
def relatorio_balanco_orcamentario():
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_balanco_orcamentario(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )

        fim = time.time()
        print(f"⏱️ Relatório de balanço orçamentário gerado em {fim - inicio:.2f} segundos")

        return render_template('balanco_orcamentario.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Receita",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/receita-estimada')
def relatorio_receita_estimada():
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_relatorio, dados_para_ia, dados_pdf = gerar_relatorio_receita_estimada(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório de receita estimada gerado em {fim - inicio:.2f} segundos")

        return render_template('relatorio_estimada.html',
                               dados_relatorio=dados_relatorio,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)

    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Receita Estimada",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/receita-por-adm')
def relatorio_receita_por_adm():
    """Relatório de receita por administração - AGORA FUNCIONAL"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        # Chama a função do motor que gera os dados para este relatório
        dados_tabela, dados_para_ia, dados_pdf = gerar_relatorio_por_adm(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório por Administração gerado em {fim - inicio:.2f} segundos")

        # Renderiza o template correto 'relatorio_por_adm.html'
        return render_template('relatorio_por_adm.html',
                               dados_relatorio=dados_tabela,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)
                               
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório por Administração",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/previsao-atualizada')
def relatorio_previsao_atualizada():
    """Relatório de previsão atualizada"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de previsão atualizada está sendo desenvolvido.")

# ===================== ROTAS DE DESPESA =====================

@app.route('/relatorio/balanco-despesa')
def relatorio_balanco_despesa():
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        if df_completo.empty:
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        colunas_necessarias = ['CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO', 'NOUG', 'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_balanco_despesa(
            df_completo, None, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório de despesa gerado em {fim - inicio:.2f} segundos")
        
        return render_template('despesas/balanco_despesa.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

# ===================== OUTRAS ROTAS (EM DESENVOLVIMENTO) =====================

@app.route('/relatorio/despesa-por-funcao')
def relatorio_despesa_por_funcao():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por função está sendo desenvolvido.")

@app.route('/relatorio/despesa-por-natureza')
def relatorio_despesa_por_natureza():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por natureza está sendo desenvolvido.")

# ===================== ROTAS DE CACHE E TESTE =====================

@app.route('/admin/cache/info')
def cache_info():
    """Mostra informações do cache"""
    info = cache_service.get_cache_info()
    return jsonify(info)

@app.route('/admin/cache/clear')
def clear_cache():
    """Limpa todo o cache"""
    cache_service.clear_cache()
    return jsonify({"status": "Cache limpo com sucesso"})

# ===================== TRATAMENTO DE ERROS =====================

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro.html', 
                         titulo="Página Não Encontrada",
                         mensagem="A página solicitada não foi encontrada."), 404

@app.errorhandler(500)
def erro_interno(e):
    traceback.print_exc()
    return render_template('erro.html', 
                         titulo="Erro Interno no Servidor",
                         mensagem=f"Ocorreu um erro inesperado. Detalhes: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)