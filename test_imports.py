#!/usr/bin/env python3
import sys
print("Python version:", sys.version)
print("=" * 50)

try:
    print("Testando imports...")
    
    print("1. Importando Flask...")
    from flask import Flask
    print("✓ Flask importado com sucesso")
    
    print("\n2. Importando config_relatorios...")
    from config_relatorios import MENU_PRINCIPAL
    print("✓ config_relatorios importado com sucesso")
    
    print("\n3. Importando blueprints...")
    from routes.receita_routes import receita_bp
    print("✓ receita_routes importado")
    
    from routes.despesa_routes import despesa_bp
    print("✓ despesa_routes importado")
    
    from routes.indicadores_routes import indicadores_bp
    print("✓ indicadores_routes importado")
    
    from routes.admin_routes import admin_bp
    print("✓ admin_routes importado")
    
    print("\n4. Importando cache_service...")
    from cache_service import cache_service
    print("✓ cache_service importado com sucesso")
    
    print("\n5. Criando app Flask...")
    app = Flask(__name__)
    print("✓ App Flask criado com sucesso")
    
    print("\n" + "=" * 50)
    print("TODOS OS IMPORTS FUNCIONARAM!")
    print("=" * 50)
    
except Exception as e:
    print("\n" + "!" * 50)
    print(f"ERRO ENCONTRADO: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    print("!" * 50)
    import traceback
    traceback.print_exc()
    sys.exit(1)