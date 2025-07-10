"""
Blueprint para rotas de relatórios de despesa
"""
import os
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações
from utils.data_loaders import carregar_dataframe_despesa

# Importações dos módulos de despesa
from relatorios.despesa import gerar_balanco_despesa
try:
    from relatorios.despesa.despesa_funcao import gerar_relatorio_despesa_funcao
    print("✅ Import de despesa_funcao bem sucedido")
except ImportError as e:
    print(f"❌ Erro ao importar despesa_funcao: {e}")
    gerar_relatorio_despesa_funcao = None

try:
    from relatorios.despesa.despesa_natureza import gerar_relatorio_despesa_natureza
    print("✅ Import de despesa_natureza bem sucedido")
except ImportError as e:
    print(f"❌ Erro ao importar despesa_natureza: {e}")
    gerar_relatorio_despesa_natureza = None

# Adicionar após os imports existentes:
try:
    from relatorios.despesa.despesa_funcao_programa import gerar_relatorio_despesa_funcao_programa
    print("✅ Import de despesa_funcao_programa bem sucedido")
except ImportError as e:
    print(f"❌ Erro ao importar despesa_funcao_programa: {e}")
    gerar_relatorio_despesa_funcao_programa = None

try:
    from relatorios.despesa.despesa_funcao_tipo_programa import gerar_relatorio_despesa_funcao_tipo_programa
    print("✅ Import de despesa_funcao_tipo_programa bem sucedido")
except ImportError as e:
    print(f"❌ Erro ao importar despesa_funcao_tipo_programa: {e}")
    gerar_relatorio_despesa_funcao_tipo_programa = None

# Cria o blueprint
despesa_bp = Blueprint('despesa', __name__)

# ===================== ROTAS DE DESPESA =====================

@despesa_bp.route('/balanco-despesa')
def balanco_despesa():
    """Relatório de balanço orçamentário da despesa"""
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

