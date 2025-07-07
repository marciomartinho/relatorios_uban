"""
Gerador PDF para Relatório Consolidado
Converte template HTML em PDF profissional usando WeasyPrint

CRIAR ESTE ARQUIVO EM: relatorios/consolidado/gerador_pdf.py
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
import traceback

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from flask import render_template, current_app
from .gerador_graficos import GeradorGraficos

class GeradorPDF:
    """
    Classe para gerar PDF do relatório consolidado
    """
    
    def __init__(self, dados_consolidados, resumo_executivo, kpis_principais, 
                 mes_referencia, noug_selecionada=None):
        """
        Inicializa o gerador PDF
        
        Args:
            dados_consolidados: Dados consolidados dos relatórios
            resumo_executivo: Resumo executivo
            kpis_principais: KPIs principais
            mes_referencia: Mês de referência
            noug_selecionada: NOUG selecionada (opcional)
        """
        self.dados_consolidados = dados_consolidados
        self.resumo_executivo = resumo_executivo
        self.kpis_principais = kpis_principais
        self.mes_referencia = mes_referencia
        self.noug_selecionada = noug_selecionada
        
        # Verificar se WeasyPrint está disponível
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint não está instalado. "
                "Instale com: pip install weasyprint"
            )
        
        # Configurações
        self.pasta_saida = 'static/pdfs/'
        self.nome_arquivo = f'relatorio_consolidado_{mes_referencia.replace("/", "_")}.pdf'
        self.caminho_completo = os.path.join(self.pasta_saida, self.nome_arquivo)
        
        # Criar pasta de saída se não existir
        self._criar_pasta_saida()
        
        print(f"📄 GeradorPDF inicializado para {mes_referencia}")
        print(f"📁 Arquivo será salvo em: {self.caminho_completo}")
    
    def _criar_pasta_saida(self):
        """Cria a pasta de saída para PDFs"""
        try:
            os.makedirs(self.pasta_saida, exist_ok=True)
            print(f"✅ Pasta de PDFs criada: {self.pasta_saida}")
        except Exception as e:
            print(f"❌ Erro ao criar pasta de PDFs: {e}")
    
    def gerar_pdf(self):
        """
        Gera o PDF completo
        
        Returns:
            str: Caminho do arquivo PDF gerado
        """
        try:
            print("🔄 Iniciando geração do PDF...")
            
            # 1. Gerar gráficos
            print("📊 Gerando gráficos...")
            graficos_gerados = self._gerar_graficos()
            
            # 2. Preparar dados para template
            print("📝 Preparando dados para o template...")
            dados_template = self._preparar_dados_template(graficos_gerados)
            
            # 3. Renderizar HTML
            print("🎨 Renderizando template HTML...")
            html_renderizado = self._renderizar_template(dados_template)
            
            # 4. Converter para PDF
            print("📄 Convertendo HTML para PDF...")
            caminho_pdf = self._converter_html_para_pdf(html_renderizado)
            
            # 5. Limpar arquivos temporários
            print("🧹 Limpando arquivos temporários...")
            self._limpar_arquivos_temporarios(graficos_gerados)
            
            print(f"✅ PDF gerado com sucesso: {caminho_pdf}")
            return caminho_pdf
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            traceback.print_exc()
            raise
    
    def _gerar_graficos(self):
        """
        Gera os gráficos necessários para o PDF
        
        Returns:
            dict: Caminhos dos gráficos gerados
        """
        try:
            gerador_graficos = GeradorGraficos(self.dados_consolidados)
            graficos_gerados = gerador_graficos.gerar_todos_graficos()
            
            # Verificar se todos os gráficos foram gerados
            graficos_esperados = ['dashboard', 'receitas_correntes', 'receitas_capital', 'evolucao_mensal']
            
            for grafico in graficos_esperados:
                if grafico not in graficos_gerados:
                    print(f"⚠️ Gráfico {grafico} não foi gerado")
                    graficos_gerados[grafico] = None
                elif graficos_gerados[grafico] and os.path.exists(graficos_gerados[grafico]):
                    print(f"✅ Gráfico {grafico} gerado: {graficos_gerados[grafico]}")
                else:
                    print(f"⚠️ Arquivo do gráfico {grafico} não encontrado")
                    graficos_gerados[grafico] = None
            
            return graficos_gerados
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos: {e}")
            return {}
    
    def _preparar_dados_template(self, graficos_gerados):
        """
        Prepara os dados para o template HTML
        
        Args:
            graficos_gerados: Dicionário com caminhos dos gráficos
            
        Returns:
            dict: Dados preparados para o template
        """
        return {
            'titulo': 'Relatório Consolidado de Receitas',
            'mes_referencia': self.mes_referencia,
            'dados_consolidados': self.dados_consolidados,
            'resumo_executivo': self.resumo_executivo,
            'kpis_principais': self.kpis_principais,
            'graficos_gerados': graficos_gerados,
            'noug_selecionada': self.noug_selecionada,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'total_relatorios': len(self.dados_consolidados),
            'tempo_geracao': self.resumo_executivo.get('tempo_geracao', 0) if self.resumo_executivo else 0
        }
    
    def _renderizar_template(self, dados_template):
        """
        Renderiza o template HTML
        
        Args:
            dados_template: Dados para o template
            
        Returns:
            str: HTML renderizado
        """
        try:
            # Usar o template PDF específico
            html_renderizado = render_template('relatorio_consolidado_pdf.html', **dados_template)
            
            print("✅ Template HTML renderizado com sucesso")
            return html_renderizado
            
        except Exception as e:
            print(f"❌ Erro ao renderizar template: {e}")
            traceback.print_exc()
            raise
    
    def _converter_html_para_pdf(self, html_renderizado):
        """
        Converte HTML renderizado para PDF
        
        Args:
            html_renderizado: HTML renderizado
            
        Returns:
            str: Caminho do arquivo PDF
        """
        try:
            # Configuração de fontes
            font_config = FontConfiguration()
            
            # CSS customizado para PDF
            css_pdf = CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                    line-height: 1.4;
                }
                
                .page-break {
                    page-break-before: always;
                }
                
                .no-break {
                    page-break-inside: avoid;
                }
                
                .grafico-pdf {
                    max-width: 100%;
                    height: auto;
                    page-break-inside: avoid;
                }
                
                table {
                    page-break-inside: avoid;
                }
                
                .tabela-receita {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                
                .tabela-receita th,
                .tabela-receita td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                
                .tabela-receita th {
                    background-color: #1f4e79;
                    color: white;
                    font-weight: bold;
                }
            """, font_config=font_config)
            
            # Criar objeto HTML do WeasyPrint
            html_obj = HTML(string=html_renderizado, base_url=current_app.root_path)
            
            # Gerar PDF
            html_obj.write_pdf(
                self.caminho_completo,
                stylesheets=[css_pdf],
                font_config=font_config,
                optimize_images=True
            )
            
            # Verificar se o arquivo foi criado
            if os.path.exists(self.caminho_completo):
                tamanho_arquivo = os.path.getsize(self.caminho_completo)
                print(f"✅ PDF criado com sucesso: {self.caminho_completo} ({tamanho_arquivo} bytes)")
                return self.caminho_completo
            else:
                raise Exception("Arquivo PDF não foi criado")
                
        except Exception as e:
            print(f"❌ Erro ao converter HTML para PDF: {e}")
            traceback.print_exc()
            raise
    
    def _limpar_arquivos_temporarios(self, graficos_gerados):
        """
        Limpa arquivos temporários (gráficos)
        
        Args:
            graficos_gerados: Dicionário com caminhos dos gráficos
        """
        try:
            # Limpar gráficos temporários
            if graficos_gerados:
                gerador_graficos = GeradorGraficos(self.dados_consolidados)
                gerador_graficos.limpar_graficos_temporarios()
                print("✅ Gráficos temporários removidos")
                
        except Exception as e:
            print(f"⚠️ Erro ao limpar arquivos temporários: {e}")
    
    def verificar_dependencias(self):
        """
        Verifica se todas as dependências estão instaladas
        
        Returns:
            dict: Status das dependências
        """
        dependencias = {
            'weasyprint': WEASYPRINT_AVAILABLE,
            'pasta_saida': os.path.exists(self.pasta_saida),
            'template_existe': False,
            'css_existe': False
        }
        
        try:
            # Verificar se o template existe
            template_path = os.path.join(current_app.template_folder, 'relatorio_consolidado_pdf.html')
            dependencias['template_existe'] = os.path.exists(template_path)
            
            # Verificar se o CSS existe
            css_path = os.path.join(current_app.static_folder, 'css', 'relatorio_consolidado.css')
            dependencias['css_existe'] = os.path.exists(css_path)
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar dependências: {e}")
        
        return dependencias
    
    def diagnosticar_problemas(self):
        """
        Diagnostica problemas comuns
        
        Returns:
            list: Lista de problemas encontrados
        """
        problemas = []
        dependencias = self.verificar_dependencias()
        
        if not dependencias['weasyprint']:
            problemas.append("WeasyPrint não está instalado. Execute: pip install weasyprint")
        
        if not dependencias['template_existe']:
            problemas.append("Template relatorio_consolidado_pdf.html não encontrado")
        
        if not dependencias['css_existe']:
            problemas.append("CSS relatorio_consolidado.css não encontrado")
        
        if not dependencias['pasta_saida']:
            problemas.append(f"Pasta de saída não existe: {self.pasta_saida}")
        
        return problemas
    
    @staticmethod
    def instalar_dependencias():
        """
        Instruções para instalar dependências
        
        Returns:
            str: Comandos de instalação
        """
        comandos = [
            "pip install weasyprint",
            "# No Windows, pode ser necessário instalar GTK3:",
            "# https://weasyprint.readthedocs.io/en/stable/install.html#windows",
            "",
            "# No Linux Ubuntu/Debian:",
            "# sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0",
            "",
            "# No macOS:",
            "# brew install pango"
        ]
        
        return "\n".join(comandos)