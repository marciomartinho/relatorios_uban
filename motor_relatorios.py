import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

# Importa as configurações do outro arquivo para ter acesso às colunas de administração
from config_relatorios import COLUNAS_TIPO_ADMINISTRACAO

class MotorRelatorios:
    """Motor unificado para relatórios de receita e despesa"""
    
    def __init__(self, df: pd.DataFrame, tipo_dados: str = 'receita'):
        self.df = df
        self.tipo_dados = tipo_dados
        self.mapas_nomes = self._criar_mapas_de_nomes()
    
    def _criar_mapas_de_nomes(self) -> Dict[str, Dict]:
        """Cria mapas de códigos para nomes para evitar buscas repetitivas no DataFrame"""
        mapas = {}
        if self.tipo_dados == 'receita':
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIARECEITA'].to_dict(),
                    'origem': self.df.drop_duplicates('ORIGEM').set_index('ORIGEM')['NOFONTERECEITA'].to_dict(),
                    'especie': self.df.drop_duplicates('ESPECIE').set_index('ESPECIE')['NOSUBFONTERECEITA'].to_dict(),
                    'alinea': self.df.drop_duplicates('ALINEA').set_index('ALINEA')['NOALINEA'].to_dict()
                })
        elif self.tipo_dados == 'despesa':
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIA'].to_dict(),
                    'grupo': self.df.drop_duplicates('GRUPO').set_index('GRUPO')['NOGRUPO'].to_dict(),
                    'modalidade': self.df.drop_duplicates('MODALIDADE').set_index('MODALIDADE')['NOMODALIDADE'].to_dict(),
                    'elemento': self.df.drop_duplicates('ELEMENTO').set_index('ELEMENTO')['NOELEMENTO'].to_dict()
                })
        return mapas
    
    @staticmethod
    def _formatar_numero(valor: float) -> str:
        """Formata números para o padrão monetário brasileiro (R$ 1.234,56)"""
        if pd.isna(valor) or valor == 0: 
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def filtrar_por_noug(self, noug_selecionada: Optional[str] = None) -> pd.DataFrame:
        """Aplica filtro por unidade gestora (NOUG) se uma for selecionada"""
        if noug_selecionada and noug_selecionada != 'todos':
            return self.df[self.df['NOUG'] == noug_selecionada].copy()
        return self.df.copy()

