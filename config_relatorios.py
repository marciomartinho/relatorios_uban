# Este arquivo armazena as "receitas" ou estruturas de todos os relatórios
# e também a configuração do menu principal da aplicação.

# --- ESTRUTURA HIERÁRQUICA DE CÓDIGOS (VERSÃO COMPLETA) ---
# Esta estrutura define a relação entre Categoria, Origem e Espécie.
# O nível da Alínea será descoberto dinamicamente pelo sistema.
HIERARQUIA_RECEITAS = {
    "1": { # Categoria: RECEITAS CORRENTES
        "11": ["111", "112", "113", "114", "115", "116", "117", "118", "119"],
        "12": ["121", "122", "123", "124", "125", "126", "127", "128", "129"],
        "13": ["131", "132", "133", "134", "135", "136", "137", "138", "139"],
        "14": ["141", "142", "143", "144", "145", "146", "147", "148", "149"],
        "15": ["151", "152", "153", "154", "155", "156", "157", "158", "159"],
        "16": ["161", "162", "163", "164", "165", "166", "167", "168", "169"],
        "17": ["171", "172", "173", "174", "175", "176", "177", "178", "179"],
        "19": ["191", "192", "193", "194", "195", "196", "197", "198", "199"]
    },
    "2": { # Categoria: RECEITAS DE CAPITAL
        "21": ["211", "212", "213", "214", "215", "216", "217", "218", "219"],
        "22": ["221", "222", "223", "224", "225", "226", "227", "228", "229"],
        "23": ["231", "232", "233", "234", "235", "236", "237", "238", "239"],
        "24": ["241", "242", "243", "244", "245", "246", "247", "248", "249"],
        "27": ["271", "272", "273", "274", "275", "276", "277", "278", "279"],
        "29": ["291", "292", "293", "294", "295", "296", "297", "298", "299"]
    },
    "7": { # Categoria: RECEITAS INTRAORÇAMENTÁRIAS CORRENTES
        "71": ["711", "712", "713", "714", "715", "716", "717", "718", "719"],
        "72": ["721", "722", "723", "724", "725", "726", "727", "728", "729"],
        "73": ["731", "732", "733", "734", "735", "736", "737", "738", "739"],
        "74": ["741", "742", "743", "744", "745", "746", "747", "748", "749"],
        "75": ["751", "752", "753", "754", "755", "756", "757", "758", "759"],
        "76": ["761", "762", "763", "764", "765", "766", "767", "768", "769"],
        "77": ["771", "772", "773", "774", "775", "776", "777", "778", "779"],
        "79": ["791", "792", "793", "794", "795", "796", "797", "798", "799"]
    },
    "9": { # Categoria: RECURSOS ARRECADADOS EM EXERCÍCIOS ANTERIORES
        # Esta categoria não tem origens detalhadas
    }
}

# --- ESTRUTURA PARA O RELATÓRIO POR ADMINISTRAÇÃO ---
COLUNAS_TIPO_ADMINISTRACAO = {
    "ADMINISTRAÇÃO DIRETA": 1,
    "AUTARQUIAS": 3,
    "FUNDAÇÕES": 4,
    "EMPRESAS": 5,
    "FUNDOS": 7
}

# --- MENU PRINCIPAL REORGANIZADO E ATUALIZADO ---
MENU_PRINCIPAL = {
    "Receita": [
        {
            "nome": "Balanço Orçamentário da Receita",
            "url": "/relatorio/balanco-orcamentario",
            "status": "ativo"
        },
        {
            "nome": "📄 Relatório Consolidado PDF",
            "url": "/relatorio/consolidado-pdf",
            "status": "ativo",
            "destaque": True,
            "descricao": "Relatório executivo que consolida todos os 13+ relatórios de receita",
            "icone": "📄",
            "categoria": "consolidado"
        }
    ],
    "Despesa": [
        {
            "nome": "Balanço Orçamentário da Despesa",
            "url": "/relatorio/balanco-despesa",
            "status": "ativo"
        },
        {
            "nome": "Despesa por Função de Governo",
            "url": "/relatorio/despesa-por-funcao",
            "status": "desenvolvimento"
        },
        {
            "nome": "Despesa por Natureza",
            "url": "/relatorio/despesa-por-natureza",
            "status": "desenvolvimento"
        },
        {
            "nome": "Despesa por Modalidade de Aplicação",
            "url": "/relatorio/despesa-por-modalidade",
            "status": "desenvolvimento"
        },
        {
            "nome": "Despesa por Unidade Gestora",
            "url": "/relatorio/despesa-por-noug",
            "status": "desenvolvimento"
        },
        {
            "nome": "Execução Orçamentária por Programa",
            "url": "/relatorio/execucao-por-programa",
            "status": "desenvolvimento"
        }
    ],
    "Relatórios do Balanço Geral": [
        {
            "nome": "Receita Estimada (Comparativo Anual)",
            "url": "/relatorio/receita-estimada",
            "status": "ativo"
        },
        {
            "nome": "Receita por Tipo de Administração",
            "url": "/relatorio/receita-por-adm",
            "status": "ativo"
        },
        {
            "nome": "Receita Atualizada X Inicial",
            "url": "/relatorio/receita-atualizada-vs-inicial",
            "status": "ativo"
        },
        {
            "nome": "Gráfico de Receita Líquida (Receita Corrente)",
            "url": "/relatorio/grafico-receita-liquida",
            "status": "ativo"
        }
    ],
    "Outros Relatórios": [
        {
            "nome": "Indicadores Orçamentários",
            "url": "/relatorio/indicadores",
            "status": "desenvolvimento"
        },
        {
            "nome": "Dashboard Executivo",
            "url": "/relatorio/dashboard",
            "status": "desenvolvimento"
        },
        {
            "nome": "Relatório por Unidade Gestora",
            "url": "/relatorio/por-noug",
            "status": "desenvolvimento"
        },
        {
            "nome": "Análise de Variações",
            "url": "/relatorio/analise-variacoes",
            "status": "desenvolvimento"
        }
    ]
}

