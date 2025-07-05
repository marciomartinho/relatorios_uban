"""
Blueprint para rotas de relatórios de receita
"""
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações
from config_relatorios import HIERARQUIA_RECEITAS
from utils.data_loaders import carregar_dataframe_receita

# Importações dos módulos de receita
from relatorios.receita import (
    gerar_balanco_orcamentario,
    gerar_relatorio_receita_estimada,
    gerar_relatorio_por_adm,
    gerar_relatorio_receita_atualizada_vs_inicial,
    gerar_grafico_receita_liquida,
    gerar_relatorio_receita_conta_corrente
)

# Cria o blueprint
receita_bp = Blueprint('receita', __name__)

# ===================== ROTAS DE RECEITA =====================

@receita_bp.route('/balanco-orcamentario')
def balanco_orcamentario():
    """Relatório de balanço orçamentário da receita"""
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

@receita_bp.route('/receita-estimada')
def receita_estimada():
    """Relatório de receita estimada comparativo entre anos"""
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

@receita_bp.route('/receita-atualizada-vs-inicial')
def receita_atualizada_vs_inicial():
    """Relatório: Receita Atualizada X Inicial"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_relatorio, dados_para_ia, dados_pdf = gerar_relatorio_receita_atualizada_vs_inicial(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório de receita atualizada vs inicial gerado em {fim - inicio:.2f} segundos")

        return render_template('relatorio_atualizada_vs_inicial.html',
                               dados_relatorio=dados_relatorio,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)

    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório Receita Atualizada vs Inicial",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@receita_bp.route('/grafico-receita-liquida')
def grafico_receita_liquida():
    """Relatório: Gráfico de Receita Líquida (Receita Corrente)"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_tabela, mes_referencia, dados_grafico, dados_chart = gerar_grafico_receita_liquida(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Gráfico de receita líquida gerado em {fim - inicio:.2f} segundos")

        return render_template('grafico_receita_liquida.html',
                               dados_relatorio=dados_tabela,
                               dados_grafico=dados_grafico,
                               dados_chart=dados_chart,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)

    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Gráfico de Receita Líquida",
                             mensagem=f"Erro ao gerar gráfico: {str(e)}")

@receita_bp.route('/receita-por-adm')
def receita_por_adm():
    """Relatório de receita por administração"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_tabela, dados_para_ia, dados_pdf = gerar_relatorio_por_adm(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório por Administração gerado em {fim - inicio:.2f} segundos")

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

@receita_bp.route('/receita-conta-corrente')
def receita_conta_corrente():
    """Relatório de receita por conta corrente (NOVO)"""
    try:
        inicio = time.time()
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_receita_conta_corrente(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        fim = time.time()
        print(f"⏱️ Relatório por Conta Corrente gerado em {fim - inicio:.2f} segundos")

        return render_template('relatorio_receita_conta_corrente.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada)
                               
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório por Conta Corrente",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")