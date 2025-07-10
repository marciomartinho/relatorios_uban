"""
Relatório: Despesa por Natureza (Categoria/Grupo)
Baseado no Balanço Orçamentário da Despesa com detalhamento por elemento de despesa
"""
from ..utils import MotorRelatorios, obter_mes_numero

def gerar_relatorio_despesa_natureza(df_completo, estrutura_hierarquica=None, noug_selecionada=None):
    """
    Gera o relatório de despesa por natureza com detalhamento por elemento
    
    REGRAS DE NEGÓCIO:
    - Agrupa primeiro por CATEGORIA/GRUPO (igual ao balanço de despesa)
    - Para cada categoria (exceto RESERVA DE CONTINGÊNCIA), permite expandir para ver elementos
    - CONATUREZA que começam com 31: PESSOAL E ENCARGOS SOCIAIS
    - CONATUREZA que começam com 32: JUROS E ENCARGOS DA DÍVIDA
    - CONATUREZA que começam com 33: OUTRAS DESPESAS CORRENTES
    - CONATUREZA que começam com 44: INVESTIMENTO
    - CONATUREZA que começam com 45: INVERSÕES FINANCEIRAS
    - CONATUREZA que começam com 46: AMORTIZAÇÃO DA DÍVIDA
    - Nome do elemento vem da coluna NOELEMENTO
    
    FÓRMULAS APLICADAS:
    - DOTAÇÃO INICIAL = DOTACAO INICIAL
    - DOTAÇÃO ATUALIZADA = DOTACAO INICIAL + DOTACAO ADICIONAL + CANCELAMENTO DE DOTACAO + CANCEL-REMANEJA DOTACAO
    - SALDO DA DOTAÇÃO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
    
    Args:
        df_completo: DataFrame com dados de despesa
        estrutura_hierarquica: Não utilizado (mantido para compatibilidade)
        noug_selecionada: NOUG selecionada para filtro (opcional)
        
    Returns:
        Tuple: (dados_numericos, mes_referencia, dados_para_ia, dados_pdf)
    """
    motor = MotorRelatorios(df_completo, tipo_dados='despesa')
    df_processar = motor.filtrar_por_noug(noug_selecionada)
    
    # Filtra apenas 2025
    df_2025 = df_processar[df_processar['COEXERCICIO'] == 2025]
    
    if df_2025.empty:
        return [], obter_mes_numero(df_processar), [], {}
    
    # Calcula mês de referência
    mes_referencia = obter_mes_numero(df_2025)
    
    dados_numericos = []
    dados_para_ia = []
    
    # Mapeamento de prefixos de CONATUREZA para categorias
    # Baseado nos nomes que aparecem no relatório
    mapa_conatureza = {
        '31': 'PESSOAL E ENCARGOS SOCIAIS',
        '32': 'JUROS E ENCARGOS DA DÍVIDA',
        '33': 'OUTRAS DESPESAS CORRENTES',
        '44': 'INVESTIMENTO',
        '45': 'INVERSÕES FINANCEIRAS',
        '46': 'AMORTIZAÇÃO DA DÍVIDA'
    }
    
    # Mapeamento reverso para facilitar a busca
    mapa_reverso = {
        'PESSOAL': '31',
        'JUROS': '32',
        'OUTRAS DESPESAS CORRENTES': '33',
        'INVESTIMENTO': '44',
        'INVERSÕES': '45',
        'INVERSOES': '45',  # Variação sem acentos
        'AMORTIZAÇÃO': '46',
        'AMORTIZACAO': '46'  # Variação sem acentos
    }
    
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
    
    # Processa cada categoria
    for _, categoria in categorias.iterrows():
        nome_categoria = categoria['NOCATEGORIA']
        dotacao_inicial = float(categoria['DOTACAO INICIAL'])
        dotacao_adicional = float(categoria['DOTACAO ADICIONAL'])
        cancelamento_dotacao = float(categoria['CANCELAMENTO DE DOTACAO'])
        cancel_remaneja = float(categoria['CANCEL-REMANEJA DOTACAO'])
        
        # FÓRMULA: DOTAÇÃO ATUALIZADA = INICIAL + ADICIONAL + CANCELAMENTO + CANCEL-REMANEJA
        dotacao_atualizada = dotacao_inicial + dotacao_adicional + cancelamento_dotacao + cancel_remaneja
        
        despesa_empenhada = float(categoria['DESPESA EMPENHADA'])
        despesa_liquidada = float(categoria['DESPESA LIQUIDADA'])
        despesa_paga = float(categoria['DESPESA PAGA'])
        
        # FÓRMULA: SALDO = DOTAÇÃO ATUALIZADA - DESPESA EMPENHADA
        saldo_dotacao = dotacao_atualizada - despesa_empenhada
        
        # Para categorias de despesa, sempre permite expansão (exceto RESERVA)
        tem_elementos = nome_categoria.upper() != 'RESERVA DE CONTINGÊNCIA'
        
        # Se tem elementos, conta quantos existem baseado nos GRUPOS
        qtd_elementos = 0
        if tem_elementos:
            # Filtra elementos desta categoria
            df_categoria = df_2025[df_2025['CATEGORIA'] == categoria['CATEGORIA']]
            
            # Para cada grupo desta categoria, verifica se tem elementos expandíveis
            grupos_expandiveis = []
            if 'NOGRUPO' in df_categoria.columns:
                grupos_unicos = df_categoria['NOGRUPO'].dropna().unique()
                
                for nome_grupo in grupos_unicos:
                    nome_grupo_upper = str(nome_grupo).upper()
                    
                    # Verifica se é um dos grupos que devem ter detalhamento
                    for palavra_chave, prefixo in mapa_reverso.items():
                        if palavra_chave in nome_grupo_upper:
                            # Conta elementos com esse prefixo
                            df_grupo = df_categoria[df_categoria['NOGRUPO'] == nome_grupo]
                            if 'CONATUREZA' in df_grupo.columns:
                                df_grupo['CONATUREZA_STR'] = df_grupo['CONATUREZA'].astype(str)
                                elementos_grupo = df_grupo[df_grupo['CONATUREZA_STR'].str.startswith(prefixo)]
                                if len(elementos_grupo) > 0:
                                    grupos_expandiveis.append(nome_grupo)
                                    qtd_elementos += len(elementos_grupo.groupby('CONATUREZA'))
                            break
            
            print(f"\nDEBUG: Categoria '{nome_categoria}' - grupos expandíveis: {grupos_expandiveis}, total elementos: {qtd_elementos}")
        
        linha_categoria = {
            'tipo': 'principal',
            'categoria_id': str(categoria['CATEGORIA']),
            'especificacao': nome_categoria,
            'dotacao_inicial': dotacao_inicial,
            'dotacao_atualizada': dotacao_atualizada,
            'despesa_empenhada': despesa_empenhada,
            'despesa_liquidada': despesa_liquidada,
            'despesa_paga': despesa_paga,
            'saldo_dotacao': saldo_dotacao,
            'dotacao_inicial_fmt': motor.formatar_numero(dotacao_inicial),
            'dotacao_atualizada_fmt': motor.formatar_numero(dotacao_atualizada),
            'despesa_empenhada_fmt': motor.formatar_numero(despesa_empenhada),
            'despesa_liquidada_fmt': motor.formatar_numero(despesa_liquidada),
            'despesa_paga_fmt': motor.formatar_numero(despesa_paga),
            'saldo_dotacao_fmt': motor.formatar_numero(saldo_dotacao),
            'tem_elementos': tem_elementos and qtd_elementos > 0,
            'qtd_elementos': qtd_elementos
        }
        
        # Debug para verificar se tem elementos
        if tem_elementos:
            print(f"DEBUG: Categoria '{nome_categoria}' - tem_elementos: {tem_elementos}, qtd_elementos: {qtd_elementos}")
        dados_numericos.append(linha_categoria)
        dados_para_ia.append(linha_categoria)
        
        # Processa grupos dentro da categoria
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
            nome_grupo = grupo['NOGRUPO']
            dot_inicial_grupo = float(grupo['DOTACAO INICIAL'])
            dot_adicional_grupo = float(grupo['DOTACAO ADICIONAL'])
            cancel_dotacao_grupo = float(grupo['CANCELAMENTO DE DOTACAO'])
            cancel_remaneja_grupo = float(grupo['CANCEL-REMANEJA DOTACAO'])
            
            # FÓRMULA PARA GRUPO
            dot_atualizada_grupo = dot_inicial_grupo + dot_adicional_grupo + cancel_dotacao_grupo + cancel_remaneja_grupo
            
            desp_emp_grupo = float(grupo['DESPESA EMPENHADA'])
            desp_liq_grupo = float(grupo['DESPESA LIQUIDADA'])
            desp_paga_grupo = float(grupo['DESPESA PAGA'])
            
            # FÓRMULA PARA SALDO DO GRUPO
            saldo_grupo = dot_atualizada_grupo - desp_emp_grupo
            
            # Verifica se este grupo pode ter elementos expandidos
            tem_elementos_grupo = False
            qtd_elementos_grupo = 0
            grupo_id = f"{categoria['CATEGORIA']}_{grupo['GRUPO']}"
            
            # Não adiciona [+] em RESERVA DE CONTINGÊNCIA
            if nome_grupo and nome_grupo.upper() != 'RESERVA DE CONTINGÊNCIA':
                nome_grupo_upper = str(nome_grupo).upper()
                
                # Verifica se é um dos grupos que devem ter detalhamento
                for palavra_chave, prefixo in mapa_reverso.items():
                    if palavra_chave in nome_grupo_upper:
                        # Conta elementos com esse prefixo
                        df_grupo_dados = df_2025[(df_2025['CATEGORIA'] == categoria['CATEGORIA']) & 
                                                (df_2025['GRUPO'] == grupo['GRUPO'])]
                        if 'CONATUREZA' in df_grupo_dados.columns:
                            df_grupo_dados['CONATUREZA_STR'] = df_grupo_dados['CONATUREZA'].astype(str)
                            elementos_grupo = df_grupo_dados[df_grupo_dados['CONATUREZA_STR'].str.startswith(prefixo)]
                            elementos_unicos = elementos_grupo.groupby('CONATUREZA').size()
                            qtd_elementos_grupo = len(elementos_unicos)
                            tem_elementos_grupo = qtd_elementos_grupo > 0
                            
                            if tem_elementos_grupo:
                                print(f"DEBUG: Grupo '{nome_grupo}' - {qtd_elementos_grupo} elementos com prefixo {prefixo}")
                        break
            
            linha_grupo = {
                'tipo': 'filha',
                'categoria_pai': str(categoria['CATEGORIA']),
                'grupo_id': grupo_id,
                'codigo_grupo': str(grupo['GRUPO']),
                'especificacao': f"  {nome_grupo}",
                'dotacao_inicial': dot_inicial_grupo,
                'dotacao_atualizada': dot_atualizada_grupo,
                'despesa_empenhada': desp_emp_grupo,
                'despesa_liquidada': desp_liq_grupo,
                'despesa_paga': desp_paga_grupo,
                'saldo_dotacao': saldo_grupo,
                'dotacao_inicial_fmt': motor.formatar_numero(dot_inicial_grupo),
                'dotacao_atualizada_fmt': motor.formatar_numero(dot_atualizada_grupo),
                'despesa_empenhada_fmt': motor.formatar_numero(desp_emp_grupo),
                'despesa_liquidada_fmt': motor.formatar_numero(desp_liq_grupo),
                'despesa_paga_fmt': motor.formatar_numero(desp_paga_grupo),
                'saldo_dotacao_fmt': motor.formatar_numero(saldo_grupo),
                'tem_elementos': tem_elementos_grupo,
                'qtd_elementos': qtd_elementos_grupo
            }
            dados_numericos.append(linha_grupo)
            
            # Se este grupo tem elementos, processa-os
            if tem_elementos_grupo:
                # Busca o prefixo correspondente
                prefixo_conatureza = None
                for palavra_chave, prefixo in mapa_reverso.items():
                    if palavra_chave in nome_grupo_upper:
                        prefixo_conatureza = prefixo
                        break
                
                if prefixo_conatureza:
                    # Filtra e agrupa elementos
                    df_elementos = elementos_grupo
                    
                    elementos = df_elementos.groupby('CONATUREZA', observed=True).agg({
                        'NOELEMENTO': 'first',
                        'DOTACAO INICIAL': 'sum',
                        'DOTACAO ADICIONAL': 'sum',
                        'CANCELAMENTO DE DOTACAO': 'sum',
                        'CANCEL-REMANEJA DOTACAO': 'sum',
                        'DESPESA EMPENHADA': 'sum',
                        'DESPESA LIQUIDADA': 'sum',
                        'DESPESA PAGA': 'sum'
                    }).reset_index()
                    
                    # Ordena por CONATUREZA
                    elementos = elementos.sort_values('CONATUREZA')
                    
                    for _, elemento in elementos.iterrows():
                        dot_inicial_elem = float(elemento['DOTACAO INICIAL'])
                        dot_adicional_elem = float(elemento['DOTACAO ADICIONAL'])
                        cancel_dotacao_elem = float(elemento['CANCELAMENTO DE DOTACAO'])
                        cancel_remaneja_elem = float(elemento['CANCEL-REMANEJA DOTACAO'])
                        
                        # FÓRMULA PARA ELEMENTO
                        dot_atualizada_elem = dot_inicial_elem + dot_adicional_elem + cancel_dotacao_elem + cancel_remaneja_elem
                        
                        desp_emp_elem = float(elemento['DESPESA EMPENHADA'])
                        desp_liq_elem = float(elemento['DESPESA LIQUIDADA'])
                        desp_paga_elem = float(elemento['DESPESA PAGA'])
                        
                        # FÓRMULA PARA SALDO DO ELEMENTO
                        saldo_elem = dot_atualizada_elem - desp_emp_elem
                        
                        linha_elemento = {
                            'tipo': 'elemento',
                            'categoria_pai': str(categoria['CATEGORIA']),
                            'grupo_pai': grupo_id,
                            'conatureza': str(elemento['CONATUREZA']),
                            'especificacao': f"    {elemento['CONATUREZA']} - {elemento['NOELEMENTO']}",
                            'dotacao_inicial': dot_inicial_elem,
                            'dotacao_atualizada': dot_atualizada_elem,
                            'despesa_empenhada': desp_emp_elem,
                            'despesa_liquidada': desp_liq_elem,
                            'despesa_paga': desp_paga_elem,
                            'saldo_dotacao': saldo_elem,
                            'dotacao_inicial_fmt': motor.formatar_numero(dot_inicial_elem),
                            'dotacao_atualizada_fmt': motor.formatar_numero(dot_atualizada_elem),
                            'despesa_empenhada_fmt': motor.formatar_numero(desp_emp_elem),
                            'despesa_liquidada_fmt': motor.formatar_numero(desp_liq_elem),
                            'despesa_paga_fmt': motor.formatar_numero(desp_paga_elem),
                            'saldo_dotacao_fmt': motor.formatar_numero(saldo_elem)
                        }
                        dados_numericos.append(linha_elemento)
    
    # Calcula totais gerais
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
            **{f'{k}_fmt': motor.formatar_numero(v) for k, v in totais.items()}
        }
        dados_numericos.append(linha_total)
        dados_para_ia.append({'especificacao': 'TOTAL GERAL', **totais})
    
    # Dados para PDF (sem elementos expandidos)
    dados_pdf = {
        "head": [['DESPESAS ORÇAMENTÁRIAS', 'DOTAÇÃO INICIAL', 'DOTAÇÃO ATUALIZADA', 
                 'DESPESA EMPENHADA', 'DESPESA LIQUIDADA', 'DESPESA PAGA', 'SALDO DA DOTAÇÃO']],
        "body": [
            [linha['especificacao'].strip(), linha.get('dotacao_inicial_fmt', 'R$ 0,00'), 
             linha.get('dotacao_atualizada_fmt', 'R$ 0,00'), linha.get('despesa_empenhada_fmt', 'R$ 0,00'),
             linha.get('despesa_liquidada_fmt', 'R$ 0,00'), linha.get('despesa_paga_fmt', 'R$ 0,00'), 
             linha.get('saldo_dotacao_fmt', 'R$ 0,00')]
            for linha in dados_numericos if linha['tipo'] != 'elemento'
        ]
    }
    
    return dados_numericos, mes_referencia, dados_para_ia, dados_pdf