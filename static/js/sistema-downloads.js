/**
 * SISTEMA DE DOWNLOADS - VERSÃO UNIFICADA E CORRIGIDA
 * Baseado no sistema original que funciona perfeitamente
 */

// Verificar e carregar bibliotecas necessárias
function verificarECarregarBibliotecas() {
    console.log('🔍 Verificando bibliotecas necessárias...');
    
    const bibliotecasNecessarias = [
        {
            nome: 'html2canvas',
            url: 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
            verificar: () => window.html2canvas
        },
        {
            nome: 'jsPDF',
            url: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
            verificar: () => window.jspdf
        },
        {
            nome: 'jsPDF-AutoTable',
            url: 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js',
            verificar: () => window.jspdf && window.jspdf.jsPDF.prototype.autoTable
        },
        {
            nome: 'JSZip',
            url: 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js',
            verificar: () => window.JSZip
        },
        {
            nome: 'FileSaver',
            url: 'https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js',
            verificar: () => window.saveAs
        }
    ];
    
    bibliotecasNecessarias.forEach(lib => {
        if (!lib.verificar()) {
            console.log(`⏳ Carregando ${lib.nome}...`);
            const script = document.createElement('script');
            script.src = lib.url;
            script.onload = () => console.log(`✅ ${lib.nome} carregado!`);
            document.head.appendChild(script);
        } else {
            console.log(`✅ ${lib.nome} já está carregado`);
        }
    });
}

// Chamar imediatamente ao carregar o script
verificarECarregarBibliotecas();

