/**
 * SISTEMA DE DOWNLOADS COM PDF OTIMIZADO
 * REMOVE RESUMO E NOUGS - FOCA NA TABELA E COMPARATIVO
 */

const SistemaDownloads = {
    config: {
        nomeRelatorio: 'Relatório',
        secoesPrincipais: [],
        tabelaPrincipal: null,
        container: 'sistema-downloads-container'
    },
    
    estado: {
        inicializado: false,
        processando: false
    },
    
    inicializar: function(configuracao) {
        console.log('🚀 Inicializando Sistema de Downloads...');
        
        this.config = { ...this.config, ...configuracao };
        this.criarHTML();
        this.adicionarEventListeners();
        
        this.estado.inicializado = true;
        console.log('✅ Sistema funcionando!');
    },
    
    criarHTML: function() {
        const container = document.getElementById(this.config.container);
        if (!container) {
            console.error('❌ Container não encontrado');
            return;
        }
        
        const html = `
            <div class="sistema-downloads">
                <div class="downloads-titulo">
                    <span class="icone">📥</span>
                    <span>Downloads do Relatório</span>
                </div>
                
                <div class="downloads-grid">
                    <button class="download-btn btn-tabela" id="btn-tabela">
                        <span class="icone">📊</span>
                        <span>Tabela Principal</span>
                    </button>
                    
                    <button class="download-btn btn-html" id="btn-html">
                        <span class="icone">🌐</span>
                        <span>Arquivo HTML</span>
                    </button>
                    
                    <button class="download-btn btn-pdf" id="btn-pdf">
                        <span class="icone">📄</span>
                        <span>Gerar PDF</span>
                    </button>
                    
                    <button class="download-btn btn-completo" id="btn-csv">
                        <span class="icone">📋</span>
                        <span>Dados CSV</span>
                    </button>
                </div>
                
                <div class="downloads-loading" id="downloads-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-texto">Processando...</div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    },
    
    adicionarEventListeners: function() {
        document.getElementById('btn-tabela').addEventListener('click', () => this.downloadTabela());
        document.getElementById('btn-html').addEventListener('click', () => this.downloadHTML());
        document.getElementById('btn-pdf').addEventListener('click', () => this.gerarPDF());
        document.getElementById('btn-csv').addEventListener('click', () => this.downloadCSV());
    },
    
    mostrarLoading: function(show = true, texto = 'Processando...') {
        const loading = document.getElementById('downloads-loading');
        const textoElement = loading?.querySelector('.loading-texto');
        
        if (loading) {
            loading.classList.toggle('ativo', show);
        }
        
        if (textoElement) {
            textoElement.textContent = texto;
        }
        
        this.estado.processando = show;
    },
    
    feedbackBotao: function(idBotao, tipo = 'sucesso') {
        const botao = document.getElementById(idBotao);
        if (!botao) return;
        
        const icone = botao.querySelector('.icone');
        const textoOriginal = icone.textContent;
        
        botao.classList.add(tipo);
        
        if (tipo === 'sucesso') {
            icone.textContent = '✅';
        } else if (tipo === 'erro') {
            icone.textContent = '❌';
        }
        
        setTimeout(() => {
            botao.classList.remove(tipo);
            icone.textContent = textoOriginal;
        }, 2000);
    },
    
    downloadTabela: function() {
        try {
            const tabela = document.querySelector('table');
            if (!tabela) {
                throw new Error('Tabela não encontrada');
            }
            
            const novaJanela = window.open('', '_blank');
            const html = this.gerarHTMLTabela(tabela);
            
            novaJanela.document.write(html);
            novaJanela.document.close();
            
            this.feedbackBotao('btn-tabela', 'sucesso');
            
        } catch (error) {
            console.error('Erro:', error);
            this.feedbackBotao('btn-tabela', 'erro');
            alert('Erro: ' + error.message);
        }
    },
    
    downloadHTML: function() {
        this.mostrarLoading(true, 'Gerando HTML...');
        
        try {
            const htmlCompleto = this.gerarHTMLCompleto();
            
            const blob = new Blob([htmlCompleto], { type: 'text/html;charset=utf-8' });
            const dataAtual = new Date().toISOString().split('T')[0];
            const nomeArquivo = `${this.config.nomeRelatorio.toLowerCase().replace(/\s/g, '-')}-${dataAtual}.html`;
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = nomeArquivo;
            link.click();
            URL.revokeObjectURL(url);
            
            this.feedbackBotao('btn-html', 'sucesso');
            
        } catch (error) {
            console.error('Erro:', error);
            this.feedbackBotao('btn-html', 'erro');
            alert('Erro: ' + error.message);
        } finally {
            this.mostrarLoading(false);
        }
    },
    
    // ✅ NOVA FUNÇÃO: PDF otimizado só com tabela e comparativo
    gerarPDF: function() {
        this.mostrarLoading(true, 'Preparando PDF...');
        
        try {
            const htmlPDF = this.gerarHTMLParaPDF();
            
            const novaJanela = window.open('', '_blank');
            novaJanela.document.write(htmlPDF);
            novaJanela.document.close();
            
            // Aguardar carregar e automaticamente abrir impressão
            novaJanela.onload = function() {
                setTimeout(function() {
                    novaJanela.print();
                }, 500);
            };
            
            this.feedbackBotao('btn-pdf', 'sucesso');
            
        } catch (error) {
            console.error('Erro:', error);
            this.feedbackBotao('btn-pdf', 'erro');
            alert('Erro: ' + error.message);
        } finally {
            this.mostrarLoading(false);
        }
    },
    
    downloadCSV: function() {
        this.mostrarLoading(true, 'Gerando CSV...');
        
        try {
            const tabela = document.querySelector('table');
            if (!tabela) {
                throw new Error('Tabela não encontrada');
            }
            
            let csv = '';
            
            const headers = tabela.querySelectorAll('thead th');
            const headerRow = Array.from(headers).map(th => `"${th.textContent.trim()}"`).join(',');
            csv += headerRow + '\n';
            
            const rows = tabela.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const rowData = Array.from(cells).map(td => {
                    let text = td.textContent.trim();
                    text = text.replace(/[🏦├─]/g, '');
                    text = text.replace(/\s+/g, ' ');
                    return `"${text}"`;
                }).join(',');
                csv += rowData + '\n';
            });
            
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
            const dataAtual = new Date().toISOString().split('T')[0];
            const nomeArquivo = `${this.config.nomeRelatorio.toLowerCase().replace(/\s/g, '-')}-${dataAtual}.csv`;
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = nomeArquivo;
            link.click();
            URL.revokeObjectURL(url);
            
            this.feedbackBotao('btn-csv', 'sucesso');
            
        } catch (error) {
            console.error('Erro:', error);
            this.feedbackBotao('btn-csv', 'erro');
            alert('Erro: ' + error.message);
        } finally {
            this.mostrarLoading(false);
        }
    },
    
    // ✅ HTML OTIMIZADO PARA PDF - SÓ TABELA E COMPARATIVO
    gerarHTMLParaPDF: function() {
        const titulo = this.config.nomeRelatorio;
        const dataAtual = new Date().toLocaleString('pt-BR');
        
        // Extrair apenas TABELA e COMPARATIVO
        let conteudoTabela = '';
        let conteudoComparativo = '';
        
        // Extrair tabela
        const elementoTabela = document.getElementById('secao-tabela-principal');
        if (elementoTabela) {
            const tabela = elementoTabela.querySelector('table');
            if (tabela) {
                conteudoTabela = tabela.outerHTML;
            }
        }
        
        // Extrair comparativo mensal
        const elementoComparativo = document.getElementById('secao-comparativo');
        if (elementoComparativo) {
            conteudoComparativo = elementoComparativo.innerHTML;
        }
        
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${titulo} - PDF</title>
    <style>
        /* === ESTILOS OTIMIZADOS PARA PDF === */
        @page {
            size: A4 landscape; /* ✅ PAISAGEM PARA MELHOR VISUALIZAÇÃO */
            margin: 12mm;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            font-size: 10px; /* ✅ FONTE MAIOR */
            line-height: 1.3;
            color: #333;
            background: white;
        }
        
        .container {
            max-width: 100%;
            margin: 0;
            padding: 0;
        }
        
        .header {
            text-align: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #003366;
            page-break-inside: avoid;
        }
        
        .header h1 {
            color: #003366;
            font-size: 16px; /* ✅ TÍTULO MAIOR */
            font-weight: bold;
            margin-bottom: 6px;
        }
        
        .header .data {
            color: #666;
            font-size: 11px;
            font-weight: normal;
        }
        
        /* === TABELA OTIMIZADA PARA PDF PAISAGEM === */
        .secao-tabela {
            margin-bottom: 20px;
            page-break-inside: avoid;
        }
        
        .secao-tabela h3 {
            color: #003366;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 8px;
            padding: 6px 10px;
            background: #f0f8ff;
            border-left: 4px solid #0066cc;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0;
            font-size: 9px; /* ✅ FONTE DA TABELA MAIOR */
            page-break-inside: auto;
        }
        
        thead {
            display: table-header-group;
        }
        
        tbody {
            display: table-row-group;
        }
        
        th {
            background: #003366 !important;
            color: white !important;
            padding: 8px 5px; /* ✅ PADDING MAIOR */
            text-align: center;
            font-weight: bold;
            font-size: 9px; /* ✅ CABEÇALHO MAIOR */
            border: 1px solid white;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        td {
            padding: 6px 4px; /* ✅ PADDING MAIOR */
            text-align: center;
            border: 1px solid #ddd;
            font-size: 9px; /* ✅ DADOS MAIORES */
            page-break-inside: avoid;
        }
        
        /* ✅ VALORES MONETÁRIOS MAIORES E MAIS LEGÍVEIS */
        td:nth-child(3), td:nth-child(4), td:nth-child(5), td:nth-child(6) {
            font-size: 9px !important; /* ✅ VALORES AINDA MAIORES */
            font-weight: 500;
            font-family: 'Courier New', monospace;
        }
        
        .especie {
            background: #e6f3ff !important;
            font-weight: bold;
            border-left: 3px solid #0066cc !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .especie td:first-child {
            font-family: 'Courier New', monospace;
            color: #003366;
            font-weight: bold;
            font-size: 8px;
        }
        
        .especie td:nth-child(2) {
            text-align: left;
            color: #003366;
            font-weight: bold;
            font-size: 9px; /* ✅ NOME DA ESPÉCIE MAIOR */
        }
        
        .alinea {
            background: #f8fbff !important;
            border-left: 2px solid #b3d9ff !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .alinea td:first-child {
            padding-left: 12px;
            font-family: 'Courier New', monospace;
            color: #666;
            font-size: 8px;
        }
        
        .alinea td:nth-child(2) {
            text-align: left;
            font-style: italic;
            color: #555;
            padding-left: 8px;
            font-size: 8px;
        }
        
        .total {
            background: #003366 !important;
            color: white !important;
            font-weight: bold;
            font-size: 10px !important; /* ✅ TOTAL MAIOR */
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .total td {
            color: white !important;
            font-weight: bold;
            font-size: 10px !important; /* ✅ VALORES DO TOTAL MAIORES */
        }
        
        .valor-positivo {
            color: #28a745 !important;
            font-weight: bold;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .valor-negativo {
            color: #dc3545 !important;
            font-weight: bold;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        /* === COMPARATIVO MENSAL OTIMIZADO === */
        .secao-comparativo {
            margin-top: 20px;
            page-break-inside: avoid;
        }
        
        .secao-comparativo h3 {
            color: #28a745;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 6px 10px;
            background: #f0f8ff;
            border-left: 4px solid #28a745;
        }
        
        .comparativo-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr); /* ✅ 3 COLUNAS EM PAISAGEM */
            gap: 8px;
            page-break-inside: avoid;
        }
        
        .comparativo-item {
            background: #f8f9fa !important;
            padding: 8px;
            border: 1px solid #ddd;
            border-left: 3px solid #28a745 !important;
            font-size: 8px;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .comparativo-mes {
            font-weight: bold;
            color: #333;
            margin-bottom: 4px;
            text-align: center;
            font-size: 9px; /* ✅ MÊS MAIOR */
        }
        
        .comparativo-valores {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2px;
            font-size: 8px;
        }
        
        .comparativo-variacao {
            border-top: 1px solid #ddd;
            padding-top: 2px;
            margin-top: 2px;
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            font-size: 8px;
        }
        
        /* === RODAPÉ === */
        .rodape {
            text-align: center;
            margin-top: 15px;
            padding-top: 8px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 9px;
            page-break-inside: avoid;
        }
        
        /* === QUEBRAS DE PÁGINA === */
        .secao-tabela {
            page-break-inside: avoid;
        }
        
        .secao-comparativo {
            page-break-inside: avoid;
        }
        
        tr {
            page-break-inside: avoid;
        }
        
        /* === IMPRESSÃO === */
        @media print {
            body {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        }
    </style>
    
    <script>
        // Abrir automaticamente a impressão quando carregar
        window.onload = function() {
            console.log('📄 Abrindo impressão automática...');
            setTimeout(function() {
                window.print();
            }, 800);
        };
        
        window.onafterprint = function() {
            console.log('📄 Impressão concluída');
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>${titulo}</h1>
            <div class="data">Relatório gerado em: ${dataAtual}</div>
        </div>
        
        <!-- ✅ SÓ A TABELA -->
        <div class="secao-tabela">
            <h3>Tabela Principal</h3>
            ${conteudoTabela}
        </div>
        
        <!-- ✅ SÓ O COMPARATIVO MENSAL -->
        ${conteudoComparativo ? `
        <div class="secao-comparativo">
            <h3>Comparativo Mensal</h3>
            ${conteudoComparativo}
        </div>
        ` : ''}
        
        <div class="rodape">
            <p><strong>Sistema de Relatórios</strong> | ${titulo} | ${dataAtual}</p>
        </div>
    </div>
</body>
</html>`;
    },
    
    // HTML limpo para a tabela
    gerarHTMLTabela: function(tabela) {
        const titulo = this.config.nomeRelatorio;
        const dataAtual = new Date().toLocaleString('pt-BR');
        
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${titulo}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #003366;
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: bold;
        }
        
        .header .data {
            color: #666;
            font-size: 14px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        th {
            background: linear-gradient(135deg, #003366, #004080);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
        }
        
        td {
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 12px;
        }
        
        .especie {
            background: linear-gradient(135deg, #e6f3ff, #cce5ff);
            font-weight: bold;
            border-left: 4px solid #0066cc;
        }
        
        .especie td:first-child {
            text-align: center;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #003366;
        }
        
        .especie td:nth-child(2) {
            text-align: left;
            font-weight: bold;
            color: #003366;
        }
        
        .alinea {
            background-color: #f8fbff;
            border-left: 3px solid #b3d9ff;
        }
        
        .alinea td:first-child {
            padding-left: 30px;
            font-family: 'Courier New', monospace;
            color: #666;
        }
        
        .alinea td:nth-child(2) {
            text-align: left;
            font-style: italic;
            color: #555;
            padding-left: 20px;
        }
        
        .total {
            background: linear-gradient(135deg, #003366, #004080);
            color: white;
            font-weight: bold;
            font-size: 13px;
        }
        
        .valor-positivo {
            color: #28a745;
            font-weight: bold;
        }
        
        .valor-negativo {
            color: #dc3545;
            font-weight: bold;
        }
        
        .rodape {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 10px;
            color: #666;
            font-size: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        @media print {
            body { 
                background: white; 
                padding: 10px;
            }
            .header, .rodape {
                box-shadow: none;
                border: 1px solid #ddd;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>${titulo}</h1>
        <div class="data">Gerado em: ${dataAtual}</div>
    </div>
    
    ${tabela.outerHTML}
    
    <div class="rodape">
        Sistema de Relatórios | ${titulo} | ${dataAtual}
    </div>
</body>
</html>`;
    },
    
    // ✅ HTML completo melhorado (REMOVENDO RESUMO E NOUGS)
    gerarHTMLCompleto: function() {
        const titulo = this.config.nomeRelatorio;
        const dataAtual = new Date().toLocaleDateString('pt-BR');
        
        let conteudoSecoes = '';
        
        // ✅ FILTRAR APENAS TABELA E COMPARATIVO
        const secoesPermitidas = ['secao-tabela-principal', 'secao-comparativo'];
        
        this.config.secoesPrincipais.forEach(secao => {
            // ✅ PULAR RESUMO E NOUGS
            if (!secoesPermitidas.includes(secao.id)) {
                return;
            }
            
            const elemento = document.getElementById(secao.id);
            if (elemento) {
                let conteudoLimpo = elemento.innerHTML;
                
                if (secao.id === 'secao-tabela-principal') {
                    const tabela = elemento.querySelector('table');
                    if (tabela) {
                        conteudoLimpo = tabela.outerHTML;
                    }
                }
                
                conteudoSecoes += `
                    <div class="secao">
                        <h3>${secao.nome}</h3>
                        <div class="conteudo-secao">
                            ${conteudoLimpo}
                        </div>
                    </div>
                `;
            }
        });
        
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${titulo} - ${dataAtual}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #003366;
        }
        
        .header h1 {
            color: #003366;
            margin: 0 0 15px 0;
            font-size: 28px;
            font-weight: bold;
        }
        
        .header .data {
            color: #666;
            font-size: 16px;
            font-weight: 500;
        }
        
        .secao {
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 5px solid #0066cc;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .secao h3 {
            color: #003366;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 20px;
            font-weight: 600;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: linear-gradient(135deg, #003366, #004080);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
        }
        
        td {
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 12px;
        }
        
        .especie {
            background: linear-gradient(135deg, #e6f3ff, #cce5ff);
            font-weight: bold;
            border-left: 4px solid #0066cc;
        }
        
        .especie td:first-child {
            font-family: 'Courier New', monospace;
            color: #003366;
        }
        
        .especie td:nth-child(2) {
            text-align: left;
            color: #003366;
        }
        
        .alinea {
            background-color: #f8fbff;
            border-left: 3px solid #b3d9ff;
        }
        
        .alinea td:first-child {
            padding-left: 30px;
            font-family: 'Courier New', monospace;
            color: #666;
        }
        
        .alinea td:nth-child(2) {
            text-align: left;
            font-style: italic;
            color: #555;
            padding-left: 20px;
        }
        
        .total {
            background: linear-gradient(135deg, #003366, #004080);
            color: white;
            font-weight: bold;
        }
        
        .valor-positivo {
            color: #28a745;
            font-weight: bold;
        }
        
        .valor-negativo {
            color: #dc3545;
            font-weight: bold;
        }
        
        .comparativo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .comparativo-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #28a745;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .rodape {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
            font-size: 14px;
        }
        
        @media print {
            body { 
                background: white; 
                padding: 10px;
            }
            .container { 
                box-shadow: none; 
                padding: 20px;
            }
            .secao {
                page-break-inside: avoid;
                margin-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>${titulo}</h1>
            <div class="data">Relatório gerado em: ${dataAtual}</div>
        </div>
        
        ${conteudoSecoes}
        
        <div class="rodape">
            <p><strong>Sistema de Relatórios</strong> | ${titulo} | Gerado automaticamente em ${new Date().toLocaleString('pt-BR')}</p>
        </div>
    </div>
</body>
</html>`;
    }
};

window.SistemaDownloads = SistemaDownloads;