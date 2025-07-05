"""
Relatório: Análise de Variações
Analisa variações entre períodos e identifica tendências
"""
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_relatorio_analise_variacoes(df_completo, estrutura_hierarquica, noug_selecionada=None, tipo_analise='mensal'):
    """
    Gera análise de variações orçamentárias
    
    TIPOS DE ANÁLISE:
    - Mensal: Variação mês a mês no exercício atual
    - Anual: Variação entre exercícios
    - Previsto vs Realizado: Variação entre previsão e execução
    
    Args:
        df_completo: DataFrame com dados (receita ou despesa)
        estrutura_hierarquica: Estrutura hierárquica
        noug_selecionada: NOUG selecionada para filtro (opcional)
        tipo_analise: Tipo de análise ('mensal', 'anual', 'previsao')
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    if df_processar.empty:
        return [], "12", [], {}
    
    mes_referencia = obter_mes_numero(df_processar)
    dados_numericos = []
    dados_para_ia = []
    
    if tipo_analise == 'mensal':
        dados_numericos = _analisar_variacao_mensal(df_processar, motor)
    elif tipo_analise == 'anual':
        dados_numericos = _analisar_variacao_anual(df_processar, motor, estrutura_hierarquica)
    elif tipo_analise == 'previsao':
        dados_numericos = _analisar_previsao_vs_realizado(df_processar, motor, estrutura_hierarquica)
    
    dados_para_ia = dados_numericos.copy()
    
    # Dados para PDF
    dados_pdf = {
        "head": [['ITEM', 'PERÍODO BASE', 'PERÍODO ATUAL', 'VARIAÇÃO ABSOLUTA', 'VARIAÇÃO %']],
        "body": [
            [linha.get('especificacao', ''), linha.get('valor_base_fmt', 'R$ 0,00'),
             linha.get('valor_atual_fmt', 'R$ 0,00'), linha.get('variacao_abs_fmt', 'R$ 0,00'),
             linha.get('variacao_perc_fmt', '0,00%')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

def _analisar_variacao_mensal(df_processar, motor):
    """
    Analisa variação mês a mês no exercício atual
    
    Args:
        df_processar: DataFrame filtrado
        motor: Instância do MotorRelatorios
        
    Returns:
        Lista com dados de variação mensal
    """
    # TODO: Implementar análise mensal
    # Comparar cada mês com o mês anterior
    
    dados = []
    
    if 'INMES' in df_processar.columns:
        meses_disponiveis = sorted(df_processar['INMES'].unique())
        
        for i, mes in enumerate(meses_disponiveis[1:], 1):  # Começa do segundo mês
            mes_anterior = meses_disponiveis[i-1]
            
            # TODO: Calcular valores por mês e comparar
            linha = {
                'especificacao': f'Mês {mes:02d}/2025',
                'periodo_base': f'{mes_anterior:02d}/2025',
                'periodo_atual': f'{mes:02d}/2025',
                'valor_base': 0,
                'valor_atual': 0,
                'variacao_abs': 0,
                'variacao_perc': 0,
                'valor_base_fmt': motor.formatar_numero(0),
                'valor_atual_fmt': motor.formatar_numero(0),
                'variacao_abs_fmt': motor.formatar_numero(0),
                'variacao_perc_fmt': formatar_percentual(0)
            }
            dados.append(linha)
    
    return dados

def _analisar_variacao_anual(df_processar, motor, estrutura_hierarquica):
    """
    Analisa variação entre exercícios (2024 vs 2025)
    
    Args:
        df_processar: DataFrame filtrado
        motor: Instância do MotorRelatorios
        estrutura_hierarquica: Estrutura hierárquica
        
    Returns:
        Lista com dados de variação anual
    """
    dados = []
    
    # Filtra dados por exercício
    df_2024 = df_processar[df_processar['COEXERCICIO'] == 2024]
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2024.empty or df_2025.empty:
        return dados
    
    # Analisa por categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria:
            continue
        
        # TODO: Calcular valores por categoria e ano
        valor_2024 = float(df_2024[df_2024['CATEGORIA'] == cod_cat]['PREVISAO INICIAL LIQUIDA'].sum())
        valor_2025 = float(df_2025[df_2025['CATEGORIA'] == cod_cat]['PREVISAO INICIAL LIQUIDA'].sum())
        
        if valor_2024 > 0 or valor_2025 > 0:
            variacao_abs = valor_2025 - valor_2024
            variacao_perc = ((valor_2025 - valor_2024) / valor_2024 * 100) if valor_2024 > 0 else 0
            
            linha = {
                'especificacao': nome_categoria,
                'periodo_base': '2024',
                'periodo_atual': '2025',
                'valor_base': valor_2024,
                'valor_atual': valor_2025,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'valor_base_fmt': motor.formatar_numero(valor_2024),
                'valor_atual_fmt': motor.formatar_numero(valor_2025),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc)
            }
            dados.append(linha)
    
    return dados

def _analisar_previsao_vs_realizado(df_processar, motor, estrutura_hierarquica):
    """
    Analisa variação entre previsão e realização
    
    Args:
        df_processar: DataFrame filtrado
        motor: Instância do MotorRelatorios
        estrutura_hierarquica: Estrutura hierárquica
        
    Returns:
        Lista com dados de previsão vs realizado
    """
    dados = []
    
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return dados
    
    # Verifica se existem as colunas necessárias
    if 'PREVISAO INICIAL LIQUIDA' not in df_2025.columns or 'RECEITA LIQUIDA' not in df_2025.columns:
        return dados
    
    # Analisa por categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria:
            continue
        
        df_categoria = df_2025[df_2025['CATEGORIA'] == cod_cat]
        
        valor_previsto = float(df_categoria['PREVISAO INICIAL LIQUIDA'].sum())
        valor_realizado = float(df_categoria['RECEITA LIQUIDA'].sum())
        
        if valor_previsto > 0 or valor_realizado > 0:
            variacao_abs = valor_realizado - valor_previsto
            variacao_perc = ((valor_realizado - valor_previsto) / valor_previsto * 100) if valor_previsto > 0 else 0
            
            linha = {
                'especificacao': nome_categoria,
                'periodo_base': 'Previsto',
                'periodo_atual': 'Realizado',
                'valor_base': valor_previsto,
                'valor_atual': valor_realizado,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'valor_base_fmt': motor.formatar_numero(valor_previsto),
                'valor_atual_fmt': motor.formatar_numero(valor_realizado),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc)
            }
            dados.append(linha)
    
    return dados