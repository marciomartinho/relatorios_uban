"""
Relatório: Gráfico de Pizza - Receita Líquida (Receita Corrente)
Gera dados para gráfico de pizza da categoria 1 (Receitas Correntes)
"""
from ..utils import MotorRelatorios, calcular_mes_referencia

def gerar_grafico_receita_liquida(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera dados para gráfico de pizza da Receita Líquida - Categoria 1 (Receitas Correntes)
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_tabela, mes_referencia, dados_grafico, dados_chart)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas categoria 1 (Receitas Correntes) e exercício 2025
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['CATEGORIA'] == '1')
    ]
    
    if df_2025.empty:
        return [], "12/2025", [], {}
    
    # Calcula mês de referência
    mes_referencia = calcular_mes_referencia(df_2025)
    
    dados_grafico = []
    dados_tabela = []
    total_geral = 0
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada")
        return [], mes_referencia, [], {}
    
    # Processa cada origem dentro da categoria 1
    origens_categoria_1 = estrutura_hierarquica.get('1', {})
    
    for cod_origem in origens_categoria_1.keys():
        nome_origem = motor.obter_nome_origem(cod_origem)
        if not nome_origem:
            continue
            
        df_origem = df_2025[df_2025['ORIGEM'] == cod_origem]
        if df_origem.empty:
            continue
            
        valor_receita = float(df_origem['RECEITA LIQUIDA'].sum())
        
        if valor_receita > 0:  # Só inclui valores positivos
            dados_origem = {
                'origem': cod_origem,
                'nome': nome_origem,
                'valor': valor_receita,
                'valor_fmt': motor.formatar_numero(valor_receita),
                'cor': _obter_cor_origem(cod_origem)
            }
            
            dados_grafico.append(dados_origem)
            dados_tabela.append(dados_origem)
            total_geral += valor_receita
    
    # Calcula percentuais
    for item in dados_grafico:
        if total_geral > 0:
            item['percentual'] = (item['valor'] / total_geral) * 100
            item['percentual_fmt'] = f"{item['percentual']:.1f}%"
        else:
            item['percentual'] = 0
            item['percentual_fmt'] = "0,0%"
    
    # Ordena por valor (maior para menor)
    dados_grafico.sort(key=lambda x: x['valor'], reverse=True)
    dados_tabela.sort(key=lambda x: x['valor'], reverse=True)
    
    # Adiciona total
    total_item = {
        'origem': 'TOTAL',
        'nome': 'TOTAL GERAL',
        'valor': total_geral,
        'valor_fmt': motor.formatar_numero(total_geral),
        'percentual': 100.0,
        'percentual_fmt': "100,0%",
        'cor': '#003366'
    }
    dados_tabela.append(total_item)
    
    # Dados para gráfico (Chart.js)
    dados_chart = {
        'labels': [item['nome'] for item in dados_grafico],
        'data': [item['valor'] for item in dados_grafico],
        'backgroundColor': [item['cor'] for item in dados_grafico],
        'total': total_geral,
        'total_fmt': motor.formatar_numero(total_geral)
    }
    
    return dados_tabela, mes_referencia, dados_grafico, dados_chart

def _obter_cor_origem(cod_origem: str) -> str:
    """
    Retorna cores personalizadas para cada origem
    
    Args:
        cod_origem: Código da origem da receita
        
    Returns:
        Código de cor hexadecimal
    """
    cores = {
        '11': '#2196F3',  # Azul - Impostos
        '12': '#4CAF50',  # Verde - Taxas  
        '13': '#FF9800',  # Laranja - Contribuições
        '14': '#9C27B0',  # Roxo - Receita Patrimonial
        '15': '#F44336',  # Vermelho - Receita Agropecuária
        '16': '#00BCD4',  # Ciano - Receita Industrial
        '17': '#8BC34A',  # Verde claro - Receita de Serviços
        '19': '#607D8B'   # Azul acinzentado - Outras Receitas
    }
    return cores.get(cod_origem, '#9E9E9E')  # Cinza como padrão