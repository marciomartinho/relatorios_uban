"""
Módulo de relatórios contábeis
Versão refatorada com arquitetura em camadas
"""

# Importa o serviço principal para compatibilidade
from .services import BensMoviesService

# Função de compatibilidade com a interface antiga
def gerar_relatorio_bens_moveis(df_completo, dados_sisgepat=None, df_depara=None, 
                               noug_selecionada=None, df_saldos_contabeis=None):
    """
    Função de compatibilidade com a interface antiga
    Usa o novo serviço internamente
    """
    service = BensMoviesService()
    
    # Se dados_sisgepat foi passado diretamente, não processar PDF
    caminho_pdf = None if dados_sisgepat else 'dados/Relatorio_Demonstrativos_Bem_Moveis.pdf'
    
    # Se dados_sisgepat não foi fornecido, será processado do PDF
    if not dados_sisgepat and caminho_pdf:
        # O serviço processará o PDF internamente
        pass
    
    return service.gerar_relatorio(
        df_completo=df_completo,
        df_depara=df_depara,
        df_saldos_contabeis=df_saldos_contabeis,
        noug_selecionada=noug_selecionada,
        caminho_pdf_sisgepat=caminho_pdf
    )

# Função de compatibilidade para processar PDF
def processar_pdf_sisgepat(caminho_pdf, df_depara):
    """
    Função de compatibilidade para processar PDF SISGEPAT
    """
    from .processors import SisgepatProcessor
    processor = SisgepatProcessor()
    return processor.processar_pdf(caminho_pdf, df_depara)

# Função de compatibilidade para processar saldos
def processar_saldos_contabeis(df_saldos, dict_contas=None):
    """
    Função de compatibilidade para processar saldos contábeis
    """
    from .processors import SaldosContabeisProcessor
    processor = SaldosContabeisProcessor()
    result = processor.processar_saldos(df_saldos, dict_contas)
    
    # Converter para dict se retornar o modelo
    if result:
        return {
            'itens': result.itens,
            'total': result.total,
            'total_fmt': result.total_fmt,
            'mes_referencia': result.mes_referencia
        }
    return None

__all__ = [
    'gerar_relatorio_bens_moveis',
    'processar_pdf_sisgepat',
    'processar_saldos_contabeis',
    'BensMoviesService'
]