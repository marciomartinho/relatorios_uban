import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Importações das configurações
from config_relatorios import HIERARQUIA_RECEITAS, MENU_PRINCIPAL

# Importações do motor unificado
from motor_relatorios import (
    gerar_balanco_orcamentario,
    gerar_balanco_despesa,
    gerar_relatorio_estimada, 
    gerar_relatorio_por_adm, 
    gerar_relatorio_previsao_atualizada
)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def carregar_dataframe_receita():
    """Carrega dados de receita"""
    caminho_arquivo = os.path.join('dados', 'RECEITA.xlsx')
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIARECEITA': str,
        'ORIGEM': str, 'NOFONTERECEITA': str,
        'ESPECIE': str, 'NOSUBFONTERECEITA': str,
        'ALINEA': str, 'NOALINEA': str,
        'INTIPOADM': int,
        'NOUG': str
    }
    return pd.read_excel(caminho_arquivo, dtype=dtype_map)

def carregar_dataframe_despesa():
    """Carrega dados de despesa"""
    caminho_arquivo = os.path.join('dados', 'DESPESA.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()
    
    # Carrega o Excel
    df = pd.read_excel(caminho_arquivo, sheet_name=0)
    
    # Aplica tipos de dados
    dtype_map = {
        'CATEGORIA': str, 'NOCATEGORIA': str,
        'GRUPO': str, 'NOGRUPO': str,
        'MODALIDADE': str, 'NOMODALIDADE': str,
        'ELEMENTO': str, 'NOELEMENTO': str,
        'COEXERCICIO': int,
        'INMES': int,
        'INTIPOADM': int,
        'NOUG': str
    }
    
    for col, dtype in dtype_map.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    
    return df

@app.route('/')
def index():
    return render_template('index.html', menu=MENU_PRINCIPAL)

# ===================== ROTAS DE RECEITA =====================

@app.route('/relatorio/balanco-orcamentario')
def relatorio_balanco_orcamentario():
    try:
        df_completo = carregar_dataframe_receita()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_balanco_orcamentario(
            df_completo, HIERARQUIA_RECEITAS, noug_selecionada
        )
        
        return render_template('balanco_orcamentario.html', 
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf)
    except Exception as e:
        return render_template('erro.html',
                             titulo="Erro no Relatório de Receita",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/receita-estimada')
def relatorio_receita_estimada():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/receita-por-adm')
def relatorio_receita_por_adm():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/previsao-atualizada')
def relatorio_previsao_atualizada():
    return "Relatório em desenvolvimento", 501

# ===================== ROTAS DE DESPESA =====================

@app.route('/relatorio/balanco-despesa')
def relatorio_balanco_despesa():
    try:
        df_completo = carregar_dataframe_despesa()
        
        # Verifica se há dados
        if df_completo.empty:
            return render_template('erro.html', 
                                 titulo="Dados de Despesa Não Encontrados",
                                 mensagem="O arquivo DESPESA.xlsx não foi encontrado ou está vazio.")
        
        # Verifica colunas necessárias
        colunas_necessarias = ['CATEGORIA', 'NOCATEGORIA', 'GRUPO', 'NOGRUPO', 'NOUG', 'DOTACAO INICIAL', 'DESPESA EMPENHADA']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df_completo.columns]
        
        if colunas_faltantes:
            return render_template('erro.html',
                                 titulo="Estrutura de Dados Incorreta",
                                 mensagem=f"Colunas faltantes: {', '.join(colunas_faltantes)}")
        
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_balanco_despesa(
            df_completo, None, noug_selecionada
        )
        
        return render_template('despesas/balanco_despesa.html',
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf)
    except Exception as e:
        return render_template('erro.html',
                             titulo="Erro no Relatório de Despesa",
                             mensagem=f"Erro ao gerar relatório: {str(e)}")

@app.route('/relatorio/despesa-por-funcao')
def relatorio_despesa_por_funcao():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/despesa-por-natureza')
def relatorio_despesa_por_natureza():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/despesa-por-modalidade')
def relatorio_despesa_por_modalidade():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/despesa-por-noug')
def relatorio_despesa_por_noug():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/execucao-por-programa')
def relatorio_execucao_por_programa():
    return "Relatório em desenvolvimento", 501

# ===================== ROTAS COMPARATIVAS =====================

@app.route('/relatorio/receita-vs-despesa')
def relatorio_receita_vs_despesa():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/evolucao-temporal')
def relatorio_evolucao_temporal():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/indicadores')
def relatorio_indicadores():
    return "Relatório em desenvolvimento", 501

# ===================== ROTAS GERENCIAIS =====================

@app.route('/relatorio/dashboard')
def relatorio_dashboard():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/restos-pagar')
def relatorio_restos_pagar():
    return "Relatório em desenvolvimento", 501

@app.route('/relatorio/tendencias')
def relatorio_tendencias():
    return "Relatório em desenvolvimento", 501

# ===================== API DA IA =====================

@app.route('/api/analise-ia', methods=['POST'])
def analise_ia():
    try:
        dados = request.json
        dados_relatorio = dados.get('dados', [])
        tipo_relatorio = dados.get('tipo_relatorio', 'generico')
        
        if not dados_relatorio:
            return jsonify({'erro': 'Nenhum dado fornecido para análise'}), 400
        
        # Prepara contexto baseado no tipo
        contextos = {
            'balanco_orcamentario': {
                'titulo': 'Análise do Balanço Orçamentário da Receita',
                'instrucao': 'Analise os dados de receita orçamentária, destacando variações entre previsão e execução, comparações entre exercícios e principais fontes de arrecadação.'
            },
            'balanco_despesa': {
                'titulo': 'Análise do Balanço Orçamentário da Despesa',
                'instrucao': 'Analise os dados de despesa orçamentária, destacando execução das dotações por categoria e grupo, percentuais de execução, principais áreas de gasto e eficiência na aplicação dos recursos.'
            }
        }
        
        contexto_info = contextos.get(tipo_relatorio, {
            'titulo': 'Análise Orçamentária Geral',
            'instrucao': 'Analise os dados orçamentários fornecidos, destacando pontos relevantes.'
        })
        
        # Prepara dados para a IA
        dados_texto = ""
        for item in dados_relatorio:
            if item.get('tipo') != 'total':
                dados_texto += f"- {item.get('especificacao', 'N/A')}: "
                for key, value in item.items():
                    if key not in ['tipo', 'especificacao', 'categoria', 'grupo'] and isinstance(value, (int, float)):
                        dados_texto += f"{key}: R$ {value:,.2f} | "
                dados_texto += "\n"
        
        # Chama OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"""Você é um especialista em análise orçamentária do setor público brasileiro. 
                    
                    Contexto: {contexto_info['titulo']}
                    
                    Instruções:
                    - {contexto_info['instrucao']}
                    - Use linguagem técnica mas acessível
                    - Destaque pontos críticos e oportunidades
                    - Forneça recomendações práticas
                    - Use formatação markdown
                    - Seja objetivo e direto"""
                },
                {
                    "role": "user",
                    "content": f"Dados para análise:\n{dados_texto}"
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        analise = response.choices[0].message.content
        return jsonify({'analise': analise})
        
    except Exception as e:
        return jsonify({'erro': f'Erro na análise: {str(e)}'}), 500

# ===================== ROTA DE TESTE =====================

@app.route('/teste-despesa')
def teste_despesa():
    """Rota para testar carregamento dos dados"""
    try:
        df = carregar_dataframe_despesa()
        
        if df.empty:
            return "❌ Arquivo DESPESA.xlsx não encontrado ou vazio"
        
        info = f"""
        <h2>✅ Dados de Despesa Carregados</h2>
        <p><strong>Linhas:</strong> {len(df):,}</p>
        <p><strong>Colunas:</strong> {len(df.columns)}</p>
        <p><strong>Exercícios:</strong> {sorted(df['COEXERCICIO'].unique().tolist()) if 'COEXERCICIO' in df.columns else 'N/A'}</p>
        <p><strong>Meses:</strong> {sorted(df['INMES'].unique().tolist()) if 'INMES' in df.columns else 'N/A'}</p>
        
        <h3>Colunas Disponíveis:</h3>
        <ul>
        {''.join(f'<li>{col}</li>' for col in df.columns)}
        </ul>
        
        <h3>Amostra dos Dados:</h3>
        {df.head().to_html()}
        
        <p><a href="/relatorio/balanco-despesa">🔗 Testar Relatório de Despesa</a></p>
        <p><a href="/">🏠 Voltar ao Menu</a></p>
        """
        
        return info
        
    except Exception as e:
        return f"❌ Erro ao carregar: {str(e)}"

# ===================== TRATAMENTO DE ERROS =====================

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro.html', 
                         titulo="Página Não Encontrada",
                         mensagem="A página solicitada não foi encontrada."), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('erro.html', 
                         titulo="Erro Interno",
                         mensagem="Ocorreu um erro interno no servidor."), 500

if __name__ == '__main__':
    app.run(debug=True)