# --- CONFIGURAÇÕES ESPECÍFICAS DO RELATÓRIO CONSOLIDADO ---
CONFIGURACAO_CONSOLIDADO = {
    "nome_completo": "Relatório Consolidado de Receitas PDF",
    "descricao_detalhada": "Documento executivo profissional que consolida automaticamente todos os relatórios de receita em um único PDF com dashboard, gráficos e análises.",
    "relatorios_incluidos": [
        "Balanço Orçamentário da Receita",
        "Receitas Tributárias", 
        "Receitas de Contribuições",
        "Receitas Patrimoniais",
        "Receitas de Serviços",
        "Receitas de Transferências Correntes",
        "Outras Receitas Correntes",
        "Receitas de Operações de Crédito",
        "Receitas de Alienação de Bens",
        "Receitas de Amortização de Empréstimos",
        "Receitas de Transferências de Capital",
        "Gráfico de Receita Corrente",
        "Gráfico de Receita de Capital",
        "Análise de Inconsistências"
    ],
    "features": [
        "Dashboard executivo com KPIs principais",
        "Consolidação automática de 13+ relatórios", 
        "Gráficos profissionais integrados",
        "Análise comparativa 2024 vs 2025",
        "Filtro por NOUG disponível",
        "Export em PDF de alta qualidade",
        "Tempo de geração otimizado",
        "Visual corporativo GDF"
    ],
    "tempo_estimado_geracao": "2-5 segundos",
    "paginas_estimadas": "10-15 páginas",
    "formato_saida": "PDF A4",
    "cores_corporativas": {
        "azul_gdf_escuro": "#003366",
        "azul_gdf_medio": "#0066cc", 
        "azul_gdf_claro": "#cce5ff",
        "azul_gdf_muito_claro": "#e7f2ff"
    }
}

# --- MAPEAMENTO DE STATUS PARA ESTILOS CSS ---
STATUS_CSS_MAPPING = {
    "ativo": "status-ativo",
    "desenvolvimento": "status-desenvolvimento", 
    "manutencao": "status-manutencao",
    "desabilitado": "status-desabilitado"
}

# --- ÍCONES PARA CADA TIPO DE RELATÓRIO ---
ICONES_RELATORIOS = {
    "balanco": "📊",
    "consolidado": "📄", 
    "grafico": "📈",
    "dashboard": "📋",
    "analise": "🔍",
    "indicadores": "📊",
    "comparativo": "⚖️",
    "por_noug": "🏛️",
    "variacoes": "📉",
    "estimada": "📈"
}

# --- CATEGORIAS DE RELATÓRIOS ---
CATEGORIAS_RELATORIOS = {
    "receita": {
        "nome": "Receitas",
        "cor": "#0066cc",
        "icone": "💰"
    },
    "despesa": {
        "nome": "Despesas", 
        "cor": "#dc3545",
        "icone": "💸"
    },
    "balanco": {
        "nome": "Balanço Geral",
        "cor": "#28a745", 
        "icone": "⚖️"
    },
    "consolidado": {
        "nome": "Relatórios Consolidados",
        "cor": "#003366",
        "icone": "📄"
    },
    "outros": {
        "nome": "Outros Relatórios",
        "cor": "#6c757d",
        "icone": "📋"
    }
}

# --- CONFIGURAÇÕES DE FILTROS DISPONÍVEIS ---
FILTROS_DISPONIVEIS = {
    "noug": {
        "nome": "Unidade Gestora (NOUG)",
        "tipo": "select",
        "obrigatorio": False,
        "multiplo": False,
        "fonte_dados": "dinamica"  # Carregado dos dados
    },
    "exercicio": {
        "nome": "Exercício",
        "tipo": "select", 
        "obrigatorio": False,
        "multiplo": True,
        "opcoes_padrao": ["2024", "2025"]
    },
    "mes_referencia": {
        "nome": "Mês de Referência",
        "tipo": "select",
        "obrigatorio": False,
        "multiplo": False,
        "fonte_dados": "dinamica"
    },
    "formato_saida": {
        "nome": "Formato de Saída",
        "tipo": "radio",
        "obrigatorio": False,
        "opcoes_padrao": [
            {"valor": "html", "nome": "Visualizar na Tela"},
            {"valor": "pdf", "nome": "Baixar PDF"}
        ]
    }
}

