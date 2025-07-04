/**
 * Função otimizada para exportar relatórios como PNG de alta qualidade
 * Exporta apenas o conteúdo do relatório (tabela + cabeçalho)
 */

function exportarRelatorioComoImagem() {
    // Seleciona os elementos necessários
    const tabela = document.querySelector('table');
    const cabecalho = document.querySelector('.report-header');
    
    if (!tabela) {
        alert('Tabela não encontrada para exportação');
        return;
    }
    
    // Cria container temporário otimizado
    const containerExport = document.createElement('div');
    containerExport.id = 'export-container';
    containerExport.style.cssText = `
        position: fixed;
        top: -10000px;
        left: -10000px;
        background: #ffffff;
        padding: 40px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        width: 1400px;
        min-height: 600px;
        z-index: 9999;
        box-shadow: none;
        border: none;
    `;
    
    // Adiciona cabeçalho se existir
    if (cabecalho) {
        const cabecalhoClone = cabecalho.cloneNode(true);
        cabecalhoClone.style.cssText = `
            text-align: center;
            margin-bottom: 30px;
            color: #003366;
        `;
        containerExport.appendChild(cabecalhoClone);
    }
    
    // Clona e otimiza a tabela
    const tabelaClone = tabela.cloneNode(true);
    tabelaClone.style.cssText = `
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        background: white;
        border: none;
        margin: 0;
        margin-bottom: 30px;
    `;
    
    // Aplica estilos específicos às células (CORES ORIGINAIS)
    const todasCelulas = tabelaClone.querySelectorAll('th, td');
    todasCelulas.forEach(celula => {
        celula.style.border = '1px solid #ddd';
        celula.style.padding = '10px 12px';
        celula.style.backgroundColor = 'white';
        celula.style.color = '#333';
        
        if (celula.tagName === 'TH') {
            celula.style.backgroundColor = '#003366';
            celula.style.color = 'white';
            celula.style.fontWeight = 'bold';
            celula.style.textAlign = 'center';
            celula.style.fontSize = '13px';
            celula.style.textTransform = 'uppercase';
        }
    });
    
    // Aplica estilos específicos por tipo de linha (CORES ORIGINAIS)
    const linhas = tabelaClone.querySelectorAll('tr');
    linhas.forEach(linha => {
        if (linha.classList.contains('principal')) {
            linha.querySelectorAll('td').forEach(td => {
                td.style.backgroundColor = '#cce5ff';  // Azul claro original
                td.style.color = '#333';               // Texto preto normal
                td.style.fontWeight = 'bold';
            });
        } else if (linha.classList.contains('filha')) {
            linha.querySelectorAll('td').forEach(td => {
                td.style.backgroundColor = '#e7f2ff';  // Azul mais claro original
                td.style.color = '#333';               // Texto preto normal
                td.style.fontWeight = 'normal';
            });
        } else if (linha.classList.contains('total')) {
            linha.querySelectorAll('td').forEach(td => {
                td.style.backgroundColor = '#003366';  // Azul escuro original
                td.style.color = 'white';
                td.style.fontWeight = 'bold';
            });
        }
        
        // Aplica cores da variação percentual (última coluna)
        const celulas = linha.querySelectorAll('td');
        if (celulas.length > 0) {
            const ultimaCelula = celulas[celulas.length - 1];
            const texto = ultimaCelula.textContent.trim();
            
            // Verifica se é uma variação percentual
            if (texto.includes('%') && (texto.includes('+') || texto.includes('-'))) {
                if (texto.includes('+')) {
                    ultimaCelula.style.color = '#28a745';  // Verde para positivo
                    ultimaCelula.style.fontWeight = '600';
                } else if (texto.includes('-')) {
                    ultimaCelula.style.color = '#dc3545';  // Vermelho para negativo
                    ultimaCelula.style.fontWeight = '600';
                }
                
                // Sobrescreve a cor se for linha total
                if (linha.classList.contains('total')) {
                    if (texto.includes('+')) {
                        ultimaCelula.style.color = '#90EE90';  // Verde claro para total positivo
                    } else if (texto.includes('-')) {
                        ultimaCelula.style.color = '#FFB6C1';  // Rosa claro para total negativo
                    }
                }
            }
        }
    });
    
    containerExport.appendChild(tabelaClone);
    document.body.appendChild(containerExport);
    
    // Aguarda um momento para o DOM se estabilizar
    setTimeout(() => {
        // Recalcula a altura real do container
        const alturaReal = containerExport.scrollHeight + 50; // Margem extra
        
        // Configurações otimizadas do html2canvas
        const opcoes = {
            scale: 4,                    // Alta resolução
            backgroundColor: '#ffffff',   // Fundo branco sólido
            useCORS: true,
            allowTaint: true,
            logging: false,
            width: 1400,
            height: alturaReal,          // Altura calculada dinamicamente
            windowWidth: 1400,
            windowHeight: alturaReal,
            removeContainer: false,
            imageTimeout: 0,
            foreignObjectRendering: false,
            onclone: function(clonedDoc) {
                const clonedContainer = clonedDoc.getElementById('export-container');
                if (clonedContainer) {
                    clonedContainer.style.position = 'static';
                    clonedContainer.style.top = 'auto';
                    clonedContainer.style.left = 'auto';
                    clonedContainer.style.transform = 'none';
                    clonedContainer.style.height = 'auto';
                }
            }
        };
        
        // Gera a imagem
        html2canvas(containerExport, opcoes).then(canvas => {
            // Remove container temporário
            document.body.removeChild(containerExport);
            
            // Cria nome do arquivo baseado no título
            const tituloPagina = document.title || 'relatorio';
            const nomeArquivo = tituloPagina.toLowerCase()
                .replace(/\s+/g, '-')
                .replace(/[^a-z0-9\-]/g, '');
            
            // Faz o download
            const link = document.createElement('a');
            link.href = canvas.toDataURL('image/png');
            link.download = `${nomeArquivo}.png`;
            link.click();
            
            // Limpa o link
            setTimeout(() => {
                URL.revokeObjectURL(link.href);
            }, 100);
            
        }).catch(error => {
            console.error('Erro ao gerar imagem:', error);
            alert('Erro ao gerar a imagem. Tente novamente.');
            
            // Remove container em caso de erro
            if (document.body.contains(containerExport)) {
                document.body.removeChild(containerExport);
            }
        });
    }, 100); // Aguarda 100ms para estabilizar
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const btnExport = document.getElementById('btn-jpg');
    if (btnExport) {
        btnExport.textContent = 'BAIXAR PNG';
        btnExport.addEventListener('click', exportarRelatorioComoImagem);
    }
});

// Função auxiliar para aguardar carregamento completo
function aguardarCarregamento() {
    return new Promise((resolve) => {
        if (document.readyState === 'complete') {
            resolve();
        } else {
            window.addEventListener('load', resolve);
        }
    });
}