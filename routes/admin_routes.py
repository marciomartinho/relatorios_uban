"""
Blueprint para rotas administrativas (cache, debug, etc.)
"""
from flask import Blueprint, jsonify

# Importa o serviço de cache
from cache_service import cache_service

# Cria o blueprint
admin_bp = Blueprint('admin', __name__)

# ===================== ROTAS DE ADMINISTRAÇÃO =====================

@admin_bp.route('/cache/info')
def cache_info():
    """Mostra informações do cache"""
    info = cache_service.get_cache_info()
    return jsonify(info)

@admin_bp.route('/cache/clear')
def clear_cache():
    """Limpa todo o cache"""
    cache_service.clear_cache()
    return jsonify({"status": "Cache limpo com sucesso"})

@admin_bp.route('/health')
def health_check():
    """Endpoint de verificação de saúde do sistema"""
    return jsonify({
        "status": "ok",
        "message": "Sistema funcionando normalmente",
        "version": "2.0.0"
    })