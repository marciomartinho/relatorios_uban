"""
Blueprint para rotas de relatórios de despesa
"""
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações
from utils.data_loaders import carregar_dataframe_despesa

# Importações dos módulos de despesa
from relatorios.despesa import gerar_balanco_despesa

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

# ===================== ROTAS EM DESENVOLVIMENTO =====================

@despesa_bp.route('/despesa-por-funcao')
def despesa_por_funcao():
    """Relatório de despesa por função (em desenvolvimento)"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por função está sendo desenvolvido. Aguardando colunas de função governamental na planilha.")

@despesa_bp.route('/despesa-por-natureza')
def despesa_por_natureza():
    """Relatório de despesa por natureza (em desenvolvimento)"""
    return render_template('erro.html',
                         titulo="Relatório em Desenvolvimento",
                         mensagem="O relatório de despesa por natureza está sendo desenvolvido. Implementação usando coluna ELEMENTO disponível.")

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