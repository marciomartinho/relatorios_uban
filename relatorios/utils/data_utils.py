"""
Funções utilitárias para trabalhar com datas e meses de referência
"""
import pandas as pd

def calcular_mes_referencia(df: pd.DataFrame) -> str:
    """
    Calcula o mês de referência com base no maior valor da coluna INMES
    Retorna no formato "MM/AAAA"
    
    Args:
        df: DataFrame com coluna INMES
        
    Returns:
        String no formato "MM/AAAA" (ex: "05/2025")
    """
    if 'INMES' in df.columns and not df.empty:
        max_mes = df['INMES'].max()
        if pd.notna(max_mes) and max_mes > 0:
            return f"{int(max_mes):02d}/2025"
    
    return "12/2025"  # Valor padrão

def obter_mes_numero(df: pd.DataFrame) -> str:
    """
    Retorna apenas o número do mês (formato "MM")
    
    Args:
        df: DataFrame com coluna INMES
        
    Returns:
        String no formato "MM" (ex: "05")
    """
    if 'INMES' in df.columns and not df.empty:
        max_mes = df['INMES'].max()
        if pd.notna(max_mes) and max_mes > 0:
            return f"{int(max_mes):02d}"
    return "12"

def validar_dados_ano(df: pd.DataFrame, ano: int) -> bool:
    """
    Valida se existem dados para um ano específico
    
    Args:
        df: DataFrame com coluna COEXERCICIO
        ano: Ano a ser validado
        
    Returns:
        True se existem dados, False caso contrário
    """
    if 'COEXERCICIO' not in df.columns:
        return False
    
    dados_ano = df[df['COEXERCICIO'] == ano]
    return not dados_ano.empty