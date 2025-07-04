import os
import time
import pandas as pd
from flask import Flask, render_template, request, jsonify

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

    # Carrega do Excel
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIARECEITA': str,
        'ORIGEM': str, 'NOFONTERECEITA': str,
        'ESPECIE': str, 'NOSUBFONTERECEITA': str,
        'ALINEA': str, 'NOALINEA': str,
        'INTIPOADM': int,
        'NOUG': str
    }
    df = pd.read_excel(caminho_arquivo, dtype=dtype_map)

    # Salva no cache
    cache_service.cache_dataframe(df, caminho_arquivo, 'receita')

    fim = time.time()
    print(f"⏱️ Dados de receita carregados em {fim - inicio:.2f} segundos")

    return df

def carregar_dataframe_despesa():
    """Carrega dados de despesa com cache e otimizações"""
    caminho_arquivo = os.path.join('dados', 'DESPESA.xlsx')

    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()

    # Tenta carregar do cache primeiro
    df_cached = cache_service.get_cached_dataframe(caminho_arquivo, 'despesa')
    if df_cached is not None:
        return df_cached

    print("🔄 Carregando dados de despesa do Excel...")
    inicio = time.time()

    # Carrega apenas as colunas necessárias para melhor performance
    colunas_necessarias = [
        'CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO',
        'MODALIDADE', 'NOMODALIDADE', 'ELEMENTO', 'NOELEMENTO',
        'COEXERCICIO', 'INMES', 'INTIPOADM', 'NOUG',
        'DOTACAO INICIAL', 'DOTACAO ADICIONAL', 'CANCELAMENTO DE DOTACAO',
        'CANCEL-REMANEJA DOTACAO', 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA',
        'DESPESA PAGA', 'SALDO DOTACAO'
    ]

    try:
        # Lê apenas as colunas necessárias
        df = pd.read_excel(
            caminho_arquivo,
            sheet_name=0,
            usecols=lambda x: x in colunas_necessarias,
            dtype={
                'CATEGORIA': str, 'NOCATEGORIA': str,
                'GRUPO': str, 'NOGRUPO': str,
                'MODALIDADE': str, 'NOMODALIDADE': str,
                'ELEMENTO': str, 'NOELEMENTO': str,
                'COEXERCICIO': 'int32',  # Usa int32 para economizar memória
                'INMES': 'int32',
                'INTIPOADM': 'int32',
                'NOUG': str,
                # Colunas numéricas como float32 para economizar memória
                'DOTACAO INICIAL': 'float32',
                'DOTACAO ADICIONAL': 'float32',
                'CANCELAMENTO DE DOTACAO': 'float32',
                'CANCEL-REMANEJA DOTACAO': 'float32',
                'DESPESA EMPENHADA': 'float32',
                'DESPESA LIQUIDADA': 'float32',
                'DESPESA PAGA': 'float32'
            }
        )

        # Pré-filtra apenas dados de 2025 para economizar memória
        df = df[df['COEXERCICIO'] == 2025].copy()

        # Otimiza strings categóricas
        for col in ['CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO', 'NOUG']:
            if col in df.columns:
                df[col] = df[col].astype('category')

        # Salva no cache
        cache_service.cache_dataframe(df, caminho_arquivo, 'despesa')

        fim = time.time()
        print(f"⏱️ Dados de despesa carregados em {fim - inicio:.2f} segundos")
        print(f"📊 {len(df):,} registros carregados (apenas 2025)")

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
        print(f"⏱️ Relatório de receita gerado em {fim - inicio:.2f} segundos")

        return render_template('balanco_orcamentario.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        return render_template('erro.html',
                             titulo="Erro no Relatório de Receita",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/receita-estimada')
def relatorio_receita_estimada():
    """Relatório de receita estimada comparativo anual - FUNCIONAL"""
    try:
        print("🔍 DEBUG: Iniciando relatório de receita estimada...")
        inicio = time.time()

        # Carrega dados
        df_completo = carregar_dataframe_receita()
        print(f"🔍 DEBUG: Dados carregados - {len(df_completo)} registros")

        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        print(f"🔍 DEBUG: NOUG selecionada: {noug_selecionada}")

        # Gera o relatório
        dados_relatorio, dados_para_ia, dados_pdf = gerar_relatorio_receita_estimada(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        print(f"🔍 DEBUG: Relatório gerado - {len(dados_relatorio)} linhas")

        fim = time.time()
        print(f"⏱️ Relatório de receita estimada gerado em {fim - inicio:.2f} segundos")

        # Renderiza template
        print("🔍 DEBUG: Renderizando template relatorio_estimada.html...")
        return render_template('relatorio_estimada.html',
                               dados_relatorio=dados_relatorio,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)

    except Exception as e:
        print(f"❌ ERRO DETALHADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Receita Estimada",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/receita-por-adm')
def relatorio_receita_por_adm():
    """Relatório de receita por administração - EM DESENVOLVIMENTO"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        # Usar o template correto que já existe (relatorio_por_adm.html)
        return render_template('relatorio_por_adm.html',
                               dados_relatorio=[],  # Vazio por enquanto
                               dados_para_ia=[],
                               dados_pdf={},
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               titulo="Relatório em Desenvolvimento",
                               mensagem="O relatório por administração está sendo desenvolvido e estará disponível em breve.")
    except Exception as e:
        return render_template('erro.html',
                             titulo="Erro no Relatório por Administração",
                             mensagem=f"Erro ao acessar relatório: {str(e)}")

@app.route('/relatorio/previsao-atualizada')
def relatorio_previsao_atualizada():
    """Relatório de previsão atualizada"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        # Por enquanto, retorna template de desenvolvimento usando o padrão
        return render_template('erro.html',
                             titulo="Relatório em Desenvolvimento",
                             mensagem="O relatório de previsão atualizada está sendo desenvolvido e estará disponível em breve.")
    except Exception as e:
        return render_template('erro.html',
                             titulo="Erro no Relatório de Previsão Atualizada",
                             mensagem=f"Erro ao acessar relatório: {str(e)}")

# ===================== ROTAS DE DESPESA =====================

@app.route('/relatorio/balanco-despesa')
def relatorio_balanco_despesa():
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        # Verifica se há dados
        if df_completo.empty:
            return render_template('erro.html',
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")

        # Verifica colunas necessárias
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
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

# ===================== ROTAS DE CACHE =====================

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

# ===================== ROTAS DE TESTE =====================

@app.route('/teste-despesa')
def teste_despesa():
    """Rota para testar carregamento dos dados"""
    try:
        inicio = time.time()
        df = carregar_dataframe_despesa()
        fim = time.time()

        if df.empty:
            return "❌ Arquivo DESPESA.xlsx não encontrado ou vazio"

        info = f"""
        <h2>✅ Dados de Despesa Carregados</h2>
        <p><strong>Tempo de carregamento:</strong> {fim - inicio:.2f} segundos</p>
        <p><strong>Linhas:</strong> {len(df):,}</p>
        <p><strong>Colunas:</strong> {len(df.columns)}</p>
        <p><strong>Exercícios:</strong> {sorted(df['COEXERCICIO'].unique().tolist()) if 'COEXERCICIO' in df.columns else 'N/A'}</p>
        <p><strong>Meses:</strong> {sorted(df['INMES'].unique().tolist()) if 'INMES' in df.columns else 'N/A'}</p>
        <p><strong>Uso de memória:</strong> {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB</p>

        <h3>Informações do Cache:</h3>
        <p><strong>Arquivos em cache:</strong> {cache_service.get_cache_info()['total_files']}</p>
        <p><strong>Tamanho do cache:</strong> {cache_service.get_cache_info()['total_size_mb']} MB</p>

        <h3>Ações:</h3>
        <p><a href="/relatorio/balanco-despesa">🔗 Testar Relatório de Despesa</a></p>
        <p><a href="/admin/cache/clear">🗑️ Limpar Cache</a></p>
        <p><a href="/">🏠 Voltar ao Menu</a></p>
        """

        return info

    except Exception as e:
        return f"❌ Erro ao carregar: {str(e)}"

# ===================== ROTA DE TESTE SIMPLES =====================

@app.route('/teste-receita-estimada')
def teste_receita_estimada():
    """Teste simples para verificar se funciona"""
    try:
        return """
        <h1>✅ Teste de Rota Funcionando!</h1>
        <p>Se você está vendo isso, a rota está funcionando.</p>
        <p><strong>Próximo passo:</strong> Testar com dados reais</p>
        <p><a href="/relatorio/receita-estimada">🔗 Testar Relatório Completo</a></p>
        <p><a href="/teste-rotas">🔍 Ver Todas as Rotas</a></p>
        <p><a href="/">🏠 Voltar ao Menu</a></p>
        """
    except Exception as e:
        return f"❌ Erro: {str(e)}"

@app.route('/teste-rotas')
def teste_rotas():
    """Rota para testar todas as rotas disponíveis"""
    try:
        rotas_info = []
        for rule in app.url_map.iter_rules():
            rotas_info.append({
                'rota': rule.rule,
                'metodos': ', '.join(rule.methods - {'HEAD', 'OPTIONS'}),
                'endpoint': rule.endpoint
            })

        # Filtra apenas as rotas de relatório
        rotas_relatorio = [r for r in rotas_info if '/relatorio/' in r['rota']]

        html = """
        <h2>🔍 Teste de Rotas - Relatórios</h2>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .ativo { color: green; font-weight: bold; }
            .dev { color: orange; }
        </style>
        <table>
            <tr>
                <th>Rota</th>
                <th>Métodos</th>
                <th>Endpoint</th>
                <th>Teste</th>
            </tr>
        """

        for rota in rotas_relatorio:
            status = "✅ ATIVO" if rota['endpoint'] == 'relatorio_receita_estimada' else "⚠️ OUTROS"
            cor_class = "ativo" if rota['endpoint'] == 'relatorio_receita_estimada' else "dev"

            html += f"""
            <tr>
                <td><a href="{rota['rota']}" target="_blank">{rota['rota']}</a></td>
                <td>{rota['metodos']}</td>
                <td>{rota['endpoint']}</td>
                <td class="{cor_class}">{status}</td>
            </tr>
            """

        html += """
        </table>
        <br>
        <h3>🎯 Teste Direto:</h3>
        <p><a href="/relatorio/receita-estimada" target="_blank">🔗 Testar /relatorio/receita-estimada</a></p>
        <p><a href="/relatorio/receita-por-adm" target="_blank">🔗 Testar /relatorio/receita-por-adm</a></p>
        <p><a href="/" target="_blank">🏠 Voltar ao Menu Principal</a></p>
        """

        return html

    except Exception as e:
        return f"❌ Erro ao testar rotas: {str(e)}"

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

@app.route('/relatorio/despesa-por-modalidade')
def relatorio_despesa_por_modalidade():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por modalidade está sendo desenvolvido.")

@app.route('/relatorio/despesa-por-noug')
def relatorio_despesa_por_noug():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por unidade gestora está sendo desenvolvido.")

@app.route('/relatorio/execucao-por-programa')
def relatorio_execucao_por_programa():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de execução por programa está sendo desenvolvido.")

@app.route('/relatorio/receita-vs-despesa')
def relatorio_receita_vs_despesa():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório comparativo receita vs despesa está sendo desenvolvido.")

@app.route('/relatorio/evolucao-temporal')
def relatorio_evolucao_temporal():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de evolução temporal está sendo desenvolvido.")

@app.route('/relatorio/indicadores')
def relatorio_indicadores():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de indicadores orçamentários está sendo desenvolvido.")

@app.route('/relatorio/dashboard')
def relatorio_dashboard():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O dashboard executivo está sendo desenvolvido.")

@app.route('/relatorio/por-noug')
def relatorio_por_noug():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório por unidade gestora está sendo desenvolvido.")

@app.route('/relatorio/analise-variacoes')
def relatorio_analise_variacoes():
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="A análise de variações está sendo desenvolvida.")

# ===================== TRATAMENTO DE ERROS =====================

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro.html',
                         titulo="Página Não Encontrada",
                         mensagem="A página solicitada não foi encontrada."), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('erro.html',
                         titulo="Erro Interno",
                         mensagem="Ocorreu um erro interno no servidor."), 500

if __name__ == '__main__':
    app.run(debug=True)