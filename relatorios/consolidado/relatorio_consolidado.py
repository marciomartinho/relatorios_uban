"""
Relatório Consolidado de Receitas - Motor Principal
Consolida todos os 13 relatórios individuais em um PDF executivo

CRIAR ESTE ARQUIVO EM: relatorios/consolidado/relatorio_consolidado.py
"""
import pandas as pd
from datetime import datetime
import os
import traceback

# Importações dos utils
from relatorios.utils import MotorRelatorios, obter_mes_numero, formatar_percentual

# Importações dos 13 relatórios individuais
from relatorios.receita.analise_inconsistencias import gerar_relatorio_analise_inconsistencias
from relatorios.receita.grafico_pizza import gerar_grafico_receita_liquida
from relatorios.receita.grafico_receita_capital import gerar_grafico_receita_capital
from relatorios.receita.receitas_alienacao_bens import gerar_relatorio_receitas_alienacao_bens
from relatorios.receita.receitas_amortizacao_emprestimo import gerar_relatorio_receitas_amortizacao_emprestimo
from relatorios.receita.receitas_contribuicoes import gerar_relatorio_receitas_contribuicoes
from relatorios.receita.receitas_operacoes_credito import gerar_grafico_receita_capital as gerar_operacoes_credito
from relatorios.receita.receitas_outras_correntes import gerar_relatorio_outras_receitas_correntes
from relatorios.receita.receitas_patrimoniais import gerar_relatorio_receitas_patrimoniais
from relatorios.receita.receitas_servicos import gerar_relatorio_receitas_servicos
from relatorios.receita.receitas_transferencia_capital import gerar_relatorio_receitas_transferencia_capital
from relatorios.receita.receitas_transferencias import gerar_relatorio_receitas_transferencias
from relatorios.receita.receitas_tributarias import gerar_relatorio_receitas_tributarias

