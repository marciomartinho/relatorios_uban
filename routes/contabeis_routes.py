"""
Blueprint para rotas de relatórios contábeis
Versão refatorada usando a nova arquitetura
"""
import time
from flask import Blueprint, render_template, request
import traceback

# Importações das configurações e utilitários
from utils.data_loaders import (
    carregar_dataframe_bens_moveis, 
    carregar_dataframe_depara, 
    carregar_saldos_contabeis
)

# Importa o novo serviço
from relatorios.contabeis.services import BensMoviesService

# Cria o blueprint
contabeis_bp = Blueprint('contabeis', __name__)

# ===================== ROTAS DE RELATÓRIOS CONTÁBEIS =====================

@contabeis_bp.route('/bens-moveis')
def bens_moveis():
    """Relatório de Bens Móveis com integração SISGEPAT"""
    try:
        inicio = time.time()
        
        # Carrega dados principais (BENSMOVEIS.xlsx)
        df_completo = carregar_dataframe_bens_moveis()
        
        # Carrega dados de saldos contábeis (19-SaldoBensMoveis.xlsx)
        df_saldos_contabeis = carregar_saldos_contabeis()
        
        # Carrega dados DE-PARA
        df_depara = None
        try:
            df_depara = carregar_dataframe_depara()
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível carregar dados DE-PARA: {str(e)}")
        
        # Lista de NOUGs únicas para o filtro
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)

        # Instancia o serviço e gera o relatório
        service = BensMoviesService()
        dados_relatorio, dados_pdf, dados_saldos_contabeis = service.gerar_relatorio(
            df_completo=df_completo,
            df_depara=df_depara,
            df_saldos_contabeis=df_saldos_contabeis,
            noug_selecionada=noug_selecionada,
            caminho_pdf_sisgepat='dados/Relatorio_Demonstrativos_Bem_Moveis.pdf'
        )

        fim = time.time()
        print(f"⏱️ Relatório de Bens Móveis gerado em {fim - inicio:.2f} segundos")

        return render_template('contabeis/relatorio_bens_moveis.html',
                               dados_relatorio=dados_relatorio,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_pdf=dados_pdf,
                               dados_saldos_contabeis=dados_saldos_contabeis)
    except Exception as e:
        traceback.print_exc()
        return render_template('erro.html',
                             titulo="Erro no Relatório de Bens Móveis",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")
