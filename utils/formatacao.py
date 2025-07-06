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

def formatar_valor(valor: float) -> str:
    """
    Alias para formatar_numero() - para compatibilidade
    Formata números para o padrão monetário brasileiro (R$ 1.234,56)
    
    Args:
        valor: Valor numérico a ser formatado
        
    Returns:
        String formatada no padrão brasileiro
    """
    return formatar_numero(valor)

def formatar_valor_milhoes(valor: float) -> str:
    """
    Formata um valor numérico em milhões de reais
    
    Args:
        valor: Valor a ser formatado
        
    Returns:
        String formatada em milhões (ex: "R$ 1,23 Mi")
    """
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00 Mi"
    
    try:
        valor_float = float(valor)
        if valor_float == 0:
            return "R$ 0,00 Mi"
        
        valor_milhoes = valor_float / 1_000_000
        
        # Formata em padrão brasileiro
        if valor_milhoes >= 1:
            valor_formatado = f"R$ {valor_milhoes:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # Se for menor que 1 milhão, mostra em milhares
            valor_milhares = valor_float / 1_000
            valor_formatado = f"R$ {valor_milhares:,.0f} mil".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return valor_formatado
        
    except (ValueError, TypeError):
        return "R$ 0,00 Mi"

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