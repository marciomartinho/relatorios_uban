"""
Relatório: Gráfico de Pizza - Total Receita de Capital (Comparativo 2024 vs 2025)
Gera dados para gráfico de pizza da categoria 2 (Receitas de Capital)
com comparativo entre anos
"""
from ..utils import MotorRelatorios, calcular_mes_referencia, obter_mes_numero, formatar_percentual
import pandas as pd

def gerar_grafico_receita_capital(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera dados para gráfico de pizza do Total Receita de Capital - Categoria 2 (Receitas de Capital)
    com comparativo 2024 vs 2025
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_tabela, mes_referencia, dados_grafico, dados_chart, comparativo_mensal)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra categoria 2 (Receitas de Capital) para 2025 e 2024
    df_2025 = df_processar[
        (df_processar['COEXERCICIO'] == 2025) & 
        (df_processar['CATEGORIA'] == '2')
    ]
    df_2024 = df_processar[
        (df_processar['COEXERCICIO'] == 2024) & 
        (df_processar['CATEGORIA'] == '2')
    ]
    
    if df_2025.empty:
        return [], "05/2025", [], {}, []
    
    # Calcula mês de referência
    mes_referencia = calcular_mes_referencia(df_2025)
    mes_numero = obter_mes_numero(df_2025)
    
    dados_grafico = []
    dados_tabela = []
    total_2025 = 0
    total_2024 = 0
    
    # Verifica se a coluna RECEITA LIQUIDA existe
    if 'RECEITA LIQUIDA' not in df_2025.columns:
        print("⚠️ Coluna 'RECEITA LIQUIDA' não encontrada")
        return [], mes_referencia, [], {}, []
    
    # Processa cada origem dentro da categoria 2
    origens_categoria_2 = estrutura_hierarquica.get('2', {})
    
    # Combinar origens de ambos os anos
    origens_2025 = set(df_2025['ORIGEM'].dropna().unique())
    origens_2024 = set(df_2024['ORIGEM'].dropna().unique()) if not df_2024.empty else set()
    todas_origens_encontradas = sorted(origens_2025.union(origens_2024))
    
    print(f"🔍 Processando origens da categoria 2: {todas_origens_encontradas}")
    
    for cod_origem in todas_origens_encontradas:
        # Só processa se a origem está na estrutura hierárquica (categoria 2)
        if cod_origem not in origens_categoria_2:
            continue
            
        nome_origem = motor.obter_nome_origem(cod_origem)
        if not nome_origem:
            nome_origem = _obter_nome_origem_padrao(cod_origem)
            
        # Calcula valores para 2025 e 2024
        df_origem_2025 = df_2025[df_2025['ORIGEM'] == cod_origem]
        df_origem_2024 = df_2024[df_2024['ORIGEM'] == cod_origem] if not df_2024.empty else pd.DataFrame()
        
        valor_2025 = float(df_origem_2025['RECEITA LIQUIDA'].sum()) if not df_origem_2025.empty else 0.0
        valor_2024 = float(df_origem_2024['RECEITA LIQUIDA'].sum()) if not df_origem_2024.empty else 0.0
        
        print(f"   📊 Origem {cod_origem} - {nome_origem}: 2024=R${valor_2024:,.2f}, 2025=R${valor_2025:,.2f}")
        
        # Só inclui se pelo menos um dos anos tem valor positivo
        if valor_2025 > 0 or valor_2024 > 0:
            # Calcula variações
            variacao_abs = valor_2025 - valor_2024
            variacao_perc = ((valor_2025 - valor_2024) / valor_2024 * 100) if valor_2024 > 0 else (100 if valor_2025 > 0 else 0)
            
            dados_origem = {
                'origem': cod_origem,
                'nome': nome_origem,
                'valor_2024': valor_2024,
                'valor_2025': valor_2025,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'valor_2024_fmt': motor.formatar_numero(valor_2024),
                'valor_2025_fmt': motor.formatar_numero(valor_2025),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc),
                'cor': _obter_cor_origem(cod_origem),
                'valor': valor_2025  # Para o gráfico, usar valor de 2025
            }
            
            dados_grafico.append(dados_origem)
            dados_tabela.append(dados_origem)
            total_2025 += valor_2025
            total_2024 += valor_2024
    
    # Calcula percentuais (baseado no total de 2025)
    for item in dados_grafico:
        if total_2025 > 0:
            item['percentual'] = (item['valor_2025'] / total_2025) * 100
            item['percentual_fmt'] = f"{item['percentual']:.1f}%"
        else:
            item['percentual'] = 0
            item['percentual_fmt'] = "0,0%"
    
    # Ordena por valor de 2025 (maior para menor)
    dados_grafico.sort(key=lambda x: x['valor_2025'], reverse=True)
    dados_tabela.sort(key=lambda x: x['valor_2025'], reverse=True)
    
    # Adiciona total
    total_variacao_abs = total_2025 - total_2024
    total_variacao_perc = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else (100 if total_2025 > 0 else 0)
    
    total_item = {
        'origem': 'TOTAL',
        'nome': 'TOTAL GERAL',
        'valor_2024': total_2024,
        'valor_2025': total_2025,
        'variacao_abs': total_variacao_abs,
        'variacao_perc': total_variacao_perc,
        'valor_2024_fmt': motor.formatar_numero(total_2024),
        'valor_2025_fmt': motor.formatar_numero(total_2025),
        'variacao_abs_fmt': motor.formatar_numero(total_variacao_abs),
        'variacao_perc_fmt': formatar_percentual(total_variacao_perc),
        'percentual': 100.0,
        'percentual_fmt': "100,0%",
        'cor': '#8B4513'
    }
    dados_tabela.append(total_item)
    
    # Dados para gráfico (Chart.js) - usar apenas dados de 2025
    dados_chart = {
        'labels': [item['nome'] for item in dados_grafico],
        'data': [item['valor_2025'] for item in dados_grafico],
        'backgroundColor': [item['cor'] for item in dados_grafico],
        'total_2025': total_2025,
        'total_2024': total_2024,
        'total_2025_fmt': motor.formatar_numero(total_2025),
        'total_2024_fmt': motor.formatar_numero(total_2024),
        'variacao_total_abs': total_variacao_abs,
        'variacao_total_perc': total_variacao_perc,
        'variacao_total_abs_fmt': motor.formatar_numero(total_variacao_abs),
        'variacao_total_perc_fmt': formatar_percentual(total_variacao_perc)
    }
    
    # Gerar comparativo mensal acumulado
    comparativo_mensal = _gerar_comparativo_mensal_acumulado(df_processar, motor, mes_numero)
    
    print(f"✅ Gráfico de receita de capital gerado: {len(dados_tabela)} origens + total")
    print(f"📅 Comparativo mensal: {len(comparativo_mensal)} meses")
    
    return dados_tabela, mes_referencia, dados_grafico, dados_chart, comparativo_mensal

