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

# --- MENU PRINCIPAL ATUALIZADO ---
MENU_PRINCIPAL = {
    "Receita": [
        {
            "nome": "Receita Estimada (Comparativo Anual)",
            "url": "/relatorio/receita-estimada",
            "descricao": "Demonstrativo comparativo da receita estimada entre dois exercícios."
        },
        {
            "nome": "Receita Estimada (por Administração)",
            "url": "/relatorio/receita-por-adm",
            "descricao": "Demonstrativo da receita por tipo de administração para o exercício de 2025."
        },
        {
            "nome": "Previsão de Receita Atualizada",
            "url": "/relatorio/previsao-atualizada",
            "descricao": "Compara a previsão inicial com a previsão atualizada para o exercício de 2025."
        },
        {
            "nome": "Balanço Orçamentário da Receita",
            "url": "/relatorio/balanco-orcamentario",
            "descricao": "Balanço da execução da receita, comparando previsto com realizado para 2025."
        }
    ],
    "Despesa": [
        {
            "nome": "Balanço Orçamentário da Despesa",
            "url": "/relatorio/balanco-despesa",
            "descricao": "Balanço da execução da despesa, comparando dotação com execução para 2025."
        },
        {
            "nome": "Despesa por Função de Governo",
            "url": "/relatorio/despesa-por-funcao",
            "descricao": "Demonstrativo da despesa organizada por função de governo (Em desenvolvimento)."
        },
        {
            "nome": "Despesa por Natureza",
            "url": "/relatorio/despesa-por-natureza",
            "descricao": "Demonstrativo da despesa organizada por grupos de natureza (Em desenvolvimento)."
        },
        {
            "nome": "Despesa por Modalidade de Aplicação",
            "url": "/relatorio/despesa-por-modalidade",
            "descricao": "Demonstrativo da despesa por modalidade de aplicação (Em desenvolvimento)."
        },
        {
            "nome": "Despesa por Unidade Gestora",
            "url": "/relatorio/despesa-por-noug",
            "descricao": "Demonstrativo da despesa por unidade gestora (Em desenvolvimento)."
        },
        {
            "nome": "Execução Orçamentária por Programa",
            "url": "/relatorio/execucao-por-programa",
            "descricao": "Demonstrativo da execução orçamentária por programa de governo (Em desenvolvimento)."
        }
    ],
    "Outros Relatórios": [
        {
            "nome": "Receita vs Despesa (Consolidado)",
            "url": "/relatorio/receita-vs-despesa",
            "descricao": "Comparativo consolidado entre receita arrecadada e despesa executada (Em desenvolvimento)."
        },
        {
            "nome": "Evolução Temporal (Multi-exercício)",
            "url": "/relatorio/evolucao-temporal",
            "descricao": "Análise da evolução da receita e despesa ao longo dos exercícios (Em desenvolvimento)."
        },
        {
            "nome": "Indicadores Orçamentários",
            "url": "/relatorio/indicadores",
            "descricao": "Principais indicadores de execução orçamentária e financeira (Em desenvolvimento)."
        },
        {
            "nome": "Dashboard Executivo",
            "url": "/relatorio/dashboard",
            "descricao": "Painel gerencial com principais indicadores e gráficos interativos (Em desenvolvimento)."
        }
    ]
}