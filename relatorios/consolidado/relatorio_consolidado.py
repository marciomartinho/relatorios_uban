"""
Classe Principal: RelatorioConsolidado
Motor principal para consolidar todos os 13+ relatórios de receita
VERSÃO CORRIGIDA - Baseada no esquema real de importações
"""
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd

# Importações dos utils
from ..utils import MotorRelatorios, obter_mes_numero, formatar_percentual, calcular_mes_referencia

# Importações dos 13 relatórios individuais (baseado no esquema real)
from ..receita.analise_inconsistencias import gerar_relatorio_analise_inconsistencias
from ..receita.grafico_pizza import gerar_grafico_receita_liquida
from ..receita.grafico_receita_capital import gerar_grafico_receita_capital
from ..receita.receitas_alienacao_bens import gerar_relatorio_receitas_alienacao_bens
from ..receita.receitas_amortizacao_emprestimo import gerar_relatorio_receitas_amortizacao_emprestimo
from ..receita.receitas_contribuicoes import gerar_relatorio_receitas_contribuicoes
from ..receita.receitas_operacoes_credito import gerar_grafico_receita_capital as gerar_operacoes_credito
from ..receita.receitas_outras_correntes import gerar_relatorio_outras_receitas_correntes
from ..receita.receitas_patrimoniais import gerar_relatorio_receitas_patrimoniais
from ..receita.receitas_servicos import gerar_relatorio_receitas_servicos
from ..receita.receitas_transferencia_capital import gerar_relatorio_receitas_transferencia_capital
from ..receita.receitas_transferencias import gerar_relatorio_receitas_transferencias
from ..receita.receitas_tributarias import gerar_relatorio_receitas_tributarias

# Dicionário de mapeamento dos relatórios (conforme esquema real)
RELATORIOS_MAPEAMENTO = {
    # Receitas Correntes
    'tributarias': {
        'funcao': gerar_relatorio_receitas_tributarias,
        'categoria': 'correntes',
        'origens': ['11', '71'],
        'nome': 'Receitas Tributárias',
        'prioridade': 1
    },
    'contribuicoes': {
        'funcao': gerar_relatorio_receitas_contribuicoes,
        'categoria': 'correntes',
        'origens': ['12', '72'],
        'nome': 'Receitas de Contribuições',
        'prioridade': 2
    },
    'patrimoniais': {
        'funcao': gerar_relatorio_receitas_patrimoniais,
        'categoria': 'correntes',
        'origens': ['13', '73'],
        'nome': 'Receitas Patrimoniais',
        'prioridade': 3
    },
    'servicos': {
        'funcao': gerar_relatorio_receitas_servicos,
        'categoria': 'correntes',
        'origens': ['16', '76'],
        'nome': 'Receitas de Serviços',
        'prioridade': 4
    },
    'transferencias': {
        'funcao': gerar_relatorio_receitas_transferencias,
        'categoria': 'correntes',
        'origens': ['17', '77'],
        'nome': 'Transferências Correntes',
        'prioridade': 5
    },
    'outras_correntes': {
        'funcao': gerar_relatorio_outras_receitas_correntes,
        'categoria': 'correntes',
        'origens': ['79', '99'],
        'nome': 'Outras Receitas Correntes',
        'prioridade': 6
    },
    
    # Receitas de Capital
    'operacoes_credito': {
        'funcao': gerar_operacoes_credito,  # Usando alias para função com nome diferente
        'categoria': 'capital',
        'origens': ['21'],
        'nome': 'Operações de Crédito',
        'prioridade': 7
    },
    'alienacao_bens': {
        'funcao': gerar_relatorio_receitas_alienacao_bens,
        'categoria': 'capital',
        'origens': ['22'],
        'nome': 'Alienação de Bens',
        'prioridade': 8
    },
    'amortizacao': {
        'funcao': gerar_relatorio_receitas_amortizacao_emprestimo,
        'categoria': 'capital',
        'origens': ['23'],
        'nome': 'Amortização de Empréstimos',
        'prioridade': 9
    },
    'transferencias_capital': {
        'funcao': gerar_relatorio_receitas_transferencia_capital,
        'categoria': 'capital',
        'origens': ['24'],
        'nome': 'Transferências de Capital',
        'prioridade': 10
    },
    
    # Gráficos e Análises
    'grafico_correntes': {
        'funcao': gerar_grafico_receita_liquida,
        'categoria': 'graficos',
        'nome': 'Gráfico Receitas Correntes',
        'prioridade': 11
    },
    'grafico_capital': {
        'funcao': gerar_grafico_receita_capital,
        'categoria': 'graficos',
        'nome': 'Gráfico Receitas Capital',
        'prioridade': 12
    },
    'inconsistencias': {
        'funcao': gerar_relatorio_analise_inconsistencias,
        'categoria': 'analises',
        'nome': 'Análise de Inconsistências',
        'prioridade': 13
    }
}