def _obter_cor_origem(cod_origem: str) -> str:
    """
    Retorna cores personalizadas para cada origem de receita de capital
    
    Args:
        cod_origem: Código da origem da receita
        
    Returns:
        Código de cor hexadecimal
    """
    cores = {
        '20': '#8B4513',  # Marrom escuro - Alienação de Bens
        '21': '#D2691E',  # Chocolate - Operações de Crédito
        '22': '#CD853F',  # Peru - Transferências de Capital
        '23': '#DEB887',  # Burlywood - Outras Receitas de Capital
        '24': '#F4A460',  # Sandy brown - Receitas de Capital Diversas
        '25': '#DAA520'   # Goldenrod - Outras origens
    }
    return cores.get(cod_origem, '#A0522D')  # Sienna como padrão

def _obter_nome_origem_padrao(cod_origem: str) -> str:
    """
    Retorna nomes padrão para origens de receita de capital
    
    Args:
        cod_origem: Código da origem
        
    Returns:
        Nome da origem
    """
    nomes_origem = {
        '20': 'Alienação de Bens',
        '21': 'Operações de Crédito',
        '22': 'Transferências de Capital',
        '23': 'Outras Receitas de Capital',
        '24': 'Receitas de Capital Diversas',
        '25': 'Receitas de Capital Extraordinárias'
    }
    return nomes_origem.get(cod_origem, f'Origem {cod_origem}')

