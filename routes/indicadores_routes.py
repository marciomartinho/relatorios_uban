"""
Blueprint para rotas de relatórios de indicadores
"""
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações
from config_relatorios import HIERARQUIA_RECEITAS
from utils.data_loaders import carregar_dataframe_receita, carregar_dataframe_despesa

# Importações dos módulos de indicadores
from relatorios.indicadores import (
    gerar_dashboard_executivo_placeholder,
    gerar_indicadores_orcamentarios_placeholder,
    gerar_analise_variacoes_placeholder,
    gerar_relatorio_por_noug_placeholder
)

# Cria o blueprint
indicadores_bp = Blueprint('indicadores', __name__)

# ===================== ROTAS DE INDICADORES E ANÁLISES =====================

@indicadores_bp.route('/dashboard')
def dashboard():
    """Dashboard executivo (placeholder)"""
    try:
        inicio = time.time()
        df_receita = carregar_dataframe_receita()
        df_despesa = carregar_dataframe_despesa()
        
        dados_dashboard, mes_referencia, dados_para_ia, dados_pdf = gerar_dashboard_executivo_placeholder(
            df_receita, None, None
        )
        
        fim = time.time()
        print(f"⏱️ Dashboard executivo (placeholder) gerado em {fim - inicio:.2f} segundos")
        
        return render_template('erro.html',
                             titulo="Dashboard Executivo - Em Desenvolvimento",
                             mensagem="O dashboard executivo está sendo desenvolvido. Estrutura criada e aguardando implementação completa.")
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Dashboard",
                             mensagem=f"Erro ao gerar dashboard: {str(e)}")

@indicadores_bp.route('/indicadores')
def indicadores():
    """Relatório de indicadores orçamentários (placeholder)"""
    try:
        inicio = time.time()
        df_receita = carregar_dataframe_receita()
        df_despesa = carregar_dataframe_despesa()
        
        dados_indicadores, mes_referencia, dados_para_ia, dados_pdf = gerar_indicadores_orcamentarios_placeholder(
            df_receita, None, None
        )
        
        fim = time.time()
        print(f"⏱️ Indicadores orçamentários (placeholder) gerado em {fim - inicio:.2f} segundos")
        
        return render_template('erro.html',
                             titulo="Indicadores Orçamentários - Em Desenvolvimento",
                             mensagem="Os indicadores orçamentários estão sendo desenvolvidos. Estrutura criada e aguardando implementação completa.")
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro nos Indicadores",
                             mensagem=f"Erro ao gerar indicadores: {str(e)}")

@indicadores_bp.route('/analise-variacoes')
def analise_variacoes():
    """Relatório de análise de variações (placeholder)"""
    try:
        inicio = time.time()
        df_receita = carregar_dataframe_receita()
        
        dados_analise, mes_referencia, dados_para_ia, dados_pdf = gerar_analise_variacoes_placeholder(
            df_receita, HIERARQUIA_RECEITAS, None
        )
        
        fim = time.time()
        print(f"⏱️ Análise de variações (placeholder) gerado em {fim - inicio:.2f} segundos")
        
        return render_template('erro.html',
                             titulo="Análise de Variações - Em Desenvolvimento",
                             mensagem="A análise de variações está sendo desenvolvida. Estrutura criada e aguardando implementação completa.")
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro na Análise de Variações",
                             mensagem=f"Erro ao gerar análise: {str(e)}")

@indicadores_bp.route('/por-noug')
def por_noug():
    """Relatório por unidade gestora (placeholder)"""
    try:
        inicio = time.time()
        df_receita = carregar_dataframe_receita()
        
        dados_noug, mes_referencia, dados_para_ia, dados_pdf = gerar_relatorio_por_noug_placeholder(
            df_receita, HIERARQUIA_RECEITAS, None
        )
        
        fim = time.time()
        print(f"⏱️ Relatório por NOUG (placeholder) gerado em {fim - inicio:.2f} segundos")
        
        return render_template('erro.html',
                             titulo="Relatório por Unidade Gestora - Em Desenvolvimento",
                             mensagem="O relatório por unidade gestora está sendo desenvolvido. Estrutura criada e aguardando implementação completa.")
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório por NOUG",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")