class RelatorioConsolidado:
    """
    Classe principal para consolidar todos os relatórios de receita em um PDF único
    """
    
    def __init__(self, df_receita: pd.DataFrame, mes_referencia: str, 
                 estrutura_hierarquica: Dict = None, noug_selecionada: Optional[str] = None):
        """
        Inicializa o consolidador de relatórios
        
        Args:
            df_receita: DataFrame com dados de receita
            mes_referencia: Mês de referência (formato "05/2025")
            estrutura_hierarquica: Estrutura hierárquica das receitas
            noug_selecionada: NOUG selecionada para filtro (opcional)
        """
        self.df_receita = df_receita
        self.mes_referencia = mes_referencia
        self.estrutura_hierarquica = estrutura_hierarquica or self._gerar_estrutura_hierarquica()
        self.noug_selecionada = noug_selecionada
        
        # Dados consolidados (será preenchido durante a execução)
        self.dados_consolidados = {}
        
        # Status de execução
        self.relatorios_executados = {}
        self.tempo_total_execucao = 0
        self.erros_encontrados = []
        
        print(f"🚀 RelatorioConsolidado inicializado para {mes_referencia}")
        if noug_selecionada:
            print(f"📍 Filtro NOUG: {noug_selecionada}")
    
    def _gerar_estrutura_hierarquica(self) -> Dict:
        """
        Gera estrutura hierárquica padrão se não fornecida
        
        Returns:
            Estrutura hierárquica das receitas
        """
        return {
            "1": {  # Receitas Correntes
                "11": ["111", "112", "113", "114", "115", "116", "117", "118", "119"],
                "12": ["121", "122", "123", "124", "125", "126", "127", "128", "129"],
                "13": ["131", "132", "133", "134", "135", "136", "137", "138", "139"],
                "16": ["161", "162", "163", "164", "165", "166", "167", "168", "169"],
                "17": ["171", "172", "173", "174", "175", "176", "177", "178", "179"],
                "19": ["191", "192", "193", "194", "195", "196", "197", "198", "199"]
            },
            "2": {  # Receitas de Capital
                "21": ["211", "212", "213", "214", "215", "216", "217", "218", "219"],
                "22": ["221", "222", "223", "224", "225", "226", "227", "228", "229"],
                "23": ["231", "232", "233", "234", "235", "236", "237", "238", "239"],
                "24": ["241", "242", "243", "244", "245", "246", "247", "248", "249"]
            }
        }
    
    def gerar_relatorio_completo(self) -> Dict[str, Any]:
        """
        Executa todos os 13 relatórios e consolida os dados
        
        Returns:
            Dicionário com todos os dados consolidados
        """
        print("🔄 Iniciando geração do relatório consolidado...")
        inicio_total = time.time()
        
        # 1. Inicializa estrutura de dados consolidados
        self._inicializar_estrutura_dados()
        
        # 2. Executa todos os relatórios
        self._executar_todos_relatorios()
        
        # 3. Consolida dados gerais
        self._consolidar_dados_gerais()
        
        # 4. Gera resumo executivo
        self._gerar_resumo_executivo()
        
        # 5. Finaliza consolidação
        fim_total = time.time()
        self.tempo_total_execucao = fim_total - inicio_total
        
        print(f"✅ Relatório consolidado gerado em {self.tempo_total_execucao:.2f} segundos")
        print(f"📊 {len(self.relatorios_executados)} relatórios executados")
        
        if self.erros_encontrados:
            print(f"⚠️ {len(self.erros_encontrados)} erros encontrados")
            for erro in self.erros_encontrados:
                print(f"   - {erro}")
        
        return self.dados_consolidados
    
    def _inicializar_estrutura_dados(self):
        """Inicializa a estrutura base dos dados consolidados"""
        
        # Calcula metadados básicos
        total_registros = len(self.df_receita) if not self.df_receita.empty else 0
        exercicios_disponiveis = sorted(self.df_receita['COEXERCICIO'].unique()) if 'COEXERCICIO' in self.df_receita.columns else []
        
        self.dados_consolidados = {
            'metadados': {
                'mes_referencia': self.mes_referencia,
                'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'noug_filtrada': self.noug_selecionada,
                'total_registros': total_registros,
                'exercicios_disponiveis': exercicios_disponiveis,
                'tempo_geracao': 0  # Será atualizado no final
            },
            'resumo_executivo': {
                'receita_total_2025': 0,
                'receita_total_2024': 0,
                'variacao_percentual': 0,
                'maior_receita': '',
                'crescimento_destaque': '',
                'principais_kpis': {}
            },
            'receitas_correntes': {
                'tributarias': {},
                'contribuicoes': {},
                'patrimoniais': {},
                'servicos': {},
                'transferencias': {},
                'outras': {}
            },
            'receitas_capital': {
                'operacoes_credito': {},
                'alienacao_bens': {},
                'amortizacao': {},
                'transferencias_capital': {}
            },
            'analises_especiais': {
                'inconsistencias': {},
                'evolucao_mensal': {},
                'comparativo_anual': {},
                'balanco_geral': {}
            },
            'graficos': {
                'dashboard_principal': None,
                'receitas_correntes': None,
                'receitas_capital': None,
                'evolucao_mensal': None
            },
            'relatorios_executados': {},
            'estatisticas_execucao': {
                'total_relatorios': len(RELATORIOS_MAPEAMENTO),
                'relatorios_bem_sucedidos': 0,
                'relatorios_com_erro': 0,
                'tempo_total': 0
            }
        }
        
        print("📋 Estrutura de dados consolidados inicializada")
    
    def _executar_todos_relatorios(self):
        """Executa todos os relatórios mapeados"""
        
        print(f"🔄 Executando {len(RELATORIOS_MAPEAMENTO)} relatórios...")
        
        # Ordena relatórios por prioridade
        relatorios_ordenados = sorted(
            RELATORIOS_MAPEAMENTO.items(),
            key=lambda x: x[1]['prioridade']
        )
        
        for codigo_relatorio, config in relatorios_ordenados:
            self._executar_relatorio_individual(codigo_relatorio, config)
    
    def _executar_relatorio_individual(self, codigo: str, config: Dict[str, Any]):
        """
        Executa um relatório individual e armazena os resultados
        
        Args:
            codigo: Código do relatório
            config: Configuração do relatório
        """
        print(f"   📊 Executando: {config['nome']}")
        inicio = time.time()
        
        try:
            # Executa o relatório conforme padrão: (df_completo, estrutura_hierarquica, noug_selecionada)
            funcao = config['funcao']
            resultado = funcao(
                self.df_receita,
                self.estrutura_hierarquica,
                self.noug_selecionada
            )
            
            # Processa resultado baseado no tipo de retorno
            dados_processados = self._processar_resultado_relatorio(codigo, resultado, config)
            
            # Armazena resultado
            fim = time.time()
            tempo_execucao = fim - inicio
            
            self.relatorios_executados[codigo] = {
                'status': 'sucesso',
                'dados': dados_processados,
                'tempo_execucao': tempo_execucao,
                'categoria': config['categoria'],
                'nome': config['nome']
            }
            
            # Armazena na estrutura consolidada baseado na categoria
            self._armazenar_por_categoria(codigo, dados_processados, config['categoria'])
            
            print(f"      ✅ Concluído em {tempo_execucao:.2f}s")
            
        except Exception as e:
            erro_msg = f"Erro em {config['nome']}: {str(e)}"
            self.erros_encontrados.append(erro_msg)
            
            self.relatorios_executados[codigo] = {
                'status': 'erro',
                'erro': str(e),
                'tempo_execucao': time.time() - inicio,
                'categoria': config['categoria'],
                'nome': config['nome']
            }
            
            print(f"      ❌ Erro: {str(e)}")
    
    def _processar_resultado_relatorio(self, codigo: str, resultado: Any, config: Dict) -> Dict[str, Any]:
        """
        Processa o resultado de um relatório baseado no padrão de retorno
        Padrão: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf, resumo_nougs, comparativo_mensal)
        
        Args:
            codigo: Código do relatório
            resultado: Resultado retornado pela função
            config: Configuração do relatório
            
        Returns:
            Dados processados e padronizados
        """
        dados_processados = {
            'codigo': codigo,
            'nome': config['nome'],
            'categoria': config['categoria'],
            'dados_originais': resultado,
            'dados_padronizados': {},
            'totais': {},
            'metadados': {}
        }
        
        try:
            # Padrão de retorno: tupla com 6 elementos
            if isinstance(resultado, tuple) and len(resultado) >= 4:
                dados_numericos, mes_ref, dados_ia, dados_pdf = resultado[:4]
                
                dados_processados['dados_padronizados'] = {
                    'dados_numericos': dados_numericos or [],
                    'mes_referencia': mes_ref,
                    'dados_para_ia': dados_ia or [],
                    'dados_pdf': dados_pdf or {}
                }
                
                # Adiciona dados extras se existirem (resumo_nougs, comparativo_mensal)
                if len(resultado) > 4:
                    extras = resultado[4:]
                    dados_processados['dados_padronizados']['extras'] = extras
                
                # Calcula totais se possível
                dados_processados['totais'] = self._calcular_totais_relatorio(dados_numericos)
                
            else:
                # Resultado não segue padrão - trata como dados diretos
                dados_processados['dados_padronizados'] = {
                    'dados_numericos': resultado if isinstance(resultado, list) else [],
                    'dados_brutos': resultado
                }
        
        except Exception as e:
            print(f"      ⚠️ Erro ao processar resultado de {codigo}: {str(e)}")
            dados_processados['erro_processamento'] = str(e)
        
        return dados_processados
    
    def _calcular_totais_relatorio(self, dados_numericos: List[Dict]) -> Dict[str, float]:
        """
        Calcula totais de um relatório baseado nos dados numéricos
        
        Args:
            dados_numericos: Lista de dados do relatório
            
        Returns:
            Dicionário com totais calculados
        """
        totais = {
            'total_2024': 0,
            'total_2025': 0,
            'variacao_absoluta': 0,
            'variacao_percentual': 0,
            'count_linhas': 0
        }
        
        if not dados_numericos or not isinstance(dados_numericos, list):
            return totais
        
        try:
            # Procura linha de total ou calcula dos dados principais
            linha_total = None
            linhas_principais = []
            
            for linha in dados_numericos:
                if isinstance(linha, dict):
                    tipo = linha.get('tipo', '')
                    if tipo == 'total':
                        linha_total = linha
                        break
                    elif tipo in ['especie', 'origem', 'principal']:
                        linhas_principais.append(linha)
            
            # Usa linha total se existir, senão calcula das principais
            if linha_total:
                totais['total_2024'] = linha_total.get('receita_2024', 0) or 0
                totais['total_2025'] = linha_total.get('receita_2025', 0) or 0
            elif linhas_principais:
                totais['total_2024'] = sum(l.get('receita_2024', 0) or 0 for l in linhas_principais)
                totais['total_2025'] = sum(l.get('receita_2025', 0) or 0 for l in linhas_principais)
            
            # Calcula variações
            if totais['total_2024'] > 0:
                totais['variacao_absoluta'] = totais['total_2025'] - totais['total_2024']
                totais['variacao_percentual'] = (totais['variacao_absoluta'] / totais['total_2024']) * 100
            elif totais['total_2025'] > 0:
                totais['variacao_absoluta'] = totais['total_2025']
                totais['variacao_percentual'] = 100
            
            totais['count_linhas'] = len(dados_numericos)
            
        except Exception as e:
            print(f"      ⚠️ Erro ao calcular totais: {str(e)}")
        
        return totais
    
    def _armazenar_por_categoria(self, codigo: str, dados: Dict, categoria: str):
        """
        Armazena dados na estrutura consolidada baseado na categoria
        
        Args:
            codigo: Código do relatório
            dados: Dados processados
            categoria: Categoria do relatório
        """
        if categoria == 'correntes':
            # Mapeia para subcategorias de receitas correntes
            if 'tributarias' in codigo:
                self.dados_consolidados['receitas_correntes']['tributarias'] = dados
            elif 'contribuicoes' in codigo:
                self.dados_consolidados['receitas_correntes']['contribuicoes'] = dados
            elif 'patrimoniais' in codigo:
                self.dados_consolidados['receitas_correntes']['patrimoniais'] = dados
            elif 'servicos' in codigo:
                self.dados_consolidados['receitas_correntes']['servicos'] = dados
            elif 'transferencias' in codigo:
                self.dados_consolidados['receitas_correntes']['transferencias'] = dados
            elif 'outras' in codigo:
                self.dados_consolidados['receitas_correntes']['outras'] = dados
        
        elif categoria == 'capital':
            # Mapeia para subcategorias de receitas de capital
            if 'operacoes' in codigo:
                self.dados_consolidados['receitas_capital']['operacoes_credito'] = dados
            elif 'alienacao' in codigo:
                self.dados_consolidados['receitas_capital']['alienacao_bens'] = dados
            elif 'amortizacao' in codigo:
                self.dados_consolidados['receitas_capital']['amortizacao'] = dados
            elif 'transferencias_capital' in codigo:
                self.dados_consolidados['receitas_capital']['transferencias_capital'] = dados
        
        elif categoria == 'analises':
            if 'inconsistencias' in codigo:
                self.dados_consolidados['analises_especiais']['inconsistencias'] = dados
        
        elif categoria == 'graficos':
            if 'correntes' in codigo:
                self.dados_consolidados['graficos']['receitas_correntes'] = dados
            elif 'capital' in codigo:
                self.dados_consolidados['graficos']['receitas_capital'] = dados
        
        # Sempre armazena também nos relatórios executados
        self.dados_consolidados['relatorios_executados'][codigo] = dados
    
    def _consolidar_dados_gerais(self):
        """Consolida dados gerais de todos os relatórios"""
        
        print("📊 Consolidando dados gerais...")
        
        # Consolida totais por categoria
        totais_correntes = self._consolidar_categoria('receitas_correntes')
        totais_capital = self._consolidar_categoria('receitas_capital')
        
        # Atualiza metadados
        self.dados_consolidados['metadados']['totais_consolidados'] = {
            'receitas_correntes': totais_correntes,
            'receitas_capital': totais_capital,
            'total_geral_2024': totais_correntes.get('total_2024', 0) + totais_capital.get('total_2024', 0),
            'total_geral_2025': totais_correntes.get('total_2025', 0) + totais_capital.get('total_2025', 0)
        }
        
        # Consolida estatísticas de execução
        self._consolidar_estatisticas_execucao()
    
    def _consolidar_categoria(self, categoria: str) -> Dict[str, float]:
        """
        Consolida totais de uma categoria específica
        
        Args:
            categoria: Nome da categoria
            
        Returns:
            Dicionário com totais consolidados
        """
        totais = {'total_2024': 0, 'total_2025': 0, 'count_relatorios': 0}
        
        categoria_dados = self.dados_consolidados.get(categoria, {})
        
        for subcategoria, dados in categoria_dados.items():
            if isinstance(dados, dict) and 'totais' in dados:
                totais_sub = dados['totais']
                totais['total_2024'] += totais_sub.get('total_2024', 0)
                totais['total_2025'] += totais_sub.get('total_2025', 0)
                totais['count_relatorios'] += 1
        
        # Calcula variação
        if totais['total_2024'] > 0:
            totais['variacao_absoluta'] = totais['total_2025'] - totais['total_2024']
            totais['variacao_percentual'] = (totais['variacao_absoluta'] / totais['total_2024']) * 100
        
        return totais
    
    def _consolidar_estatisticas_execucao(self):
        """Consolida estatísticas de execução dos relatórios"""
        
        stats = self.dados_consolidados['estatisticas_execucao']
        
        bem_sucedidos = sum(1 for r in self.relatorios_executados.values() if r['status'] == 'sucesso')
        com_erro = sum(1 for r in self.relatorios_executados.values() if r['status'] == 'erro')
        tempo_total = sum(r['tempo_execucao'] for r in self.relatorios_executados.values())
        
        stats.update({
            'relatorios_bem_sucedidos': bem_sucedidos,
            'relatorios_com_erro': com_erro,
            'tempo_total': tempo_total,
            'taxa_sucesso': (bem_sucedidos / len(RELATORIOS_MAPEAMENTO)) * 100 if RELATORIOS_MAPEAMENTO else 0
        })
    
    def _gerar_resumo_executivo(self):
        """Gera resumo executivo com KPIs principais"""
        
        print("📈 Gerando resumo executivo...")
        
        totais = self.dados_consolidados['metadados'].get('totais_consolidados', {})
        
        total_2024 = totais.get('total_geral_2024', 0)
        total_2025 = totais.get('total_geral_2025', 0)
        variacao_perc = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else 0
        
        # Identifica maior receita e maior crescimento
        maior_receita, crescimento_destaque = self._identificar_destaques()
        
        self.dados_consolidados['resumo_executivo'].update({
            'receita_total_2025': total_2025,
            'receita_total_2024': total_2024,
            'variacao_percentual': variacao_perc,
            'maior_receita': maior_receita,
            'crescimento_destaque': crescimento_destaque,
            'principais_kpis': {
                'total_relatorios_gerados': len(self.relatorios_executados),
                'tempo_total_geracao': self.tempo_total_execucao,
                'relatorios_com_dados': sum(1 for r in self.relatorios_executados.values() 
                                          if r['status'] == 'sucesso' and r.get('dados', {}).get('totais', {}).get('total_2025', 0) > 0)
            }
        })
    
    def _identificar_destaques(self) -> Tuple[str, str]:
        """
        Identifica maior receita e maior crescimento
        
        Returns:
            Tupla com (maior_receita, crescimento_destaque)
        """
        maior_receita = "Não identificada"
        crescimento_destaque = "Não identificado"
        
        maior_valor = 0
        maior_crescimento = 0
        
        try:
            # Analisa receitas correntes
            for nome, dados in self.dados_consolidados['receitas_correntes'].items():
                if isinstance(dados, dict) and 'totais' in dados:
                    totais = dados['totais']
                    valor_2025 = totais.get('total_2025', 0)
                    variacao_perc = totais.get('variacao_percentual', 0)
                    
                    if valor_2025 > maior_valor:
                        maior_valor = valor_2025
                        maior_receita = nome.title()
                    
                    if variacao_perc > maior_crescimento:
                        maior_crescimento = variacao_perc
                        crescimento_destaque = nome.title()
            
            # Analisa receitas de capital
            for nome, dados in self.dados_consolidados['receitas_capital'].items():
                if isinstance(dados, dict) and 'totais' in dados:
                    totais = dados['totais']
                    valor_2025 = totais.get('total_2025', 0)
                    variacao_perc = totais.get('variacao_percentual', 0)
                    
                    if valor_2025 > maior_valor:
                        maior_valor = valor_2025
                        maior_receita = nome.replace('_', ' ').title()
                    
                    if variacao_perc > maior_crescimento:
                        maior_crescimento = variacao_perc
                        crescimento_destaque = nome.replace('_', ' ').title()
        
        except Exception as e:
            print(f"⚠️ Erro ao identificar destaques: {str(e)}")
        
        return maior_receita, crescimento_destaque
    
    def obter_status_consolidacao(self) -> Dict[str, Any]:
        """
        Retorna status atual da consolidação
        
        Returns:
            Dicionário com status detalhado
        """
        return {
            'relatorios_mapeados': len(RELATORIOS_MAPEAMENTO),
            'relatorios_executados': len(self.relatorios_executados),
            'relatorios_com_sucesso': sum(1 for r in self.relatorios_executados.values() if r['status'] == 'sucesso'),
            'relatorios_com_erro': len(self.erros_encontrados),
            'tempo_total': self.tempo_total_execucao,
            'dados_consolidados_gerados': bool(self.dados_consolidados),
            'estrutura_completa': all(key in self.dados_consolidados for key in 
                                    ['metadados', 'resumo_executivo', 'receitas_correntes', 'receitas_capital'])
        }


# Função auxiliar para facilitar uso direto
def gerar_relatorio_consolidado_completo(df_receita: pd.DataFrame, mes_referencia: str = None,
                                       estrutura_hierarquica: Dict = None, noug_selecionada: str = None) -> Dict[str, Any]:
    """
    Função auxiliar para gerar relatório consolidado completo
    
    Args:
        df_receita: DataFrame com dados de receita
        mes_referencia: Mês de referência (se None, será calculado automaticamente)
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG para filtro (opcional)
        
    Returns:
        Dados consolidados completos
    """
    # Calcula mês de referência se não fornecido
    if not mes_referencia:
        if 'INMES' in df_receita.columns:
            max_mes = df_receita['INMES'].max()
            mes_referencia = f"{max_mes:02d}/2025"
        else:
            mes_referencia = "05/2025"
    
    # Cria instância do consolidador
    consolidador = RelatorioConsolidado(
        df_receita=df_receita,
        mes_referencia=mes_referencia,
        estrutura_hierarquica=estrutura_hierarquica,
        noug_selecionada=noug_selecionada
    )
    
    # Gera relatório completo
    dados_consolidados = consolidador.gerar_relatorio_completo()
    
    return dados_consolidados