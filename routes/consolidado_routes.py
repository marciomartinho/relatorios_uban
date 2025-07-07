"""
Rotas do Relatório Consolidado - VERSÃO FINAL
Inclui geração de PDF completo

SUBSTITUIR: routes/consolidado_routes.py
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from decimal import Decimal
import traceback
from datetime import datetime
import os

# Criar Blueprint
consolidado_bp = Blueprint('consolidado', __name__, url_prefix='/relatorio')

# FUNÇÃO DE SANITIZAÇÃO PARA JSON
def sanitizar_para_json(dados):
    """
    Converte tipos pandas/numpy para tipos nativos Python serializáveis em JSON
    """
    if isinstance(dados, dict):
        return {key: sanitizar_para_json(value) for key, value in dados.items()}
    elif isinstance(dados, list):
        return [sanitizar_para_json(item) for item in dados]
    elif isinstance(dados, tuple):
        return tuple(sanitizar_para_json(item) for item in dados)
    elif isinstance(dados, (np.int64, np.int32, np.int16, np.int8)):
        return int(dados)
    elif isinstance(dados, (np.float64, np.float32)):
        return float(dados)
    elif isinstance(dados, np.bool_):
        return bool(dados)
    elif isinstance(dados, Decimal):
        return float(dados)
    elif pd.isna(dados):
        return None
    elif hasattr(dados, 'item'):  # Tipos numpy genéricos
        try:
            return dados.item()
        except:
            return str(dados)
    else:
        return dados

@consolidado_bp.route('/consolidado-pdf')
def gerar_relatorio_consolidado_pdf():
    """Gera relatório consolidado de receitas em PDF"""
    try:
        print("🚀 Iniciando geração do relatório consolidado...")
        
        # Parâmetros da requisição
        noug_selecionada = request.args.get('noug', None)
        if noug_selecionada == 'None' or noug_selecionada == '':
            noug_selecionada = None
        
        # Carrega dados da receita
        try:
            from utils.data_loaders import carregar_dataframe_receita
            df_receita = carregar_dataframe_receita()
            print(f"📊 Dados de receita carregados: {len(df_receita)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise Exception(f"Erro ao carregar dados de receita: {e}")
        
        if df_receita.empty:
            raise Exception("Dados de receita não encontrados ou vazio")
        
        # Calcula mês de referência
        try:
            if 'INMES' in df_receita.columns:
                mes_ref = int(df_receita['INMES'].max())
                mes_referencia = f"{mes_ref:02d}/2025"
            else:
                mes_referencia = "05/2025"
        except:
            mes_referencia = "05/2025"
        
        print(f"📅 Mês de referência: {mes_referencia}")
        
        # Importar e executar relatório consolidado
        try:
            from relatorios.consolidado.relatorio_consolidado import RelatorioConsolidado
            
            print("🔧 Iniciando consolidação...")
            consolidado = RelatorioConsolidado(df_receita, mes_referencia, noug_selecionada)
            
            print("🔄 Executando todos os relatórios...")
            dados_consolidados = consolidado.executar_todos_relatorios()
            
            print("📊 Gerando resumo executivo...")
            resumo_executivo = consolidado.gerar_resumo_executivo()
            
            print("📈 Gerando KPIs principais...")
            kpis_principais = consolidado.gerar_kpis_principais()
            
            print("✅ Relatórios consolidados gerados com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao executar consolidação: {e}")
            traceback.print_exc()
            raise Exception(f"Erro na consolidação: {e}")
        
        # Preparar dados para template
        dados_template = {
            'titulo': 'Relatório Consolidado de Receitas',
            'mes_referencia': mes_referencia,
            'dados_consolidados': dados_consolidados,
            'resumo_executivo': resumo_executivo,
            'kpis_principais': kpis_principais,
            'noug_selecionada': noug_selecionada,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'total_relatorios': len(dados_consolidados),
            'tempo_geracao': resumo_executivo.get('tempo_geracao', 0.0)
        }
        
        print("🧹 Sanitizando dados para JSON...")
        
        # APLICAR SANITIZAÇÃO
        try:
            dados_template_limpos = sanitizar_para_json(dados_template)
            print("✅ Dados sanitizados com sucesso")
        except Exception as e:
            print(f"⚠️ Erro na sanitização, usando fallback: {e}")
            # Fallback mais simples
            dados_template_limpos = {}
            for key, value in dados_template.items():
                try:
                    # Testa se é serializável
                    import json
                    json.dumps(value)
                    dados_template_limpos[key] = value
                except:
                    # Se não for, converte para string
                    dados_template_limpos[key] = str(value)
        
        print("🎨 Renderizando template...")
        
        return render_template('relatorio_consolidado.html', **dados_template_limpos)
        
    except Exception as e:
        print(f"❌ Erro geral ao gerar relatório consolidado: {e}")
        traceback.print_exc()
        
        return render_template('erro.html', 
                             erro="Erro ao gerar relatório consolidado", 
                             detalhes=str(e))

@consolidado_bp.route('/consolidado-pdf-download')
def gerar_relatorio_consolidado_pdf_download():
    """Gera e baixa o relatório consolidado em PDF"""
    try:
        print("📥 Iniciando download do PDF consolidado...")
        
        # Parâmetros da requisição
        noug_selecionada = request.args.get('noug', None)
        if noug_selecionada == 'None' or noug_selecionada == '':
            noug_selecionada = None
        
        # Carrega dados da receita
        try:
            from utils.data_loaders import carregar_dataframe_receita
            df_receita = carregar_dataframe_receita()
            print(f"📊 Dados de receita carregados: {len(df_receita)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise Exception(f"Erro ao carregar dados de receita: {e}")
        
        if df_receita.empty:
            raise Exception("Dados de receita não encontrados")
        
        # Calcula mês de referência
        try:
            if 'INMES' in df_receita.columns:
                mes_ref = int(df_receita['INMES'].max())
                mes_referencia = f"{mes_ref:02d}/2025"
            else:
                mes_referencia = "05/2025"
        except:
            mes_referencia = "05/2025"
        
        print(f"📅 Mês de referência: {mes_referencia}")
        
        # Executar consolidação
        try:
            from relatorios.consolidado.relatorio_consolidado import RelatorioConsolidado
            
            print("🔧 Iniciando consolidação...")
            consolidado = RelatorioConsolidado(df_receita, mes_referencia, noug_selecionada)
            
            print("🔄 Executando todos os relatórios...")
            dados_consolidados = consolidado.executar_todos_relatorios()
            
            print("📊 Gerando resumo executivo...")
            resumo_executivo = consolidado.gerar_resumo_executivo()
            
            print("📈 Gerando KPIs principais...")
            kpis_principais = consolidado.gerar_kpis_principais()
            
            print("✅ Dados consolidados prontos")
            
        except Exception as e:
            print(f"❌ Erro ao executar consolidação: {e}")
            traceback.print_exc()
            raise Exception(f"Erro na consolidação: {e}")
        
        # Gerar PDF
        try:
            print("📄 Iniciando geração do PDF...")
            from relatorios.consolidado.gerador_pdf import GeradorPDF
            
            # Criar gerador PDF
            gerador_pdf = GeradorPDF(
                dados_consolidados=dados_consolidados,
                resumo_executivo=resumo_executivo,
                kpis_principais=kpis_principais,
                mes_referencia=mes_referencia,
                noug_selecionada=noug_selecionada
            )
            
            # Verificar dependências
            problemas = gerador_pdf.diagnosticar_problemas()
            if problemas:
                print("⚠️ Problemas encontrados:")
                for problema in problemas:
                    print(f"   - {problema}")
                
                # Se WeasyPrint não estiver disponível, retornar instruções
                if not gerador_pdf.verificar_dependencias()['weasyprint']:
                    return jsonify({
                        'status': 'error',
                        'message': 'WeasyPrint não está instalado',
                        'detalhes': problemas,
                        'instrucoes': gerador_pdf.instalar_dependencias()
                    })
            
            # Gerar PDF
            caminho_pdf = gerador_pdf.gerar_pdf()
            
            # Verificar se arquivo foi criado
            if not os.path.exists(caminho_pdf):
                raise Exception("Arquivo PDF não foi criado")
            
            print(f"✅ PDF gerado: {caminho_pdf}")
            
            # Retornar arquivo para download
            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name=f'relatorio_consolidado_{mes_referencia.replace("/", "_")}.pdf',
                mimetype='application/pdf'
            )
            
        except ImportError as e:
            print(f"❌ Erro de importação: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Dependências do PDF não estão instaladas',
                'detalhes': str(e),
                'instrucoes': 'Execute: pip install weasyprint'
            })
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'Erro ao gerar PDF: {e}',
                'detalhes': str(e)
            })
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao gerar relatório consolidado: {e}',
            'detalhes': str(e)
        })

@consolidado_bp.route('/consolidado-json')
def gerar_relatorio_consolidado_json():
    """Retorna dados do relatório consolidado em formato JSON"""
    try:
        print("📊 Gerando relatório consolidado em JSON...")
        
        # Parâmetros da requisição
        noug_selecionada = request.args.get('noug', None)
        if noug_selecionada == 'None' or noug_selecionada == '':
            noug_selecionada = None
        
        # Carrega dados da receita
        from utils.data_loaders import carregar_dataframe_receita
        df_receita = carregar_dataframe_receita()
        
        if df_receita.empty:
            raise Exception("Dados de receita não encontrados")
        
        # Calcula mês de referência
        try:
            if 'INMES' in df_receita.columns:
                mes_ref = int(df_receita['INMES'].max())
                mes_referencia = f"{mes_ref:02d}/2025"
            else:
                mes_referencia = "05/2025"
        except:
            mes_referencia = "05/2025"
        
        # Executar consolidação
        from relatorios.consolidado.relatorio_consolidado import RelatorioConsolidado
        
        consolidado = RelatorioConsolidado(df_receita, mes_referencia, noug_selecionada)
        dados_consolidados = consolidado.executar_todos_relatorios()
        resumo_executivo = consolidado.gerar_resumo_executivo()
        kpis_principais = consolidado.gerar_kpis_principais()
        
        # Preparar resposta JSON
        resposta = {
            'status': 'success',
            'mes_referencia': mes_referencia,
            'dados_consolidados': dados_consolidados,
            'resumo_executivo': resumo_executivo,
            'kpis_principais': kpis_principais,
            'noug_selecionada': noug_selecionada,
            'data_geracao': datetime.now().isoformat(),
            'total_relatorios': len(dados_consolidados)
        }
        
        # Sanitizar para JSON
        resposta_limpa = sanitizar_para_json(resposta)
        
        return jsonify(resposta_limpa)
        
    except Exception as e:
        print(f"❌ Erro ao gerar JSON: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao gerar relatório consolidado: {e}',
            'details': str(e)
        })

@consolidado_bp.route('/consolidado-diagnostico')
def diagnosticar_sistema():
    """Diagnostica o sistema e dependências"""
    try:
        print("🔍 Executando diagnóstico do sistema...")
        
        diagnostico = {
            'status': 'info',
            'timestamp': datetime.now().isoformat(),
            'dependencias': {},
            'problemas': [],
            'instrucoes': []
        }
        
        # Verificar dependências básicas
        try:
            from utils.data_loaders import carregar_dataframe_receita
            df_receita = carregar_dataframe_receita()
            diagnostico['dependencias']['dados_receita'] = {
                'disponivel': True,
                'registros': len(df_receita) if not df_receita.empty else 0
            }
        except Exception as e:
            diagnostico['dependencias']['dados_receita'] = {
                'disponivel': False,
                'erro': str(e)
            }
            diagnostico['problemas'].append(f"Dados de receita: {e}")
        
        # Verificar consolidação
        try:
            from relatorios.consolidado.relatorio_consolidado import RelatorioConsolidado
            diagnostico['dependencias']['consolidacao'] = {'disponivel': True}
        except Exception as e:
            diagnostico['dependencias']['consolidacao'] = {
                'disponivel': False,
                'erro': str(e)
            }
            diagnostico['problemas'].append(f"Consolidação: {e}")
        
        # Verificar gráficos
        try:
            from relatorios.consolidado.gerador_graficos import GeradorGraficos
            diagnostico['dependencias']['graficos'] = {'disponivel': True}
        except Exception as e:
            diagnostico['dependencias']['graficos'] = {
                'disponivel': False,
                'erro': str(e)
            }
            diagnostico['problemas'].append(f"Gráficos: {e}")
        
        # Verificar PDF
        try:
            from relatorios.consolidado.gerador_pdf import GeradorPDF
            
            # Criar instância temporária para diagnóstico
            gerador_pdf = GeradorPDF({}, {}, {}, "01/2025")
            dependencias_pdf = gerador_pdf.verificar_dependencias()
            problemas_pdf = gerador_pdf.diagnosticar_problemas()
            
            diagnostico['dependencias']['pdf'] = dependencias_pdf
            diagnostico['problemas'].extend(problemas_pdf)
            
            if problemas_pdf:
                diagnostico['instrucoes'].append(gerador_pdf.instalar_dependencias())
                
        except Exception as e:
            diagnostico['dependencias']['pdf'] = {
                'disponivel': False,
                'erro': str(e)
            }
            diagnostico['problemas'].append(f"PDF: {e}")
        
        # Verificar templates
        try:
            from flask import current_app
            template_path = os.path.join(current_app.template_folder, 'relatorio_consolidado_pdf.html')
            css_path = os.path.join(current_app.static_folder, 'css', 'relatorio_consolidado.css')
            
            diagnostico['dependencias']['templates'] = {
                'template_pdf': os.path.exists(template_path),
                'css_consolidado': os.path.exists(css_path)
            }
            
            if not os.path.exists(template_path):
                diagnostico['problemas'].append("Template relatorio_consolidado_pdf.html não encontrado")
            
            if not os.path.exists(css_path):
                diagnostico['problemas'].append("CSS relatorio_consolidado.css não encontrado")
                
        except Exception as e:
            diagnostico['dependencias']['templates'] = {
                'disponivel': False,
                'erro': str(e)
            }
            diagnostico['problemas'].append(f"Templates: {e}")
        
        # Definir status final
        if not diagnostico['problemas']:
            diagnostico['status'] = 'success'
            diagnostico['message'] = 'Sistema funcionando corretamente'
        else:
            diagnostico['status'] = 'warning'
            diagnostico['message'] = f'{len(diagnostico["problemas"])} problemas encontrados'
        
        return jsonify(diagnostico)
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro no diagnóstico: {e}',
            'details': str(e)
        })

# Registrar Blueprint (adicionar no seu app.py se não estiver)
def registrar_rotas_consolidado(app):
    """Função para registrar as rotas do consolidado"""
    app.register_blueprint(consolidado_bp)


@consolidado_bp.route('/consolidado-alternativo')
def gerar_relatorio_consolidado_alternativo():
    """Gera relatório consolidado alternativo (sem matplotlib/weasyprint)"""
    try:
        print("🚀 Iniciando geração do relatório consolidado alternativo...")
        
        # Parâmetros da requisição
        noug_selecionada = request.args.get('noug', None)
        if noug_selecionada == 'None' or noug_selecionada == '':
            noug_selecionada = None
        
        # Carrega dados da receita
        try:
            from utils.data_loaders import carregar_dataframe_receita
            df_receita = carregar_dataframe_receita()
            print(f"📊 Dados de receita carregados: {len(df_receita)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise Exception(f"Erro ao carregar dados de receita: {e}")
        
        if df_receita.empty:
            raise Exception("Dados de receita não encontrados ou vazio")
        
        # Calcula mês de referência
        try:
            if 'INMES' in df_receita.columns:
                mes_ref = int(df_receita['INMES'].max())
                mes_referencia = f"{mes_ref:02d}/2025"
            else:
                mes_referencia = "05/2025"
        except:
            mes_referencia = "05/2025"
        
        print(f"📅 Mês de referência: {mes_referencia}")
        
        # Executar consolidação
        try:
            from relatorios.consolidado.relatorio_consolidado import RelatorioConsolidado
            
            print("🔧 Iniciando consolidação...")
            consolidado = RelatorioConsolidado(df_receita, mes_referencia, noug_selecionada)
            
            print("🔄 Executando todos os relatórios...")
            dados_consolidados = consolidado.executar_todos_relatorios()
            
            print("📊 Gerando resumo executivo...")
            resumo_executivo = consolidado.gerar_resumo_executivo()
            
            print("📈 Gerando KPIs principais...")
            kpis_principais = consolidado.gerar_kpis_principais()
            
            print("✅ Dados consolidados prontos")
            
        except Exception as e:
            print(f"❌ Erro ao executar consolidação: {e}")
            traceback.print_exc()
            raise Exception(f"Erro na consolidação: {e}")
        
        # Gerar gráficos HTML (sem matplotlib)
        try:
            print("🎨 Gerando gráficos HTML...")
            from relatorios.consolidado.gerador_graficos_html import GeradorGraficosHTML
            
            gerador_graficos = GeradorGraficosHTML(dados_consolidados)
            graficos_html = gerador_graficos.gerar_todos_graficos()
            
            print("✅ Gráficos HTML gerados")
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos HTML: {e}")
            graficos_html = {}
        
        # Preparar dados para template
        dados_template = {
            'titulo': 'Relatório Consolidado de Receitas',
            'mes_referencia': mes_referencia,
            'dados_consolidados': dados_consolidados,
            'resumo_executivo': resumo_executivo,
            'kpis_principais': kpis_principais,
            'graficos_html': graficos_html,  # Gráficos HTML em vez de PNG
            'noug_selecionada': noug_selecionada,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'total_relatorios': len(dados_consolidados),
            'tempo_geracao': resumo_executivo.get('tempo_geracao', 0.0)
        }
        
        print("🧹 Sanitizando dados para template...")
        
        # Sanitizar dados
        try:
            dados_template_limpos = sanitizar_para_json(dados_template)
            print("✅ Dados sanitizados com sucesso")
        except Exception as e:
            print(f"⚠️ Erro na sanitização: {e}")
            dados_template_limpos = dados_template
        
        print("🎨 Renderizando template alternativo...")
        
        return render_template('relatorio_consolidado_html.html', **dados_template_limpos)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()
        
        return render_template('erro.html', 
                             erro="Erro ao gerar relatório consolidado alternativo", 
                             detalhes=str(e))