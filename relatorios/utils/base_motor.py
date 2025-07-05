"""
Classe base para motores de relatórios
Contém funcionalidades comuns a todos os relatórios
"""
import pandas as pd
from typing import Dict, Optional
from .formatacao import formatar_numero

class MotorRelatorios:
    """
    Motor unificado para relatórios de receita e despesa
    Classe base que contém funcionalidades comuns
    """
    
    def __init__(self, df: pd.DataFrame, tipo_dados: str = 'receita'):
        """
        Inicializa o motor de relatórios
        
        Args:
            df: DataFrame com os dados
            tipo_dados: Tipo de dados ('receita' ou 'despesa')
        """
        self.df = df
        self.tipo_dados = tipo_dados
        self.mapas_nomes = self._criar_mapas_de_nomes()
    
    def _criar_mapas_de_nomes(self) -> Dict[str, Dict]:
        """
        Cria mapas de códigos para nomes para evitar buscas repetitivas no DataFrame
        
        Returns:
            Dicionário com mapeamentos de códigos para nomes
        """
        mapas = {}
        
        if self.tipo_dados == 'receita':
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIARECEITA'].to_dict(),
                    'origem': self.df.drop_duplicates('ORIGEM').set_index('ORIGEM')['NOFONTERECEITA'].to_dict(),
                    'especie': self.df.drop_duplicates('ESPECIE').set_index('ESPECIE')['NOSUBFONTERECEITA'].to_dict(),
                    'alinea': self.df.drop_duplicates('ALINEA').set_index('ALINEA')['NOALINEA'].to_dict()
                })
                
        elif self.tipo_dados == 'despesa':
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIA'].to_dict(),
                    'grupo': self.df.drop_duplicates('GRUPO').set_index('GRUPO')['NOGRUPO'].to_dict(),
                    'modalidade': self.df.drop_duplicates('MODALIDADE').set_index('MODALIDADE')['NOMODALIDADE'].to_dict(),
                    'elemento': self.df.drop_duplicates('ELEMENTO').set_index('ELEMENTO')['NOELEMENTO'].to_dict()
                })
                
        return mapas
    
    def filtrar_por_noug(self, noug_selecionada: Optional[str] = None) -> pd.DataFrame:
        """
        Aplica filtro por unidade gestora (NOUG) se uma for selecionada
        
        Args:
            noug_selecionada: NOUG para filtrar ou None para todas
            
        Returns:
            DataFrame filtrado
        """
        if noug_selecionada and noug_selecionada != 'todos':
            return self.df[self.df['NOUG'] == noug_selecionada].copy()
        return self.df.copy()
    
    def obter_nome_categoria(self, codigo: str) -> str:
        """
        Obtém o nome da categoria pelo código
        
        Args:
            codigo: Código da categoria
            
        Returns:
            Nome da categoria ou string vazia se não encontrado
        """
        return self.mapas_nomes.get('categoria', {}).get(codigo, '')
    
    def obter_nome_origem(self, codigo: str) -> str:
        """
        Obtém o nome da origem pelo código
        
        Args:
            codigo: Código da origem
            
        Returns:
            Nome da origem ou string vazia se não encontrado
        """
        return self.mapas_nomes.get('origem', {}).get(codigo, '')
    
    def formatar_numero(self, valor: float) -> str:
        """
        Wrapper para a função de formatação de números
        
        Args:
            valor: Valor a ser formatado
            
        Returns:
            String formatada
        """
        return formatar_numero(valor)