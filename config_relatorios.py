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