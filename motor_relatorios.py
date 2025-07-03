import pandas as pd

# --- FUNÇÕES AUXILIARES ---
def _formatar_numero(valor):
    if pd.isna(valor) or valor == 0: return "R$ 0,00"
    if valor < 0: return f"(R$ {abs(valor):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _criar_mapas_de_nomes(df):
    mapas = {
        'categoria': df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIARECEITA'].to_dict(),
        'origem': df.drop_duplicates('ORIGEM').set_index('ORIGEM')['NOFONTERECEITA'].to_dict(),
        'especie': df.drop_duplicates('ESPECIE').set_index('ESPECIE')['NOSUBFONTERECEITA'].to_dict(),
        'alinea': df.drop_duplicates('ALINEA').set_index('ALINEA')['NOALINEA'].to_dict()
    }
    return mapas

# --- MOTOR DO BALANÇO ORÇAMENTÁRIO (COM TODAS AS REGRAS INTEGRADAS) ---
def gerar_balanco_orcamentario(df_completo, estrutura_hierarquica, noug_selecionada=None):
    # Pega o mês de referência ANTES de qualquer filtro
    mes_referencia_str = "N/A"
    df_2025_geral = df_completo[df_completo['COEXERCICIO'] == 2025]
    if not df_2025_geral.empty and 'INMES' in df_2025_geral.columns:
        max_mes_num = int(df_2025_geral['INMES'].max())
        meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        mes_referencia_str = meses_map.get(max_mes_num, "Mês Inválido")

    df_processar = df_completo.copy()
    if noug_selecionada and noug_selecionada != 'todos':
        df_processar = df_processar[df_processar['NOUG'] == noug_selecionada]

    mapas_nomes = _criar_mapas_de_nomes(df_processar)
    dados_numericos = []
    grandes_totais = {'pi_2025': 0, 'pa_2025': 0, 'rr_2025': 0, 'rr_2024': 0}

    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = mapas_nomes.get('categoria', {}).get(cod_cat)
        df_categoria = df_processar[df_processar['CATEGORIA'] == cod_cat]
        pi = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
        pa = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum())
        rr_2025 = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum())
        rr_2024 = float(df_categoria[df_categoria['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
        
        if nome_categoria and any(v != 0 for v in [pi, pa, rr_2025, rr_2024]):
            linha_dados = {'tipo': 'level-1', 'especificacao': nome_categoria, 'pi_2025': pi, 'pa_2025': pa, 'rr_2025': rr_2025, 'rr_2024': rr_2024}
            dados_numericos.append(linha_dados)
            grandes_totais['pi_2025'] += pi; grandes_totais['pa_2025'] += pa; grandes_totais['rr_2025'] += rr_2025; grandes_totais['rr_2024'] += rr_2024
            
            if not origens: continue
            for cod_orig, especies in origens.items():
                nome_origem = mapas_nomes.get('origem', {}).get(cod_orig)
                df_origem = df_processar[df_processar['ORIGEM'] == cod_orig]
                pi_o = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum()); pa_o = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum()); rr_o_2025 = float(df_origem[df_origem['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum()); rr_o_2024 = float(df_origem[df_origem['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
                if nome_origem and any(v != 0 for v in [pi_o, pa_o, rr_o_2025, rr_o_2024]):
                    dados_numericos.append({'tipo': 'level-2', 'especificacao': nome_origem, 'pi_2025': pi_o, 'pa_2025': pa_o, 'rr_2025': rr_o_2025, 'rr_2024': rr_o_2024})

                if not especies: continue
                for cod_esp in especies:
                    nome_especie = mapas_nomes.get('especie', {}).get(cod_esp)
                    df_especie = df_processar[df_processar['ESPECIE'] == cod_esp]
                    pi_e = float(df_especie[df_especie['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum()); pa_e = float(df_especie[df_especie['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum()); rr_e_2025 = float(df_especie[df_especie['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum()); rr_e_2024 = float(df_especie[df_especie['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
                    if nome_especie and any(v != 0 for v in [pi_e, pa_e, rr_e_2025, rr_e_2024]):
                        dados_numericos.append({'tipo': 'level-3', 'especificacao': nome_especie, 'pi_2025': pi_e, 'pa_2025': pa_e, 'rr_2025': rr_e_2025, 'rr_2024': rr_e_2024})

                        df_alineas_da_especie = df_processar[df_processar['ALINEA'].str.startswith(cod_esp, na=False)]
                        if not df_alineas_da_especie.empty:
                            for cod_alinea, group_alinea in df_alineas_da_especie.sort_values('ALINEA').groupby('ALINEA'):
                                nome_alinea = mapas_nomes.get('alinea', {}).get(cod_alinea)
                                pi_a = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum()); pa_a = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum()); rr_a_2025 = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum()); rr_a_2024 = float(group_alinea[group_alinea['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
                                if nome_alinea and any(v != 0 for v in [pi_a, pa_a, rr_a_2025, rr_a_2024]):
                                    dados_numericos.append({'tipo': 'level-4', 'especificacao': nome_alinea, 'pi_2025': pi_a, 'pa_2025': pa_a, 'rr_2025': rr_a_2025, 'rr_2024': rr_a_2024})

    dados_numericos.append({'tipo': 'total', 'especificacao': 'SOMATÓRIO', **grandes_totais})
    
    dados_tabela_formatados = []
    for linha in dados_numericos:
        linha_fmt = linha.copy()
        linha_fmt['saldo'] = linha['rr_2025'] - linha['rr_2024']
        linha_fmt['pi_2025_fmt'] = _formatar_numero(linha['pi_2025'])
        linha_fmt['pa_2025_fmt'] = _formatar_numero(linha['pa_2025'])
        linha_fmt['rr_2025_fmt'] = _formatar_numero(linha['rr_2025'])
        linha_fmt['rr_2024_fmt'] = _formatar_numero(linha['rr_2024'])
        linha_fmt['saldo_fmt'] = _formatar_numero(linha_fmt['saldo'])
        dados_tabela_formatados.append(linha_fmt)
        
    dados_pdf = {
        "head": [['RECEITAS', 'PREVISÃO INICIAL\n2025', 'PREVISÃO ATUALIZADA\n2025', f'RECEITA REALIZADA\n{mes_referencia_str}/2025', f'RECEITA REALIZADA\n{mes_referencia_str}/2024', 'VARIAÇÃO\n2025 x 2024']],
        "body": [
            [
                linha['especificacao'], 
                _formatar_numero(linha['pi_2025']),
                _formatar_numero(linha['pa_2025']),
                _formatar_numero(linha['rr_2025']),
                _formatar_numero(linha['rr_2024']),
                _formatar_numero(linha['rr_2025'] - linha['rr_2024'])
            ] 
            for linha in dados_numericos
        ]
    }
        
    return dados_tabela_formatados, mes_referencia_str, dados_numericos, dados_pdf

# As outras funções de relatório permanecem aqui para não quebrar o sistema.
def gerar_relatorio_estimada(df, h): return [], []
def gerar_relatorio_por_adm(df, h, c): return [], {}, {}, []
def gerar_relatorio_previsao_atualizada(df, h): return [], {}, []
