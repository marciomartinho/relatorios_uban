"""
Modelos de dados para o relatório de bens móveis
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DadosBenMovel:
    """Representa os dados de um bem móvel"""
    coug: str
    subitem: str
    bens_moveis: float
    bens_moveis_almox: float
    bens_moveis_import: float
    sisgepat: float = 0.0
    
    @property
    def saldo_siggo(self) -> float:
        """Calcula o saldo total no SIGGO"""
        return self.bens_moveis + self.bens_moveis_almox + self.bens_moveis_import
    
    @property
    def diferenca(self) -> float:
        """Calcula a diferença entre SIGGO e SISGEPAT"""
        return self.saldo_siggo - self.sisgepat

@dataclass
class SubtotalNoug:
    """Representa o subtotal de uma NOUG"""
    noug: str
    bens_moveis: float
    bens_moveis_almox: float
    bens_moveis_import: float
    sisgepat: float
    
    @property
    def saldo_siggo(self) -> float:
        return self.bens_moveis + self.bens_moveis_almox + self.bens_moveis_import
    
    @property
    def diferenca(self) -> float:
        return self.saldo_siggo - self.sisgepat

@dataclass
class DadosSaldosContabeis:
    """Representa os dados de saldos contábeis"""
    itens: List[Dict[str, any]]
    total: float
    total_fmt: str
    mes_referencia: str

@dataclass
class ResultadoConciliacao:
    """Resultado da conciliação SIGGO x SISGEPAT"""
    dados_por_noug: Dict[str, List[DadosBenMovel]]
    total_geral: Dict[str, float]
    dados_pdf: Dict
    dados_saldos_contabeis: Optional[DadosSaldosContabeis] = None
    
    @property
    def total_siggo(self) -> float:
        return (self.total_geral['BENS_MOVEIS'] + 
                self.total_geral['BENS_MOVEIS_ALMOX'] + 
                self.total_geral['BENS_MOVEIS_IMPORT'])
    
    @property
    def total_sisgepat(self) -> float:
        return self.total_geral['SISGEPAT']
    
    @property
    def diferenca_total(self) -> float:
        return self.total_siggo - self.total_sisgepat