# --- METADADOS PARA SEO E DOCUMENTAÇÃO ---
METADADOS_SISTEMA = {
    "nome_sistema": "Sistema UBAN - Relatórios de Receita",
    "versao": "2.0",
    "autor": "Governo do Distrito Federal",
    "secretaria": "Secretaria de Economia", 
    "descricao": "Sistema de geração de relatórios orçamentários e financeiros do GDF",
    "keywords": ["orçamento", "receita", "GDF", "relatórios", "balanço"],
    "data_atualizacao": "2025-07-07"
}

# --- FUNÇÃO AUXILIAR PARA OBTER RELATÓRIOS POR CATEGORIA ---
def obter_relatorios_por_categoria(categoria=None):
    """
    Retorna relatórios filtrados por categoria
    
    Args:
        categoria (str): Nome da categoria para filtrar
        
    Returns:
        dict: Relatórios da categoria especificada ou todos se categoria=None
    """
    if categoria is None:
        return MENU_PRINCIPAL
    
    return {categoria: MENU_PRINCIPAL.get(categoria, [])}

# --- FUNÇÃO AUXILIAR PARA OBTER RELATÓRIOS ATIVOS ---
def obter_relatorios_ativos():
    """
    Retorna apenas os relatórios com status 'ativo'
    
    Returns:
        dict: Relatórios ativos organizados por categoria
    """
    relatorios_ativos = {}
    
    for categoria, relatorios in MENU_PRINCIPAL.items():
        relatorios_categoria = [
            relatorio for relatorio in relatorios 
            if relatorio.get("status") == "ativo"
        ]
        if relatorios_categoria:
            relatorios_ativos[categoria] = relatorios_categoria
    
    return relatorios_ativos

# --- FUNÇÃO AUXILIAR PARA VERIFICAR SE RELATÓRIO EXISTE ---
def verificar_relatorio_existe(url):
    """
    Verifica se uma URL de relatório existe no menu
    
    Args:
        url (str): URL do relatório a verificar
        
    Returns:
        bool: True se o relatório existe, False caso contrário
    """
    for categoria, relatorios in MENU_PRINCIPAL.items():
        for relatorio in relatorios:
            if relatorio.get("url") == url:
                return True
    return False

# --- FUNÇÃO AUXILIAR PARA OBTER CONFIGURAÇÃO DE RELATÓRIO ---
def obter_configuracao_relatorio(url):
    """
    Obtém a configuração completa de um relatório pela URL
    
    Args:
        url (str): URL do relatório
        
    Returns:
        dict or None: Configuração do relatório ou None se não encontrado
    """
    for categoria, relatorios in MENU_PRINCIPAL.items():
        for relatorio in relatorios:
            if relatorio.get("url") == url:
                relatorio_config = relatorio.copy()
                relatorio_config["categoria_sistema"] = categoria
                return relatorio_config
    return None

# --- VALIDAÇÃO DA CONFIGURAÇÃO ---
def validar_configuracao():
    """
    Valida se a configuração está correta
    
    Returns:
        tuple: (bool, list) - (válido, lista_de_erros)
    """
    erros = []
    
    # Verifica se todas as categorias têm pelo menos um relatório
    for categoria, relatorios in MENU_PRINCIPAL.items():
        if not relatorios:
            erros.append(f"Categoria '{categoria}' não possui relatórios")
    
    # Verifica se URLs são únicas
    urls_vistas = set()
    for categoria, relatorios in MENU_PRINCIPAL.items():
        for relatorio in relatorios:
            url = relatorio.get("url")
            if url in urls_vistas:
                erros.append(f"URL duplicada encontrada: {url}")
            urls_vistas.add(url)
    
    # Verifica se o relatório consolidado foi adicionado corretamente
    consolidado_encontrado = False
    for categoria, relatorios in MENU_PRINCIPAL.items():
        for relatorio in relatorios:
            if relatorio.get("url") == "/relatorio/consolidado-pdf":
                consolidado_encontrado = True
                break
    
    if not consolidado_encontrado:
        erros.append("Relatório consolidado não foi encontrado no menu")
    
    return len(erros) == 0, erros

# --- EXECUTAR VALIDAÇÃO NO IMPORT ---
if __name__ == "__main__":
    valido, erros = validar_configuracao()
    if valido:
        print("✅ Configuração validada com sucesso!")
        print(f"📊 Total de categorias: {len(MENU_PRINCIPAL)}")
        total_relatorios = sum(len(relatorios) for relatorios in MENU_PRINCIPAL.values())
        print(f"📋 Total de relatórios: {total_relatorios}")
        relatorios_ativos = sum(
            len([r for r in relatorios if r.get("status") == "ativo"]) 
            for relatorios in MENU_PRINCIPAL.values()
        )
        print(f"✅ Relatórios ativos: {relatorios_ativos}")
    else:
        print("❌ Erros encontrados na configuração:")
        for erro in erros:
            print(f"   - {erro}")