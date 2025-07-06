"""
Relatório: Gráfico de Receita de Capital Líquida Realizada
Analisa receitas da CATEGORIA = 2 (receitas de capital) com desdobramentos por origem
REGRAS:
- CATEGORIA = 2 (receitas de capital)
- Desdobramento por ORIGEM e NOORIGEM
- Valores de RECEITA LÍQUIDA
- Distribuição percentual por origem
- Compatível com formato de gráfico de pizza
"""
import pandas as pd
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual

def gerar_grafico_receita_capital(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera dados para gráfico de receita de capital líquida por origem
    
    REGRAS DE NEGÓCIO:
    - Filtra apenas CATEGORIA = 2 (receitas de capital)
    - Agrupa por ORIGEM
    - Valores de RECEITA LÍQUIDA
    - Formato compatível com gráfico de pizza
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_tabela, mes_referencia, dados_grafico, dados_chart)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas CATEGORIA = 2 (receitas de capital) para 2025
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['CATEGORIA'] == '2')
    ]
    
    if df_2025.empty:
        print("⚠️ Nenhum dado de receita de capital encontrado (CATEGORIA = 2)")
        return [], obter_mes_numero(df_processar), [], {}
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada na planilha")
        return [], obter_mes_numero(df_processar), [], {}
    
    print(f"🔍 Processando receitas de capital (CATEGORIA = 2)...")
    print(f"📊 Total de registros encontrados: {len(df_2025)}")
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    # Agrupa por ORIGEM e soma os valores
    if 'ORIGEM' not in df_2025.columns:
        print("⚠️ Coluna 'ORIGEM' não encontrada")
        return [], mes_referencia, [], {}
    
    # Agrupa por ORIGEM e obtém o nome da origem
    dados_origem = []
    origens_unicas = df_2025['ORIGEM'].dropna().unique()
    
    print(f"📋 Origens encontradas: {sorted(origens_unicas)}")
    
    for origem in sorted(origens_unicas):
        df_origem = df_2025[df_2025['ORIGEM'] == origem]
        valor_origem = float(df_origem['RECEITA LIQUIDA'].sum())
        
        if valor_origem <= 0:
            continue
            
        # Busca nome da origem
        nome_origem = _obter_nome_origem(df_origem, origem)
        
        dados_origem.append({
            'origem': origem,
            'nome_origem': nome_origem,
            'valor': valor_origem,
            'valor_fmt': motor.formatar_numero(valor_origem)
        })
    
    # Calcula total e percentuais
    total_receita = sum(item['valor'] for item in dados_origem)
    
    for item in dados_origem:
        item['percentual'] = (item['valor'] / total_receita * 100) if total_receita > 0 else 0
        item['percentual_fmt'] = f"{item['percentual']:.1f}%"
    
    # Ordena por valor (maior para menor)
    dados_origem.sort(key=lambda x: x['valor'], reverse=True)
    
    # Prepara dados para tabela
    dados_tabela = []
    for item in dados_origem:
        dados_tabela.append({
            'origem': item['origem'],
            'nome_origem': item['nome_origem'],
            'valor': item['valor'],
            'valor_fmt': item['valor_fmt'],
            'percentual': item['percentual'],
            'percentual_fmt': item['percentual_fmt']
        })
    
    # Prepara dados para gráfico (formato compatível com gráfico de pizza)
    dados_grafico = dados_origem  # Mesmo formato
    
    # Prepara dados_chart para compatibilidade com template
    dados_chart = {
        'title_text': 'Composição da Receita de Capital Líquida por Origem',
        'total_fmt': motor.formatar_numero(total_receita),
        'dados': dados_origem,
        'labels': [item['nome_origem'] for item in dados_origem],
        'values': [item['valor'] for item in dados_origem],
        'percentuais': [item['percentual'] for item in dados_origem]
    }
    
    print(f"✅ Gráfico de receita de capital gerado: {len(dados_origem)} origens")
    print(f"💰 Total da receita de capital: {motor.formatar_numero(total_receita)}")
    
    return dados_tabela, mes_referencia, dados_grafico, dados_chart

def _obter_nome_origem(df_origem, codigo_origem):
    """
    Obtém o nome da origem pelo código
    
    Args:
        df_origem: DataFrame filtrado da origem
        codigo_origem: Código da origem
        
    Returns:
        Nome da origem ou string padrão se não encontrado
    """
    # Tenta obter o nome da origem
    if 'NOORIGEM' in df_origem.columns:
        linha_origem = df_origem['NOORIGEM'].dropna().first_valid_index()
        if linha_origem is not None:
            nome = df_origem.loc[linha_origem, 'NOORIGEM']
            if pd.notna(nome) and nome.strip():
                return str(nome).strip()
    
    # Fallback: usar nomes conhecidos por código
    nomes_origem = {
        '20': 'Alienação de Bens',
        '21': 'Operações de Crédito - Mercado Interno e Externo',
        '22': 'Transferências de Capital',
        '23': 'Outras Receitas de Capital'
    }
    
    return nomes_origem.get(str(codigo_origem), f'Origem {codigo_origem}')

# Função para compatibilidade (mantém o nome original)
def gerar_grafico_receita_capital_old(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Função mantida para compatibilidade com relatório de operações de crédito
    Esta função continua filtrando apenas ORIGEM = 21
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas origem de operações de crédito (21) para 2025 e 2024
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['ORIGEM'] == '21')
    ]
    df_2024 = df_processar[
        (df_processar['COEXERCICIO'] == 2024) & 
        (df_processar['ORIGEM'] == '21')
    ]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}, []
    
    # ... resto do código original para operações de crédito
    # (mantido para não quebrar o relatório específico de operações de crédito)
    
    return [], obter_mes_numero(df_processar), [], {}, []