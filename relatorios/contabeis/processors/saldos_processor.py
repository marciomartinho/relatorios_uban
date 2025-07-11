"""
Processador para saldos contábeis
"""
import pandas as pd
from typing import Dict, Optional
from utils.formatacao import formatar_numero
from ..models.bens_moveis_models import DadosSaldosContabeis

class SaldosContabeisProcessor:
    """Processa os saldos contábeis da planilha 19-SaldoBensMoveis.xlsx"""
    
    @staticmethod
    def processar_saldos(df_saldos: pd.DataFrame, 
                        dict_contas: Optional[Dict] = None) -> Optional[DadosSaldosContabeis]:
        """
        Processa os saldos contábeis
        
        Args:
            df_saldos: DataFrame carregado da planilha
            dict_contas: Dicionário com mapeamento COCONTACONTABIL -> NOCONTACONTABIL
            
        Returns:
            DadosSaldosContabeis ou None se não houver dados
        """
        if df_saldos is None or df_saldos.empty:
            return None
            
        dados_saldos = []
        
        try:
            print(f"📊 Processando saldos contábeis...")
            
            # Pega a primeira coluna (códigos) e a última coluna (saldos)
            primeira_coluna = df_saldos.columns[0]
            ultima_coluna = df_saldos.columns[-1]
            
            print(f"📊 Coluna de códigos: {primeira_coluna}")
            print(f"📊 Coluna de saldos: {ultima_coluna}")
            
            # Identifica colunas numéricas para determinar o mês
            colunas_numericas = []
            for col in df_saldos.columns:
                try:
                    num = int(str(col))
                    if 1 <= num <= 12:  # Apenas meses válidos
                        colunas_numericas.append(num)
                except:
                    pass
            
            # Determina o mês de referência
            if colunas_numericas:
                mes_numero = max(colunas_numericas)
                meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                mes_referencia = f"{meses[mes_numero]}/2025"
            else:
                mes_referencia = "Junho/2025"
            
            print(f"📊 Mês de referência: {mes_referencia}")
            
            # Processa cada linha
            for idx, row in df_saldos.iterrows():
                try:
                    # Pega o código da primeira coluna
                    codigo = str(row[primeira_coluna]).strip()
                    
                    # Verifica se é um código válido (começa com números)
                    if not codigo or not codigo[0].isdigit():
                        continue
                    
                    # Remove possível .0 no final se existir
                    if codigo.endswith('.0'):
                        codigo = codigo[:-2]
                    
                    # Adiciona '00' ao final do código
                    codigo_formatado = codigo + '00'
                    
                    # Busca o nome da conta se o dicionário foi fornecido
                    nome_conta = ""
                    if dict_contas and codigo_formatado in dict_contas:
                        nome_conta = dict_contas[codigo_formatado]
                    
                    # Pega o saldo da última coluna
                    saldo = row[ultima_coluna]
                    
                    # Converte para float
                    if pd.isna(saldo) or saldo == '':
                        saldo = 0
                    else:
                        saldo = float(saldo)
                    
                    # Adiciona apenas se tiver saldo positivo
                    if saldo > 0:
                        dados_saldos.append({
                            'codigo': codigo_formatado,
                            'nome': nome_conta,
                            'saldo': saldo,
                            'saldo_fmt': formatar_numero(saldo)
                        })
                        
                except Exception as e:
                    continue
            
            # Calcula o total
            total_saldos = sum(item['saldo'] for item in dados_saldos)
            
            print(f"✅ Total de contas com saldo: {len(dados_saldos)}")
            print(f"💰 Total geral: {formatar_numero(total_saldos)}")
            
            if not dados_saldos:
                return None
            
            return DadosSaldosContabeis(
                itens=sorted(dados_saldos, key=lambda x: x['codigo']),
                total=total_saldos,
                total_fmt=formatar_numero(total_saldos),
                mes_referencia=mes_referencia
            )
            
        except Exception as e:
            print(f"❌ Erro ao processar saldos contábeis: {str(e)}")
            return None