# =================================================================================
# FUNÇÃO: BALANÇO ORÇAMENTÁRIO DA RECEITA
# =================================================================================
def gerar_balanco_orcamentario(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera o balanço orçamentário da receita comparando previsão com realização
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra dados de 2025 e 2024
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    df_2024 = df_processar[df_processar['COEXERCICIO'] == 2024]
    
    if df_2025.empty:
        return [], "12", [], {}
    
    # Calcula o mês de referência dinamicamente a partir da coluna INMES
    mes_referencia = "12"  # Valor padrão
    if 'INMES' in df_2025.columns:
        max_mes = df_2025['INMES'].max()
        if pd.notna(max_mes):
            mes_referencia = str(int(max_mes)).zfill(2)  # Formata com 2 dígitos
    
    dados_numericos = []
    dados_para_ia = []
    
    # Processa cada categoria
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.mapas_nomes.get('categoria', {}).get(cod_cat)
        if not nome_categoria: continue
            
        df_cat_2025 = df_2025[df_2025['CATEGORIA'] == cod_cat]
        df_cat_2024 = df_2024[df_2024['CATEGORIA'] == cod_cat]
        
        if df_cat_2025.empty: continue
        
        # Calcula valores da categoria usando as colunas corretas
        pi_2025 = float(df_cat_2025['PREVISAO INICIAL LIQUIDA'].sum())
        
        # Verifica se a coluna PREVISAO ATUALIZADA LIQUIDA existe
        if 'PREVISAO ATUALIZADA LIQUIDA' in df_cat_2025.columns:
            pa_2025 = float(df_cat_2025['PREVISAO ATUALIZADA LIQUIDA'].sum())
        else:
            pa_2025 = pi_2025  # Usa previsão inicial se não existir atualizada
        
        # Verifica se a coluna RECEITA LIQUIDA existe
        if 'RECEITA LIQUIDA' in df_cat_2025.columns:
            rr_2025 = float(df_cat_2025['RECEITA LIQUIDA'].sum())
        else:
            rr_2025 = 0.0  # Se não existir, considera zero
            
        if 'RECEITA LIQUIDA' in df_cat_2024.columns and not df_cat_2024.empty:
            rr_2024 = float(df_cat_2024['RECEITA LIQUIDA'].sum())
        else:
            rr_2024 = 0.0
            
        saldo = rr_2025 - rr_2024
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': nome_categoria,
            'pi_2025': pi_2025,
            'pa_2025': pa_2025,
            'rr_2025': rr_2025,
            'rr_2024': rr_2024,
            'saldo': saldo,
            'pi_2025_fmt': motor._formatar_numero(pi_2025),
            'pa_2025_fmt': motor._formatar_numero(pa_2025),
            'rr_2025_fmt': motor._formatar_numero(rr_2025),
            'rr_2024_fmt': motor._formatar_numero(rr_2024),
            'saldo_fmt': motor._formatar_numero(saldo)
        }
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Processa origens dentro da categoria
        for cod_orig in origens.keys():
            nome_origem = motor.mapas_nomes.get('origem', {}).get(cod_orig)
            if not nome_origem: continue
            
            df_orig_2025 = df_cat_2025[df_cat_2025['ORIGEM'] == cod_orig]
            df_orig_2024 = df_cat_2024[df_cat_2024['ORIGEM'] == cod_orig]
            
            if df_orig_2025.empty: continue
            
            pi_2025_orig = float(df_orig_2025['PREVISAO INICIAL LIQUIDA'].sum())
            
            if 'PREVISAO ATUALIZADA LIQUIDA' in df_orig_2025.columns:
                pa_2025_orig = float(df_orig_2025['PREVISAO ATUALIZADA LIQUIDA'].sum())
            else:
                pa_2025_orig = pi_2025_orig
                
            if 'RECEITA LIQUIDA' in df_orig_2025.columns:
                rr_2025_orig = float(df_orig_2025['RECEITA LIQUIDA'].sum())
            else:
                rr_2025_orig = 0.0
                
            if 'RECEITA LIQUIDA' in df_orig_2024.columns and not df_orig_2024.empty:
                rr_2024_orig = float(df_orig_2024['RECEITA LIQUIDA'].sum())
            else:
                rr_2024_orig = 0.0
                
            saldo_orig = rr_2025_orig - rr_2024_orig
            
            linha_origem = {
                'tipo': 'filha',
                'especificacao': f"  {nome_origem}",
                'pi_2025': pi_2025_orig,
                'pa_2025': pa_2025_orig,
                'rr_2025': rr_2025_orig,
                'rr_2024': rr_2024_orig,
                'saldo': saldo_orig,
                'pi_2025_fmt': motor._formatar_numero(pi_2025_orig),
                'pa_2025_fmt': motor._formatar_numero(pa_2025_orig),
                'rr_2025_fmt': motor._formatar_numero(rr_2025_orig),
                'rr_2024_fmt': motor._formatar_numero(rr_2024_orig),
                'saldo_fmt': motor._formatar_numero(saldo_orig)
            }
            dados_numericos.append(linha_origem)
    
    # Calcula totais gerais
    linhas_principais = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_principais:
        totais = {
            'pi_2025': sum(l['pi_2025'] for l in linhas_principais),
            'pa_2025': sum(l['pa_2025'] for l in linhas_principais),
            'rr_2025': sum(l['rr_2025'] for l in linhas_principais),
            'rr_2024': sum(l['rr_2024'] for l in linhas_principais),
        }
        totais['saldo'] = totais['rr_2025'] - totais['rr_2024']
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            **{f'{k}_fmt': motor._formatar_numero(v) for k, v in totais.items()}
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF
    dados_pdf = {
        "head": [['RECEITAS', 'PREVISÃO INICIAL 2025', 'PREVISÃO ATUALIZADA 2025', f'RECEITA REALIZADA {mes_referencia}/2025', f'RECEITA REALIZADA {mes_referencia}/2024', 'VARIAÇÃO 2025 x 2024']],
        "body": [
            [linha['especificacao'], linha.get('pi_2025_fmt', 'R$ 0,00'), linha.get('pa_2025_fmt', 'R$ 0,00'), 
             linha.get('rr_2025_fmt', 'R$ 0,00'), linha.get('rr_2024_fmt', 'R$ 0,00'), linha.get('saldo_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

# =================================================================================
# FUNÇÃO: BALANÇO ORÇAMENTÁRIO DA DESPESA (CORRIGIDA)
# =================================================================================
def gerar_balanco_despesa(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera o balanço orçamentário da despesa comparando dotação com execução
    FÓRMULAS CORRIGIDAS:
    - DOTAÇÃO INICIAL = DOTACAO INICIAL
    - DOTAÇÃO ATUALIZADA = DOTACAO INICIAL + DOTACAO ADICIONAL + CANCELAMENTO DE DOTACAO + CANCEL-REMANEJA DOTACAO
    - SALDO DA DOTAÇÃO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
    """
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], "12", [], {}
    
    # Calcula o mês de referência dinamicamente a partir da coluna INMES
    mes_referencia = "12"  # Valor padrão
    if 'INMES' in df_2025.columns:
        max_mes = df_2025['INMES'].max()
        if pd.notna(max_mes):
            mes_referencia = str(int(max_mes)).zfill(2)  # Formata com 2 dígitos
    
    dados_numericos = []
    dados_para_ia = []
    
    # Agrupa por categoria com observed=True para evitar warning
    categorias = df_2025.groupby('CATEGORIA', observed=True).agg({
        'NOCATEGORIA': 'first',
        'DOTACAO INICIAL': 'sum',
        'DOTACAO ADICIONAL': 'sum',
        'CANCELAMENTO DE DOTACAO': 'sum',
        'CANCEL-REMANEJA DOTACAO': 'sum',
        'DESPESA EMPENHADA': 'sum',
        'DESPESA LIQUIDADA': 'sum',
        'DESPESA PAGA': 'sum'
    }).reset_index()
    
    for _, categoria in categorias.iterrows():
        dotacao_inicial = float(categoria['DOTACAO INICIAL'])
        dotacao_adicional = float(categoria['DOTACAO ADICIONAL'])
        cancelamento_dotacao = float(categoria['CANCELAMENTO DE DOTACAO'])
        cancel_remaneja = float(categoria['CANCEL-REMANEJA DOTACAO'])
        
        # FÓRMULA CORRIGIDA: DOTAÇÃO ATUALIZADA = INICIAL + ADICIONAL + CANCELAMENTO + CANCEL-REMANEJA
        dotacao_atualizada = dotacao_inicial + dotacao_adicional + cancelamento_dotacao + cancel_remaneja
        
        despesa_empenhada = float(categoria['DESPESA EMPENHADA'])
        despesa_liquidada = float(categoria['DESPESA LIQUIDADA'])
        despesa_paga = float(categoria['DESPESA PAGA'])
        
        # FÓRMULA CORRIGIDA: SALDO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
        saldo_dotacao = dotacao_atualizada - despesa_empenhada
        
        linha_categoria = {
            'tipo': 'principal',
            'especificacao': categoria['NOCATEGORIA'],
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'saldo_dotacao': saldo_dotacao,
            'dotacao_inicial_fmt': motor._formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor._formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor._formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor._formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor._formatar_numero(despesa_paga),
            'saldo_dotacao_fmt': motor._formatar_numero(saldo_dotacao)
        }
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Grupos dentro da categoria com observed=True
        grupos = df_2025[df_2025['CATEGORIA'] == categoria['CATEGORIA']].groupby('GRUPO', observed=True).agg({
            'NOGRUPO': 'first',
            'DOTACAO INICIAL': 'sum',
            'DOTACAO ADICIONAL': 'sum',
            'CANCELAMENTO DE DOTACAO': 'sum',
            'CANCEL-REMANEJA DOTACAO': 'sum',
            'DESPESA EMPENHADA': 'sum',
            'DESPESA LIQUIDADA': 'sum',
            'DESPESA PAGA': 'sum'
        }).reset_index()
        
        for _, grupo in grupos.iterrows():
            dot_inicial_grupo = float(grupo['DOTACAO INICIAL'])
            dot_adicional_grupo = float(grupo['DOTACAO ADICIONAL'])
            cancel_dotacao_grupo = float(grupo['CANCELAMENTO DE DOTACAO'])
            cancel_remaneja_grupo = float(grupo['CANCEL-REMANEJA DOTACAO'])
            
            # FÓRMULA CORRIGIDA PARA GRUPO
            dot_atualizada_grupo = dot_inicial_grupo + dot_adicional_grupo + cancel_dotacao_grupo + cancel_remaneja_grupo
            
            desp_emp_grupo = float(grupo['DESPESA EMPENHADA'])
            desp_liq_grupo = float(grupo['DESPESA LIQUIDADA'])
            desp_paga_grupo = float(grupo['DESPESA PAGA'])
            
            # FÓRMULA CORRIGIDA PARA SALDO DO GRUPO
            saldo_grupo = dot_atualizada_grupo - desp_emp_grupo
            
            linha_grupo = {
                'tipo': 'filha',
                'especificacao': f"  {grupo['NOGRUPO']}",
                'dotacao_inicial': dot_inicial_grupo,
                'dotacao_atualizada': dot_atualizada_grupo,
                'despesa_empenhada': desp_emp_grupo,
                'despesa_liquidada': desp_liq_grupo,
                'despesa_paga': desp_paga_grupo,
                'saldo_dotacao': saldo_grupo,
                'dotacao_inicial_fmt': motor._formatar_numero(dot_inicial_grupo),
                'dotacao_atualizada_fmt': motor._formatar_numero(dot_atualizada_grupo),
                'despesa_empenhada_fmt': motor._formatar_numero(desp_emp_grupo),
                'despesa_liquidada_fmt': motor._formatar_numero(desp_liq_grupo),
                'despesa_paga_fmt': motor._formatar_numero(desp_paga_grupo),
                'saldo_dotacao_fmt': motor._formatar_numero(saldo_grupo)
            }
            dados_numericos.append(linha_grupo)
    
    # Total geral
    linhas_principais = [d for d in dados_numericos if d['tipo'] == 'principal']
    if linhas_principais:
        totais = {
            'dotacao_inicial': sum(l['dotacao_inicial'] for l in linhas_principais),
            'dotacao_atualizada': sum(l['dotacao_atualizada'] for l in linhas_principais),
            'despesa_empenhada': sum(l['despesa_empenhada'] for l in linhas_principais),
            'despesa_liquidada': sum(l['despesa_liquidada'] for l in linhas_principais),
            'despesa_paga': sum(l['despesa_paga'] for l in linhas_principais),
            'saldo_dotacao': sum(l['saldo_dotacao'] for l in linhas_principais)
        }
        
        linha_total = {
            'tipo': 'total',
            'especificacao': 'TOTAL GERAL',
            **{f'{k}_fmt': motor._formatar_numero(v) for k, v in totais.items()}
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF
    dados_pdf = {
        "head": [['DESPESAS ORÇAMENTÁRIAS', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', 'SALDO DA DOTAÇÃO']],
        "body": [
            [linha['especificacao'], linha.get('dotacao_inicial_fmt', 'R$ 0,00'), linha.get('dotacao_atualizada_fmt', 'R$ 0,00'),
             linha.get('despesa_empenhada_fmt', 'R$ 0,00'), linha.get('despesa_liquidada_fmt', 'R$ 0,00'), 
             linha.get('despesa_paga_fmt', 'R$ 0,00'), linha.get('saldo_dotacao_fmt', 'R$ 0,00')]
            for linha in dados_numericos
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf

# =================================================================================
# FUNÇÃO: RECEITA POR ADMINISTRAÇÃO
# =================================================================================
def gerar_relatorio_por_adm(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """
    Gera relatório de receita por tipo de administração, com detalhamento por ORIGEM.
    """
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], [], {}
    
    dados_numericos = []
    dados_para_ia = []
    
    # Itera sobre cada CATEGORIA principal
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.mapas_nomes.get('categoria', {}).get(cod_cat)
        if not nome_categoria: continue
            
        df_categoria = df_2025[df_2025['CATEGORIA'] == cod_cat]
        if df_categoria.empty: continue
        
        # Calcula os valores totais para a CATEGORIA
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

            # Itera sobre cada ORIGEM dentro da CATEGORIA
            for cod_orig in origens.keys():
                nome_origem = motor.mapas_nomes.get('origem', {}).get(cod_orig)
                if not nome_origem: continue
                
                df_origem = df_categoria[df_categoria['ORIGEM'] == cod_orig]
                if df_origem.empty: continue

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
                 linha_fmt[f'{campo}_fmt'] = motor._formatar_numero(valor)
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
            **{f'{k}_fmt': motor._formatar_numero(v) for k, v in totais_gerais.items()}
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

# =================================================================================
# FUNÇÃO: RECEITA ESTIMADA (COMPARATIVO ANUAL)
# =================================================================================
def gerar_relatorio_receita_estimada(df_completo, estrutura_hierarquica, noug_selecionada=None):
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    dados_numericos, dados_para_ia = [], []
    totais = {
        2024: float(df_processar[df_processar['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum()),
        2025: float(df_processar[df_processar['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
    }
    for cod_cat, origens in estrutura_hierarquica.items():
        nome_categoria = motor.mapas_nomes.get('categoria', {}).get(cod_cat)
        if not nome_categoria: continue
        df_categoria = df_processar[df_processar['CATEGORIA'] == cod_cat]
        valor_2024_cat = float(df_categoria[df_categoria['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum())
        valor_2025_cat = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
        if valor_2024_cat == 0 and valor_2025_cat == 0: continue
        perc_2024_cat = (valor_2024_cat / totais[2024] * 100) if totais[2024] > 0 else 0
        perc_2025_cat = (valor_2025_cat / totais[2025] * 100) if totais[2025] > 0 else 0
        delta_perc_cat = ((valor_2025_cat - valor_2024_cat) / valor_2024_cat) * 100 if valor_2024_cat > 0 else (100 if valor_2025_cat > 0 else 0)
        linha_categoria = {'tipo': 'principal', 'especificacao': nome_categoria, 'valor_2024': valor_2024_cat, 'valor_2025': valor_2025_cat, 'perc_2024': perc_2024_cat, 'perc_2025': perc_2025_cat, 'delta': delta_perc_cat, 'valor_2024_fmt': motor._formatar_numero(valor_2024_cat), 'valor_2025_fmt': motor._formatar_numero(valor_2025_cat), 'perc_2024_fmt': f"{perc_2024_cat:.2f}%", 'perc_2025_fmt': f"{perc_2025_cat:.2f}%", 'delta_fmt': f"{delta_perc_cat:+.2f}%"}
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        for cod_orig in origens.keys():
            nome_origem = motor.mapas_nomes.get('origem', {}).get(cod_orig)
            if not nome_origem: continue
            df_origem = df_categoria[df_categoria['ORIGEM'] == cod_orig]
            valor_2024_orig = float(df_origem[df_origem['COEXERCICIO'] == 2024]['PREVISAO INICIAL LIQUIDA'].sum())
            valor_2025_orig = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
            if valor_2024_orig == 0 and valor_2025_orig == 0: continue
            perc_2024_orig = (valor_2024_orig / totais[2024] * 100) if totais[2024] > 0 else 0
            perc_2025_orig = (valor_2025_orig / totais[2025] * 100) if totais[2025] > 0 else 0
            delta_perc_orig = ((valor_2025_orig - valor_2024_orig) / valor_2024_orig) * 100 if valor_2024_orig > 0 else (100 if valor_2025_orig > 0 else 0)
            linha_origem = {'tipo': 'filha', 'especificacao': f"  {nome_origem}", 'valor_2024': valor_2024_orig, 'valor_2025': valor_2025_orig, 'perc_2024': perc_2024_orig, 'perc_2025': perc_2025_orig, 'delta': delta_perc_orig, 'valor_2024_fmt': motor._formatar_numero(valor_2024_orig), 'valor_2025_fmt': motor._formatar_numero(valor_2025_orig), 'perc_2024_fmt': f"{perc_2024_orig:.2f}%", 'perc_2025_fmt': f"{perc_2025_orig:.2f}%", 'delta_fmt': f"{delta_perc_orig:+.2f}%"}
            dados_numericos.append(linha_origem)
            dados_para_ia.append(linha_origem)
    if totais[2024] > 0 or totais[2025] > 0:
        delta_total = ((totais[2025] - totais[2024]) / totais[2024] * 100) if totais[2024] > 0 else 100
        linha_total = {'tipo': 'total', 'especificacao': 'TOTAL GERAL', 'valor_2024': totais[2024], 'valor_2025': totais[2025], 'perc_2024': 100.0, 'perc_2025': 100.0, 'delta': delta_total, 'valor_2024_fmt': motor._formatar_numero(totais[2024]), 'valor_2025_fmt': motor._formatar_numero(totais[2025]), 'perc_2024_fmt': "100,00%", 'perc_2025_fmt': "100,00%", 'delta_fmt': f"{delta_total:+.2f}%"}
        dados_numericos.append(linha_total)
        dados_para_ia.append(linha_total)
    dados_pdf = {"head": [['ESPECIFICAÇÃO', 'RECEITA PREVISTA 2024', '% 2024', 'RECEITA PREVISTA 2025', '% 2025', 'Δ%']], "body": [[linha['especificacao'], linha['valor_2024_fmt'], linha['perc_2024_fmt'], linha['valor_2025_fmt'], linha['perc_2025_fmt'], linha['delta_fmt']] for linha in dados_numericos]}
    return dados_numericos, dados_para_ia, dados_pdf

# =================================================================================
# FUNÇÕES DE COMPATIBILIDADE E ALIAS
# =================================================================================
def gerar_relatorio_estimada(df, h, n=None): 
    return gerar_relatorio_receita_estimada(df, h, n)

def gerar_relatorio_previsao_atualizada(df, h, n=None): 
    return [], [], {}