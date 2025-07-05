import os
from flask import Flask, render_template
import traceback

# Importações das configurações
from config_relatorios import MENU_PRINCIPAL

# Importações dos Blueprints
from routes.receita_routes import receita_bp
from routes.despesa_routes import despesa_bp
from routes.indicadores_routes import indicadores_bp
from routes.admin_routes import admin_bp

# Importa o serviço de cache
from cache_service import cache_service

app = Flask(__name__)

# ===================== REGISTRO DOS BLUEPRINTS =====================
# Cada blueprint gerencia suas próprias rotas
app.register_blueprint(receita_bp, url_prefix='/relatorio')
app.register_blueprint(despesa_bp, url_prefix='/relatorio')
app.register_blueprint(indicadores_bp, url_prefix='/relatorio')
app.register_blueprint(admin_bp, url_prefix='/admin')

# ===================== ROTAS PRINCIPAIS =====================

@app.route('/')
def index():
    """Página inicial com menu principal"""
    return render_template('index.html', menu=MENU_PRINCIPAL)

# ===================== TRATAMENTO DE ERROS =====================

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro.html', 
                         titulo="Página Não Encontrada",
                         mensagem="A página solicitada não foi encontrada."), 404

@app.errorhandler(500)
def erro_interno(e):
    traceback.print_exc()
    return render_template('erro.html', 
                         titulo="Erro Interno no Servidor",
                         mensagem=f"Ocorreu um erro inesperado. Detalhes: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)