def _gerar_comparativo_mensal_acumulado(df_completo, motor, mes_referencia):
    """
    Gera comparativo mensal acumulado 2024 vs 2025 para receitas de capital
    
    REGRA: 
    - Mês 1: soma INMES=1
    - Mês 2: soma INMES=1+2 (acumulado)
    - Mês 3: soma INMES=1+2+3 (acumulado)
    - etc.
    
    Args:
        df_completo: DataFrame completo
        motor: Instância do MotorRelatorios
        mes_referencia: Mês de referência atual
        
    Returns:
        Lista com comparativos mensais
    """
    try:
        # Filtra apenas receitas de capital (categoria 2)
        df_capital = df_completo[df_completo['CATEGORIA'] == '2'].copy()
        
        if df_capital.empty or 'INMES' not in df_capital.columns:
            print("⚠️ Dados insuficientes para comparativo mensal de receitas de capital")
            return []
        
        # Obtém meses disponíveis em 2025
        meses_2025 = sorted(df_capital[df_capital['COEXERCICIO'] == 2025]['INMES'].dropna().unique())
        meses_2024 = sorted(df_capital[df_capital['COEXERCICIO'] == 2024]['INMES'].dropna().unique())
        
        if not meses_2025:
            return []
        
        max_mes = max(meses_2025)
        print(f"📅 Gerando comparativo mensal de receitas de capital até mês {max_mes-1} (referência: {max_mes})")
        
        comparativo = []
        
        # Gera comparativo para cada mês (exceto o último)
        for mes_atual in range(1, max_mes):  # Para até max_mes-1
            if mes_atual not in meses_2025:
                continue
                
            # Calcula saldo acumulado até o mês atual
            # 2025: soma de INMES 1 até mes_atual
            df_2025_acum = df_capital[
                (df_capital['COEXERCICIO'] == 2025) &
                (df_capital['INMES'] <= mes_atual)
            ]
            saldo_2025 = float(df_2025_acum['RECEITA LIQUIDA'].sum()) if 'RECEITA LIQUIDA' in df_2025_acum.columns else 0.0
            
            # 2024: soma de INMES 1 até mes_atual
            df_2024_acum = df_capital[
                (df_capital['COEXERCICIO'] == 2024) &
                (df_capital['INMES'] <= mes_atual)
            ]
            saldo_2024 = float(df_2024_acum['RECEITA LIQUIDA'].sum()) if 'RECEITA LIQUIDA' in df_2024_acum.columns else 0.0
            
            # Calcula variação
            variacao_abs = saldo_2025 - saldo_2024
            variacao_perc = ((saldo_2025 - saldo_2024) / saldo_2024 * 100) if saldo_2024 > 0 else (100 if saldo_2025 > 0 else 0)
            
            comparativo.append({
                'mes': mes_atual,
                'mes_fmt': f"{mes_atual:02d}",
                'saldo_2024': saldo_2024,
                'saldo_2025': saldo_2025,
                'variacao_abs': variacao_abs,
                'variacao_perc': variacao_perc,
                'saldo_2024_fmt': motor.formatar_numero(saldo_2024),
                'saldo_2025_fmt': motor.formatar_numero(saldo_2025),
                'variacao_abs_fmt': motor.formatar_numero(variacao_abs),
                'variacao_perc_fmt': formatar_percentual(variacao_perc)
            })
        
        print(f"✅ Comparativo mensal de receitas de capital gerado: {len(comparativo)} períodos")
        return comparativo
        
    except Exception as e:
        print(f"❌ Erro ao gerar comparativo mensal de receitas de capital: {e}")
        return []