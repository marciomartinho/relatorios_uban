# relatorios/consolidado/gerador_pdf.py
"""
Gerador PDF para o Relatório Consolidado
Responsável por converter os dados consolidados em PDF profissional
"""
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

class GeradorPDF:
    """
    Classe responsável por gerar o PDF final do relatório consolidado
    """
    
    def __init__(self, dados_consolidados: Dict[str, Any], graficos_paths: Dict[str, str] = None):
        """
        Inicializa o gerador de PDF
        
        Args:
            dados_consolidados: Dados consolidados de todos os relatórios
            graficos_paths: Caminhos para arquivos de gráficos gerados
        """
        self.dados = dados_consolidados
        self.graficos = graficos_paths or {}
        self.pasta_temp = Path('static/images/graficos_temp/')
        
        # Cria pasta temporária se não existir
        self.pasta_temp.mkdir(parents=True, exist_ok=True)
    
    def gerar_pdf(self, caminho_saida: str) -> str:
        """
        Gera o PDF consolidado
        
        Args:
            caminho_saida: Caminho onde salvar o PDF
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        # Placeholder para implementação do WeasyPrint
        # Será implementado na Fase 4
        print(f"📄 Gerando PDF consolidado para: {caminho_saida}")
        
        # TODO: Implementar geração real do PDF
        # - Renderizar HTML completo
        # - Converter para PDF usando WeasyPrint
        # - Aplicar estilos profissionais
        
        return caminho_saida


# relatorios/consolidado/dashboard_executivo.py
"""
Dashboard Executivo para o Relatório Consolidado
Gera KPIs e resumos executivos dos dados consolidados
"""
from typing import Dict, Any, List
import pandas as pd

class DashboardExecutivo:
    """
    Classe responsável por gerar dashboard executivo com KPIs principais
    """
    
    def __init__(self, dados_consolidados: Dict[str, Any]):
        """
        Inicializa o dashboard executivo
        
        Args:
            dados_consolidados: Dados consolidados de todos os relatórios
        """
        self.dados = dados_consolidados
    
    def gerar_kpis_principais(self) -> Dict[str, Any]:
        """
        Gera os 4 KPIs principais do dashboard
        
        Returns:
            Dicionário com KPIs formatados
        """
        totais = self.dados.get('metadados', {}).get('totais_consolidados', {})
        
        # KPI 1: Receita Total 2025
        receita_total_2025 = totais.get('total_geral_2025', 0)
        
        # KPI 2: Variação vs 2024
        receita_total_2024 = totais.get('total_geral_2024', 0)
        variacao_perc = ((receita_total_2025 - receita_total_2024) / receita_total_2024 * 100) if receita_total_2024 > 0 else 0
        
        # KPI 3: Maior Fonte
        resumo = self.dados.get('resumo_executivo', {})
        maior_receita = resumo.get('maior_receita', 'Não identificada')
        
        # KPI 4: Meta Cumprida (placeholder - será calculado quando houver dados de meta)
        meta_cumprida = 0  # TODO: Implementar cálculo real da meta
        
        return {
            'receita_total_2025': {
                'valor': receita_total_2025,
                'valor_fmt': self._formatar_valor(receita_total_2025),
                'titulo': 'Receita Total 2025'
            },
            'variacao_vs_2024': {
                'valor': variacao_perc,
                'valor_fmt': f"{variacao_perc:+.1f}%",
                'titulo': 'Variação vs 2024',
                'classe_css': 'positivo' if variacao_perc > 0 else 'negativo' if variacao_perc < 0 else 'neutro'
            },
            'maior_fonte': {
                'valor': maior_receita,
                'valor_fmt': maior_receita,
                'titulo': 'Maior Fonte'
            },
            'meta_cumprida': {
                'valor': meta_cumprida,
                'valor_fmt': f"{meta_cumprida:.1f}%",
                'titulo': 'Meta Cumprida',
                'classe_css': 'alto' if meta_cumprida >= 80 else 'medio' if meta_cumprida >= 60 else 'baixo'
            }
        }
    
    def gerar_alertas_visuais(self) -> List[Dict[str, Any]]:
        """
        Gera alertas visuais baseados nos dados
        
        Returns:
            Lista de alertas com cores e mensagens
        """
        alertas = []
        
        # Analisa inconsistências
        inconsistencias = self.dados.get('analises_especiais', {}).get('inconsistencias', {})
        if inconsistencias and inconsistencias.get('totais', {}).get('total_2025', 0) > 0:
            alertas.append({
                'tipo': 'warning',
                'cor': 'amarelo',
                'emoji': '🟡',
                'titulo': 'Inconsistências Detectadas',
                'mensagem': 'Foram encontradas inconsistências nos dados que requerem atenção'
            })
        
        # Analisa variação geral
        totais = self.dados.get('metadados', {}).get('totais_consolidados', {})
        receita_2025 = totais.get('total_geral_2025', 0)
        receita_2024 = totais.get('total_geral_2024', 0)
        
        if receita_2024 > 0:
            variacao = ((receita_2025 - receita_2024) / receita_2024) * 100
            
            if variacao > 10:
                alertas.append({
                    'tipo': 'success',
                    'cor': 'verde',
                    'emoji': '🟢',
                    'titulo': 'Crescimento Acima da Meta',
                    'mensagem': f'Receita cresceu {variacao:.1f}% em relação ao ano anterior'
                })
            elif variacao < -5:
                alertas.append({
                    'tipo': 'error',
                    'cor': 'vermelho',
                    'emoji': '🔴',
                    'titulo': 'Queda Significativa',
                    'mensagem': f'Receita caiu {abs(variacao):.1f}% em relação ao ano anterior'
                })
            else:
                alertas.append({
                    'tipo': 'info',
                    'cor': 'amarelo',
                    'emoji': '🟡',
                    'titulo': 'Dentro da Normalidade',
                    'mensagem': f'Variação de {variacao:.1f}% está dentro do esperado'
                })
        
        return alertas
    
    def gerar_mini_graficos(self) -> Dict[str, Any]:
        """
        Gera dados para mini-gráficos (sparklines, gauges, barras de progresso)
        
        Returns:
            Dados para renderização de mini-gráficos
        """
        # Placeholder para dados de mini-gráficos
        # Será expandido nas próximas fases
        return {
            'sparklines_evolucao': [],
            'gauges_performance': [],
            'barras_progresso': []
        }
    
    def _formatar_valor(self, valor: float) -> str:
        """
        Formata valor monetário para exibição
        
        Args:
            valor: Valor a ser formatado
            
        Returns:
            String formatada
        """
        if valor == 0:
            return "R$ 0,00"
        
        # Formata em milhões para valores grandes
        if abs(valor) >= 1_000_000:
            valor_milhoes = valor / 1_000_000
            return f"R$ {valor_milhoes:,.2f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# relatorios/consolidado/templates/base_consolidado.html
"""
Template base para o relatório consolidado
Estrutura HTML principal que será usada para gerar o PDF
"""
base_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Relatório Consolidado de Receitas - {{ mes_referencia }}</title>
    <link rel="stylesheet" href="relatorio_consolidado.css">
    <style>
        /* Estilos específicos para PDF */
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.4;
            color: #333;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
    </style>
</head>
<body class="relatorio-pdf">
    <!-- Cabeçalho Principal -->
    <header class="header-principal">
        <div class="logo-gdf">
            <!-- Logo do GDF será inserido aqui -->
        </div>
        <div class="titulo-principal">
            <h1>RELATÓRIO CONSOLIDADO DE RECEITAS</h1>
            <h2>{{ mes_referencia }}</h2>
            <h3>Governo do Distrito Federal</h3>
        </div>
        <div class="data-geracao">
            <p>Gerado em: {{ data_geracao }}</p>
        </div>
    </header>
    
    <!-- Conteúdo Dinâmico -->
    {% block conteudo %}{% endblock %}
    
    <!-- Rodapé -->
    <footer class="footer-consolidado">
        <div class="info-tecnica">
            <p>Sistema UBAN - Relatório Consolidado | {{ total_registros }} registros processados</p>
            <p>Tempo de geração: {{ tempo_geracao }}s | {{ data_geracao }}</p>
        </div>
    </footer>
</body>
</html>
'''

# relatorios/consolidado/templates/capa.html
capa_template = '''
{% extends "base_consolidado.html" %}

{% block conteudo %}
<div class="capa-relatorio">
    <div class="titulo-capa">
        <h1>RELATÓRIO CONSOLIDADO</h1>
        <h2>DE RECEITAS PDF</h2>
        <h3>{{ mes_referencia }}</h3>
    </div>
    
    <div class="resumo-capa">
        <div class="kpi-destaque">
            <span class="valor-principal">{{ receita_total_fmt }}</span>
            <span class="label-principal">Receita Total {{ ano_referencia }}</span>
        </div>
        
        <div class="variacao-destaque">
            <span class="variacao {{ classe_variacao }}">{{ variacao_fmt }}</span>
            <span class="label-variacao">vs. Ano Anterior</span>
        </div>
    </div>
    
    <div class="destaques-capa">
        <div class="destaque-item">
            <span class="icone">📊</span>
            <span class="texto">{{ total_relatorios }} Relatórios Consolidados</span>
        </div>
        
        <div class="destaque-item">
            <span class="icone">🏛️</span>
            <span class="texto">{{ maior_receita }}</span>
        </div>
        
        <div class="destaque-item">
            <span class="icone">📈</span>
            <span class="texto">{{ crescimento_destaque }}</span>
        </div>
    </div>
</div>
{% endblock %}
'''

# relatorios/consolidado/templates/dashboard.html
dashboard_template = '''
{% extends "base_consolidado.html" %}

{% block conteudo %}
<div class="dashboard-executivo page-break">
    <h2 class="titulo-secao">Dashboard Executivo</h2>
    
    <!-- KPIs Principais -->
    <div class="kpis-grid">
        {% for kpi_key, kpi in kpis_principais.items() %}
        <div class="kpi-card {{ kpi.classe_css }}">
            <div class="kpi-titulo">{{ kpi.titulo }}</div>
            <div class="kpi-valor">{{ kpi.valor_fmt }}</div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Alertas Visuais -->
    <div class="alertas-container">
        <h3>Status Geral</h3>
        <div class="alertas-grid">
            {% for alerta in alertas %}
            <div class="alerta-item {{ alerta.tipo }}">
                <span class="alerta-emoji">{{ alerta.emoji }}</span>
                <div class="alerta-conteudo">
                    <strong>{{ alerta.titulo }}</strong>
                    <p>{{ alerta.mensagem }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Gráfico Principal -->
    <div class="grafico-principal">
        <h3>Evolução das Receitas</h3>
        <div class="grafico-container">
            {% if grafico_principal %}
            <img src="{{ grafico_principal }}" alt="Gráfico Principal" class="grafico-img">
            {% else %}
            <div class="grafico-placeholder">
                [Gráfico será inserido na Fase 2]
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
'''

# relatorios/consolidado/templates/secao_receita.html
secao_template = '''
{% extends "base_consolidado.html" %}

{% block conteudo %}
<div class="secao-receita page-break">
    <h2 class="titulo-secao">{{ titulo_secao }}</h2>
    
    <!-- Resumo da Seção -->
    <div class="resumo-secao">
        <div class="totais-secao">
            <div class="total-item">
                <span class="label">{{ ano_anterior }}</span>
                <span class="valor">{{ total_2024_fmt }}</span>
            </div>
            <div class="total-item">
                <span class="label">{{ ano_atual }}</span>
                <span class="valor">{{ total_2025_fmt }}</span>
            </div>
            <div class="total-item variacao">
                <span class="label">Variação</span>
                <span class="valor {{ classe_variacao }}">{{ variacao_fmt }}</span>
            </div>
        </div>
    </div>
    
    <!-- Tabela de Dados -->
    <div class="tabela-container">
        <table class="tabela-receita">
            <thead>
                <tr>
                    <th>Tipo de Receita</th>
                    <th>{{ ano_anterior }}</th>
                    <th>{{ ano_atual }}</th>
                    <th>Variação Absoluta</th>
                    <th>Variação %</th>
                </tr>
            </thead>
            <tbody>
                {% for linha in dados_tabela %}
                <tr class="{{ linha.tipo }}">
                    <td>{{ linha.nome }}</td>
                    <td>{{ linha.valor_2024_fmt }}</td>
                    <td>{{ linha.valor_2025_fmt }}</td>
                    <td>{{ linha.variacao_abs_fmt }}</td>
                    <td class="{{ linha.classe_variacao }}">{{ linha.variacao_perc_fmt }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Gráfico da Seção (se houver) -->
    {% if grafico_secao %}
    <div class="grafico-secao">
        <h3>Composição {{ titulo_secao }}</h3>
        <img src="{{ grafico_secao }}" alt="Gráfico {{ titulo_secao }}" class="grafico-img">
    </div>
    {% endif %}
</div>
{% endblock %}
'''

# relatorios/consolidado/templates/anexos.html
anexos_template = '''
{% extends "base_consolidado.html" %}

{% block conteudo %}
<div class="anexos-relatorio page-break">
    <h2 class="titulo-secao">Anexos e Informações Técnicas</h2>
    
    <!-- Estatísticas de Geração -->
    <div class="estatisticas-geracao">
        <h3>Estatísticas de Geração</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">Total de Relatórios</span>
                <span class="stat-valor">{{ total_relatorios }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Relatórios Bem-sucedidos</span>
                <span class="stat-valor">{{ relatorios_sucesso }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Tempo Total de Geração</span>
                <span class="stat-valor">{{ tempo_total }}s</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Taxa de Sucesso</span>
                <span class="stat-valor">{{ taxa_sucesso }}%</span>
            </div>
        </div>
    </div>
    
    <!-- Lista de Relatórios Incluídos -->
    <div class="lista-relatorios">
        <h3>Relatórios Incluídos</h3>
        <ul class="relatorios-lista">
            {% for codigo, relatorio in relatorios_executados.items() %}
            <li class="relatorio-item {{ relatorio.status }}">
                <span class="relatorio-nome">{{ relatorio.nome }}</span>
                <span class="relatorio-categoria">{{ relatorio.categoria }}</span>
                <span class="relatorio-tempo">{{ relatorio.tempo_execucao }}s</span>
                <span class="relatorio-status">{{ relatorio.status }}</span>
            </li>
            {% endfor %}
        </ul>
    </div>
    
    <!-- Metadados Técnicos -->
    <div class="metadados-tecnicos">
        <h3>Informações Técnicas</h3>
        <table class="tabela-metadados">
            <tr>
                <td>Mês de Referência</td>
                <td>{{ mes_referencia }}</td>
            </tr>
            <tr>
                <td>Data de Geração</td>
                <td>{{ data_geracao }}</td>
            </tr>
            <tr>
                <td>Filtro NOUG</td>
                <td>{{ noug_filtrada or "Todos" }}</td>
            </tr>
            <tr>
                <td>Total de Registros</td>
                <td>{{ total_registros }}</td>
            </tr>
            <tr>
                <td>Exercícios Analisados</td>
                <td>{{ exercicios_disponiveis | join(", ") }}</td>
            </tr>
        </table>
    </div>
</div>
{% endblock %}
'''