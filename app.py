import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
from config_relatorios import HIERARQUIA_RECEITAS, MENU_PRINCIPAL
from motor_relatorios import (
    gerar_relatorio_estimada, 
    gerar_relatorio_por_adm, 
    gerar_relatorio_previsao_atualizada, 
    gerar_balanco_orcamentario
)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def carregar_dataframe():
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

@app.route('/')
def index():
    return render_template('index.html', menu=MENU_PRINCIPAL)

@app.route('/relatorio/balanco-orcamentario')
def relatorio_balanco_orcamentario():
    try:
        df_completo = carregar_dataframe()
        lista_nougs = sorted(df_completo['NOUG'].dropna().unique().tolist())
        noug_selecionada = request.args.get('noug', None)
        
        dados_tabela, mes_referencia, dados_para_ia, dados_pdf = gerar_balanco_orcamentario(df_completo, HIERARQUIA_RECEITAS, noug_selecionada)
        
        return render_template('balanco_orcamentario.html', 
                               dados_relatorio=dados_tabela,
                               mes_ref=mes_referencia,
                               lista_nougs=lista_nougs,
                               noug_selecionada=noug_selecionada,
                               dados_para_ia=dados_para_ia,
                               dados_pdf=dados_pdf)
    except KeyError as e:
        return f"Ocorreu um erro: A coluna {e} não foi encontrada no Excel."
    except Exception as e:
        return f"Ocorreu um erro ao gerar o relatório: <pre>{e}</pre>"

# As outras rotas e a API da IA permanecem aqui
# ...

if __name__ == '__main__':
    app.run(debug=True)
