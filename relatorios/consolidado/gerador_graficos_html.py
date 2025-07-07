"""
Gerador de Gráficos HTML/CSS - SEM MATPLOTLIB
Gera gráficos usando apenas HTML, CSS e JavaScript

CRIAR ESTE ARQUIVO EM: relatorios/consolidado/gerador_graficos_html.py
"""

import os
import json
from datetime import datetime

class GeradorGraficosHTML:
    """
    Classe para gerar gráficos usando HTML/CSS (sem matplotlib)
    """
    
    def __init__(self, dados_consolidados):
        """
        Inicializa o gerador de gráficos HTML
        
        Args:
            dados_consolidados: Dados vindos da Fase 1 (RelatorioConsolidado)
        """
        self.dados = dados_consolidados
        self.cores_gdf = {
            'azul_principal': '#1f4e79',
            'azul_claro': '#5b9bd5',
            'cinza_escuro': '#404040',
            'cinza_claro': '#d9d9d9',
            'verde_positivo': '#70ad47',
            'vermelho_negativo': '#c5504b',
            'laranja_alerta': '#ffc000'
        }
        
        print(f"🎨 GeradorGraficosHTML inicializado (sem matplotlib)")
    
    def gerar_todos_graficos(self):
        """
        Gera todos os gráficos em formato HTML
        
        Returns:
            dict: Dicionário com HTML dos gráficos gerados
        """
        print("📊 Gerando gráficos HTML...")
        
        graficos_html = {}
        
        try:
            # Gráfico 1: Dashboard Principal
            print("   🎯 Gerando dashboard principal...")
            graficos_html['dashboard'] = self.gerar_dashboard_principal()
            
            # Gráfico 2: Receitas Correntes
            print("   📈 Gerando gráfico de receitas correntes...")
            graficos_html['receitas_correntes'] = self.gerar_grafico_receitas_correntes()
            
            # Gráfico 3: Receitas de Capital
            print("   📊 Gerando gráfico de receitas de capital...")
            graficos_html['receitas_capital'] = self.gerar_grafico_receitas_capital()
            
            # Gráfico 4: Evolução Mensal
            print("   📉 Gerando gráfico de evolução mensal...")
            graficos_html['evolucao_mensal'] = self.gerar_grafico_evolucao_mensal()
            
            print("✅ Todos os gráficos HTML gerados com sucesso!")
            return graficos_html
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos HTML: {e}")
            return {}
    
    def gerar_dashboard_principal(self):
        """
        Gera o dashboard principal em HTML
        
        Returns:
            str: HTML do dashboard principal
        """
        try:
            # Extrair KPIs
            kpis = self._extrair_kpis_principais()
            
            html = f"""
            <div class="dashboard-html">
                <h3 style="text-align: center; color: {self.cores_gdf['azul_principal']}; margin-bottom: 30px;">
                    Dashboard Executivo
                </h3>
                
                <div class="kpis-grid-html">
                    <div class="kpi-card-html" style="background: {self.cores_gdf['azul_principal']};">
                        <div class="kpi-titulo">Receita Total 2025</div>
                        <div class="kpi-valor">R$ {self._formatar_valor(kpis.get('receita_total_2025', 0))}</div>
                    </div>
                    
                    <div class="kpi-card-html" style="background: {self.cores_gdf['azul_claro']};">
                        <div class="kpi-titulo">Receita Total 2024</div>
                        <div class="kpi-valor">R$ {self._formatar_valor(kpis.get('receita_total_2024', 0))}</div>
                    </div>
                    
                    <div class="kpi-card-html" style="background: {self.cores_gdf['verde_positivo'] if kpis.get('variacao_percentual', 0) >= 0 else self.cores_gdf['vermelho_negativo']};">
                        <div class="kpi-titulo">Variação</div>
                        <div class="kpi-valor">{kpis.get('variacao_percentual', '0%')}</div>
                    </div>
                    
                    <div class="kpi-card-html" style="background: {self.cores_gdf['laranja_alerta']};">
                        <div class="kpi-titulo">Maior Categoria</div>
                        <div class="kpi-valor">{kpis.get('maior_categoria', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="grafico-barras-html">
                    {self._gerar_grafico_barras_comparativo()}
                </div>
            </div>
            
            <style>
                .dashboard-html {{ margin: 20px 0; }}
                .kpis-grid-html {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 30px; 
                }}
                .kpi-card-html {{ 
                    color: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                }}
                .kpi-card-html .kpi-titulo {{ 
                    font-size: 0.9em; 
                    opacity: 0.9; 
                    margin-bottom: 10px; 
                    font-weight: bold; 
                }}
                .kpi-card-html .kpi-valor {{ 
                    font-size: 1.5em; 
                    font-weight: bold; 
                }}
                .grafico-barras-html {{ 
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    border: 1px solid #ddd; 
                }}
            </style>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Erro ao gerar dashboard HTML: {e}")
            return "<div>Erro ao gerar dashboard</div>"
    
    def gerar_grafico_receitas_correntes(self):
        """
        Gera gráfico de receitas correntes em HTML
        
        Returns:
            str: HTML do gráfico de receitas correntes
        """
        try:
            # Extrair dados
            dados_receitas = self._extrair_dados_receitas_correntes()
            
            if not dados_receitas:
                return "<div>Nenhum dado de receitas correntes encontrado</div>"
            
            # Calcular percentuais
            total = sum(item['valor'] for item in dados_receitas.values())
            
            html_items = []
            cores = [
                self.cores_gdf['azul_principal'],
                self.cores_gdf['azul_claro'],
                self.cores_gdf['verde_positivo'],
                self.cores_gdf['laranja_alerta'],
                self.cores_gdf['cinza_escuro'],
                self.cores_gdf['cinza_claro']
            ]
            
            for i, (codigo, item) in enumerate(dados_receitas.items()):
                percentual = (item['valor'] / total * 100) if total > 0 else 0
                cor = cores[i % len(cores)]
                
                html_items.append(f"""
                    <div class="pizza-item">
                        <div class="pizza-cor" style="background: {cor};"></div>
                        <div class="pizza-info">
                            <div class="pizza-label">{item['nome']}</div>
                            <div class="pizza-valor">R$ {self._formatar_valor(item['valor'])} ({percentual:.1f}%)</div>
                        </div>
                    </div>
                """)
            
            html = f"""
            <div class="receitas-correntes-html">
                <h3 style="text-align: center; color: {self.cores_gdf['azul_principal']}; margin-bottom: 20px;">
                    Receitas Correntes por Categoria
                </h3>
                
                <div class="pizza-legenda">
                    {''.join(html_items)}
                </div>
            </div>
            
            <style>
                .receitas-correntes-html {{ margin: 20px 0; }}
                .pizza-legenda {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 15px; 
                }}
                .pizza-item {{ 
                    display: flex; 
                    align-items: center; 
                    gap: 10px; 
                    padding: 10px; 
                    background: #f8f9fa; 
                    border-radius: 5px; 
                }}
                .pizza-cor {{ 
                    width: 20px; 
                    height: 20px; 
                    border-radius: 50%; 
                }}
                .pizza-info {{ flex: 1; }}
                .pizza-label {{ 
                    font-weight: bold; 
                    font-size: 0.9em; 
                    color: {self.cores_gdf['azul_principal']}; 
                }}
                .pizza-valor {{ 
                    font-size: 0.8em; 
                    color: {self.cores_gdf['cinza_escuro']}; 
                }}
            </style>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico receitas correntes HTML: {e}")
            return "<div>Erro ao gerar gráfico de receitas correntes</div>"
    
    def gerar_grafico_receitas_capital(self):
        """
        Gera gráfico de receitas de capital em HTML
        
        Returns:
            str: HTML do gráfico de receitas de capital
        """
        try:
            # Extrair dados
            dados_receitas = self._extrair_dados_receitas_capital()
            
            if not dados_receitas:
                return "<div>Nenhum dado de receitas de capital encontrado</div>"
            
            # Gerar barras
            html_barras = []
            max_valor = max(max(item['valor_2025'], item['valor_2024']) for item in dados_receitas.values())
            
            for codigo, item in dados_receitas.items():
                percentual_2025 = (item['valor_2025'] / max_valor * 100) if max_valor > 0 else 0
                percentual_2024 = (item['valor_2024'] / max_valor * 100) if max_valor > 0 else 0
                
                html_barras.append(f"""
                    <div class="barra-item">
                        <div class="barra-label">{item['nome']}</div>
                        <div class="barras-container">
                            <div class="barra-row">
                                <span class="barra-ano">2025</span>
                                <div class="barra-bg">
                                    <div class="barra-fill" style="width: {percentual_2025}%; background: {self.cores_gdf['azul_principal']};"></div>
                                </div>
                                <span class="barra-valor">R$ {self._formatar_valor(item['valor_2025'])}</span>
                            </div>
                            <div class="barra-row">
                                <span class="barra-ano">2024</span>
                                <div class="barra-bg">
                                    <div class="barra-fill" style="width: {percentual_2024}%; background: {self.cores_gdf['azul_claro']};"></div>
                                </div>
                                <span class="barra-valor">R$ {self._formatar_valor(item['valor_2024'])}</span>
                            </div>
                        </div>
                    </div>
                """)
            
            html = f"""
            <div class="receitas-capital-html">
                <h3 style="text-align: center; color: {self.cores_gdf['azul_principal']}; margin-bottom: 20px;">
                    Receitas de Capital - Comparativo 2024 vs 2025
                </h3>
                
                <div class="barras-lista">
                    {''.join(html_barras)}
                </div>
            </div>
            
            <style>
                .receitas-capital-html {{ margin: 20px 0; }}
                .barras-lista {{ display: flex; flex-direction: column; gap: 20px; }}
                .barra-item {{ 
                    background: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    border: 1px solid #ddd; 
                }}
                .barra-label {{ 
                    font-weight: bold; 
                    color: {self.cores_gdf['azul_principal']}; 
                    margin-bottom: 10px; 
                }}
                .barras-container {{ display: flex; flex-direction: column; gap: 8px; }}
                .barra-row {{ 
                    display: grid; 
                    grid-template-columns: 50px 1fr 120px; 
                    gap: 10px; 
                    align-items: center; 
                }}
                .barra-ano {{ 
                    font-size: 0.9em; 
                    font-weight: bold; 
                    color: {self.cores_gdf['cinza_escuro']}; 
                }}
                .barra-bg {{ 
                    height: 20px; 
                    background: #f0f0f0; 
                    border-radius: 10px; 
                    overflow: hidden; 
                }}
                .barra-fill {{ 
                    height: 100%; 
                    transition: width 0.3s ease; 
                }}
                .barra-valor {{ 
                    font-size: 0.8em; 
                    color: {self.cores_gdf['cinza_escuro']}; 
                    text-align: right; 
                }}
            </style>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico receitas capital HTML: {e}")
            return "<div>Erro ao gerar gráfico de receitas de capital</div>"
    
    def gerar_grafico_evolucao_mensal(self):
        """
        Gera gráfico de evolução mensal em HTML
        
        Returns:
            str: HTML do gráfico de evolução mensal
        """
        try:
            # Dados simulados de evolução mensal
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            # Simular crescimento acumulado
            total_2024 = sum(self._extrair_valor_total_relatorio(rel['dados'], 2024) or 0 
                           for rel in self.dados.values() 
                           if rel.get('status') == 'sucesso' and rel.get('dados'))
            
            total_2025 = sum(self._extrair_valor_total_relatorio(rel['dados'], 2025) or 0 
                           for rel in self.dados.values() 
                           if rel.get('status') == 'sucesso' and rel.get('dados'))
            
            # Distribuir proporcionalmente
            pontos_2024 = []
            pontos_2025 = []
            
            for i in range(12):
                valor_2024 = total_2024 * (i + 1) / 12
                valor_2025 = total_2025 * (i + 1) / 12
                pontos_2024.append(valor_2024)
                pontos_2025.append(valor_2025)
            
            # Normalizar para percentuais
            max_valor = max(max(pontos_2024), max(pontos_2025))
            
            html_pontos = []
            for i in range(12):
                perc_2024 = (pontos_2024[i] / max_valor * 100) if max_valor > 0 else 0
                perc_2025 = (pontos_2025[i] / max_valor * 100) if max_valor > 0 else 0
                
                html_pontos.append(f"""
                    <div class="linha-mes">
                        <div class="mes-label">{meses[i]}</div>
                        <div class="linha-container">
                            <div class="linha-ponto" style="bottom: {perc_2024}%; background: {self.cores_gdf['azul_claro']};" title="2024: R$ {self._formatar_valor(pontos_2024[i])}"></div>
                            <div class="linha-ponto" style="bottom: {perc_2025}%; background: {self.cores_gdf['azul_principal']};" title="2025: R$ {self._formatar_valor(pontos_2025[i])}"></div>
                        </div>
                    </div>
                """)
            
            html = f"""
            <div class="evolucao-mensal-html">
                <h3 style="text-align: center; color: {self.cores_gdf['azul_principal']}; margin-bottom: 20px;">
                    Evolução Mensal - 2024 vs 2025
                </h3>
                
                <div class="linha-grafico">
                    {''.join(html_pontos)}
                </div>
                
                <div class="linha-legenda">
                    <div class="legenda-item">
                        <div class="legenda-cor" style="background: {self.cores_gdf['azul_claro']};"></div>
                        <span>2024</span>
                    </div>
                    <div class="legenda-item">
                        <div class="legenda-cor" style="background: {self.cores_gdf['azul_principal']};"></div>
                        <span>2025</span>
                    </div>
                </div>
            </div>
            
            <style>
                .evolucao-mensal-html {{ margin: 20px 0; }}
                .linha-grafico {{ 
                    display: flex; 
                    justify-content: space-between; 
                    height: 200px; 
                    background: white; 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    padding: 20px; 
                    margin-bottom: 20px; 
                    position: relative; 
                }}
                .linha-mes {{ 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    flex: 1; 
                }}
                .mes-label {{ 
                    font-size: 0.8em; 
                    color: {self.cores_gdf['cinza_escuro']}; 
                    margin-bottom: 10px; 
                }}
                .linha-container {{ 
                    position: relative; 
                    height: 150px; 
                    width: 100%; 
                }}
                .linha-ponto {{ 
                    position: absolute; 
                    width: 8px; 
                    height: 8px; 
                    border-radius: 50%; 
                    left: 50%; 
                    transform: translateX(-50%); 
                    cursor: pointer; 
                }}
                .linha-legenda {{ 
                    display: flex; 
                    justify-content: center; 
                    gap: 20px; 
                }}
                .legenda-item {{ 
                    display: flex; 
                    align-items: center; 
                    gap: 5px; 
                }}
                .legenda-cor {{ 
                    width: 12px; 
                    height: 12px; 
                    border-radius: 50%; 
                }}
            </style>
            """
            
            return html
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico evolução mensal HTML: {e}")
            return "<div>Erro ao gerar gráfico de evolução mensal</div>"
    
    def _gerar_grafico_barras_comparativo(self):
        """Gera gráfico de barras comparativo simples"""
        try:
            # Dados simplificados
            dados_comparacao = self._extrair_dados_comparacao()
            
            if not dados_comparacao:
                return "<div>Sem dados para comparação</div>"
            
            html_barras = []
            max_valor = max(max(item['valor_2025'], item['valor_2024']) for item in dados_comparacao.values())
            
            for categoria, item in dados_comparacao.items():
                perc_2025 = (item['valor_2025'] / max_valor * 100) if max_valor > 0 else 0
                perc_2024 = (item['valor_2024'] / max_valor * 100) if max_valor > 0 else 0
                
                html_barras.append(f"""
                    <div class="comp-item">
                        <div class="comp-label">{item['nome']}</div>
                        <div class="comp-barras">
                            <div class="comp-barra" style="width: {perc_2025}%; background: {self.cores_gdf['azul_principal']};" title="2025: R$ {self._formatar_valor(item['valor_2025'])}"></div>
                            <div class="comp-barra" style="width: {perc_2024}%; background: {self.cores_gdf['azul_claro']};" title="2024: R$ {self._formatar_valor(item['valor_2024'])}"></div>
                        </div>
                    </div>
                """)
            
            return f"""
            <div class="comparativo-barras">
                <h4 style="color: {self.cores_gdf['azul_principal']}; margin-bottom: 15px;">Comparativo por Categoria</h4>
                {''.join(html_barras)}
            </div>
            
            <style>
                .comparativo-barras {{ margin: 20px 0; }}
                .comp-item {{ margin-bottom: 15px; }}
                .comp-label {{ 
                    font-weight: bold; 
                    color: {self.cores_gdf['azul_principal']}; 
                    margin-bottom: 5px; 
                }}
                .comp-barras {{ 
                    display: flex; 
                    flex-direction: column; 
                    gap: 3px; 
                }}
                .comp-barra {{ 
                    height: 20px; 
                    border-radius: 10px; 
                    cursor: pointer; 
                    transition: opacity 0.3s ease; 
                }}
                .comp-barra:hover {{ opacity: 0.8; }}
            </style>
            """
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico comparativo: {e}")
            return "<div>Erro no gráfico comparativo</div>"
    
    # Métodos auxiliares (copiados do gerador original)
    def _extrair_kpis_principais(self):
        """Extrai KPIs principais"""
        try:
            kpis = {
                'receita_total_2025': 0,
                'receita_total_2024': 0,
                'variacao_percentual': '0%',
                'maior_categoria': 'N/A'
            }
            
            for codigo, relatorio in self.dados.items():
                if relatorio.get('status') == 'sucesso' and relatorio.get('dados'):
                    valor_2025 = self._extrair_valor_total_relatorio(relatorio['dados'], 2025)
                    valor_2024 = self._extrair_valor_total_relatorio(relatorio['dados'], 2024)
                    
                    kpis['receita_total_2025'] += valor_2025 or 0
                    kpis['receita_total_2024'] += valor_2024 or 0
            
            if kpis['receita_total_2024'] > 0:
                variacao = ((kpis['receita_total_2025'] - kpis['receita_total_2024']) / kpis['receita_total_2024']) * 100
                kpis['variacao_percentual'] = f"{variacao:+.1f}%"
            
            return kpis
            
        except Exception as e:
            print(f"❌ Erro ao extrair KPIs: {e}")
            return {'receita_total_2025': 0, 'receita_total_2024': 0, 'variacao_percentual': '0%', 'maior_categoria': 'N/A'}
    
    def _extrair_dados_receitas_correntes(self):
        """Extrai dados das receitas correntes"""
        dados_receitas = {}
        
        try:
            mapeamento = {
                'tributarias': 'Tributárias',
                'contribuicoes': 'Contribuições',
                'patrimoniais': 'Patrimoniais',
                'servicos': 'Serviços',
                'transferencias': 'Transferências',
                'outras_correntes': 'Outras Correntes'
            }
            
            for codigo, relatorio in self.dados.items():
                if (relatorio.get('categoria') == 'correntes' and 
                    relatorio.get('status') == 'sucesso' and 
                    relatorio.get('dados')):
                    
                    valor_total = self._extrair_valor_total_relatorio(relatorio['dados'])
                    
                    if valor_total and valor_total > 0:
                        nome_categoria = mapeamento.get(codigo, codigo.title())
                        dados_receitas[codigo] = {
                            'nome': nome_categoria,
                            'valor': valor_total
                        }
            
            return dados_receitas
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados receitas correntes: {e}")
            return {}
    
    def _extrair_dados_receitas_capital(self):
        """Extrai dados das receitas de capital"""
        dados_receitas = {}
        
        try:
            mapeamento = {
                'operacoes_credito': 'Operações de Crédito',
                'alienacao_bens': 'Alienação de Bens',
                'amortizacao': 'Amortização de Empréstimos',
                'transferencias_capital': 'Transferências de Capital'
            }
            
            for codigo, relatorio in self.dados.items():
                if (relatorio.get('categoria') == 'capital' and 
                    relatorio.get('status') == 'sucesso' and 
                    relatorio.get('dados')):
                    
                    valor_2025 = self._extrair_valor_total_relatorio(relatorio['dados'], 2025)
                    valor_2024 = self._extrair_valor_total_relatorio(relatorio['dados'], 2024)
                    
                    if valor_2025 or valor_2024:
                        nome_categoria = mapeamento.get(codigo, codigo.title())
                        dados_receitas[codigo] = {
                            'nome': nome_categoria,
                            'valor_2025': valor_2025 or 0,
                            'valor_2024': valor_2024 or 0
                        }
            
            return dados_receitas
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados receitas capital: {e}")
            return {}
    
    def _extrair_dados_comparacao(self):
        """Extrai dados para comparação"""
        try:
            dados = {}
            
            for categoria in ['correntes', 'capital']:
                valor_2025 = 0
                valor_2024 = 0
                
                for codigo, relatorio in self.dados.items():
                    if (relatorio.get('categoria') == categoria and 
                        relatorio.get('status') == 'sucesso' and 
                        relatorio.get('dados')):
                        
                        valor_2025 += self._extrair_valor_total_relatorio(relatorio['dados'], 2025) or 0
                        valor_2024 += self._extrair_valor_total_relatorio(relatorio['dados'], 2024) or 0
                
                if valor_2025 > 0 or valor_2024 > 0:
                    dados[categoria] = {
                        'nome': 'Receitas Correntes' if categoria == 'correntes' else 'Receitas de Capital',
                        'valor_2025': valor_2025,
                        'valor_2024': valor_2024
                    }
            
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados comparação: {e}")
            return {}
    
    def _extrair_valor_total_relatorio(self, dados_relatorio, ano=2025):
        """Extrai valor total de um relatório"""
        try:
            campo_ano = f'receita_{ano}'
            
            if isinstance(dados_relatorio, dict):
                dados_numericos = dados_relatorio.get('dados_numericos', [])
                
                for linha in dados_numericos:
                    if isinstance(linha, dict) and linha.get('tipo') == 'total':
                        return linha.get(campo_ano, 0) or 0
            
            elif isinstance(dados_relatorio, (list, tuple)) and len(dados_relatorio) >= 1:
                dados_numericos = dados_relatorio[0] if dados_relatorio[0] else []
                
                for linha in dados_numericos:
                    if isinstance(linha, dict) and linha.get('tipo') == 'total':
                        return linha.get(campo_ano, 0) or 0
            
            return 0
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair valor total: {e}")
            return 0
    
    def _formatar_valor(self, valor):
        """Formata valor em milhões"""
        if valor >= 1000000:
            return f"{valor/1000000:.1f}M"
        elif valor >= 1000:
            return f"{valor/1000:.1f}K"
        else:
            return f"{valor:.2f}"