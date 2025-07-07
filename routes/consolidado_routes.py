"""
Arquivo COMPLETO: routes/consolidado_routes.py
COPIE E COLE ESTE ARQUIVO INTEIRO substituindo o seu atual
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from decimal import Decimal
import traceback
from datetime import datetime

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
            from utils.data_loaders import carregar_dados_receita
            df_receita = carregar_dados_receita()
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
            
            consolidado = RelatorioConsolidado(df_receita, mes_referencia, noug_selecionada)
            print("🔄 Executando todos os relatórios...")
            
            dados_consolidados = consolidado.executar_todos_relatorios()
            print("📊 Gerando resumo executivo...")
            
            resumo_executivo = consolidado.gerar_resumo_executivo()
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
            'total_relatorios': len(dados_consolidados)
        }
        
        print("🧹 Sanitizando dados para JSON...")
        
        # APLICAR SANITIZAÇÃO - ESTA É A CORREÇÃO PRINCIPAL
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
        print("📥 Iniciando download do relatório consolidado...")
        
        # Mesmo processo da rota anterior
        noug_selecionada = request.args.get('noug', None)
        if noug_selecionada == 'None' or noug_selecionada == '':
            noug_selecionada = None
        
        from utils.data_loaders import carregar_dados_receita
        df_receita = carregar_dados_receita()
        
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
        
        # Gerar PDF
        try:
            from relatorios.consolidado.gerador_pdf import GeradorPDF
            
            gerador_pdf = GeradorPDF(dados_consolidados, resumo_executivo, kpis_principais)
            caminho_pdf = gerador_pdf.gerar_pdf()
            
            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name=f'relatorio_consolidado_{mes_referencia.replace("/", "_")}.pdf',
                mimetype='application/pdf'
            )
            
        except ImportError:
            # Se o gerador PDF não existir ainda, redireciona para visualização
            return jsonify({
                'status': 'info',
                'message': 'Gerador PDF em desenvolvimento. Redirecionando para visualização.',
                'redirect': '/relatorio/consolidado-pdf'
            })
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao gerar PDF: {e}'
        })

# Registrar Blueprint (adicionar no seu app.py se não estiver)
def registrar_rotas_consolidado(app):
    """Função para registrar as rotas do consolidado"""
    app.register_blueprint(consolidado_bp)