"""
Serviço principal para relatório de bens móveis
"""
from typing import Tuple, Optional
import pandas as pd

from ..processors.sisgepat_processor import SisgepatProcessor
from ..processors.saldos_processor import SaldosContabeisProcessor
from ..processors.conciliacao_processor import ConciliacaoProcessor
from ..formatters.bens_moveis_formatter import BensMoviesFormatter
from ..models.bens_moveis_models import DadosSaldosContabeis
from utils.data_loaders import carregar_conta_contabil

class BensMoviesService:
    """Serviço principal para relatório de bens móveis"""
    
    def __init__(self):
        self.sisgepat_processor = SisgepatProcessor()
        self.saldos_processor = SaldosContabeisProcessor()
        self.conciliacao_processor = ConciliacaoProcessor()
        self.formatter = BensMoviesFormatter()
    
    def gerar_relatorio(self,
                       df_completo: pd.DataFrame,
                       df_depara: Optional[pd.DataFrame] = None,
                       df_saldos_contabeis: Optional[pd.DataFrame] = None,
                       noug_selecionada: Optional[str] = None,
                       caminho_pdf_sisgepat: Optional[str] = None) -> Tuple:
        """
        Gera o relatório completo de bens móveis
        
        Args:
            df_completo: DataFrame com dados de bens móveis
            df_depara: DataFrame com DE-PARA Local -> COUG
            df_saldos_contabeis: DataFrame com saldos contábeis
            noug_selecionada: NOUG selecionada para filtro
            caminho_pdf_sisgepat: Caminho para o PDF do SISGEPAT
            
        Returns:
            Tupla com (dados_relatorio, dados_pdf, dados_saldos_contabeis)
        """
        # 1. Processar saldos contábeis (se não houver filtro)
        dados_saldos_contabeis = None
        if (not noug_selecionada or noug_selecionada == 'todos') and df_saldos_contabeis is not None:
            try:
                dict_contas = carregar_conta_contabil()
            except:
                dict_contas = None
                print("⚠️ Não foi possível carregar nomes das contas contábeis")
                
            dados_saldos_contabeis = self.saldos_processor.processar_saldos(
                df_saldos_contabeis, dict_contas
            )
        
        # 2. Processar dados SISGEPAT
        dados_sisgepat = {}
        if df_depara is not None and caminho_pdf_sisgepat:
            try:
                dados_sisgepat = self.sisgepat_processor.processar_pdf(
                    caminho_pdf_sisgepat, df_depara
                )
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível processar dados SISGEPAT: {str(e)}")
        
        # 3. Realizar conciliação
        resultado = self.conciliacao_processor.processar_conciliacao(
            df_completo, dados_sisgepat, df_depara, noug_selecionada
        )
        
        # 4. Formatar dados para apresentação
        dados_relatorio = self.formatter.formatar_para_tabela(resultado)
        
        # 5. Adicionar dados de saldos ao resultado (se disponível)
        if dados_saldos_contabeis:
            resultado.dados_saldos_contabeis = dados_saldos_contabeis
        
        # 6. Converter dados_saldos_contabeis para dict se for DadosSaldosContabeis
        dados_saldos_dict = None
        if isinstance(dados_saldos_contabeis, DadosSaldosContabeis):
            dados_saldos_dict = {
                'itens': dados_saldos_contabeis.itens,
                'total': dados_saldos_contabeis.total,
                'total_fmt': dados_saldos_contabeis.total_fmt,
                'mes_referencia': dados_saldos_contabeis.mes_referencia
            }
        
        return dados_relatorio, resultado.dados_pdf, dados_saldos_dict