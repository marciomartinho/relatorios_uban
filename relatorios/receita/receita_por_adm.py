"""
Relatório: Receita por Tipo de Administração
Mostra receita distribuída por administração direta, autarquias, fundações, etc.
"""
from ..utils import MotorRelatorios
from config_relatorios import COLUNAS_TIPO_ADMINISTRACAO

def gerar_relatorio_por_adm(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera relatório de receita por tipo de administração
    
    Args:
        df_completo: DataFrame com dados de receita
        estrutura_hierarquica: Estrutura hierárquica das receitas
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_formatados, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], [], {}
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada categoria principal
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.obter_nome_categoria(cod_cat)
        if not nome_categoria:
            continue
            
        df_categoria = df_2025[df_2025['CATEGORIA'] == cod_cat]
        if df_categoria.empty:
            continue
        
        # Calcula os valores totais para a categoria por tipo de administração
        valores_cat_por_adm = {
            nome_adm: float(df_categoria[df_categoria['INTIPOADM'] == cod_adm]['PREVISAO INICIAL LIQUIDA'].sum())
            for nome_adm, cod_adm in COLUNAS_TIPO_ADMINISTRACAO.items()
        }
        total_categoria = sum(valores_cat_por_adm.values())
        
        if total_categoria > 0:
            linha_categoria = {
                'tipo': 'principal',
                'especificacao': nome_categoria,
                'adm_direta': valores_cat_por_adm.get('ADMINISTRAÇÃO DIRETA', 0),
                'autarquias': valores_cat_por_adm.get('AUTARQUIAS', 0),
                'fundacoes': valores_cat_por_adm.get('FUNDAÇÕES', 0),
                'empresas': valores_cat_por_adm.get('EMPRESAS', 0),
                'fundos': valores_cat_por_adm.get('FUNDOS', 0),
                'total': total_categoria
            }
            dados_numericos.append(linha_categoria)
            dados_para_ia.append(linha_categoria)

            # Processa cada origem dentro da categoria
            for cod_orig in origens.keys():
                nome_origem = motor.obter_nome_origem(cod_orig)
                if not nome_origem:
                    continue
                
                df_origem = df_categoria[df_categoria['ORIGEM'] == cod_orig]
                if df_origem.empty:
                    continue

                valores_orig_por_adm = {
                    nome_adm: float(df_origem[df_origem['INTIPOADM'] == cod_adm]['PREVISAO INICIAL LIQUIDA'].sum())
                    for nome_adm, cod_adm in COLUNAS_TIPO_ADMINISTRACAO.items()
                }
                total_origem = sum(valores_orig_por_adm.values())

                if total_origem > 0:
                    linha_origem = {
                        'tipo': 'filha',
                        'especificacao': f"  {nome_origem}",
                        'adm_direta': valores_orig_por_adm.get('ADMINISTRAÇÃO DIRETA', 0),
                        'autarquias': valores_orig_por_adm.get('AUTARQUIAS', 0),
                        'fundacoes': valores_orig_por_adm.get('FUNDAÇÕES', 0),
                        'empresas': valores_orig_por_adm.get('EMPRESAS', 0),
                        'fundos': valores_orig_por_adm.get('FUNDOS', 0),
                        'total': total_origem
                    }
                    dados_numericos.append(linha_origem)
    
    # Formata todos os dados para exibição
    dados_formatados = []
    for linha in dados_numericos:
        linha_fmt = linha.copy()
        for campo, valor in linha.items():
            if isinstance(valor, (int, float)):
                linha_fmt[f'{campo}_fmt'] = motor.formatar_numero(valor)
        dados_formatados.append(linha_fmt)

    # Calcula totais gerais
    linhas_de_categoria_para_total = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_de_categoria_para_total:
        totais_gerais = {
            'adm_direta': sum(l['adm_direta'] for l in linhas_de_categoria_para_total),
            'autarquias': sum(l['autarquias'] for l in linhas_de_categoria_para_total),
            'fundacoes': sum(l['fundacoes'] for l in linhas_de_categoria_para_total),
            'empresas': sum(l['empresas'] for l in linhas_de_categoria_para_total),
            'fundos': sum(l['fundos'] for l in linhas_de_categoria_para_total),
        }
        totais_gerais['total'] = sum(totais_gerais.values())
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            **{f'{k}_fmt': motor.formatar_numero(v) for k, v in totais_gerais.items()}
        }
        dados_formatados.append(linha_total)
        dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais_gerais})
    
    # Gera dados para PDF
    dados_pdf = {
        "head": [['ESPECIFICAÇÃO', 'ADMINISTRAÇÃO DIRETA', 'AUTARQUIAS', 'FUNDAÇÕES', 'EMPRESAS', 'FUNDOS', 'TOTAL']],
        "body": [
            [
                linha['especificacao'],
                linha.get('adm_direta_fmt', 'R$ 0,00'),
                linha.get('autarquias_fmt', 'R$ 0,00'),
                linha.get('fundacoes_fmt', 'R$ 0,00'),
                linha.get('empresas_fmt', 'R$ 0,00'),
                linha.get('fundos_fmt', 'R$ 0,00'),
                linha.get('total_fmt', 'R$ 0,00')
            ]
            for linha in dados_formatados
        ]
    }
    
    return dados_formatados, dados_para_ia, dados_pdf