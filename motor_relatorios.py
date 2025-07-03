import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

class MotorRelatorios:
    """Motor unificado para relatórios de receita e despesa"""
    
    def __init__(self, df: pd.DataFrame, tipo_dados: str = 'receita'):
        self.df = df
        self.tipo_dados = tipo_dados  # 'receita' ou 'despesa'
        self.mapas_nomes = self._criar_mapas_de_nomes()
    
    def _criar_mapas_de_nomes(self) -> Dict[str, Dict]:
        """Cria mapas de códigos para nomes de forma genérica"""
        mapas = {}
        
        if self.tipo_dados == 'receita':
            # Mapeamentos para receita
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIARECEITA'].to_dict(),
                    'origem': self.df.drop_duplicates('ORIGEM').set_index('ORIGEM')['NOFONTERECEITA'].to_dict(),
                    'especie': self.df.drop_duplicates('ESPECIE').set_index('ESPECIE')['NOSUBFONTERECEITA'].to_dict(),
                    'alinea': self.df.drop_duplicates('ALINEA').set_index('ALINEA')['NOALINEA'].to_dict()
                })
        
        elif self.tipo_dados == 'despesa':
            # Mapeamentos para despesa
            if 'CATEGORIA' in self.df.columns:
                mapas.update({
                    'categoria': self.df.drop_duplicates('CATEGORIA').set_index('CATEGORIA')['NOCATEGORIA'].to_dict(),
                    'grupo': self.df.drop_duplicates('GRUPO').set_index('GRUPO')['NOGRUPO'].to_dict(),
                    'modalidade': self.df.drop_duplicates('MODALIDADE').set_index('MODALIDADE')['NOMODALIDADE'].to_dict(),
                    'elemento': self.df.drop_duplicates('ELEMENTO').set_index('ELEMENTO')['NOELEMENTO'].to_dict(),
                })
        
        return mapas
    
    @staticmethod
    def _formatar_numero(valor: float) -> str:
        """Formata números para padrão brasileiro"""
        if pd.isna(valor) or valor == 0: 
            return "R$ 0,00"
        if valor < 0: 
            return f"(R$ {abs(valor):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def _formatar_numero_despesa(valor: float) -> str:
        """Formata números para despesa (sem R$)"""
        if pd.isna(valor) or valor == 0: 
            return "0,00"
        if valor < 0: 
            return f"({abs(valor):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def filtrar_por_noug(self, noug_selecionada: Optional[str] = None) -> pd.DataFrame:
        """Aplica filtro por unidade gestora"""
        if noug_selecionada and noug_selecionada != 'todos':
            return self.df[self.df['NOUG'] == noug_selecionada]
        return self.df.copy()
    
    def obter_mes_referencia(self, exercicio: int = None) -> str:
        """Obtém mês de referência dos dados"""
        if exercicio is None:
            exercicio = 2025  # SEMPRE usar 2025 para ambos (receita e despesa)
            
        df_exercicio = self.df[self.df['COEXERCICIO'] == exercicio]
        if not df_exercicio.empty and 'INMES' in df_exercicio.columns:
            max_mes_num = int(df_exercicio['INMES'].max())
            meses_map = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            return meses_map.get(max_mes_num, "Mês Inválido")
        return "N/A"
    
    # ===================== MÉTODOS PARA RECEITA =====================
    
    def processar_hierarquia_receita(self, estrutura_hierarquica: Dict, noug_selecionada: Optional[str] = None) -> Tuple[List[Dict], Dict]:
        """Processa hierarquia de receitas"""
        df_processar = self.filtrar_por_noug(noug_selecionada)
        dados_numericos = []
        grandes_totais = {'pi_2025': 0, 'pa_2025': 0, 'rr_2025': 0, 'rr_2024': 0}
        
        for cod_cat, origens in estrutura_hierarquica.items():
            nome_categoria = self.mapas_nomes.get('categoria', {}).get(cod_cat)
            df_categoria = df_processar[df_processar['CATEGORIA'] == cod_cat]
            
            # Cálculos da categoria
            pi = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
            pa = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum())
            rr_2025 = float(df_categoria[df_categoria['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum())
            rr_2024 = float(df_categoria[df_categoria['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
            
            if nome_categoria and any(v != 0 for v in [pi, pa, rr_2025, rr_2024]):
                linha_dados = {
                    'tipo': 'level-1', 
                    'especificacao': nome_categoria, 
                    'pi_2025': pi, 'pa_2025': pa, 
                    'rr_2025': rr_2025, 'rr_2024': rr_2024
                }
                dados_numericos.append(linha_dados)
                
                # Atualiza totais
                for key in grandes_totais.keys():
                    grandes_totais[key] += linha_dados[key]
                
                # Processa origens e espécies
                dados_numericos.extend(self._processar_origens_especies(
                    df_processar, origens, cod_cat
                ))
        
        # Adiciona linha de total
        dados_numericos.append({
            'tipo': 'total', 
            'especificacao': 'SOMATÓRIO', 
            **grandes_totais
        })
        
        return dados_numericos, grandes_totais
    
    def _processar_origens_especies(self, df_processar: pd.DataFrame, origens: Dict, cod_cat: str) -> List[Dict]:
        """Processa origens e espécies de uma categoria"""
        dados = []
        
        if not origens:
            return dados
        
        for cod_orig, especies in origens.items():
            nome_origem = self.mapas_nomes.get('origem', {}).get(cod_orig)
            df_origem = df_processar[df_processar['ORIGEM'] == cod_orig]
            
            # Cálculos da origem
            pi_o = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
            pa_o = float(df_origem[df_origem['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum())
            rr_o_2025 = float(df_origem[df_origem['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum())
            rr_o_2024 = float(df_origem[df_origem['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
            
            if nome_origem and any(v != 0 for v in [pi_o, pa_o, rr_o_2025, rr_o_2024]):
                dados.append({
                    'tipo': 'level-2', 
                    'especificacao': nome_origem, 
                    'pi_2025': pi_o, 'pa_2025': pa_o, 
                    'rr_2025': rr_o_2025, 'rr_2024': rr_o_2024
                })
                
                # Processa espécies
                dados.extend(self._processar_especies_alineas(
                    df_processar, especies
                ))
        
        return dados
    
    def _processar_especies_alineas(self, df_processar: pd.DataFrame, especies: List[str]) -> List[Dict]:
        """Processa espécies e alíneas"""
        dados = []
        
        if not especies:
            return dados
        
        for cod_esp in especies:
            nome_especie = self.mapas_nomes.get('especie', {}).get(cod_esp)
            df_especie = df_processar[df_processar['ESPECIE'] == cod_esp]
            
            # Cálculos da espécie
            pi_e = float(df_especie[df_especie['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
            pa_e = float(df_especie[df_especie['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum())
            rr_e_2025 = float(df_especie[df_especie['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum())
            rr_e_2024 = float(df_especie[df_especie['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
            
            if nome_especie and any(v != 0 for v in [pi_e, pa_e, rr_e_2025, rr_e_2024]):
                dados.append({
                    'tipo': 'level-3', 
                    'especificacao': nome_especie, 
                    'pi_2025': pi_e, 'pa_2025': pa_e, 
                    'rr_2025': rr_e_2025, 'rr_2024': rr_e_2024
                })
                
                # Processa alíneas
                dados.extend(self._processar_alineas(
                    df_processar, cod_esp
                ))
        
        return dados
    
    def _processar_alineas(self, df_processar: pd.DataFrame, cod_esp: str) -> List[Dict]:
        """Processa alíneas de uma espécie"""
        dados = []
        
        df_alineas = df_processar[df_processar['ALINEA'].str.startswith(cod_esp, na=False)]
        
        if not df_alineas.empty:
            for cod_alinea, group_alinea in df_alineas.sort_values('ALINEA').groupby('ALINEA'):
                nome_alinea = self.mapas_nomes.get('alinea', {}).get(cod_alinea)
                
                pi_a = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['PREVISAO INICIAL LIQUIDA'].sum())
                pa_a = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['PREVISAO ATUALIZADA LIQUIDA'].sum())
                rr_a_2025 = float(group_alinea[group_alinea['COEXERCICIO'] == 2025]['RECEITA LIQUIDA'].sum())
                rr_a_2024 = float(group_alinea[group_alinea['COEXERCICIO'] == 2024]['RECEITA LIQUIDA'].sum())
                
                if nome_alinea and any(v != 0 for v in [pi_a, pa_a, rr_a_2025, rr_a_2024]):
                    dados.append({
                        'tipo': 'level-4', 
                        'especificacao': nome_alinea, 
                        'pi_2025': pi_a, 'pa_2025': pa_a, 
                        'rr_2025': rr_a_2025, 'rr_2024': rr_a_2024
                    })
        
        return dados
    
    # ===================== MÉTODOS PARA DESPESA =====================
    
    def processar_balanco_despesa(self, noug_selecionada: Optional[str] = None) -> Tuple[List[Dict], str, List[Dict], Dict]:
        """Processa balanço orçamentário da despesa"""
        df_processar = self.filtrar_por_noug(noug_selecionada)
        mes_referencia = self.obter_mes_referencia(2025)
        
        dados_numericos = []
        
        # Filtra apenas dados do exercício 2025
        df_atual = df_processar[df_processar['COEXERCICIO'] == 2025]
        
        if df_atual.empty:
            return [], mes_referencia, [], {}
        
        # Calcula dotação atualizada
        df_atual = df_atual.copy()
        df_atual['DOTACAO_ATUALIZADA'] = (
            df_atual['DOTACAO INICIAL'] + 
            df_atual['DOTACAO ADICIONAL'] - 
            df_atual['CANCELAMENTO DE DOTACAO'] - 
            df_atual['CANCEL-REMANEJA DOTACAO']
        )
        
        # Agrupa por categoria - APENAS onde há dados não-zero
        categorias = df_atual.groupby(['CATEGORIA', 'NOCATEGORIA']).agg({
            'DOTACAO INICIAL': 'sum',
            'DOTACAO ADICIONAL': 'sum',
            'DESPESA EMPENHADA': 'sum',
            'DESPESA LIQUIDADA': 'sum',
            'DESPESA PAGA': 'sum',
            'DOTACAO_ATUALIZADA': 'sum'
        }).reset_index()
        
        # FILTRO: Remove categorias onde TODOS os valores são zero
        categorias = categorias[
            (categorias['DOTACAO INICIAL'] != 0) | 
            (categorias['DOTACAO ADICIONAL'] != 0) | 
            (categorias['DESPESA EMPENHADA'] != 0) | 
            (categorias['DESPESA LIQUIDADA'] != 0) | 
            (categorias['DESPESA PAGA'] != 0) | 
            (categorias['DOTACAO_ATUALIZADA'] != 0)
        ].copy()
        
        # Ordena por categoria
        categorias = categorias.sort_values('CATEGORIA')
        
        # Processa cada categoria
        for _, row in categorias.iterrows():
            categoria_cod = row['CATEGORIA']
            categoria_nome = row['NOCATEGORIA']
            
            # Calcula saldo da dotação
            saldo_dotacao = row['DOTACAO_ATUALIZADA'] - row['DESPESA EMPENHADA']
            
            # Linha da categoria principal
            linha_categoria = {
                'tipo': 'level-1',
                'categoria': categoria_cod,
                'especificacao': f"DESPESAS {categoria_nome.upper()} (CATEGORIA {categoria_cod})",
                'dotacao_inicial': float(row['DOTACAO INICIAL']),
                'dotacao_adicional': float(row['DOTACAO ADICIONAL']),
                'dotacao_atualizada': float(row['DOTACAO_ATUALIZADA']),
                'despesa_empenhada': float(row['DESPESA EMPENHADA']),
                'despesa_liquidada': float(row['DESPESA LIQUIDADA']),
                'despesa_paga': float(row['DESPESA PAGA']),
                'saldo_dotacao': float(saldo_dotacao)
            }
            dados_numericos.append(linha_categoria)
            
            # Processa grupos dentro da categoria
            df_categoria = df_atual[df_atual['CATEGORIA'] == categoria_cod]
            grupos = df_categoria.groupby(['GRUPO', 'NOGRUPO']).agg({
                'DOTACAO INICIAL': 'sum',
                'DOTACAO ADICIONAL': 'sum',
                'DESPESA EMPENHADA': 'sum',
                'DESPESA LIQUIDADA': 'sum',
                'DESPESA PAGA': 'sum',
                'DOTACAO_ATUALIZADA': 'sum'
            }).reset_index()
            
            # FILTRO: Remove grupos onde TODOS os valores são zero
            grupos = grupos[
                (grupos['DOTACAO INICIAL'] != 0) | 
                (grupos['DOTACAO ADICIONAL'] != 0) | 
                (grupos['DESPESA EMPENHADA'] != 0) | 
                (grupos['DESPESA LIQUIDADA'] != 0) | 
                (grupos['DESPESA PAGA'] != 0) | 
                (grupos['DOTACAO_ATUALIZADA'] != 0)
            ].copy()
            
            # Ordena grupos por código
            grupos = grupos.sort_values('GRUPO')
            
            for _, grupo_row in grupos.iterrows():
                grupo_cod = grupo_row['GRUPO']
                grupo_nome = grupo_row['NOGRUPO']
                
                saldo_grupo = grupo_row['DOTACAO_ATUALIZADA'] - grupo_row['DESPESA EMPENHADA']
                
                linha_grupo = {
                    'tipo': 'level-2',
                    'categoria': categoria_cod,
                    'grupo': grupo_cod,
                    'especificacao': f"  {grupo_nome.title()}",
                    'dotacao_inicial': float(grupo_row['DOTACAO INICIAL']),
                    'dotacao_adicional': float(grupo_row['DOTACAO ADICIONAL']),
                    'dotacao_atualizada': float(grupo_row['DOTACAO_ATUALIZADA']),
                    'despesa_empenhada': float(grupo_row['DESPESA EMPENHADA']),
                    'despesa_liquidada': float(grupo_row['DESPESA LIQUIDADA']),
                    'despesa_paga': float(grupo_row['DESPESA PAGA']),
                    'saldo_dotacao': float(saldo_grupo)
                }
                dados_numericos.append(linha_grupo)
        
        # Calcula totais gerais apenas dos dados que realmente existem
        if not dados_numericos:
            return [], mes_referencia, [], {}
            
        # Formata dados para apresentação
        dados_formatados = self._formatar_dados_despesa(dados_numericos)
        
        # Gera dados para PDF
        dados_pdf = self._gerar_dados_pdf_despesa(dados_numericos, mes_referencia)
        
        return dados_formatados, mes_referencia, dados_numericos, dados_pdf
    
    def _formatar_dados_despesa(self, dados_numericos: List[Dict]) -> List[Dict]:
        """Formata dados de despesa para apresentação"""
        dados_formatados = []
        
        for linha in dados_numericos:
            linha_fmt = linha.copy()
            
            # Formata valores monetários (sem R$ para despesa)
            campos_monetarios = [
                'dotacao_inicial', 'dotacao_adicional', 'dotacao_atualizada',
                'despesa_empenhada', 'despesa_liquidada', 'despesa_paga', 'saldo_dotacao'
            ]
            
            for campo in campos_monetarios:
                if campo in linha_fmt:
                    linha_fmt[f'{campo}_fmt'] = self._formatar_numero_despesa(linha_fmt[campo])
            
            dados_formatados.append(linha_fmt)
        
        return dados_formatados
    
    def _gerar_dados_pdf_despesa(self, dados_numericos: List[Dict], mes_referencia: str) -> Dict:
        """Gera dados para PDF de despesa"""
        return {
            "head": [[
                'DESPESAS ORÇAMENTÁRIAS',
                'DOTAÇÃO INICIAL',
                'DOTAÇÃO ADICIONAL',
                'DESPESA EMPENHADA',
                'DESPESA LIQUIDADA',
                'DESPESA PAGA',
                'SALDO DA DOTAÇÃO'
            ]],
            "body": [
                [
                    linha['especificacao'],
                    self._formatar_numero_despesa(linha.get('dotacao_inicial', 0)),
                    self._formatar_numero_despesa(linha.get('dotacao_adicional', 0)),
                    self._formatar_numero_despesa(linha.get('despesa_empenhada', 0)),
                    self._formatar_numero_despesa(linha.get('despesa_liquidada', 0)),
                    self._formatar_numero_despesa(linha.get('despesa_paga', 0)),
                    self._formatar_numero_despesa(linha.get('saldo_dotacao', 0))
                ]
                for linha in dados_numericos
            ]
        }
    
    # ===================== MÉTODOS COMUNS =====================
    
    def formatar_dados_para_apresentacao(self, dados_numericos: List[Dict]) -> List[Dict]:
        """Formata dados numéricos para apresentação"""
        dados_formatados = []
        
        for linha in dados_numericos:
            linha_fmt = linha.copy()
            
            # Calcula saldo se necessário
            if 'rr_2025' in linha and 'rr_2024' in linha:
                linha_fmt['saldo'] = linha['rr_2025'] - linha['rr_2024']
            
            # Formata todos os valores numéricos
            for key, valor in linha.items():
                if isinstance(valor, (int, float)) and key not in ['tipo']:
                    linha_fmt[f'{key}_fmt'] = self._formatar_numero(valor)
            
            # Formata saldo se existe
            if 'saldo' in linha_fmt:
                linha_fmt['saldo_fmt'] = self._formatar_numero(linha_fmt['saldo'])
            
            dados_formatados.append(linha_fmt)
        
        return dados_formatados
    
    def gerar_dados_pdf(self, dados_numericos: List[Dict], mes_referencia: str, tipo_relatorio: str = 'balanco') -> Dict:
        """Gera dados formatados para PDF"""
        if tipo_relatorio == 'balanco' and self.tipo_dados == 'receita':
            return {
                "head": [[
                    'RECEITAS', 
                    'PREVISÃO INICIAL\n2025', 
                    'PREVISÃO ATUALIZADA\n2025', 
                    f'RECEITA REALIZADA\n{mes_referencia}/2025', 
                    f'RECEITA REALIZADA\n{mes_referencia}/2024', 
                    'VARIAÇÃO\n2025 x 2024'
                ]],
                "body": [
                    [
                        linha['especificacao'], 
                        self._formatar_numero(linha.get('pi_2025', 0)),
                        self._formatar_numero(linha.get('pa_2025', 0)),
                        self._formatar_numero(linha.get('rr_2025', 0)),
                        self._formatar_numero(linha.get('rr_2024', 0)),
                        self._formatar_numero(linha.get('rr_2025', 0) - linha.get('rr_2024', 0))
                    ] 
                    for linha in dados_numericos
                ]
            }
        
        return {"head": [], "body": []}


# ===================== FUNÇÕES DE COMPATIBILIDADE =====================

def gerar_balanco_orcamentario(df_completo, estrutura_hierarquica, noug_selecionada=None):
    """Mantém compatibilidade com código atual - RECEITA"""
    motor = MotorRelatorios(df_completo, tipo_dados='receita')
    mes_referencia = motor.obter_mes_referencia()
    
    dados_numericos, grandes_totais = motor.processar_hierarquia_receita(
        estrutura_hierarquica, noug_selecionada
    )
    
    dados_formatados = motor.formatar_dados_para_apresentacao(dados_numericos)
    dados_pdf = motor.gerar_dados_pdf(dados_numericos, mes_referencia)
    
    return dados_formatados, mes_referencia, dados_numericos, dados_pdf

def gerar_balanco_despesa(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """Função para balanço de despesa"""
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    return motor.processar_balanco_despesa(noug_selecionada)

# Placeholder para futuras implementações
def gerar_relatorio_estimada(df, h): 
    return [], []

def gerar_relatorio_por_adm(df, h, c): 
    return [], {}, {}, []

def gerar_relatorio_previsao_atualizada(df, h): 
    return [], {}, []