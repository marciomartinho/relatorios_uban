"""
Módulo de rotas organizadas por blueprints
"""

# Importa todos os blueprints para facilitar o uso
from .receita_routes import receita_bp
from .despesa_routes import despesa_bp
from .indicadores_routes import indicadores_bp
from .admin_routes import admin_bp

__all__ = [
    'receita_bp',
    'despesa_bp', 
    'indicadores_bp',
    'admin_bp'
]