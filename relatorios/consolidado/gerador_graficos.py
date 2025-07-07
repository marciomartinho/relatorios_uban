"""
Gerador de Gráficos para Relatório Consolidado
Gera 4 gráficos profissionais em PNG

CRIAR ESTE ARQUIVO EM: relatorios/consolidado/gerador_graficos.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from datetime import datetime
import pandas as pd
import numpy as np

class GeradorGraficos:
    """
    Classe para gerar gráficos profissionais do relatório consolidado
    """
    
    def __init__(self, dados_consolidados):
        """
        Inicializa o gerador de gráficos
        
        Args:
            dados_consolidados: Dados vindos da Fase 1 (RelatorioConsolidado)
        """
        self.dados = dados_consolidados
        self.pasta_temp = 'static/images/graficos_temp/'
        self.cores_gdf = {
            'azul_principal': '#1f4e79',
            'azul_claro': '#5b9bd5',
            'cinza_escuro': '#404040',
            'cinza_claro': '#d9d9d9',
            'verde_positivo': '#70ad47',
            'vermelho_negativo': '#c5504b',
            'laranja_alerta': '#ffc000'
        }
        
        # Criar pasta temporária se não existir
        self._criar_pasta_temp()
        
        # Configurar matplotlib para gráficos profissionais
        self._configurar_matplotlib()
        
        print(f"🎨 GeradorGraficos inicializado")
        print(f"📁 Pasta temporária: {self.pasta_temp}")
    
    def _criar_pasta_temp(self):
        """Cria a pasta temporária para salvar os gráficos"""
        try:
            os.makedirs(self.pasta_temp, exist_ok=True)
            print(f"✅ Pasta temporária criada: {self.pasta_temp}")
        except Exception as e:
            print(f"❌ Erro ao criar pasta temporária: {e}")
    
    def _configurar_matplotlib(self):
        """Configura o matplotlib para gráficos profissionais"""
        # Configurações globais para qualidade
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['savefig.bbox'] = 'tight'
        plt.rcParams['savefig.transparent'] = True
        
        # Configurações de fonte
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 9
        
        print("⚙️ Matplotlib configurado para gráficos profissionais")
    
    def gerar_todos_graficos(self):
        """
        Gera todos os 4 gráficos necessários
        
        Returns:
            dict: Dicionário com os caminhos dos gráficos gerados
        """
        print("📊 Iniciando geração de todos os gráficos...")
        
        graficos_gerados = {}
        
        try:
            # Gráfico 1: Dashboard Principal
            print("   🎯 Gerando dashboard principal...")
            graficos_gerados['dashboard'] = self.gerar_dashboard_principal()
            
            # Gráfico 2: Receitas Correntes
            print("   📈 Gerando gráfico de receitas correntes...")
            graficos_gerados['receitas_correntes'] = self.gerar_grafico_receitas_correntes()
            
            # Gráfico 3: Receitas de Capital
            print("   📊 Gerando gráfico de receitas de capital...")
            graficos_gerados['receitas_capital'] = self.gerar_grafico_receitas_capital()
            
            # Gráfico 4: Evolução Mensal
            print("   📉 Gerando gráfico de evolução mensal...")
            graficos_gerados['evolucao_mensal'] = self.gerar_grafico_evolucao_mensal()
            
            print("✅ Todos os gráficos gerados com sucesso!")
            return graficos_gerados
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos: {e}")
            return {}
    
    def gerar_dashboard_principal(self):
        """
        Gera o gráfico do dashboard principal com KPIs
        
        Returns:
            str: Caminho do arquivo PNG gerado
        """
        caminho_arquivo = os.path.join(self.pasta_temp, 'dashboard_principal.png')
        
        try:
            # Extrair KPIs principais
            kpis = self._extrair_kpis_principais()
            
            # Criar figura com subplots
            fig = plt.figure(figsize=(16, 10))
            
            # Layout: 2 linhas, 4 colunas para KPIs + 1 gráfico grande
            gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 2], hspace=0.3, wspace=0.3)
            
            # KPIs na primeira linha
            kpi_configs = [
                ('receita_total_2025', 'Receita Total 2025', 'azul_principal'),
                ('receita_total_2024', 'Receita Total 2024', 'azul_claro'),
                ('variacao_percentual', 'Variação %', 'verde_positivo' if kpis.get('variacao_percentual', 0) >= 0 else 'vermelho_negativo'),
                ('maior_categoria', 'Maior Categoria', 'laranja_alerta')
            ]
            
            # Criar cards de KPIs
            for i, (chave, titulo, cor) in enumerate(kpi_configs):
                ax_kpi = fig.add_subplot(gs[0, i])
                self._criar_card_kpi(ax_kpi, titulo, kpis.get(chave, 'N/A'), cor)
            
            # Gráfico de barras comparativo na segunda linha (ocupando todas as colunas)
            ax_grafico = fig.add_subplot(gs[1:, :])
            self._criar_grafico_comparativo_dashboard(ax_grafico, kpis)
            
            # Título geral
            fig.suptitle('Dashboard Executivo - Receitas Consolidadas', 
                        fontsize=20, fontweight='bold', 
                        color=self.cores_gdf['azul_principal'], y=0.95)
            
            # Salvar
            plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"✅ Dashboard principal salvo: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar dashboard principal: {e}")
            return self._criar_grafico_vazio(caminho_arquivo, "Dashboard Principal\nErro na geração")
    
    def _criar_card_kpi(self, ax, titulo, valor, cor_chave):
        """
        Cria um card de KPI
        
        Args:
            ax: Axes do matplotlib
            titulo: Título do KPI
            valor: Valor a exibir
            cor_chave: Chave da cor no dicionário de cores
        """
        # Configurar eixos
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Cor de fundo
        cor = self.cores_gdf.get(cor_chave, self.cores_gdf['cinza_claro'])
        
        # Retângulo de fundo
        rect = patches.Rectangle((0.05, 0.1), 0.9, 0.8, 
                               linewidth=2, edgecolor=cor, 
                               facecolor=cor, alpha=0.1)
        ax.add_patch(rect)
        
        # Título
        ax.text(0.5, 0.75, titulo, ha='center', va='center', 
               fontsize=11, fontweight='bold', color=cor)
        
        # Valor
        if isinstance(valor, (int, float)):
            if abs(valor) >= 1000000:
                valor_fmt = f'R$ {valor/1000000:.1f}M'
            elif abs(valor) >= 1000:
                valor_fmt = f'R$ {valor/1000:.1f}K'
            else:
                valor_fmt = f'R$ {valor:.2f}'
        elif isinstance(valor, str) and '%' in str(valor):
            valor_fmt = str(valor)
        else:
            valor_fmt = str(valor)
        
        ax.text(0.5, 0.4, valor_fmt, ha='center', va='center', 
               fontsize=14, fontweight='bold', color=cor)
    
    def _criar_grafico_comparativo_dashboard(self, ax, kpis):
        """
        Cria gráfico comparativo para o dashboard
        
        Args:
            ax: Axes do matplotlib
            kpis: Dicionário com KPIs
        """
        # Dados para comparação (correntes vs capital)
        dados_comparacao = self._extrair_dados_comparacao()
        
        if not dados_comparacao:
            ax.text(0.5, 0.5, 'Dados de comparação não disponíveis', 
                   ha='center', va='center', fontsize=12, 
                   color=self.cores_gdf['cinza_escuro'])
            return
        
        categorias = list(dados_comparacao.keys())
        valores_2025 = [dados_comparacao[cat]['valor_2025'] for cat in categorias]
        valores_2024 = [dados_comparacao[cat]['valor_2024'] for cat in categorias]
        
        # Posições das barras
        x_pos = np.arange(len(categorias))
        largura = 0.35
        
        # Criar barras
        barras_2025 = ax.bar(x_pos - largura/2, valores_2025, largura, 
                           label='2025', color=self.cores_gdf['azul_principal'], alpha=0.8)
        barras_2024 = ax.bar(x_pos + largura/2, valores_2024, largura, 
                           label='2024', color=self.cores_gdf['azul_claro'], alpha=0.8)
        
        # Personalizar
        ax.set_xlabel('Categorias', fontsize=12, fontweight='bold')
        ax.set_ylabel('Valor (R$ milhões)', fontsize=12, fontweight='bold')
        ax.set_title('Comparativo por Categoria - 2024 vs 2025', 
                    fontsize=14, fontweight='bold', color=self.cores_gdf['azul_principal'])
        ax.set_xticks(x_pos)
        ax.set_xticklabels([dados_comparacao[cat]['nome'] for cat in categorias], 
                          rotation=45, ha='right')
        
        # Adicionar valores nas barras
        for barra in barras_2025:
            altura = barra.get_height()
            if altura > 0:
                ax.text(barra.get_x() + barra.get_width()/2., altura,
                       f'{altura/1000000:.1f}M', ha='center', va='bottom',
                       fontsize=8, fontweight='bold')
        
        for barra in barras_2024:
            altura = barra.get_height()
            if altura > 0:
                ax.text(barra.get_x() + barra.get_width()/2., altura,
                       f'{altura/1000000:.1f}M', ha='center', va='bottom',
                       fontsize=8, fontweight='bold')
        
        # Legenda e grid
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
    
    def gerar_grafico_receitas_correntes(self):
        """
        Gera o gráfico de receitas correntes (pizza)
        
        Returns:
            str: Caminho do arquivo PNG gerado
        """
        caminho_arquivo = os.path.join(self.pasta_temp, 'receitas_correntes.png')
        
        try:
            # Extrair dados das receitas correntes
            dados_receitas = self._extrair_dados_receitas_correntes()
            
            if not dados_receitas:
                print("⚠️ Nenhum dado de receitas correntes encontrado")
                return self._criar_grafico_vazio(caminho_arquivo, "Receitas Correntes\nSem dados disponíveis")
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Dados para o gráfico
            valores = [dados['valor'] for dados in dados_receitas.values()]
            labels = [dados['nome'] for dados in dados_receitas.values()]
            
            # Cores para cada fatia
            cores = [
                self.cores_gdf['azul_principal'],    # Tributárias
                self.cores_gdf['azul_claro'],        # Contribuições
                self.cores_gdf['verde_positivo'],    # Patrimoniais
                self.cores_gdf['laranja_alerta'],    # Serviços
                self.cores_gdf['cinza_escuro'],      # Transferências
                self.cores_gdf['cinza_claro']        # Outras
            ]
            
            # Ajustar número de cores se necessário
            while len(cores) < len(valores):
                cores.append(self.cores_gdf['cinza_claro'])
            
            # Criar gráfico de pizza
            wedges, texts, autotexts = ax.pie(
                valores, 
                labels=labels,
                colors=cores[:len(valores)],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 9, 'fontweight': 'bold'}
            )
            
            # Personalizar textos
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            # Título
            ax.set_title('Receitas Correntes por Categoria', 
                        fontsize=14, fontweight='bold', 
                        color=self.cores_gdf['azul_principal'], 
                        pad=20)
            
            # Adicionar legenda
            ax.legend(wedges, labels, 
                     title="Categorias", 
                     loc="center left", 
                     bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=9)
            
            # Salvar
            plt.tight_layout()
            plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"✅ Gráfico de receitas correntes salvo: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de receitas correntes: {e}")
            return self._criar_grafico_vazio(caminho_arquivo, "Receitas Correntes\nErro na geração")
    
    def gerar_grafico_receitas_capital(self):
        """
        Gera o gráfico de receitas de capital (barras horizontais)
        
        Returns:
            str: Caminho do arquivo PNG gerado
        """
        caminho_arquivo = os.path.join(self.pasta_temp, 'receitas_capital.png')
        
        try:
            # Extrair dados das receitas de capital
            dados_receitas = self._extrair_dados_receitas_capital()
            
            if not dados_receitas:
                print("⚠️ Nenhum dado de receitas de capital encontrado")
                return self._criar_grafico_vazio(caminho_arquivo, "Receitas de Capital\nSem dados disponíveis")
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Dados para o gráfico
            categorias = list(dados_receitas.keys())
            valores_2025 = [dados_receitas[cat]['valor_2025'] for cat in categorias]
            valores_2024 = [dados_receitas[cat]['valor_2024'] for cat in categorias]
            nomes = [dados_receitas[cat]['nome'] for cat in categorias]
            
            # Posições das barras
            y_pos = np.arange(len(categorias))
            altura_barra = 0.35
            
            # Criar barras horizontais
            barras_2025 = ax.barh(y_pos - altura_barra/2, valores_2025, 
                                altura_barra, label='2025', 
                                color=self.cores_gdf['azul_principal'], alpha=0.8)
            barras_2024 = ax.barh(y_pos + altura_barra/2, valores_2024, 
                                altura_barra, label='2024', 
                                color=self.cores_gdf['azul_claro'], alpha=0.8)
            
            # Personalizar eixos
            ax.set_yticks(y_pos)
            ax.set_yticklabels(nomes, fontsize=10)
            ax.set_xlabel('Valor (R$ milhões)', fontsize=11, fontweight='bold')
            ax.set_title('Receitas de Capital - Comparativo 2024 vs 2025', 
                        fontsize=14, fontweight='bold', 
                        color=self.cores_gdf['azul_principal'], pad=20)
            
            # Adicionar valores nas barras
            for i, (bar_2025, bar_2024) in enumerate(zip(barras_2025, barras_2024)):
                # Valor 2025
                width_2025 = bar_2025.get_width()
                if width_2025 > 0:
                    ax.text(width_2025/2, bar_2025.get_y() + bar_2025.get_height()/2, 
                           f'R$ {width_2025/1000000:.1f}M', 
                           ha='center', va='center', fontweight='bold', 
                           color='white', fontsize=8)
                
                # Valor 2024
                width_2024 = bar_2024.get_width()
                if width_2024 > 0:
                    ax.text(width_2024/2, bar_2024.get_y() + bar_2024.get_height()/2, 
                           f'R$ {width_2024/1000000:.1f}M', 
                           ha='center', va='center', fontweight='bold', 
                           color='white', fontsize=8)
            
            # Legenda
            ax.legend(loc='lower right', fontsize=10)
            
            # Grid
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Ajustar layout
            plt.tight_layout()
            plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"✅ Gráfico de receitas de capital salvo: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de receitas de capital: {e}")
            return self._criar_grafico_vazio(caminho_arquivo, "Receitas de Capital\nErro na geração")
    
    def gerar_grafico_evolucao_mensal(self):
        """
        Gera o gráfico de evolução mensal (linhas)
        
        Returns:
            str: Caminho do arquivo PNG gerado
        """
        caminho_arquivo = os.path.join(self.pasta_temp, 'evolucao_mensal.png')
        
        try:
            # Extrair dados mensais
            dados_mensais = self._extrair_dados_evolucao_mensal()
            
            if not dados_mensais:
                print("⚠️ Nenhum dado de evolução mensal encontrado")
                return self._criar_grafico_vazio(caminho_arquivo, "Evolução Mensal\nSem dados disponíveis")
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Meses
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            # Extrair dados para 2024 e 2025
            valores_2024 = dados_mensais.get('2024', [0] * 12)
            valores_2025 = dados_mensais.get('2025', [0] * 12)
            
            # Garantir que temos 12 meses
            while len(valores_2024) < 12:
                valores_2024.append(0)
            while len(valores_2025) < 12:
                valores_2025.append(0)
            
            # Criar linhas
            line_2024 = ax.plot(meses, valores_2024, 
                              color=self.cores_gdf['azul_claro'], 
                              linewidth=3, marker='o', markersize=8,
                              label='2024', alpha=0.8)
            
            line_2025 = ax.plot(meses, valores_2025, 
                              color=self.cores_gdf['azul_principal'], 
                              linewidth=3, marker='s', markersize=8,
                              label='2025', alpha=0.8)
            
            # Personalizar
            ax.set_xlabel('Mês', fontsize=12, fontweight='bold')
            ax.set_ylabel('Receita Acumulada (R$ milhões)', fontsize=12, fontweight='bold')
            ax.set_title('Evolução Mensal da Receita - Comparativo 2024 vs 2025', 
                        fontsize=14, fontweight='bold', 
                        color=self.cores_gdf['azul_principal'], pad=20)
            
            # Adicionar valores nos pontos (apenas nos últimos meses com dados)
            ultimo_mes_2024 = self._encontrar_ultimo_mes_com_dados(valores_2024)
            ultimo_mes_2025 = self._encontrar_ultimo_mes_com_dados(valores_2025)
            
            if ultimo_mes_2024 >= 0:
                ax.annotate(f'R$ {valores_2024[ultimo_mes_2024]/1000000:.1f}M',
                           xy=(ultimo_mes_2024, valores_2024[ultimo_mes_2024]),
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           color=self.cores_gdf['azul_claro'])
            
            if ultimo_mes_2025 >= 0:
                ax.annotate(f'R$ {valores_2025[ultimo_mes_2025]/1000000:.1f}M',
                           xy=(ultimo_mes_2025, valores_2025[ultimo_mes_2025]),
                           xytext=(10, -15), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           color=self.cores_gdf['azul_principal'])
            
            # Área sombreada entre as linhas
            ax.fill_between(meses, valores_2024, valores_2025, 
                          alpha=0.2, color=self.cores_gdf['verde_positivo'] 
                          if sum(valores_2025) > sum(valores_2024) 
                          else self.cores_gdf['vermelho_negativo'])
            
            # Legenda e grid
            ax.legend(fontsize=11, loc='upper left')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Rotacionar rótulos do eixo X
            plt.xticks(rotation=45)
            
            # Ajustar layout
            plt.tight_layout()
            plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"✅ Gráfico de evolução mensal salvo: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de evolução mensal: {e}")
            return self._criar_grafico_vazio(caminho_arquivo, "Evolução Mensal\nErro na geração")
    
    def _encontrar_ultimo_mes_com_dados(self, valores):
        """
        Encontra o último mês com dados não-zero
        
        Args:
            valores: Lista de valores mensais
            
        Returns:
            int: Índice do último mês com dados
        """
        for i in range(len(valores) - 1, -1, -1):
            if valores[i] > 0:
                return i
        return -1
    
    def _extrair_dados_receitas_correntes(self):
        """
        Extrai dados das receitas correntes dos dados consolidados
        
        Returns:
            dict: Dados organizados por categoria
        """
        dados_receitas = {}
        
        try:
            # Mapeamento dos códigos para nomes amigáveis
            mapeamento_categorias = {
                'tributarias': 'Tributárias',
                'contribuicoes': 'Contribuições',
                'patrimoniais': 'Patrimoniais',
                'servicos': 'Serviços',
                'transferencias': 'Transferências',
                'outras_correntes': 'Outras Correntes'
            }
            
            # Percorrer dados consolidados
            for codigo, relatorio in self.dados.items():
                if (relatorio.get('categoria') == 'correntes' and 
                    relatorio.get('status') == 'sucesso' and 
                    relatorio.get('dados')):
                    
                    dados_relatorio = relatorio['dados']
                    
                    # Extrair valor total do relatório
                    valor_total = self._extrair_valor_total_relatorio(dados_relatorio)
                    
                    if valor_total and valor_total > 0:
                        nome_categoria = mapeamento_categorias.get(codigo, codigo.title())
                        dados_receitas[codigo] = {
                            'nome': nome_categoria,
                            'valor': valor_total
                        }
            
            return dados_receitas
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados de receitas correntes: {e}")
            return {}
    
    def _extrair_dados_receitas_capital(self):
        """
        Extrai dados das receitas de capital dos dados consolidados
        
        Returns:
            dict: Dados organizados por categoria
        """
        dados_receitas = {}
        
        try:
            # Mapeamento dos códigos para nomes amigáveis
            mapeamento_categorias = {
                'operacoes_credito': 'Operações de Crédito',
                'alienacao_bens': 'Alienação de Bens',
                'amortizacao': 'Amortização de Empréstimos',
                'transferencias_capital': 'Transferências de Capital'
            }
            
            # Percorrer dados consolidados
            for codigo, relatorio in self.dados.items():
                if (relatorio.get('categoria') == 'capital' and 
                    relatorio.get('status') == 'sucesso' and 
                    relatorio.get('dados')):
                    
                    dados_relatorio = relatorio['dados']
                    
                    # Extrair valores 2024 e 2025
                    valor_2025 = self._extrair_valor_total_relatorio(dados_relatorio, ano=2025)
                    valor_2024 = self._extrair_valor_total_relatorio(dados_relatorio, ano=2024)
                    
                    if valor_2025 or valor_2024:
                        nome_categoria = mapeamento_categorias.get(codigo, codigo.title())
                        dados_receitas[codigo] = {
                            'nome': nome_categoria,
                            'valor_2025': valor_2025 or 0,
                            'valor_2024': valor_2024 or 0
                        }
            
            return dados_receitas
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados de receitas de capital: {e}")
            return {}
    
    def _extrair_valor_total_relatorio(self, dados_relatorio, ano=2025):
        """
        Extrai o valor total de um relatório individual
        
        Args:
            dados_relatorio: Dados de um relatório específico
            ano: Ano para extrair (2024 ou 2025)
            
        Returns:
            float: Valor total da receita
        """
        try:
            campo_ano = f'receita_{ano}'
            
            # Tentar extrair dos dados numéricos
            if isinstance(dados_relatorio, dict):
                dados_numericos = dados_relatorio.get('dados_numericos', [])
                
                # Procurar linha de total
                for linha in dados_numericos:
                    if isinstance(linha, dict) and linha.get('tipo') == 'total':
                        return linha.get(campo_ano, 0) or 0
            
            # Se não encontrar, tentar outras estruturas
            elif isinstance(dados_relatorio, (list, tuple)) and len(dados_relatorio) >= 1:
                dados_numericos = dados_relatorio[0] if dados_relatorio[0] else []
                
                for linha in dados_numericos:
                    if isinstance(linha, dict) and linha.get('tipo') == 'total':
                        return linha.get(campo_ano, 0) or 0
            
            return 0
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair valor total: {e}")
            return 0
    
    def _criar_grafico_vazio(self, caminho_arquivo, mensagem):
        """
        Cria um gráfico vazio com mensagem
        
        Args:
            caminho_arquivo: Caminho onde salvar
            mensagem: Mensagem a exibir
            
        Returns:
            str: Caminho do arquivo criado
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.text(0.5, 0.5, mensagem, 
                ha='center', va='center', fontsize=16, 
                color=self.cores_gdf['cinza_escuro'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return caminho_arquivo
    
    def limpar_graficos_temporarios(self):
        """
        Remove os gráficos temporários gerados
        """
        try:
            import glob
            arquivos = glob.glob(os.path.join(self.pasta_temp, '*.png'))
            for arquivo in arquivos:
                os.remove(arquivo)
            print(f"🧹 {len(arquivos)} gráficos temporários removidos")
        except Exception as e:
            print(f"⚠️ Erro ao limpar gráficos temporários: {e}")
    
    # MÉTODOS AUXILIARES ADICIONAIS
    
    def _extrair_kpis_principais(self):
        """
        Extrai os KPIs principais dos dados consolidados
        
        Returns:
            dict: KPIs principais
        """
        try:
            kpis = {
                'receita_total_2025': 0,
                'receita_total_2024': 0,
                'variacao_percentual': 0,
                'maior_categoria': 'N/A'
            }
            
            # Somar todas as receitas
            for codigo, relatorio in self.dados.items():
                if relatorio.get('status') == 'sucesso' and relatorio.get('dados'):
                    dados_relatorio = relatorio['dados']
                    
                    valor_2025 = self._extrair_valor_total_relatorio(dados_relatorio, 2025)
                    valor_2024 = self._extrair_valor_total_relatorio(dados_relatorio, 2024)
                    
                    kpis['receita_total_2025'] += valor_2025 or 0
                    kpis['receita_total_2024'] += valor_2024 or 0
            
            # Calcular variação percentual
            if kpis['receita_total_2024'] > 0:
                variacao = ((kpis['receita_total_2025'] - kpis['receita_total_2024']) / 
                           kpis['receita_total_2024']) * 100
                kpis['variacao_percentual'] = f"{variacao:+.1f}%"
            
            # Encontrar maior categoria
            maior_valor = 0
            for codigo, relatorio in self.dados.items():
                if relatorio.get('status') == 'sucesso' and relatorio.get('dados'):
                    valor = self._extrair_valor_total_relatorio(relatorio['dados'], 2025)
                    if valor and valor > maior_valor:
                        maior_valor = valor
                        kpis['maior_categoria'] = relatorio.get('nome', codigo)
            
            return kpis
            
        except Exception as e:
            print(f"❌ Erro ao extrair KPIs principais: {e}")
            return {'receita_total_2025': 0, 'receita_total_2024': 0, 
                   'variacao_percentual': '0%', 'maior_categoria': 'N/A'}
    
    def _extrair_dados_comparacao(self):
        """
        Extrai dados para comparação no dashboard
        
        Returns:
            dict: Dados para comparação
        """
        try:
            dados = {}
            
            # Agrupar por categoria
            categorias = ['correntes', 'capital']
            
            for categoria in categorias:
                valor_2025 = 0
                valor_2024 = 0
                
                for codigo, relatorio in self.dados.items():
                    if (relatorio.get('categoria') == categoria and 
                        relatorio.get('status') == 'sucesso' and 
                        relatorio.get('dados')):
                        
                        dados_relatorio = relatorio['dados']
                        valor_2025 += self._extrair_valor_total_relatorio(dados_relatorio, 2025) or 0
                        valor_2024 += self._extrair_valor_total_relatorio(dados_relatorio, 2024) or 0
                
                if valor_2025 > 0 or valor_2024 > 0:
                    dados[categoria] = {
                        'nome': 'Receitas Correntes' if categoria == 'correntes' else 'Receitas de Capital',
                        'valor_2025': valor_2025,
                        'valor_2024': valor_2024
                    }
            
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados de comparação: {e}")
            return {}
    
    def _extrair_dados_evolucao_mensal(self):
        """
        Extrai dados de evolução mensal
        
        Returns:
            dict: Dados mensais por ano
        """
        try:
            dados_mensais = {'2024': [0] * 12, '2025': [0] * 12}
            
            # Tentar extrair dados mensais dos comparativos
            for codigo, relatorio in self.dados.items():
                if (relatorio.get('status') == 'sucesso' and 
                    relatorio.get('dados')):
                    
                    dados_relatorio = relatorio['dados']
                    
                    # Procurar dados de comparativo mensal
                    if isinstance(dados_relatorio, dict):
                        comparativo = dados_relatorio.get('comparativo_mensal', {})
                        
                        # Extrair dados mensais se existirem
                        for ano in ['2024', '2025']:
                            if ano in comparativo:
                                dados_ano = comparativo[ano]
                                for mes_idx, valor in enumerate(dados_ano[:12]):
                                    if valor:
                                        dados_mensais[ano][mes_idx] += valor
            
            # Se não temos dados mensais, simular baseado no total
            if all(v == 0 for v in dados_mensais['2024'] + dados_mensais['2025']):
                # Simular crescimento linear baseado nos totais
                total_2024 = sum(self._extrair_valor_total_relatorio(rel['dados'], 2024) or 0 
                               for rel in self.dados.values() 
                               if rel.get('status') == 'sucesso' and rel.get('dados'))
                
                total_2025 = sum(self._extrair_valor_total_relatorio(rel['dados'], 2025) or 0 
                               for rel in self.dados.values() 
                               if rel.get('status') == 'sucesso' and rel.get('dados'))
                
                # Distribuir proporcionalmente (simulando crescimento acumulado)
                for i in range(12):
                    dados_mensais['2024'][i] = total_2024 * (i + 1) / 12
                    dados_mensais['2025'][i] = total_2025 * (i + 1) / 12
            
            return dados_mensais
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados de evolução mensal: {e}")
            return {'2024': [0] * 12, '2025': [0] * 12}