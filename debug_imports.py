#!/usr/bin/env python3
"""
Script para debugar as importações e verificar se tudo está funcionando
"""

def verificar_imports():
    print("🔍 Verificando importações...")
    
    try:
        # Testa config_relatorios
        print("1. Testando config_relatorios...")
        from config_relatorios import HIERARQUIA_RECEITAS, MENU_PRINCIPAL
        print(f"   ✅ HIERARQUIA_RECEITAS carregada: {len(HIERARQUIA_RECEITAS)} categorias")
        print(f"   ✅ MENU_PRINCIPAL carregado: {len(MENU_PRINCIPAL)} seções")
        
        # Verifica se receita-estimada está no menu
        for secao, relatorios in MENU_PRINCIPAL.items():
            for relatorio in relatorios:
                if 'receita-estimada' in relatorio['url']:
                    print(f"   ✅ Encontrado no menu: {relatorio['nome']} -> {relatorio['url']}")
    
    except Exception as e:
        print(f"   ❌ Erro em config_relatorios: {e}")
    
    try:
        # Testa motor_relatorios
        print("2. Testando motor_relatorios...")
        from motor_relatorios import gerar_relatorio_receita_estimada
        print("   ✅ gerar_relatorio_receita_estimada importada")
        
    except Exception as e:
        print(f"   ❌ Erro em motor_relatorios: {e}")
    
    try:
        # Testa pandas
        print("3. Testando pandas...")
        import pandas as pd
        print("   ✅ pandas importado")
        
    except Exception as e:
        print(f"   ❌ Erro em pandas: {e}")
    
    try:
        # Testa Flask
        print("4. Testando Flask...")
        from flask import Flask, render_template
        print("   ✅ Flask importado")
        
    except Exception as e:
        print(f"   ❌ Erro em Flask: {e}")

def verificar_arquivos():
    print("\n🔍 Verificando arquivos...")
    import os
    
    arquivos_necessarios = [
        'app.py',
        'motor_relatorios.py',
        'config_relatorios.py',
        'cache_service.py',
        'templates/relatorio_estimada.html',
        'templates/base_relatorio.html',
        'templates/erro.html',
        'templates/index.html',
        'static/css/relatorios.css',
        'static/js/export_relatorio.js',
        'dados/RECEITA.xlsx'
    ]
    
    for arquivo in arquivos_necessarios:
        existe = os.path.exists(arquivo)
        status = "✅ EXISTE" if existe else "❌ FALTA"
        print(f"   {status} {arquivo}")

if __name__ == "__main__":
    verificar_imports()
    verificar_arquivos()
    print("\n🎯 Para testar:")
    print("   1. Acesse: http://127.0.0.1:5000/teste-receita-estimada")
    print("   2. Acesse: http://127.0.0.1:5000/teste-rotas")
    print("   3. Acesse: http://127.0.0.1:5000/relatorio/receita-estimada")
    print("   4. Verifique o console para logs de debug")