const SistemaDownloads = {
    config: {
        nomeRelatorio: 'Relatório',
        secoesPrincipais: [],
        tabelaPrincipal: 'secao-tabela-principal'
    },
    
    inicializar: function(configuracao) {
        console.log('🚀 Inicializando Sistema de Downloads...');
        
        // Mesclar configurações
        this.config = { ...this.config, ...configuracao };
        
        // Aguardar bibliotecas carregarem
        setTimeout(() => {
            this.criarInterface();
            this.verificarBibliotecas();
        }, 1500);
        
        console.log('✅ Sistema de Downloads inicializado!');
    },
    
    criarInterface: function() {
        const container = document.getElementById('sistema-downloads-container');
        if (!container) {
            console.error('❌ Container do sistema de downloads não encontrado!');
            return;
        }
        
        container.innerHTML = `
            <div class="download-section">
                <h4>
                    <span>📥</span>
                    <span>Downloads do Relatório</span>
                </h4>
                
                <div class="download-buttons">
                    <button class="download-btn btn-png" onclick="SistemaDownloads.downloadTablePNG()">
                        <span>📊</span>
                        <span>Tabela Principal</span>
                    </button>
                    <button class="download-btn btn-zip" onclick="SistemaDownloads.downloadAllPNG()">
                        <span>🗜️</span>
                        <span>Relatório Completo</span>
                    </button>
                    <button class="download-btn btn-html" onclick="SistemaDownloads.downloadHTML()">
                        <span>🌐</span>
                        <span>Arquivo HTML</span>
                    </button>
                    <button class="download-btn btn-pdf" onclick="SistemaDownloads.downloadPDF()">
                        <span>📄</span>
                        <span>PDF Otimizado</span>
                    </button>
                </div>
                
                <div class="download-loading" id="downloadLoading">
                    <div class="download-spinner"></div>
                    <div class="download-loading-text">Processando download...</div>
                </div>
            </div>
        `;
    },
    
    verificarBibliotecas: function() {
        console.log('🔍 Verificando bibliotecas de download...');
        const bibliotecas = [
            { nome: 'html2canvas', objeto: window.html2canvas },
            { nome: 'jsPDF', objeto: window.jspdf },
            { nome: 'JSZip', objeto: window.JSZip },
            { nome: 'FileSaver', objeto: window.saveAs }
        ];
        
        bibliotecas.forEach(lib => {
            if (lib.objeto) {
                console.log(`✅ ${lib.nome} carregado`);
            } else {
                console.error(`❌ ${lib.nome} não carregado`);
            }
        });
    },
    
    showDownloadLoading: function(show = true) {
        const loading = document.getElementById('downloadLoading');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    },
    
    // 1. Download PNG da tabela
    downloadTablePNG: async function() {
        this.showDownloadLoading(true);
        try {
            const elemento = document.getElementById(this.config.tabelaPrincipal);
            if (!elemento) {
                throw new Error('Tabela principal não encontrada');
            }
            
            const canvas = await html2canvas(elemento, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#ffffff',
                logging: false
            });
            
            const link = document.createElement('a');
            link.download = `${this.config.nomeRelatorio.toLowerCase().replace(/\s+/g, '-')}-tabela-${new Date().toISOString().split('T')[0]}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
            
            console.log('✅ Download da tabela concluído');
        } catch (error) {
            console.error('❌ Erro no download da tabela:', error);
            alert('Erro ao gerar imagem da tabela: ' + error.message);
        } finally {
            this.showDownloadLoading(false);
        }
    },
    
    // 2. Download ZIP completo
    downloadAllPNG: async function() {
        this.showDownloadLoading(true);
        try {
            if (!window.JSZip || !window.saveAs) {
                throw new Error('Bibliotecas JSZip ou FileSaver não carregadas');
            }
            
            const zip = new JSZip();
            
            for (const secao of this.config.secoesPrincipais) {
                const elemento = document.getElementById(secao.id);
                if (elemento) {
                    const canvas = await html2canvas(elemento, {
                        scale: 2,
                        useCORS: true,
                        backgroundColor: '#ffffff',
                        logging: false
                    });
                    
                    const blob = await new Promise(resolve => {
                        canvas.toBlob(resolve, 'image/png', 0.95);
                    });
                    
                    zip.file(`${secao.nome}.png`, blob);
                    console.log(`✅ Seção ${secao.nome} adicionada ao ZIP`);
                }
            }
            
            const zipBlob = await zip.generateAsync({
                type: 'blob',
                compression: 'DEFLATE',
                compressionOptions: { level: 6 }
            });
            
            const dataAtual = new Date().toISOString().split('T')[0];
            saveAs(zipBlob, `${this.config.nomeRelatorio.toLowerCase().replace(/\s+/g, '-')}-completo-${dataAtual}.zip`);
            
            console.log('✅ Download do ZIP concluído');
        } catch (error) {
            console.error('❌ Erro no download do ZIP:', error);
            alert('Erro ao gerar arquivo ZIP: ' + error.message);
        } finally {
            this.showDownloadLoading(false);
        }
    },
    
    // 3. Download HTML - VERSÃO CORRIGIDA
    downloadHTML: function() {
        this.showDownloadLoading(true);
        try {
            console.log('🌐 Iniciando geração do HTML...');
            
            const htmlCompleto = this.gerarHTMLCompleto();
            
            if (!htmlCompleto || htmlCompleto.length < 100) {
                throw new Error('HTML gerado está vazio ou muito pequeno');
            }
            
            const blob = new Blob([htmlCompleto], { type: 'text/html;charset=utf-8' });
            const dataFormatada = new Date().toISOString().split('T')[0];
            const nomeArquivo = `${this.config.nomeRelatorio.toLowerCase().replace(/\s+/g, '-')}-completo-${dataFormatada}.html`;
            
            // Verificar se saveAs está disponível
            if (window.saveAs) {
                saveAs(blob, nomeArquivo);
            } else {
                // Fallback caso FileSaver não esteja carregado
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = nomeArquivo;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }
            
            console.log('✅ HTML completo gerado com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao gerar HTML:', error);
            alert('Erro ao gerar arquivo HTML: ' + error.message);
        } finally {
            this.showDownloadLoading(false);
        }
    },
    
    // 4. Download PDF
    downloadPDF: async function() {
        this.showDownloadLoading(true);
        try {
            if (!window.jspdf) {
                throw new Error('Biblioteca jsPDF não carregada');
            }
            
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('landscape', 'mm', 'a4');
            
            console.log('📄 Iniciando geração do PDF em paisagem...');
            
            // Cabeçalho
            let posY = this.adicionarCabecalhoPDF(pdf);
            
            // Tabela principal
            posY = await this.adicionarTabelaPDF(pdf, posY);
            
            // Outras seções
            await this.adicionarOutrasSecoesPDF(pdf);
            
            // Rodapé
            this.adicionarRodapePDF(pdf);
            
            // Salvar
            const dataAtual = new Date().toISOString().split('T')[0];
            pdf.save(`${this.config.nomeRelatorio.toLowerCase().replace(/\s+/g, '-')}-${dataAtual}.pdf`);
            
            console.log('✅ PDF gerado com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao gerar PDF:', error);
            alert('Erro ao gerar PDF: ' + error.message);
        } finally {
            this.showDownloadLoading(false);
        }
    },
    
    // Função auxiliar CORRIGIDA para gerar HTML completo
    gerarHTMLCompleto: function() {
        const titulo = this.config.nomeRelatorio;
        const dataAtual = new Date().toLocaleString('pt-BR');
        
        // Tentar diferentes seletores para encontrar o container principal
        let containerPrincipal = null;
        const seletores = ['.container', '.content-wrapper', 'main', 'body > div:first-child'];
        
        for (const seletor of seletores) {
            containerPrincipal = document.querySelector(seletor);
            if (containerPrincipal) {
                console.log(`✅ Container encontrado com seletor: ${seletor}`);
                break;
            }
        }
        
        // Se não encontrar nenhum container, usar o body inteiro
        if (!containerPrincipal) {
            console.warn('⚠️ Container principal não encontrado, usando body completo');
            containerPrincipal = document.body;
        }
        
        // Clonar o container
        const container = containerPrincipal.cloneNode(true);
        
        // Remover elementos desnecessários
        const elementosRemover = [
            '#sistema-downloads-container',
            '.download-section',
            '.sistema-downloads',
            'script',
            '.info-container' // Remove a caixa de informações
        ];
        
        elementosRemover.forEach(seletor => {
            const elementos = container.querySelectorAll(seletor);
            elementos.forEach(el => el.remove());
        });
        
        // Extrair todos os estilos da página atual
        let estilosCompletos = '';
        const folhasEstilo = document.styleSheets;
        
        try {
            for (let i = 0; i < folhasEstilo.length; i++) {
                const folha = folhasEstilo[i];
                try {
                    const regras = folha.cssRules || folha.rules;
                    if (regras) {
                        for (let j = 0; j < regras.length; j++) {
                            estilosCompletos += regras[j].cssText + '\n';
                        }
                    }
                } catch (e) {
                    // Ignora erros de CORS para estilos externos
                    console.warn('Não foi possível acessar folha de estilo:', e);
                }
            }
        } catch (e) {
            console.warn('Erro ao extrair estilos:', e);
        }
        
        // Adicionar estilos inline também
        const estilosInline = document.querySelectorAll('style');
        estilosInline.forEach(style => {
            estilosCompletos += style.innerHTML + '\n';
        });
        
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${titulo} - ${dataAtual}</title>
    <style>
        /* Estilos base */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        /* Estilos extraídos da página */
        ${estilosCompletos}
        
        /* Ajustes para o HTML exportado */
        body { background: white !important; }
        .container, .content-wrapper, main { 
            max-width: 1200px !important; 
            margin: 0 auto !important; 
            padding: 20px !important;
        }
        
        /* Garantir que tabelas fiquem visíveis */
        table { 
            width: 100% !important; 
            border-collapse: collapse !important; 
            margin: 20px 0 !important;
        }
        
        th { 
            background: #003366 !important; 
            color: white !important; 
            padding: 10px !important;
            text-align: center !important;
        }
        
        td { 
            padding: 8px !important; 
            border-bottom: 1px solid #ddd !important;
        }
        
        .especie { background-color: #cce5ff !important; }
        .alinea { background-color: #f0f8ff !important; }
        .total { 
            background-color: #003366 !important; 
            color: white !important; 
        }
        
        .valor-positivo { color: #28a745 !important; font-weight: bold !important; }
        .valor-negativo { color: #dc3545 !important; font-weight: bold !important; }
        
        /* Remover elementos de interface */
        .download-section, .sistema-downloads, #sistema-downloads-container {
            display: none !important;
        }
        
        /* Ajustar gráficos */
        .chart-container {
            page-break-inside: avoid;
            margin: 20px 0;
        }
        
        /* Impressão */
        @media print {
            body { margin: 0; padding: 10px; }
            .chart-container { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    ${container.innerHTML}
    
    <div style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666;">
        <p><strong>${titulo}</strong> - Gerado em ${dataAtual}</p>
        <p>Sistema de Relatórios Financeiros</p>
    </div>
</body>
</html>`;
    },
    
    adicionarCabecalhoPDF: function(pdf) {
        const largura = 297;
        const centro = largura / 2;
        let posY = 15;
        
        pdf.setFontSize(16);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(0, 51, 102);
        pdf.text(this.config.nomeRelatorio.toUpperCase(), centro, posY, { align: 'center' });
        posY += 8;
        
        pdf.setFontSize(12);
        pdf.setFont(undefined, 'normal');
        pdf.setTextColor(80, 80, 80);
        pdf.text('Comparativo 2024 vs 2025', centro, posY, { align: 'center' });
        posY += 10;
        
        pdf.setFontSize(10);
        pdf.setTextColor(100, 100, 100);
        const agora = new Date().toLocaleString('pt-BR');
        pdf.text(`Gerado em: ${agora}`, centro, posY, { align: 'center' });
        posY += 15;
        
        return posY;
    },
    
    adicionarTabelaPDF: async function(pdf, posY) {
        console.log('📊 Adicionando tabela ao PDF...');
        
        const dadosTabela = this.extrairDadosTabela();
        
        if (!dadosTabela || dadosTabela.length === 0) {
            console.warn('⚠️ Nenhum dado encontrado na tabela');
            return posY + 20;
        }
        
        const colunas = [
            { header: 'CÓDIGO', dataKey: 'codigo' },
            { header: 'NOME', dataKey: 'nome' },
            { header: 'RECEITA 2024', dataKey: 'valor2024' },
            { header: 'RECEITA 2025', dataKey: 'valor2025' },
            { header: 'VARIAÇÃO ABS', dataKey: 'variacaoAbs' },
            { header: 'VAR %', dataKey: 'variacaoPerc' }
        ];
        
        pdf.autoTable({
            columns: colunas,
            body: dadosTabela,
            startY: posY,
            margin: { left: 10, right: 10 },
            styles: {
                fontSize: 8,
                cellPadding: 3
            },
            headStyles: {
                fillColor: [0, 51, 102],
                textColor: [255, 255, 255],
                fontStyle: 'bold'
            },
            didParseCell: function(data) {
                const rowData = dadosTabela[data.row.index];
                if (rowData && rowData.tipo) {
                    switch (rowData.tipo) {
                        case 'especie':
                            data.cell.styles.fillColor = [230, 240, 255];
                            data.cell.styles.fontStyle = 'bold';
                            break;
                        case 'alinea':
                            data.cell.styles.fillColor = [248, 250, 255];
                            break;
                        case 'total':
                            data.cell.styles.fillColor = [0, 51, 102];
                            data.cell.styles.textColor = [255, 255, 255];
                            data.cell.styles.fontStyle = 'bold';
                            break;
                    }
                }
            }
        });
        
        return pdf.lastAutoTable.finalY + 20;
    },
    
    extrairDadosTabela: function() {
        const dados = [];
        const tabela = document.querySelector(`#${this.config.tabelaPrincipal} table`);
        
        if (!tabela) {
            console.error('Tabela não encontrada');
            return dados;
        }
        
        const linhas = tabela.querySelectorAll('tbody tr');
        
        linhas.forEach(linha => {
            const celulas = linha.querySelectorAll('td');
            if (celulas.length >= 6) {
                let tipo = 'normal';
                if (linha.classList.contains('especie')) tipo = 'especie';
                else if (linha.classList.contains('alinea')) tipo = 'alinea';
                else if (linha.classList.contains('total')) tipo = 'total';
                
                dados.push({
                    tipo: tipo,
                    codigo: celulas[0].textContent.trim().replace(/[🏛️🔧💰🏢🔄🏦├─]/g, ''),
                    nome: celulas[1].textContent.trim(),
                    valor2024: celulas[2].textContent.trim(),
                    valor2025: celulas[3].textContent.trim(),
                    variacaoAbs: celulas[4].textContent.trim(),
                    variacaoPerc: celulas[5].textContent.trim()
                });
            }
        });
        
        return dados;
    },
    
    adicionarOutrasSecoesPDF: async function(pdf) {
        for (const secao of this.config.secoesPrincipais) {
            if (secao.id === this.config.tabelaPrincipal) continue;
            
            const elemento = document.getElementById(secao.id);
            if (elemento) {
                pdf.addPage('landscape');
                let posY = 20;
                
                pdf.setFontSize(13);
                pdf.setFont(undefined, 'bold');
                pdf.setTextColor(0, 51, 102);
                pdf.text(secao.nome, 15, posY);
                posY += 12;
                
                try {
                    const canvas = await html2canvas(elemento, {
                        scale: 1.5,
                        useCORS: true,
                        backgroundColor: '#ffffff',
                        logging: false
                    });
                    
                    const imgData = canvas.toDataURL('image/png', 0.85);
                    const aspectRatio = canvas.height / canvas.width;
                    const larguraImg = 250;
                    const alturaImg = Math.min(larguraImg * aspectRatio, 150);
                    
                    pdf.addImage(imgData, 'PNG', 15, posY, larguraImg, alturaImg);
                    
                    console.log(`✅ Seção ${secao.nome} adicionada ao PDF`);
                } catch (error) {
                    console.error(`❌ Erro ao capturar ${secao.nome}:`, error);
                    pdf.setFontSize(11);
                    pdf.setTextColor(220, 53, 69);
                    pdf.text('Erro ao capturar esta seção.', 15, posY);
                }
            }
        }
    },
    
    adicionarRodapePDF: function(pdf) {
        const totalPaginas = pdf.internal.getNumberOfPages();
        
        for (let i = 1; i <= totalPaginas; i++) {
            pdf.setPage(i);
            
            pdf.setDrawColor(200, 200, 200);
            pdf.line(15, 200, 280, 200);
            
            pdf.setFontSize(8);
            pdf.setTextColor(120, 120, 120);
            pdf.text('Sistema de Relatórios', 15, 205);
            
            const agora = new Date().toLocaleString('pt-BR');
            pdf.text(`Gerado: ${agora}`, 148, 205, { align: 'center' });
            pdf.text(`Página ${i} de ${totalPaginas}`, 280, 205, { align: 'right' });
        }
    }
};

// Exportar globalmente
window.SistemaDownloads = SistemaDownloads;