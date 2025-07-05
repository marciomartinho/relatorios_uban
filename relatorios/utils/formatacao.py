"""
Funções de formatação para números e valores monetários
"""
import pandas as pd

def formatar_numero(valor: float) -> str:
    """
    Formata números para o padrão monetário brasileiro (R$ 1.234,56)
    
    Args:
        valor: Valor numérico a ser formatado
        
    Returns:
        String formatada no padrão brasileiro
    """
    if pd.isna(valor) or valor == 0: 
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor: float, decimais: int = 2) -> str:
    """
    Formata percentuais com sinal (padrão brasileiro)
    
    Args:
        valor: Valor percentual
        decimais: Número de casas decimais
        
    Returns:
        String formatada (ex: "+5,23%")
    """
    if valor == 0:
        return "0,00%"
    
    # Formatar com sinal e substituir ponto por vírgula (padrão brasileiro)
    resultado = f"{valor:+.{decimais}f}%".replace(".", ",")
    return resultado

def formatar_percentual_simples(valor: float, decimais: int = 2) -> str:
    """
    Formata percentuais sem sinal (padrão brasileiro)
    
    Args:
        valor: Valor percentual  
        decimais: Número de casas decimais
        
    Returns:
        String formatada (ex: "5,23%")
    """
    if valor == 0:
        return "0,00%"
    
    # Formatar sem sinal e substituir ponto por vírgula (padrão brasileiro)
    resultado = f"{valor:.{decimais}f}%".replace(".", ",")
    return resultado