class RelatorioConsolidado:
    """
    Classe principal para consolidar todos os relatórios de receita
    """
    
    def __init__(self, df_receita, mes_referencia, noug_selecionada=None):
        self.df_receita = df_receita
        self.mes_referencia = mes_referencia
        self.noug_selecionada = noug_selecionada
        self.estrutura_hierarquica = self._gerar_estrutura_hierarquica()
        self.dados_consolidados = {}
        self.resumo_executivo = {}
        self.kpis_principais = {}
        
        print(f"🚀 RelatorioConsolidado inicializado para {mes_referencia}")
    
    def _gerar_estrutura_hierarquica(self):
        """Gera estrutura hierárquica básica das receitas"""
        # Estrutura básica por categoria
        return {
            '1': {  # Receitas Correntes
                '11': 'Impostos, Taxas e Contribuições de Melhoria',
                '12': 'Contribuições',
                '13': 'Receita Patrimonial',
                '16': 'Receita de Serviços',
                '17': 'Transferências Correntes',
                '19': 'Outras Receitas Correntes'
            },
            '2': {  # Receitas de Capital
                '21': 'Operações de Crédito',
                '22': 'Alienação de Bens',
                '23': 'Amortização de Empréstimos',
                '24': 'Transferências de Capital'
            },
            '7': {  # Receitas Correntes Intra
                '71': 'Impostos, Taxas e Contribuições de Melhoria - Intra',
                '72': 'Contribuições',
                '76': 'Receita de Serviços',
                '77': 'Transferências Correntes Intra'
            }
        }
    
    def executar_todos_relatorios(self):
        """Executa todos os 13 relatórios e consolida os dados"""
        
        # Mapeamento dos relatórios
        relatorios_mapeamento = {
            'tributarias': {
                'funcao': gerar_relatorio_receitas_tributarias,
                'categoria': 'correntes',
                'origens': ['11', '71'],
                'nome': 'Receitas Tributárias'
            },
            'contribuicoes': {
                'funcao': gerar_relatorio_receitas_contribuicoes,
                'categoria': 'correntes',
                'origens': ['12', '72'],
                'nome': 'Receitas de Contribuições'
            },
            'patrimoniais': {
                'funcao': gerar_relatorio_receitas_patrimoniais,
                'categoria': 'correntes',
                'origens': ['13', '73'],
                'nome': 'Receitas Patrimoniais'
            },
            'servicos': {
                'funcao': gerar_relatorio_receitas_servicos,
                'categoria': 'correntes',
                'origens': ['16', '76'],
                'nome': 'Receitas de Serviços'
            },
            'transferencias': {
                'funcao': gerar_relatorio_receitas_transferencias,
                'categoria': 'correntes',
                'origens': ['17', '77'],
                'nome': 'Transferências Correntes'
            },
            'outras_correntes': {
                'funcao': gerar_relatorio_outras_receitas_correntes,
                'categoria': 'correntes',
                'origens': ['79', '99'],
                'nome': 'Outras Receitas Correntes'
            },
            'operacoes_credito': {
                'funcao': gerar_operacoes_credito,
                'categoria': 'capital',
                'origens': ['21'],
                'nome': 'Operações de Crédito'
            },
            'alienacao_bens': {
                'funcao': gerar_relatorio_receitas_alienacao_bens,
                'categoria': 'capital',
                'origens': ['22'],
                'nome': 'Alienação de Bens'
            },
            'amortizacao': {
                'funcao': gerar_relatorio_receitas_amortizacao_emprestimo,
                'categoria': 'capital',
                'origens': ['23'],
                'nome': 'Amortização de Empréstimos'
            },
            'transferencias_capital': {
                'funcao': gerar_relatorio_receitas_transferencia_capital,
                'categoria': 'capital',
                'origens': ['24'],
                'nome': 'Transferências de Capital'
            },
            'grafico_correntes': {
                'funcao': gerar_grafico_receita_liquida,
                'categoria': 'graficos',
                'nome': 'Gráfico Receitas Correntes'
            },
            'grafico_capital': {
                'funcao': gerar_grafico_receita_capital,
                'categoria': 'graficos',
                'nome': 'Gráfico Receitas Capital'
            },
            'inconsistencias': {
                'funcao': gerar_relatorio_analise_inconsistencias,
                'categoria': 'analises',
                'nome': 'Análise de Inconsistências'
            }
        }
        
        print(f"📊 Executando {len(relatorios_mapeamento)} relatórios...")
        
        for codigo, config in relatorios_mapeamento.items():
            try:
                print(f"   📊 Executando: {config['nome']}")
                inicio = datetime.now()
                
                resultado = config['funcao'](
                    self.df_receita,
                    self.estrutura_hierarquica,
                    self.noug_selecionada
                )
                
                fim = datetime.now()
                tempo = (fim - inicio).total_seconds()
                
                self.dados_consolidados[codigo] = {
                    'dados': self._sanitizar_resultado_relatorio(resultado),
                    'categoria': config['categoria'],
                    'nome': config['nome'],
                    'status': 'sucesso',
                    'tempo_execucao': tempo,
                    'timestamp': fim.isoformat()
                }
                
                print(f"      ✅ Concluído em {tempo:.2f}s")
                
            except Exception as e:
                print(f"      ❌ Erro no relatório {config['nome']}: {e}")
                self.dados_consolidados[codigo] = {
                    'dados': None,
                    'categoria': config['categoria'],
                    'nome': config['nome'],
                    'status': 'erro',
                    'erro': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        print(f"✅ Relatório consolidado gerado em {sum(item.get('tempo_execucao', 0) for item in self.dados_consolidados.values()):.2f} segundos")
        print(f"📊 {len([r for r in self.dados_consolidados.values() if r['status'] == 'sucesso'])} relatórios executados")
        
        return self.dados_consolidados
    
    def _sanitizar_resultado_relatorio(self, resultado):
        """Sanitiza resultado de um relatório individual"""
        if not resultado or len(resultado) != 6:
            return resultado
        
        dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs, comparativo_mensal = resultado
        
        return {
            'dados_numericos': dados_numericos,
            'mes_referencia': mes_referencia,
            'dados_para_ia': dados_para_ia,
            'dados_pdf': dados_pdf,
            'resumo_nougs': resumo_nougs,
            'comparativo_mensal': comparativo_mensal
        }
    
    def gerar_resumo_executivo(self):
        """Gera resumo executivo consolidado"""
        print("📊 Consolidando dados gerais...")
        
        try:
            # Calcular totais por categoria
            total_correntes_2025 = 0
            total_correntes_2024 = 0
            total_capital_2025 = 0
            total_capital_2024 = 0
            
            relatorios_sucesso = 0
            relatorios_erro = 0
            
            for codigo, relatorio in self.dados_consolidados.items():
                if relatorio['status'] == 'sucesso':
                    relatorios_sucesso += 1
                    
                    # Extrair dados se disponível
                    if relatorio['dados'] and isinstance(relatorio['dados'], dict):
                        dados_numericos = relatorio['dados'].get('dados_numericos', [])
                        
                        # Procurar linha de total
                        for linha in dados_numericos:
                            if isinstance(linha, dict) and linha.get('tipo') == 'total':
                                valor_2025 = linha.get('receita_2025', 0)
                                valor_2024 = linha.get('receita_2024', 0)
                                
                                if relatorio['categoria'] == 'correntes':
                                    total_correntes_2025 += valor_2025
                                    total_correntes_2024 += valor_2024
                                elif relatorio['categoria'] == 'capital':
                                    total_capital_2025 += valor_2025
                                    total_capital_2024 += valor_2024
                                break
                else:
                    relatorios_erro += 1
            
            # Calcular totais gerais
            total_geral_2025 = total_correntes_2025 + total_capital_2025
            total_geral_2024 = total_correntes_2024 + total_capital_2024
            
            variacao_absoluta = total_geral_2025 - total_geral_2024
            variacao_percentual = ((total_geral_2025 - total_geral_2024) / total_geral_2024 * 100) if total_geral_2024 > 0 else 0
            
            # Identificar maior categoria
            maior_categoria = "Receitas Correntes" if total_correntes_2025 > total_capital_2025 else "Receitas de Capital"
            
            self.resumo_executivo = {
                'total_geral_2025': total_geral_2025,
                'total_geral_2024': total_geral_2024,
                'total_correntes_2025': total_correntes_2025,
                'total_correntes_2024': total_correntes_2024,
                'total_capital_2025': total_capital_2025,
                'total_capital_2024': total_capital_2024,
                'variacao_absoluta': variacao_absoluta,
                'variacao_percentual': variacao_percentual,
                'maior_categoria': maior_categoria,
                'relatorios_sucesso': relatorios_sucesso,
                'relatorios_erro': relatorios_erro,
                'mes_referencia': self.mes_referencia,
                'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            
            print("📈 Gerando resumo executivo...")
            return self.resumo_executivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar resumo executivo: {e}")
            return {
                'erro': str(e),
                'mes_referencia': self.mes_referencia,
                'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
    
    def gerar_kpis_principais(self):
        """Gera KPIs principais para dashboard"""
        try:
            motor = MotorRelatorios(self.df_receita, tipo_dados='receita')
            
            self.kpis_principais = {
                'receita_total_2025': self.resumo_executivo.get('total_geral_2025', 0),
                'receita_total_2024': self.resumo_executivo.get('total_geral_2024', 0),
                'variacao_percentual': self.resumo_executivo.get('variacao_percentual', 0),
                'maior_fonte': self.resumo_executivo.get('maior_categoria', 'N/A'),
                'relatorios_processados': self.resumo_executivo.get('relatorios_sucesso', 0),
                'mes_referencia': self.mes_referencia,
                
                # Formatados
                'receita_total_2025_fmt': motor.formatar_numero(self.resumo_executivo.get('total_geral_2025', 0)),
                'receita_total_2024_fmt': motor.formatar_numero(self.resumo_executivo.get('total_geral_2024', 0)),
                'variacao_percentual_fmt': formatar_percentual(self.resumo_executivo.get('variacao_percentual', 0)),
                'variacao_absoluta_fmt': motor.formatar_numero(self.resumo_executivo.get('variacao_absoluta', 0))
            }
            
            return self.kpis_principais
            
        except Exception as e:
            print(f"❌ Erro ao gerar KPIs: {e}")
            return {
                'erro': str(e),
                'mes_referencia': self.mes_referencia
            }