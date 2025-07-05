/**
 * Scripts padrão para todos os relatórios
 */

// Configurações padrão para PDF
const PDF_CONFIG = {
    orientation: 'p',
    unit: 'pt',
    format: 'a4',
    putOnlyUsedFonts: true,
    floatPrecision: 16
};

const PDF_STYLES = {
    theme: 'grid',
    headStyles: {
        fillColor: [0, 51, 102],
        textColor: [255, 255, 255],
        halign: 'center',
        fontSize: 11,
        fontStyle: 'bold'
    },
    bodyStyles: {
        fontSize: 10
    },
    alternateRowStyles: {
        fillColor: [250, 250, 250]
    },
    margin: { top: 60, right: 40, bottom: 40, left: 40 }
};

// Cores padrão por nível
const NIVEL_CORES = {
    'level-1': { fill: [204, 229, 255], text: [0, 0, 0], bold: true },
    'level-2': { fill: [231, 242, 255], text: [0, 0, 0], bold: true },
    'level-3': { fill: [245, 249, 255], text: [0, 0, 0], bold: false },
    'level-4': { fill: [250, 252, 255], text: [85, 85, 85], bold: false },
    'total': { fill: [0, 51, 102], text: [255, 255, 255], bold: true }
};

// Função para aplicar filtro de NOUG
function aplicarFiltro() {
    const select = document.getElementById('filtro-noug');
    if (!select) return;
    
    const nougSelecionada = select.value;
    const urlAtual = window.location.pathname;
    
    if (nougSelecionada === 'todos') {
        window.location.href = urlAtual;
    } else {
        window.location.href = `${urlAtual}?noug=${encodeURIComponent(nougSelecionada)}`;
    }
}

// Função para atualizar dados
function atualizarDados() {
    const btn = document.getElementById('btn-atualizar');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Atualizando...';
    }
    window.location.reload(true);
}

// Função genérica para gerar PDF
function gerarPDF(config) {
    const {
        titulo,
        subtitulo,
        dados,
        nomeArquivo,
        orientacao = 'p',
        colunasTipos = null
    } = config;
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ ...PDF_CONFIG, orientation: orientacao });
    
    // Título
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.text(titulo, doc.internal.pageSize.getWidth() / 2, 40, { align: 'center' });
    
    // Subtítulo
    if (subtitulo) {
        doc.setFontSize(12);
        doc.setFont(undefined, 'normal');
        doc.text(subtitulo, doc.internal.pageSize.getWidth() / 2, 55, { align: 'center' });
    }
    
    // Configuração da tabela
    const tableConfig = {
        ...PDF_STYLES,
        startY: subtitulo ? 70 : 60,
        head: dados.head,
        body: dados.body
    };
    
    // Aplicar estilos customizados se houver dados de tipos
    if (colunasTipos) {
        tableConfig.willDrawCell = (data) => {
            if (data.section === 'body') {
                const tipo = colunasTipos[data.row.index];
                if (tipo && NIVEL_CORES[tipo]) {
                    const estilo = NIVEL_CORES[tipo];
                    doc.setFillColor(...estilo.fill);
                    doc.setTextColor(...estilo.text);
                    if (estilo.bold) {
                        doc.setFont(undefined, 'bold');
                    }
                }
            }
        };
    }
    
    // Gerar tabela
    doc.autoTable(tableConfig);
    
    // Salvar
    doc.save(nomeArquivo);
}

// Formatar número para padrão brasileiro
function formatarNumero(valor) {
    if (typeof valor !== 'number') return valor;
    
    return valor.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Função para detectar se um texto é um valor monetário negativo
function ehValorMonetarioNegativo(texto) {
    // Remove espaços em branco
    const textoLimpo = texto.trim();
    
    // Verifica se tem parênteses E se parece com um valor monetário
    if (textoLimpo.includes('(') && textoLimpo.includes(')')) {
        // Padrões de valor monetário negativo:
        // (R$ 1.234,56), (1.234,56), R$ (1.234,56), etc.
        const padraoMonetario = /(\(.*R\$.*\)|R\$.*\(.*\)|\(\s*[\d.,]+\s*\))/;
        return padraoMonetario.test(textoLimpo);
    }
    
    // Também verifica valores com sinal negativo explícito
    if (textoLimpo.includes('-') && textoLimpo.includes('R$')) {
        return true;
    }
    
    return false;
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Botão de atualizar
    const btnAtualizar = document.getElementById('btn-atualizar');
    if (btnAtualizar) {
        btnAtualizar.addEventListener('click', atualizarDados);
    }
    
    // Aplicar classes de formatação automática - VERSÃO CORRIGIDA
    document.querySelectorAll('td').forEach(td => {
        const texto = td.textContent.trim();
        
        // CORREÇÃO: Detectar valores monetários negativos (não qualquer texto com parênteses)
        if (ehValorMonetarioNegativo(texto)) {
            td.classList.add('valor-negativo');
        }
        
        // Detectar valores zero
        if (texto === 'R$ 0,00' || texto === '0,00') {
            td.classList.add('valor-zero');
        }
        
        // Detectar percentuais positivos (para variações)
        if (texto.includes('+') && texto.includes('%')) {
            td.classList.add('valor-positivo');
        }
    });
    
    // Adicionar tooltips em valores truncados
    document.querySelectorAll('td:first-child').forEach(td => {
        if (td.scrollWidth > td.clientWidth) {
            td.title = td.textContent;
        }
    });
});

// Exportar funções para uso global
window.RelatorioUtils = {
    aplicarFiltro,
    atualizarDados,
    gerarPDF,
    formatarNumero,
    ehValorMonetarioNegativo,
    NIVEL_CORES,
    PDF_CONFIG,
    PDF_STYLES
};