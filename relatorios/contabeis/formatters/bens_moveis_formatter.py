"""
Formatador para relatório de bens móveis
"""
from typing import List, Dict
from utils.formatacao import formatar_numero
from ..models.bens_moveis_models import ResultadoConciliacao, DadosBenMovel, SubtotalNoug
from ..processors.sisgepat_processor import SisgepatProcessor

class BensMoviesFormatter:
    """Formatador específico para relatório de bens móveis"""
    
    def formatar_para_tabela(self, resultado: ResultadoConciliacao) -> List[Dict]:
        """
        Formata dados para exibição na tabela HTML
        
        Args:
            resultado: ResultadoConciliacao com os dados processados
            
        Returns:
            Lista de dicionários formatados para a tabela
        """
        dados_formatados = []
        
        # Processa NOUGs normais (exceto DFTRANS)
        for noug in sorted(resultado.dados_por_noug.keys()):
            if noug == SisgepatProcessor.NOME_DFTRANS:
                continue
                
            # Adiciona cabeçalho da NOUG
            dados_formatados.append({
                'tipo': 'header_noug',
                'noug': noug,
                'colspan': 8
            })
            
            # Processa dados da NOUG
            dados_noug = resultado.dados_por_noug[noug]
            subtotal = self._processar_noug(dados_noug, dados_formatados)
            
            # Adiciona subtotal
            self._adicionar_subtotal(subtotal, noug, dados_formatados)
            
            # Adiciona separador (exceto após a última NOUG)
            if noug != list(sorted(resultado.dados_por_noug.keys()))[-1]:
                dados_formatados.append({'tipo': 'separador'})
        
        # Processa DFTRANS por último se existir
        if SisgepatProcessor.NOME_DFTRANS in resultado.dados_por_noug:
            self._processar_dftrans(resultado, dados_formatados)
        
        # Adiciona total geral
        self._adicionar_total_geral(resultado, dados_formatados)
        
        return dados_formatados
    
    def _processar_noug(self, dados_noug: List[DadosBenMovel], 
                       dados_formatados: List[Dict]) -> SubtotalNoug:
        """Processa dados de uma NOUG e retorna subtotal"""
        subtotal = {
            'BENS_MOVEIS': 0,
            'BENS_MOVEIS_ALMOX': 0,
            'BENS_MOVEIS_IMPORT': 0,
            'SISGEPAT': 0
        }
        
        # Ordena por COUG e SUBITEM
        for item in sorted(dados_noug, key=lambda x: (x.coug, x.subitem)):
            # Adiciona linha de dados
            linha_dados = {
                'tipo': 'dados',
                'coug': item.coug,
                'subitem': item.subitem,
                'bens_moveis': item.bens_moveis,
                'bens_moveis_almox': item.bens_moveis_almox,
                'bens_moveis_import': item.bens_moveis_import,
                'saldo_total': item.saldo_siggo,
                'saldo_sisgepat': item.sisgepat,
                'diferenca': item.diferenca,
                'bens_moveis_fmt': formatar_numero(item.bens_moveis),
                'bens_moveis_almox_fmt': formatar_numero(item.bens_moveis_almox),
                'bens_moveis_import_fmt': formatar_numero(item.bens_moveis_import),
                'saldo_total_fmt': formatar_numero(item.saldo_siggo),
                'saldo_sisgepat_fmt': formatar_numero(item.sisgepat),
                'diferenca_fmt': formatar_numero(item.diferenca)
            }
            dados_formatados.append(linha_dados)
            
            # Acumula subtotais
            subtotal['BENS_MOVEIS'] += item.bens_moveis
            subtotal['BENS_MOVEIS_ALMOX'] += item.bens_moveis_almox
            subtotal['BENS_MOVEIS_IMPORT'] += item.bens_moveis_import
            subtotal['SISGEPAT'] += item.sisgepat
        
        return subtotal
    
    def _adicionar_subtotal(self, subtotal: Dict, noug: str, 
                           dados_formatados: List[Dict]):
        """Adiciona linha de subtotal"""
        total_siggo = subtotal['BENS_MOVEIS'] + subtotal['BENS_MOVEIS_ALMOX'] + subtotal['BENS_MOVEIS_IMPORT']
        diferenca = total_siggo - subtotal['SISGEPAT']
        
        linha_subtotal = {
            'tipo': 'subtotal',
            'noug': noug,
            'bens_moveis': subtotal['BENS_MOVEIS'],
            'bens_moveis_almox': subtotal['BENS_MOVEIS_ALMOX'],
            'bens_moveis_import': subtotal['BENS_MOVEIS_IMPORT'],
            'saldo_total': total_siggo,
            'saldo_sisgepat': subtotal['SISGEPAT'],
            'diferenca': diferenca,
            'bens_moveis_fmt': formatar_numero(subtotal['BENS_MOVEIS']),
            'bens_moveis_almox_fmt': formatar_numero(subtotal['BENS_MOVEIS_ALMOX']),
            'bens_moveis_import_fmt': formatar_numero(subtotal['BENS_MOVEIS_IMPORT']),
            'saldo_total_fmt': formatar_numero(total_siggo),
            'saldo_sisgepat_fmt': formatar_numero(subtotal['SISGEPAT']),
            'diferenca_fmt': formatar_numero(diferenca)
        }
        dados_formatados.append(linha_subtotal)
    
    def _processar_dftrans(self, resultado: ResultadoConciliacao, 
                          dados_formatados: List[Dict]):
        """Processa dados específicos do DFTRANS"""
        dados_dftrans = resultado.dados_por_noug.get(SisgepatProcessor.NOME_DFTRANS, [])
        
        if not dados_dftrans:
            return
        
        # Adiciona cabeçalho do DFTRANS
        dados_formatados.append({
            'tipo': 'header_noug',
            'noug': SisgepatProcessor.NOME_DFTRANS,
            'colspan': 8
        })
        
        # Processa dados
        subtotal_dftrans = {
            'BENS_MOVEIS': 0,
            'BENS_MOVEIS_ALMOX': 0,
            'BENS_MOVEIS_IMPORT': 0,
            'SISGEPAT': 0
        }
        
        for item in sorted(dados_dftrans, key=lambda x: (x.coug, x.subitem)):
            # Para DFTRANS, saldo SIGGO é sempre 0
            linha_dados = {
                'tipo': 'dados',
                'coug': item.coug,
                'subitem': item.subitem,
                'bens_moveis': 0,
                'bens_moveis_almox': 0,
                'bens_moveis_import': 0,
                'saldo_total': 0,
                'saldo_sisgepat': item.sisgepat,
                'diferenca': -item.sisgepat,
                'bens_moveis_fmt': formatar_numero(0),
                'bens_moveis_almox_fmt': formatar_numero(0),
                'bens_moveis_import_fmt': formatar_numero(0),
                'saldo_total_fmt': formatar_numero(0),
                'saldo_sisgepat_fmt': formatar_numero(item.sisgepat),
                'diferenca_fmt': formatar_numero(-item.sisgepat)
            }
            dados_formatados.append(linha_dados)
            
            subtotal_dftrans['SISGEPAT'] += item.sisgepat
        
        # Adiciona subtotal do DFTRANS
        self._adicionar_subtotal(subtotal_dftrans, SisgepatProcessor.NOME_DFTRANS, dados_formatados)
    
    def _adicionar_total_geral(self, resultado: ResultadoConciliacao, 
                              dados_formatados: List[Dict]):
        """Adiciona linha de total geral"""
        total_siggo = resultado.total_siggo
        total_sisgepat = resultado.total_sisgepat
        diferenca = resultado.diferenca_total
        
        linha_total = {
            'tipo': 'total',
            'bens_moveis': resultado.total_geral['BENS_MOVEIS'],
            'bens_moveis_almox': resultado.total_geral['BENS_MOVEIS_ALMOX'],
            'bens_moveis_import': resultado.total_geral['BENS_MOVEIS_IMPORT'],
            'saldo_total': total_siggo,
            'saldo_sisgepat': total_sisgepat,
            'diferenca': diferenca,
            'bens_moveis_fmt': formatar_numero(resultado.total_geral['BENS_MOVEIS']),
            'bens_moveis_almox_fmt': formatar_numero(resultado.total_geral['BENS_MOVEIS_ALMOX']),
            'bens_moveis_import_fmt': formatar_numero(resultado.total_geral['BENS_MOVEIS_IMPORT']),
            'saldo_total_fmt': formatar_numero(total_siggo),
            'saldo_sisgepat_fmt': formatar_numero(total_sisgepat),
            'diferenca_fmt': formatar_numero(diferenca)
        }
        dados_formatados.append(linha_total)