"""
Processador para conciliação SIGGO x SISGEPAT
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from ..models.bens_moveis_models import DadosBenMovel, ResultadoConciliacao
from .sisgepat_processor import SisgepatProcessor

class ConciliacaoProcessor:
    """Processa a conciliação entre SIGGO e SISGEPAT"""
    
    # COUGs a serem excluídas da apresentação consolidada
    COUGS_EXCLUIDAS = [
        '10101',    # CÂMARA LEGISLATIVA DO DISTRITO FEDERAL
        '150206',   # AGÊNCIA REGULADORA DE ÁGUAS E SANEAMENTO BÁSICO DO DF – ADASA
        '170202',   # FUNDAÇÃO HEMOCENTRO DE BRASÍLIA – FHB
        '190201',   # COMPANHIA URBANIZADORA DA NOVA CAPITAL DO BRASIL – NOVACAP
        '200201',   # SOCIEDADE DE TRANSPORTES COLETIVOS DE BRASÍLIA – TCB
        '200202',   # DEPARTAMENTO DE ESTRADAS DE RODAGEM DO DF – DER/DF
        '200204',   # COMPANHIA DO METROPOLITANO DO DF – METRÔ-DF
        '210203',   # EMPRESA DE ASSISTÊNCIA TÉCNICA E EXTENSÃO RURAL DO DF – EMATER
        '220201',   # DEPARTAMENTO DE TRÂNSITO DO DF – DETRAN-DF
        '280208',   # INSTITUTO DE MEIO AMBIENTE E RECURSOS HÍDRICOS DO DF
        '280209',   # COMPANHIA DE DESENVOLVIMENTO DA HABITAÇÃO DO DF – CODHAB
        '320205',   # SOCIEDADE DE ABASTECIMENTO DE BRASÍLIA – SAB
        '180902',   # FUNDO DE ASSISTÊNCIA SOCIAL DO DISTRITO FEDERAL
        '110903',   # FUNDO DE MANUTENÇÃO E DESENVOLVIMENTO DA EDUCAÇÃO BÁSICA
        '130911',   # FUNDO DE DEFESA DOS DIREITOS DO CONSUMIDOR
        '150901',   # FUNDO DA RECEITA TRIBUTÁRIA DO DF – PRÓ-RECEITA
        '160903',   # FUNDO ÚNICO DE MEIO AMBIENTE DO DISTRITO FEDERAL
        '220904',   # FUNDO DE MODERNIZAÇÃO, MANUTENÇÃO E REEQUIPAMENTO DA PMDF – FUNPM
        '280901',   # FUNDO PENITENCIÁRIO DO DF – FUNPDF
        '220908',   # FUNDO DE SEGURANÇA PÚBLICA DO DISTRITO FEDERAL
        '220909',   # FUNDO DE DESENVOLVIMENTO URBANO DO DISTRITO FEDERAL
        '120901',   # Fundos adicionais
        '180904',   # Fundos adicionais
        '150203',   # INSTITUTO DE ECOLOGIA E MEIO AMBIENTE
        '230201',   # FUNDAÇÃO CULTURAL DO DF
        '530101',   # SEC. DE EST. DE MICRO E PEQ. EMP. E ECON. SOL. DF
        '550101'    # SECRETARIA DE EST. DE REGUL. DE CONDOMÍNIOS DO DF
    ]
    
    def processar_conciliacao(self, 
                            df_completo: pd.DataFrame,
                            dados_sisgepat: Dict[Tuple[str, str], float],
                            df_depara: Optional[pd.DataFrame] = None,
                            noug_selecionada: Optional[str] = None) -> ResultadoConciliacao:
        """
        Realiza a conciliação entre SIGGO e SISGEPAT
        
        Args:
            df_completo: DataFrame com dados de bens móveis
            dados_sisgepat: Dicionário com dados do SISGEPAT
            df_depara: DataFrame com DE-PARA Local -> COUG
            noug_selecionada: NOUG selecionada para filtro
            
        Returns:
            ResultadoConciliacao com os dados processados
        """
        # Se não temos dados SISGEPAT, cria dicionário vazio
        if dados_sisgepat is None:
            dados_sisgepat = {}
        
        # Filtra as COUGs excluídas
        df_filtrado = df_completo[~df_completo['COUG'].astype(str).isin(self.COUGS_EXCLUIDAS)].copy()
        
        # Aplica filtro de NOUG se especificado
        if noug_selecionada and noug_selecionada != 'todos':
            df_filtrado = df_filtrado[df_filtrado['NOUG'] == noug_selecionada].copy()
        
        # Identifica COUG do DFTRANS
        coug_dftrans = None
        if df_depara is not None:
            coug_dftrans = SisgepatProcessor.identificar_coug_dftrans(df_depara)
        
        # Cria estrutura de dados combinados
        dados_combinados = self._combinar_dados_siggo_sisgepat(
            df_filtrado, dados_sisgepat, coug_dftrans
        )
        
        # Processa dados do DFTRANS
        dados_dftrans = self._processar_dftrans(dados_sisgepat, coug_dftrans)
        
        # Converte para modelo de dados
        dados_por_noug = self._converter_para_modelo(dados_combinados)
        
        # Se houver DFTRANS, adiciona como NOUG especial
        if dados_dftrans:
            dados_por_noug[SisgepatProcessor.NOME_DFTRANS] = [
                DadosBenMovel(
                    coug=dados['COUG'],
                    subitem=dados['SUBITEM'],
                    bens_moveis=0,
                    bens_moveis_almox=0,
                    bens_moveis_import=0,
                    sisgepat=dados['SISGEPAT']
                )
                for dados in dados_dftrans.values()
            ]
        
        # Calcula totais
        total_geral = self._calcular_totais(dados_por_noug)
        
        # Prepara dados para PDF
        dados_pdf = self._preparar_dados_pdf(dados_por_noug, total_geral)
        
        return ResultadoConciliacao(
            dados_por_noug=dados_por_noug,
            total_geral=total_geral,
            dados_pdf=dados_pdf
        )
    
    def _combinar_dados_siggo_sisgepat(self, df_filtrado: pd.DataFrame, 
                                      dados_sisgepat: Dict,
                                      coug_dftrans: str) -> Dict:
        """Combina dados do SIGGO com dados do SISGEPAT"""
        dados_combinados = {}
        
        print(f"\n📊 Processando {len(df_filtrado)} linhas da planilha base...")
        linhas_com_valor = 0
        
        for _, row in df_filtrado.iterrows():
            coug = str(row['COUG']).strip()
            
            # Garante que SUBITEM seja formatado corretamente
            try:
                subitem = str(int(float(row['SUBITEM']))).zfill(2) if pd.notna(row['SUBITEM']) else '00'
            except:
                subitem = str(row['SUBITEM']).strip().zfill(2) if pd.notna(row['SUBITEM']) else '00'
                
            noug = row['NOUG']
            
            if noug not in dados_combinados:
                dados_combinados[noug] = {}
            
            chave = (coug, subitem)
            
            # Captura os valores
            bens_moveis = float(row['BENS_MOVEIS']) if pd.notna(row['BENS_MOVEIS']) else 0.0
            bens_moveis_almox = float(row['BENS_MOVEIS_ALMOX']) if pd.notna(row['BENS_MOVEIS_ALMOX']) else 0.0
            bens_moveis_import = float(row['BENS_MOVEIS_IMPORT']) if pd.notna(row['BENS_MOVEIS_IMPORT']) else 0.0
            
            # Debug para valores que deveriam aparecer
            total_linha = bens_moveis + bens_moveis_almox + bens_moveis_import
            if total_linha > 0:
                linhas_com_valor += 1
                if linhas_com_valor <= 10:
                    print(f"  ✅ COUG {coug}, Subitem {subitem}: BM={bens_moveis:,.2f}, ALMOX={bens_moveis_almox:,.2f}, IMPORT={bens_moveis_import:,.2f}")
            
            # Se a chave já existe, SOMA os valores
            if chave in dados_combinados[noug]:
                dados_combinados[noug][chave]['BENS_MOVEIS'] += bens_moveis
                dados_combinados[noug][chave]['BENS_MOVEIS_ALMOX'] += bens_moveis_almox
                dados_combinados[noug][chave]['BENS_MOVEIS_IMPORT'] += bens_moveis_import
                print(f"  ➕ Somando valores para COUG {coug}, Subitem {subitem} (linha duplicada)")
            else:
                dados_combinados[noug][chave] = {
                    'COUG': coug,
                    'SUBITEM': subitem,
                    'BENS_MOVEIS': bens_moveis,
                    'BENS_MOVEIS_ALMOX': bens_moveis_almox,
                    'BENS_MOVEIS_IMPORT': bens_moveis_import,
                    'SISGEPAT': dados_sisgepat.get(chave, 0)
                }
        
        print(f"📊 Total de linhas com valores > 0: {linhas_com_valor}")
        
        # Adiciona dados que existem apenas no SISGEPAT (exceto DFTRANS e COUGs excluídas)
        for (coug, subitem), valor in dados_sisgepat.items():
            if coug in self.COUGS_EXCLUIDAS or coug == coug_dftrans:
                continue
                
            # Busca NOUG da COUG
            noug_match = df_filtrado[df_filtrado['COUG'] == coug]['NOUG'].values
            if len(noug_match) > 0:
                noug = noug_match[0]
                
                if noug not in dados_combinados:
                    dados_combinados[noug] = {}
                    
                chave = (coug, subitem)
                if chave not in dados_combinados[noug]:
                    dados_combinados[noug][chave] = {
                        'COUG': coug,
                        'SUBITEM': subitem,
                        'BENS_MOVEIS': 0,
                        'BENS_MOVEIS_ALMOX': 0,
                        'BENS_MOVEIS_IMPORT': 0,
                        'SISGEPAT': valor
                    }
        
        return dados_combinados
    
    def _processar_dftrans(self, dados_sisgepat: Dict, coug_dftrans: str) -> Dict:
        """Processa dados específicos do DFTRANS"""
        dados_dftrans = {}
        
        if coug_dftrans:
            for (coug, subitem), valor in dados_sisgepat.items():
                if coug == coug_dftrans:
                    dados_dftrans[(coug, subitem)] = {
                        'COUG': coug,
                        'SUBITEM': subitem,
                        'BENS_MOVEIS': 0,
                        'BENS_MOVEIS_ALMOX': 0,
                        'BENS_MOVEIS_IMPORT': 0,
                        'SISGEPAT': valor
                    }
        
        return dados_dftrans
    
    def _converter_para_modelo(self, dados_combinados: Dict) -> Dict[str, List[DadosBenMovel]]:
        """Converte dados combinados para o modelo DadosBenMovel"""
        dados_por_noug = {}
        
        for noug, dados_noug in dados_combinados.items():
            dados_por_noug[noug] = [
                DadosBenMovel(
                    coug=dados['COUG'],
                    subitem=dados['SUBITEM'],
                    bens_moveis=dados['BENS_MOVEIS'],
                    bens_moveis_almox=dados['BENS_MOVEIS_ALMOX'],
                    bens_moveis_import=dados['BENS_MOVEIS_IMPORT'],
                    sisgepat=dados['SISGEPAT']
                )
                for dados in dados_noug.values()
            ]
        
        return dados_por_noug
    
    def _calcular_totais(self, dados_por_noug: Dict[str, List[DadosBenMovel]]) -> Dict[str, float]:
        """Calcula totais gerais"""
        totais = {
            'BENS_MOVEIS': 0,
            'BENS_MOVEIS_ALMOX': 0,
            'BENS_MOVEIS_IMPORT': 0,
            'SISGEPAT': 0
        }
        
        for dados_noug in dados_por_noug.values():
            for item in dados_noug:
                totais['BENS_MOVEIS'] += item.bens_moveis
                totais['BENS_MOVEIS_ALMOX'] += item.bens_moveis_almox
                totais['BENS_MOVEIS_IMPORT'] += item.bens_moveis_import
                totais['SISGEPAT'] += item.sisgepat
        
        return totais
    
    def _preparar_dados_pdf(self, dados_por_noug: Dict[str, List[DadosBenMovel]], 
                           total_geral: Dict[str, float]) -> Dict:
        """Prepara dados para exportação PDF"""
        from utils.formatacao import formatar_numero
        
        dados_pdf_body = []
        
        for noug, dados_noug in sorted(dados_por_noug.items()):
            # Adiciona linhas de dados
            for item in sorted(dados_noug, key=lambda x: (x.coug, x.subitem)):
                dados_pdf_body.append([
                    noug,
                    item.coug,
                    item.subitem,
                    formatar_numero(item.bens_moveis),
                    formatar_numero(item.bens_moveis_almox),
                    formatar_numero(item.bens_moveis_import),
                    formatar_numero(item.saldo_siggo),
                    formatar_numero(item.sisgepat),
                    formatar_numero(item.diferenca)
                ])
        
        # Adiciona total geral
        total_siggo = total_geral['BENS_MOVEIS'] + total_geral['BENS_MOVEIS_ALMOX'] + total_geral['BENS_MOVEIS_IMPORT']
        diferenca_total = total_siggo - total_geral['SISGEPAT']
        
        dados_pdf_body.append([
            'TOTAL GERAL',
            '',
            '',
            formatar_numero(total_geral['BENS_MOVEIS']),
            formatar_numero(total_geral['BENS_MOVEIS_ALMOX']),
            formatar_numero(total_geral['BENS_MOVEIS_IMPORT']),
            formatar_numero(total_siggo),
            formatar_numero(total_geral['SISGEPAT']),
            formatar_numero(diferenca_total)
        ])
        
        return {
            "head": [[
                'NOUG',
                'Código\nda UG',
                'Subitem',
                'Saldo\nBens Móveis',
                'Saldo Bens\nMóveis em\nAlmoxarifado',
                'Saldo Bens\nMóveis em\nImportação',
                'Saldo Total\nBens Móveis\nno SIGGO',
                'Saldo Total\nBens Móveis\nno SISGEPAT',
                'Diferença'
            ]],
            "body": dados_pdf_body
        }