@despesa_bp.route('/despesa-por-funcao')
def despesa_por_funcao():
    """Relatório de despesa por função de governo com detalhamento por subfunção"""
    try:
        print("\n🎯 [ROTA] Iniciando despesa-por-funcao")
        print(f"🎯 [ROTA] Diretório atual: {os.getcwd()}")
        print(f"🎯 [ROTA] Pasta dados existe? {os.path.exists('dados')}")
        
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        if df_completo.empty:
            print("🎯 [ROTA] DataFrame vazio!")
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        print(f"🎯 [ROTA] DataFrame carregado: {len(df_completo)} registros")
        print(f"🎯 [ROTA] Colunas disponíveis: {list(df_completo.columns)[:10]}...")
        
        # DEBUG: Listar TODAS as colunas
        print("\n📋 TODAS AS COLUNAS DA DESPESA:")
        for i, col in enumerate(df_completo.columns, 1):
            print(f"   {i:3d}. {col}")
        
        # Procurar colunas com FUNC
        print("\n🔍 Colunas com 'FUNC':")
        func_cols = [col for col in df_completo.columns if 'FUNC' in col.upper()]
        print(f"   {func_cols}")
        
        print("\n")
        
        # Verifica colunas específicas para este relatório
        colunas_necessarias = ['COFUNCAO', 'COSUBFUNCAO', 'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            print(f"🎯 [ROTA] Colunas faltantes: {colunas_faltantes}")
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes para relatório por função: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        if gerar_relatorio_despesa_funcao is None:
            print("🎯 [ROTA] Função gerar_relatorio_despesa_funcao não está disponível!")
            return render_template('erro.html',
                                 titulo="Erro de Importação",
                                 mensagem="Módulo despesa_funcao não pôde ser importado.")
        
        print("🎯 [ROTA] Chamando gerar_relatorio_despesa_funcao...")
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_despesa_funcao(
            df_completo, None, noug_selecionada
        )
        
        print(f"🎯 [ROTA] Retorno: {len(dados_tabela)} linhas de dados")
        
        fim = time.time()
        print(f"⏱️ Relatório de despesa por função gerado em {fim - inicio:.2f} segundos")
        
        print("🎯 [ROTA] Tentando renderizar template...")
        try:
            return render_template('despesas/despesa_por_funcao.html',
                                   dados_relatorio=dados_tabela,
                                   mes_ref=mes_referencia,
                                   lista_nougs=lista_nougs,
                                   noug_selecionada=noug_selecionada,
                                   dados_pdf=dados_pdf)
        except Exception as template_error:
            print(f"🎯 [ROTA] Erro ao renderizar template: {str(template_error)}")
            traceback.print_exc()
            # Tenta um template mínimo para debug
            return f"""
            <html>
            <body>
                <h1>Debug - Despesa por Função</h1>
                <p>Dados carregados: {len(dados_tabela)} linhas</p>
                <p>Mês referência: {mes_referencia}</p>
                <p>NOUGs: {len(lista_nougs)}</p>
                <pre>{str(dados_tabela[:2]) if dados_tabela else 'Sem dados'}</pre>
            </body>
            </html>
            """
    except Exception as e:
        print(f"🎯 [ROTA] ERRO: {str(e)}")
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa por Função",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@despesa_bp.route('/despesa-por-natureza')
def despesa_por_natureza():
    """Relatório de despesa por natureza com detalhamento por elemento"""
    try:
        print("\n🎯 [ROTA] Iniciando despesa-por-natureza")
        
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        if df_completo.empty:
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        print(f"🎯 [ROTA] DataFrame carregado: {len(df_completo)} registros")
        
        # Verifica colunas necessárias
        colunas_necessarias = ['CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO', 'NOUG', 
                              'CONATUREZA', 'NOELEMENTO', 'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            print(f"🎯 [ROTA] Colunas faltantes: {colunas_faltantes}")
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        if gerar_relatorio_despesa_natureza is None:
            print("🎯 [ROTA] Função gerar_relatorio_despesa_natureza não está disponível!")
            return render_template('erro.html',
                                 titulo="Erro de Importação",
                                 mensagem="Módulo despesa_natureza não pôde ser importado.")
        
        print("🎯 [ROTA] Chamando gerar_relatorio_despesa_natureza...")
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_despesa_natureza(
            df_completo, None, noug_selecionada
        )
        
        print(f"🎯 [ROTA] Retorno: {len(dados_tabela)} linhas de dados")
        
        fim = time.time()
        print(f"⏱️ Relatório de despesa por natureza gerado em {fim - inicio:.2f} segundos")
        
        return render_template('despesas/despesa_natureza.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        print(f"🎯 [ROTA] ERRO: {str(e)}")
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa por Natureza",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@despesa_bp.route('/despesa-por-funcao-programa')
def despesa_por_funcao_programa():
    """Relatório de despesa por função/subfunção/programa de trabalho"""
    try:
        print("\n🎯 [ROTA] Iniciando despesa-por-funcao-programa")
        print(f"🎯 [ROTA] Diretório atual: {os.getcwd()}")
        print(f"🎯 [ROTA] Pasta dados existe? {os.path.exists('dados')}")
        
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        if df_completo.empty:
            print("🎯 [ROTA] DataFrame vazio!")
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        print(f"🎯 [ROTA] DataFrame carregado: {len(df_completo)} registros")
        
        # Verifica colunas específicas para este relatório
        colunas_necessarias = ['COFUNCAO', 'COSUBFUNCAO', 'COPROGRAMA', 'COPROJETO', 'COSUBTITULO',
                              'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            print(f"🎯 [ROTA] Colunas faltantes: {colunas_faltantes}")
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes para relatório: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        if gerar_relatorio_despesa_funcao_programa is None:
            print("🎯 [ROTA] Função gerar_relatorio_despesa_funcao_programa não está disponível!")
            return render_template('erro.html',
                                 titulo="Erro de Importação",
                                 mensagem="Módulo despesa_funcao_programa não pôde ser importado.")
        
        print("🎯 [ROTA] Chamando gerar_relatorio_despesa_funcao_programa...")
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_despesa_funcao_programa(
            df_completo, None, noug_selecionada
        )
        
        print(f"🎯 [ROTA] Retorno: {len(dados_tabela)} linhas de dados")
        
        fim = time.time()
        print(f"⏱️ Relatório gerado em {fim - inicio:.2f} segundos")
        
        return render_template('despesas/despesa_por_funcao_programa.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        print(f"🎯 [ROTA] ERRO: {str(e)}")
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa por Função/Programa",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@despesa_bp.route('/despesa-por-funcao-tipo-programa')
def despesa_por_funcao_tipo_programa():
    """Relatório de despesa por função/tipo de despesa/programa de trabalho"""
    try:
        print("\n🎯 [ROTA] Iniciando despesa-por-funcao-tipo-programa")
        print(f"🎯 [ROTA] Diretório atual: {os.getcwd()}")
        print(f"🎯 [ROTA] Pasta dados existe? {os.path.exists('dados')}")
        
        inicio = time.time()
        df_completo = carregar_dataframe_despesa()

        if df_completo.empty:
            print("🎯 [ROTA] DataFrame vazio!")
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        print(f"🎯 [ROTA] DataFrame carregado: {len(df_completo)} registros")
        
        # Verifica colunas específicas para este relatório
        colunas_necessarias = ['COFUNCAO', 'COSUBFUNCAO', 'COPROGRAMA', 'COPROJETO', 'COSUBTITULO',
                              'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            print(f"🎯 [ROTA] Colunas faltantes: {colunas_faltantes}")
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes para relatório: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        if gerar_relatorio_despesa_funcao_tipo_programa is None:
            print("🎯 [ROTA] Função gerar_relatorio_despesa_funcao_tipo_programa não está disponível!")
            return render_template('erro.html',
                                 titulo="Erro de Importação",
                                 mensagem="Módulo despesa_funcao_tipo_programa não pôde ser importado.")
        
        print("🎯 [ROTA] Chamando gerar_relatorio_despesa_funcao_tipo_programa...")
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_despesa_funcao_tipo_programa(
            df_completo, None, noug_selecionada
        )
        
        print(f"🎯 [ROTA] Retorno: {len(dados_tabela)} linhas de dados")
        
        fim = time.time()
        print(f"⏱️ Relatório gerado em {fim - inicio:.2f} segundos")
        
        return render_template('despesas/despesa_por_funcao_tipo_programa.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        print(f"🎯 [ROTA] ERRO: {str(e)}")
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa por Função/Tipo/Programa",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

# ===================== ROTAS EM DESENVOLVIMENTO =====================

@despesa_bp.route('/despesa-por-modalidade')
def despesa_por_modalidade():
    """Relatório de despesa por modalidade (em desenvolvimento)"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por modalidade está sendo desenvolvido. Implementação usando coluna MODALIDADE disponível.")

@despesa_bp.route('/despesa-por-noug')
def despesa_por_noug():
    """Relatório de despesa por unidade gestora (em desenvolvimento)"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por unidade gestora está sendo desenvolvido.")

@despesa_bp.route('/execucao-por-programa')
def execucao_por_programa():
    """Relatório de execução por programa (em desenvolvimento)"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de execução por programa está sendo desenvolvido.")

"""
Blueprint para rotas de relatórios contábeis
"""
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações e utilitários
from utils.data_loaders import carregar_dataframe_bens_moveis, carregar_dataframe_sisgepat, carregar_dataframe_depara
from relatorios.contabeis import gerar_relatorio_bens_moveis

# Cria o blueprint
contabeis_bp = Blueprint('contabeis', __name__)

# ===================== ROTAS DE RELATÓRIOS CONTÁBEIS =====================

@contabeis_bp.route('/bens-moveis')
def bens_moveis():
    """Relatório de Bens Móveis com integração SISGEPAT"""
    try:
        inicio = time.time()
        
        # Carrega dados principais
        df_completo = carregar_dataframe_bens_moveis()
        
        # Carrega dados SISGEPAT e DE-PARA
        try:
            df_sisgepat = carregar_dataframe_sisgepat()
            df_depara = carregar_dataframe_depara()
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível carregar dados SISGEPAT: {str(e)}")
            df_sisgepat = None
            df_depara = None
        
        # Lista de NOUGs únicas para o filtro
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        # Gera relatório com dados SISGEPAT se disponíveis
        dados_relatorio, dados_pdf = gerar_relatorio_bens_moveis(
            df_completo, 
            df_sisgepat, 
            df_depara,
            noug_selecionada
        )

        fim = time.time()
        print(f"⏱️ Relatório de Bens Móveis gerado em {fim - inicio:.2f} segundos")

        return render_template('contabeis/relatorio_bens_moveis.html',
                               dados_relatorio=dados_relatorio,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf)
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Bens Móveis",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")