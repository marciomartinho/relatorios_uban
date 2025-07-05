#!/usr/bin/env python3
"""
Script para debugar as importações e verificar se tudo está funcionando
ATUALIZADO PARA A NOVA ESTRUTURA MODULAR
"""

def verificar_imports():
    print("🔍 Verificando importações modulares...")
    
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
        # Testa módulo de receita (NOVA ESTRUTURA)
        print("2. Testando módulo relatorios.receita...")
        from relatorios.receita import (
            gerar_balanco_orcamentario,
            gerar_relatorio_receita_estimada,
            gerar_relatorio_por_adm,
            gerar_relatorio_receita_atualizada_vs_inicial,
            gerar_grafico_receita_liquida
        )
        print("   ✅ Todas as funções de receita importadas")
        
    except Exception as e:
        print(f"   ❌ Erro em relatorios.receita: {e}")
    
    try:
        # Testa módulo de despesa (NOVA ESTRUTURA)
        print("3. Testando módulo relatorios.despesa...")
        from relatorios.despesa import gerar_balanco_despesa
        print("   ✅ Funções de despesa importadas")
        
    except Exception as e:
        print(f"   ❌ Erro em relatorios.despesa: {e}")
    
    try:
        # Testa módulo de indicadores (NOVA ESTRUTURA)
        print("4. Testando módulo relatorios.indicadores...")
        from relatorios.indicadores import (
            gerar_dashboard_executivo_placeholder,
            gerar_indicadores_orcamentarios_placeholder,
            gerar_analise_variacoes_placeholder,
            gerar_relatorio_por_noug_placeholder
        )
        print("   ✅ Placeholders de indicadores importados")
        
    except Exception as e:
        print(f"   ❌ Erro em relatorios.indicadores: {e}")
    
    try:
        # Testa módulo de utilitários (NOVA ESTRUTURA)
        print("5. Testando módulo relatorios.utils...")
        from relatorios.utils import (
            formatar_numero,
            calcular_mes_referencia,
            obter_mes_numero,
            MotorRelatorios
        )
        print("   ✅ Utilitários importados")
        
    except Exception as e:
        print(f"   ❌ Erro em relatorios.utils: {e}")
    
    try:
        # Testa cache_service
        print("6. Testando cache_service...")
        from cache_service import cache_service
        print("   ✅ cache_service importado")
        
    except Exception as e:
        print(f"   ❌ Erro em cache_service: {e}")
    
    try:
        # Testa pandas
        print("7. Testando pandas...")
        import pandas as pd
        print("   ✅ pandas importado")
        
    except Exception as e:
        print(f"   ❌ Erro em pandas: {e}")
    
    try:
        # Testa Flask
        print("8. Testando Flask...")
        from flask import Flask, render_template
        print("   ✅ Flask importado")
        
    except Exception as e:
        print(f"   ❌ Erro em Flask: {e}")

def verificar_arquivos():
    print("\n🔍 Verificando arquivos...")
    import os
    
    arquivos_necessarios = [
        'app.py',
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
    
    # Arquivos da nova estrutura modular
    arquivos_modulares = [
        'relatorios/__init__.py',
        'relatorios/utils/__init__.py',
        'relatorios/utils/formatacao.py',
        'relatorios/utils/data_utils.py',
        'relatorios/utils/base_motor.py',
        'relatorios/receita/__init__.py',
        'relatorios/receita/balanco_orcamentario.py',
        'relatorios/receita/receita_estimada.py',
        'relatorios/receita/receita_por_adm.py',
        'relatorios/receita/receita_atualizada.py',
        'relatorios/receita/grafico_pizza.py',
        'relatorios/despesa/__init__.py',
        'relatorios/despesa/balanco_despesa.py',
        'relatorios/despesa/despesa_funcao.py',
        'relatorios/despesa/despesa_natureza.py',
        'relatorios/despesa/despesa_modalidade.py',
        'relatorios/indicadores/__init__.py',
        'relatorios/indicadores/placeholders.py',
        'relatorios/indicadores/dashboard_executivo.py',
        'relatorios/indicadores/indicadores_orcamentarios.py',
        'relatorios/indicadores/analise_variacoes.py'
    ]
    
    print("\n📂 Arquivos principais:")
    for arquivo in arquivos_necessarios:
        existe = os.path.exists(arquivo)
        status = "✅ EXISTE" if existe else "❌ FALTA"
        print(f"   {status} {arquivo}")
    
    print("\n📂 Estrutura modular:")
    for arquivo in arquivos_modulares:
        existe = os.path.exists(arquivo)
        status = "✅ EXISTE" if existe else "❌ FALTA"
        print(f"   {status} {arquivo}")

def verificar_motor_antigo():
    print("\n🔍 Verificando motor_relatorios.py antigo...")
    import os
    
    if os.path.exists('motor_relatorios.py'):
        print("   ⚠️  motor_relatorios.py ainda existe")
        print("   📝 Recomendação: Manter temporariamente até confirmar que tudo funciona")
        print("   🗑️  Pode ser removido depois dos testes")
    else:
        print("   ✅ motor_relatorios.py não encontrado (já foi removido)")

def testar_funcionalidades():
    print("\n🧪 Testando funcionalidades básicas...")
    
    try:
        # Testa formatação
        from relatorios.utils import formatar_numero
        resultado = formatar_numero(1234.56)
        print(f"   ✅ Formatação: {resultado}")
        
    except Exception as e:
        print(f"   ❌ Erro na formatação: {e}")
    
    try:
        # Testa motor de relatórios
        import pandas as pd
        from relatorios.utils import MotorRelatorios
        
        df_test = pd.DataFrame({
            'CATEGORIA': ['1', '2'],
            'NOCATEGORIARECEITA': ['Receitas Correntes', 'Receitas de Capital'],
            'PREVISAO INICIAL LIQUIDA': [1000, 2000]
        })
        
        motor = MotorRelatorios(df_test, tipo_dados='receita')
        print("   ✅ MotorRelatorios instanciado com sucesso")
        
    except Exception as e:
        print(f"   ❌ Erro no MotorRelatorios: {e}")

if __name__ == "__main__":
    verificar_imports()
    verificar_arquivos()
    verificar_motor_antigo()
    testar_funcionalidades()
    
    print("\n🎯 Para testar a nova estrutura:")
    print("   1. Execute: python debug_imports.py")
    print("   2. Execute: python app.py")
    print("   3. Acesse: http://127.0.0.1:5000/")
    print("   4. Teste os relatórios:")
    print("      - http://127.0.0.1:5000/relatorio/balanco-orcamentario")
    print("      - http://127.0.0.1:5000/relatorio/receita-estimada")
    print("      - http://127.0.0.1:5000/relatorio/balanco-despesa")
    print("   5. Verifique o console para logs de debug")
    print("\n🔧 Se houver erros:")
    print("   - Verifique se todos os arquivos foram criados")
    print("   - Verifique se as pastas relatorios/ existem")
    print("   - Verifique se os __init__.py foram criados")
    print("   - Execute novamente este script para debug")