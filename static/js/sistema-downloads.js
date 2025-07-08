/**
 * SISTEMA DE DOWNLOADS - VERSÃO 2.1 CORRIGIDA
 * Sistema unificado e reutilizável para downloads de relatórios
 * Com foco especial em HTML auto-suficiente e completo
 */

// Gerenciador de bibliotecas externas
const BibliotecasDownload = {
    bibliotecas: [
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
    ],
    
    carregarTodas: async function() {
        console.log('🔍 Verificando e carregando bibliotecas...');
        
        const promessas = this.bibliotecas.map(lib => {
            if (!lib.verificar()) {
                return this.carregarBiblioteca(lib);
            }
            console.log(`✅ ${lib.nome} já carregado`);
            return Promise.resolve();
        });
        
        await Promise.all(promessas);
        console.log('✅ Todas as bibliotecas carregadas!');
    },
    
    carregarBiblioteca: function(lib) {
        return new Promise((resolve, reject) => {
            console.log(`⏳ Carregando ${lib.nome}...`);
            const script = document.createElement('script');
            script.src = lib.url;
            script.onload = () => {
                console.log(`✅ ${lib.nome} carregado com sucesso!`);
                resolve();
            };
            script.onerror = () => {
                console.error(`❌ Erro ao carregar ${lib.nome}`);
                reject(new Error(`Falha ao carregar ${lib.nome}`));
            };
            document.head.appendChild(script);
        });
    }
};

// Sistema principal de downloads
const SistemaDownloads = {
    // Configurações padrão
    config: {
        nomeRelatorio: 'Relatório',
        titulo: 'RELATÓRIO DO SISTEMA',
        subtitulo: 'Documento gerado automaticamente',
        secoesPrincipais: [],
        tabelaPrincipal: 'secao-tabela-principal',
        seletoresRemover: [
            '#sistema-downloads-container',
            '.download-section',
            '.sistema-downloads',
            '.info-container',
            '.download-loading',
            'script',
            'style[data-download-system]',
            // ADICIONAR SELETORES DE GRÁFICO
            '[id*="grafico"]',
            '.chart-container',
            '.grafico-container',
            '[class*="grafico"]',
            '.secao-relatorio:has(canvas)',
            'section:has(.chart-container)'
        ],
        estilosCustomizados: '',
        metadados: {
            autor: 'Sistema de Relatórios',
            versao: '2.1'
        }
    },
    
    // Estratégias de extração de dados
    estrategiasExtracao: {
        tabela: {
            extrair: function(elemento) {
                return SistemaDownloads.ExtratorTabela.extrair(elemento);
            }
        },
        resumo: {
            extrair: function(elemento) {
                return SistemaDownloads.ExtratorResumo.extrair(elemento);
            }
        },
        comparativo: {
            extrair: function(elemento) {
                return SistemaDownloads.ExtratorComparativo.extrair(elemento);
            }
        },
        lista: {
            extrair: function(elemento) {
                return SistemaDownloads.ExtratorLista.extrair(elemento);
            }
        },
        grafico: {
            extrair: function(elemento) {
                return SistemaDownloads.ExtratorGrafico.extrair(elemento);
            }
        }
    },
    
    // Inicialização do sistema
    inicializar: async function(configuracao = {}) {
        console.log('🚀 Inicializando Sistema de Downloads v2.1...');
        
        // Mesclar configurações
        this.config = { ...this.config, ...configuracao };
        
        // Carregar bibliotecas necessárias
        try {
            await BibliotecasDownload.carregarTodas();
        } catch (error) {
            console.error('❌ Erro ao carregar bibliotecas:', error);
        }
        
        // Criar interface
        this.criarInterface();
        
        // Adicionar estilos
        this.adicionarEstilos();
        
        console.log('✅ Sistema de Downloads inicializado!');
    },
    
    // Criar interface de download
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
    
    // Adicionar estilos do sistema
    adicionarEstilos: function() {
        // Verificar se já existe
        if (document.querySelector('style[data-download-system]')) {
            return;
        }
        
        const style = document.createElement('style');
        style.setAttribute('data-download-system', 'true');
        style.textContent = `
            /* === SISTEMA DE DOWNLOADS === */
            .download-section {
                margin: 20px 0 30px 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                color: white;
            }
            
            .download-section h4 {
                margin: 0 0 20px 0;
                color: white;
                font-size: 18px;
                text-align: center;
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .download-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            
            .download-btn {
                padding: 15px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .download-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            
            .btn-png {
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
            }
            
            .btn-html {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
            }
            
            .btn-zip {
                background: linear-gradient(135deg, #ffc107, #ff8f00);
                color: #333;
            }
            
            .btn-pdf {
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: white;
            }
            
            .download-loading {
                display: none;
                text-align: center;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                margin: 15px 0;
                backdrop-filter: blur(10px);
            }
            
            .download-spinner {
                border: 3px solid rgba(255,255,255,0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .download-loading-text {
                color: white;
                font-weight: 500;
                font-size: 14px;
            }
        `;
        document.head.appendChild(style);
    },
    
    // Mostrar/ocultar loading
    showDownloadLoading: function(show = true) {
        const loading = document.getElementById('downloadLoading');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    },
    
    // ===== DOWNLOAD HTML - MÉTODO PRINCIPAL =====
    downloadHTML: function() {
        this.showDownloadLoading(true);
        try {
            console.log('🌐 Iniciando geração do HTML completo e auto-suficiente...');
            
            // Gerar HTML completo
            const htmlCompleto = this.gerarHTMLCompletoAutoSuficiente();
            
            // Validar HTML gerado
            if (!htmlCompleto || htmlCompleto.length < 1000) {
                throw new Error('HTML gerado está vazio ou incompleto');
            }
            
            // Criar blob e fazer download
            const blob = new Blob([htmlCompleto], { type: 'text/html;charset=utf-8' });
            const dataFormatada = new Date().toISOString().split('T')[0];
            const nomeArquivo = `${this.config.nomeRelatorio.toLowerCase().replace(/\s+/g, '-')}-completo-${dataFormatada}.html`;
            
            // Download usando FileSaver ou fallback
            if (window.saveAs) {
                saveAs(blob, nomeArquivo);
            } else {
                this.downloadFallback(blob, nomeArquivo);
            }
            
            console.log('✅ HTML completo gerado com sucesso!');
            console.log(`📊 Tamanho do arquivo: ${(blob.size / 1024).toFixed(2)} KB`);
            
        } catch (error) {
            console.error('❌ Erro ao gerar HTML:', error);
            alert('Erro ao gerar arquivo HTML: ' + error.message);
        } finally {
            this.showDownloadLoading(false);
        }
    },
    
    // Gerar HTML completo e auto-suficiente
    gerarHTMLCompletoAutoSuficiente: function() {
        console.log('🔨 Construindo HTML auto-suficiente...');
        
        // Metadados
        const titulo = this.config.titulo;
        const subtitulo = this.config.subtitulo;
        const dataAtual = new Date().toLocaleDateString('pt-BR');
        const horaAtual = new Date().toLocaleTimeString('pt-BR');
        
        // Extrair conteúdo principal
        const conteudoPrincipal = this.extrairConteudoPrincipal();
        
        // Extrair todos os estilos
        const estilosCompletos = this.extrairTodosEstilos();
        
        // Montar HTML completo
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="${this.config.metadados.autor}">
    <meta name="generator" content="Sistema de Downloads v${this.config.metadados.versao}">
    <meta name="description" content="${titulo} - ${subtitulo}">
    <meta name="created" content="${new Date().toISOString()}">
    
    <title>${titulo} - ${dataAtual}</title>
    
    <style>
        /* ===== RESET E BASE ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* ===== CONTAINER PRINCIPAL ===== */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        
        /* ===== CABEÇALHO ===== */
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #003366;
        }
        
        .header h1 {
            color: #003366;
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .header h2 {
            color: #666;
            font-size: 16px;
            margin-bottom: 10px;
            font-weight: normal;
        }
        
        .header .data-geracao {
            color: #888;
            font-size: 14px;
            font-style: italic;
        }
        
        /* ===== SEÇÕES ===== */
        .secao {
            margin-bottom: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
        }
        
        .secao h3 {
            color: #003366;
            margin-bottom: 20px;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* ===== TABELAS ===== */
        .tabela-container {
            overflow-x: auto;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            font-size: 12px;
        }
        
        th {
            background: #003366;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        td {
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 11px;
        }
        
        tbody tr:hover {
            background-color: rgba(0, 102, 204, 0.05);
            transition: background-color 0.2s ease;
        }
        
        /* Classes específicas para tipos de linha */
        .especie {
            background-color: #cce5ff;
            font-weight: bold;
        }
        
        .detalhamento, .alinea {
            background-color: #f0f8ff;
        }
        
        .detalhamento td:first-child,
        .alinea td:first-child {
            padding-left: 30px;
            font-weight: normal;
            color: #555;
        }
        
        .detalhamento td:nth-child(2),
        .alinea td:nth-child(2) {
            font-style: italic;
            color: #666;
            text-align: left;
        }
        
        .total {
            background-color: #003366;
            color: white;
            font-weight: bold;
        }
        
        .total td {
            border-bottom: none;
        }
        
        /* Valores positivos e negativos */
        .valor-positivo {
            color: #28a745;
            font-weight: bold;
        }
        
        .valor-negativo {
            color: #dc3545;
            font-weight: bold;
        }
        
        /* ===== GRIDS E CARDS ===== */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
            max-height: none !important;  /* Sem limite de altura */
            overflow: visible !important; /* Sem scroll */
        }
        
        .card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #0066cc;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            min-height: auto;  /* Altura automática */
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .card strong {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-size: 13px;
        }
        
        .card .valor {
            font-size: 18px;
            font-weight: bold;
            color: #0066cc;
        }
        
        /* ===== GRÁFICOS E IMAGENS ===== */
        .grafico-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .grafico-container img,
        .grafico-container canvas {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        
        /* ===== RODAPÉ ===== */
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        .footer .sistema-info {
            margin-top: 10px;
            font-size: 11px;
            color: #999;
        }
        
        /* ===== RESPONSIVIDADE ===== */
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                padding: 15px;
                border-radius: 5px;
            }
            
            .header h1 {
                font-size: 20px;
            }
            
            .header h2 {
                font-size: 14px;
            }
            
            .grid-container {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 10px;
            }
            
            th, td {
                padding: 6px 4px;
            }
            
            .card {
                padding: 12px;
            }
            
            .card .valor {
                font-size: 16px;
            }
        }
        
        /* ===== IMPRESSÃO ===== */
        @media print {
            body {
                background: white;
                color: black;
            }
            
            .container {
                box-shadow: none;
                margin: 0;
                padding: 0;
                max-width: 100%;
            }
            
            .secao {
                page-break-inside: avoid;
                margin-bottom: 20px;
                border: 1px solid #ddd;
            }
            
            .tabela-container {
                page-break-inside: avoid;
            }
            
            .header {
                margin-bottom: 20px;
                padding-bottom: 10px;
            }
            
            .footer {
                margin-top: 30px;
                padding-top: 10px;
            }
            
            table {
                font-size: 9px;
            }
            
            th, td {
                padding: 4px;
            }
            
            .grid-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        /* ===== ESTILOS CUSTOMIZADOS ===== */
        ${this.config.estilosCustomizados}
        
        /* ===== ESTILOS EXTRAÍDOS DA PÁGINA ===== */
        ${estilosCompletos}
    </style>
</head>
<body>
    <div class="container">
        <!-- Cabeçalho -->
        <div class="header">
            <h1>${titulo}</h1>
            <h2>${subtitulo}</h2>
            <div class="data-geracao">
                Relatório gerado em: ${dataAtual} às ${horaAtual}
            </div>
        </div>
        
        <!-- Conteúdo Principal -->
        ${conteudoPrincipal}
        
        <!-- Rodapé -->
        <div class="footer">
            <p><strong>${titulo}</strong></p>
            <p>Documento gerado automaticamente pelo ${this.config.metadados.autor}</p>
            <div class="sistema-info">
                <p>Versão do Sistema: ${this.config.metadados.versao} | Data de Geração: ${dataAtual} ${horaAtual}</p>
                <p>Este documento é auto-suficiente e pode ser visualizado em qualquer navegador web</p>
            </div>
        </div>
    </div>
</body>
</html>`;
    },
    
    // Extrair conteúdo principal preservando estrutura
    extrairConteudoPrincipal: function() {
        console.log('📋 Extraindo conteúdo principal...');
        
        // Primeiro, tentar extrair apenas as seções configuradas
        if (this.config.secoesPrincipais && this.config.secoesPrincipais.length > 0) {
            return this.extrairSecoesConfiguradas();
        }
        
        // Se não houver seções configuradas, usar o método antigo
        let container = null;
        const seletoresPrincipais = [
            '.container',
            '.content-wrapper',
            '.main-content',
            'main',
            '#content',
            'article',
            '.relatorio-content'
        ];
        
        for (const seletor of seletoresPrincipais) {
            container = document.querySelector(seletor);
            if (container) {
                console.log(`✅ Container principal encontrado: ${seletor}`);
                break;
            }
        }
        
        if (!container) {
            console.warn('⚠️ Container principal não encontrado, usando body');
            container = document.body;
        }
        
        // Clonar e limpar
        const clone = container.cloneNode(true);
        
        // IMPORTANTE: Remover seções de gráfico ANTES de processar
        const graficos = clone.querySelectorAll('[id*="grafico"], .chart-container, .grafico-container, [class*="grafico"]');
        graficos.forEach(el => {
            console.log('🗑️ Removendo elemento de gráfico:', el.id || el.className);
            el.remove();
        });
        
        // Remover elementos desnecessários
        this.config.seletoresRemover.forEach(seletor => {
            const elementos = clone.querySelectorAll(seletor);
            elementos.forEach(el => el.remove());
        });
        
        // Processar elementos especiais
        this.processarElementosEspeciais(clone);
        
        return clone.innerHTML;
    },
    
    // Novo método para extrair apenas seções configuradas
    extrairSecoesConfiguradas: function() {
        console.log('📑 Extraindo seções configuradas...');
        let conteudoHTML = '';
        
        for (const secao of this.config.secoesPrincipais) {
            // PULAR COMPLETAMENTE SEÇÕES DE GRÁFICO NO HTML
            if (secao.tipo === 'grafico') {
                console.log(`⏭️ Pulando seção de gráfico: ${secao.nome}`);
                continue;
            }
            
            const elemento = document.getElementById(secao.id);
            
            if (elemento) {
                console.log(`📋 Processando seção: ${secao.nome}`);
                
                // Determinar estratégia de extração
                const estrategia = secao.tipo || 'default';
                let conteudoExtraido = '';
                
                if (this.estrategiasExtracao[estrategia]) {
                    conteudoExtraido = this.estrategiasExtracao[estrategia].extrair(elemento);
                } else {
                    // Extração padrão
                    conteudoExtraido = this.extrairSecaoPadrao(elemento);
                }
                
                // Adicionar seção ao HTML apenas se tiver conteúdo
                if (conteudoExtraido && conteudoExtraido.trim() !== '') {
                    conteudoHTML += `
                        <div class="secao" id="${secao.id}-exportado">
                            <h3>${secao.icone || '📊'} ${secao.nome}</h3>
                            ${conteudoExtraido}
                        </div>
                    `;
                }
            } else {
                console.warn(`⚠️ Seção não encontrada: ${secao.id}`);
            }
        }
        
        return conteudoHTML;
    },
    
    // Extrair todos os estilos da página
    extrairTodosEstilos: function() {
        console.log('🎨 Extraindo estilos da página...');
        let estilos = '';
        
        try {
            // Extrair de folhas de estilo
            const folhasEstilo = document.styleSheets;
            for (let i = 0; i < folhasEstilo.length; i++) {
                try {
                    const folha = folhasEstilo[i];
                    const regras = folha.cssRules || folha.rules;
                    
                    if (regras) {
                        for (let j = 0; j < regras.length; j++) {
                            const regra = regras[j].cssText;
                            // Filtrar regras do sistema de download
                            if (!regra.includes('download-section') && 
                                !regra.includes('download-btn') &&
                                !regra.includes('download-loading')) {
                                estilos += regra + '\n';
                            }
                        }
                    }
                } catch (e) {
                    // Ignora erros CORS
                    if (e.name !== 'SecurityError') {
                        console.warn('Erro ao acessar folha de estilo:', e);
                    }
                }
            }
            
            // Extrair estilos inline
            const estilosInline = document.querySelectorAll('style:not([data-download-system])');
            estilosInline.forEach(style => {
                estilos += '\n/* Estilo inline */\n' + style.innerHTML + '\n';
            });
            
            console.log(`✅ ${estilos.length} caracteres de CSS extraídos`);
            
        } catch (error) {
            console.error('❌ Erro ao extrair estilos:', error);
        }
        
        return estilos;
    },
    
    // Extração padrão de seção
    extrairSecaoPadrao: function(elemento) {
        const clone = elemento.cloneNode(true);
        
        // Limpar IDs para evitar duplicatas
        clone.querySelectorAll('[id]').forEach(el => {
            el.id = el.id + '-clone';
        });
        
        // Processar elementos especiais
        this.processarElementosEspeciais(clone);
        
        return clone.innerHTML;
    },
    
    // Processar elementos especiais (remover emojis desnecessários, etc)
    processarElementosEspeciais: function(elemento) {
        // Limpar emojis de estrutura (mantendo emojis de conteúdo)
        const textoNodes = this.obterNosDeTexto(elemento);
        textoNodes.forEach(node => {
            node.textContent = node.textContent
                .replace(/[🏛️├─│└]/g, '')  // Remover símbolos de estrutura
                .replace(/\s+/g, ' ')        // Normalizar espaços
                .trim();
        });
        
        // Processar imagens base64
        elemento.querySelectorAll('img').forEach(img => {
            if (img.src && img.src.startsWith('data:')) {
                // Manter imagens base64
                console.log('✅ Imagem base64 preservada');
            } else if (img.src) {
                // Para imagens externas, adicionar URL completa se necessário
                if (!img.src.startsWith('http')) {
                    img.src = new URL(img.src, window.location.href).href;
                }
            }
        });
        
        // Processar canvas (converter para imagem)
        elemento.querySelectorAll('canvas').forEach(canvas => {
            try {
                // Verificar se o canvas está visível e tem conteúdo
                if (canvas.offsetWidth > 0 && canvas.offsetHeight > 0) {
                    const img = document.createElement('img');
                    img.src = canvas.toDataURL('image/png');
                    img.className = canvas.className;
                    img.style.cssText = canvas.style.cssText;
                    img.alt = 'Gráfico exportado';
                    canvas.parentNode.replaceChild(img, canvas);
                    console.log('✅ Canvas convertido para imagem');
                }
            } catch (e) {
                console.warn('⚠️ Não foi possível converter canvas:', e);
            }
        });
    },
    
    // Obter todos os nós de texto
    obterNosDeTexto: function(elemento) {
        const nos = [];
        const walker = document.createTreeWalker(
            elemento,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                nos.push(node);
            }
        }
        
        return nos;
    },
    
    // Fallback para download
    downloadFallback: function(blob, nomeArquivo) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = nomeArquivo;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },
    
    // ===== EXTRATORES ESPECIALIZADOS =====
    
    // Extrator de Tabelas
    ExtratorTabela: {
        extrair: function(elemento) {
            const tabela = elemento.querySelector('table');
            if (!tabela) return '<p>Tabela não encontrada</p>';
            
            const clone = tabela.cloneNode(true);
            
            // Processar células
            clone.querySelectorAll('td, th').forEach(celula => {
                // Limpar texto
                celula.textContent = celula.textContent
                    .replace(/[🏛️🔧💰🏢🔄🏦├─│└]/g, '')
                    .trim();
            });
            
            return `<div class="tabela-container">${clone.outerHTML}</div>`;
        }
    },
    
    // Extrator de Resumo
    ExtratorResumo: {
        extrair: function(elemento) {
            const itens = elemento.querySelectorAll('.resumo-item, .card, [class*="col"]');
            
            if (itens.length === 0) {
                return this.extrairPorTexto(elemento);
            }
            
            let html = '<div class="grid-container">';
            
            itens.forEach(item => {
                const textoCompleto = item.textContent.trim();
                const linhas = textoCompleto.split('\n').filter(l => l.trim());
                
                if (linhas.length >= 2) {
                    const label = linhas[0];
                    const valor = linhas[1];
                    
                    html += `
                        <div class="card">
                            <strong>${label}</strong>
                            <div class="valor">${valor}</div>
                        </div>
                    `;
                }
            });
            
            html += '</div>';
            return html;
        },
        
        extrairPorTexto: function(elemento) {
            // Fallback: extrair por análise de texto
            const texto = elemento.textContent;
            const padrao = /([^:]+):\s*([^\n]+)/g;
            let match;
            let html = '<div class="grid-container">';
            
            while ((match = padrao.exec(texto)) !== null) {
                html += `
                    <div class="card">
                        <strong>${match[1].trim()}</strong>
                        <div class="valor">${match[2].trim()}</div>
                    </div>
                `;
            }
            
            html += '</div>';
            return html;
        }
    },
    
    // Extrator de Comparativo
    ExtratorComparativo: {
        extrair: function(elemento) {
            const itens = elemento.querySelectorAll('[class*="comparativo"] > div > div');
            
            if (itens.length === 0) {
                return elemento.innerHTML;
            }
            
            let html = '<div class="grid-container">';
            
            itens.forEach(item => {
                const titulo = item.querySelector('div:first-child')?.textContent || '';
                const valores = item.querySelectorAll('div:not(:first-child)');
                
                if (titulo && valores.length > 0) {
                    html += '<div class="card">';
                    html += `<strong>${titulo}</strong>`;
                    
                    valores.forEach(valor => {
                        const spans = valor.querySelectorAll('span');
                        if (spans.length >= 2) {
                            const label = spans[0].textContent;
                            const val = spans[1].textContent;
                            const classe = val.includes('-') ? 'valor-negativo' : 
                                         val.includes('+') ? 'valor-positivo' : '';
                            
                            html += `
                                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                                    <span>${label}</span>
                                    <span class="${classe}">${val}</span>
                                </div>
                            `;
                        }
                    });
                    
                    html += '</div>';
                }
            });
            
            html += '</div>';
            return html;
        }
    },
    
    // Extrator de Listas
    ExtratorLista: {
        extrair: function(elemento) {
            // Procurar por listas de itens
            let itens = elemento.querySelectorAll('.lista-item, .noug-item, li');
            
            // Se não encontrar, tentar buscar dentro de containers com scroll
            if (itens.length === 0) {
                const listaContainer = elemento.querySelector('.nougs-lista, .lista-container, [style*="overflow"]');
                if (listaContainer) {
                    itens = listaContainer.querySelectorAll('.noug-item, .lista-item, li, div > div');
                }
            }
            
            if (itens.length === 0) {
                return elemento.innerHTML;
            }
            
            // Criar grid sem limite de altura (sem scroll)
            let html = '<div class="grid-container" style="max-height: none; overflow: visible;">';
            
            itens.forEach(item => {
                // Tentar diferentes seletores para nome e valor
                let nome = '';
                let valor = '';
                
                // Primeiro tentar seletores específicos
                const nomeEl = item.querySelector('.nome, .noug-nome, span:first-child');
                const valorEl = item.querySelector('.valor, .noug-saldo, span:last-child');
                
                if (nomeEl && valorEl) {
                    nome = nomeEl.textContent.trim();
                    valor = valorEl.textContent.trim();
                } else {
                    // Se não encontrar, tentar extrair do texto completo
                    const texto = item.textContent.trim();
                    const partes = texto.split(/\s{2,}|\t/); // Dividir por múltiplos espaços ou tab
                    if (partes.length >= 2) {
                        nome = partes[0].trim();
                        valor = partes[partes.length - 1].trim();
                    } else {
                        nome = texto;
                    }
                }
                
                if (nome) {
                    html += `
                        <div class="card" style="min-height: auto;">
                            <strong>${nome}</strong>
                            ${valor ? `<div class="valor">${valor}</div>` : ''}
                        </div>
                    `;
                }
            });
            
            html += '</div>';
            
            // Adicionar total se existir
            const totalEl = elemento.querySelector('.nougs-total, .total-container, [class*="total"]');
            if (totalEl) {
                html += `
                    <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 6px; text-align: center; border: 2px solid #28a745;">
                        ${totalEl.innerHTML}
                    </div>
                `;
            }
            
            return html;
        }
    },
    
    // Extrator de Gráficos - SIMPLIFICADO (não inclui no HTML)
    ExtratorGrafico: {
        extrair: async function(elemento) {
            console.log('📊 Gráfico ignorado na exportação HTML');
            
            // Simplesmente não incluir o gráfico no HTML exportado
            return '';
        }
    },
    
    // ===== OUTROS MÉTODOS DE DOWNLOAD =====
    
    // Download PNG da tabela
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
    
    // Download ZIP completo
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
                    
                    const nomeArquivo = `${String(secao.ordem || 0).padStart(2, '0')}-${secao.nome.toLowerCase().replace(/\s+/g, '-')}.png`;
                    zip.file(nomeArquivo, blob);
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
    
    // Download PDF
    downloadPDF: async function() {
        this.showDownloadLoading(true);
        try {
            if (!window.jspdf) {
                throw new Error('Biblioteca jsPDF não carregada');
            }
            
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('landscape', 'mm', 'a4');
            
            console.log('📄 Iniciando geração do PDF...');
            
            // Adicionar cabeçalho
            let posY = this.adicionarCabecalhoPDF(pdf);
            
            // Adicionar tabela principal
            posY = await this.adicionarTabelaPDF(pdf, posY);
            
            // Adicionar outras seções
            await this.adicionarOutrasSecoesPDF(pdf);
            
            // Adicionar rodapé
            this.adicionarRodapePDF(pdf);
            
            // Salvar PDF
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
    
    // Adicionar cabeçalho ao PDF
    adicionarCabecalhoPDF: function(pdf) {
        const largura = 297; // A4 landscape
        const centro = largura / 2;
        let posY = 15;
        
        // Título principal
        pdf.setFontSize(16);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(0, 51, 102);
        pdf.text(this.config.titulo.toUpperCase(), centro, posY, { align: 'center' });
        posY += 8;
        
        // Subtítulo
        pdf.setFontSize(12);
        pdf.setFont(undefined, 'normal');
        pdf.setTextColor(80, 80, 80);
        pdf.text(this.config.subtitulo, centro, posY, { align: 'center' });
        posY += 10;
        
        // Data de geração
        pdf.setFontSize(10);
        pdf.setTextColor(100, 100, 100);
        const agora = new Date().toLocaleString('pt-BR');
        pdf.text(`Gerado em: ${agora}`, centro, posY, { align: 'center' });
        posY += 15;
        
        return posY;
    },
    
    // Adicionar tabela ao PDF
    adicionarTabelaPDF: async function(pdf, posY) {
        console.log('📊 Adicionando tabela ao PDF...');
        
        const dadosTabela = this.extrairDadosTabela();
        
        if (!dadosTabela || dadosTabela.length === 0) {
            console.warn('⚠️ Nenhum dado encontrado na tabela');
            return posY + 20;
        }
        
        // Configurar colunas
        const colunas = [
            { header: 'CÓDIGO', dataKey: 'codigo', width: 25 },      // Aumentado de 22 para 25
            { header: 'NOME', dataKey: 'nome', width: 125 },         // Reduzido de 128 para 125 para compensar
            { header: 'RECEITA 2024', dataKey: 'valor2024', width: 35 },
            { header: 'RECEITA 2025', dataKey: 'valor2025', width: 35 },
            { header: 'VARIAÇÃO ABS', dataKey: 'variacaoAbs', width: 35 },
            { header: 'VAR %', dataKey: 'variacaoPerc', width: 20 }
        ];
        
        // Adicionar título da seção
        pdf.setFontSize(14);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(0, 51, 102);
        pdf.text('Tabela Principal', 15, posY);
        posY += 10;
        
        // Gerar tabela
        pdf.autoTable({
            columns: colunas,
            body: dadosTabela,
            startY: posY,
            margin: { left: 10, right: 10 },
            styles: {
                fontSize: 8,              // Voltando para 8 para caber melhor
                cellPadding: 3,           // Voltando para 3
                textColor: [30, 30, 30],
                lineColor: [180, 180, 180],
                lineWidth: 0.5,
                overflow: 'linebreak',
                cellWidth: 'wrap',
                valign: 'middle'          // Alinhamento vertical ao centro
            },
            headStyles: {
                fillColor: [0, 51, 102],
                textColor: [255, 255, 255],
                fontStyle: 'bold',
                fontSize: 9,              // Reduzido de 10 para 9
                halign: 'center',
                valign: 'middle',         // Alinhamento vertical ao centro
                cellPadding: 4            // Reduzido de 5 para 4
            },
            columnStyles: {
                codigo: { 
                    halign: 'center', 
                    fontFamily: 'courier',
                    fontSize: 7,
                    cellWidth: 25         // Atualizado de 22 para 25
                },
                nome: { 
                    halign: 'left',
                    cellPadding: { left: 5, right: 3 },
                    valign: 'middle'      // Alinhamento vertical ao centro
                },
                valor2024: { 
                    halign: 'right',
                    fontFamily: 'courier',
                    fontSize: 7
                },
                valor2025: { 
                    halign: 'right',
                    fontFamily: 'courier',
                    fontSize: 7
                },
                variacaoAbs: { 
                    halign: 'right',
                    fontFamily: 'courier',
                    fontSize: 7
                },
                variacaoPerc: { 
                    halign: 'center', 
                    fontWeight: 'bold',
                    fontSize: 8
                }
            },
            didParseCell: function(data) {
                const rowData = dadosTabela[data.row.index];
                if (rowData && rowData.tipo) {
                    switch (rowData.tipo) {
                        case 'especie':
                            // Azul mais escuro e visível
                            data.cell.styles.fillColor = [66, 139, 202];  // Azul médio
                            data.cell.styles.textColor = [255, 255, 255];  // Texto branco
                            data.cell.styles.fontStyle = 'bold';
                            break;
                        case 'alinea':
                        case 'detalhamento':
                            // Cinza claro
                            data.cell.styles.fillColor = [245, 245, 245];  // Cinza bem claro
                            data.cell.styles.textColor = [50, 50, 50];     // Texto escuro
                            if (data.column.dataKey === 'nome') {
                                data.cell.styles.fontStyle = 'italic';
                                data.cell.styles.textColor = [100, 100, 100]; // Cinza para itálico
                            }
                            break;
                        case 'total':
                            data.cell.styles.fillColor = [0, 51, 102];     // Azul escuro
                            data.cell.styles.textColor = [255, 255, 255];  // Texto branco
                            data.cell.styles.fontStyle = 'bold';
                            break;
                    }
                    
                    // Para linhas com fundo azul (especie), manter texto branco nas variações
                    if (rowData.tipo === 'especie' && (data.column.dataKey === 'variacaoAbs' || data.column.dataKey === 'variacaoPerc')) {
                        data.cell.styles.textColor = [255, 255, 255];  // Texto branco
                        data.cell.styles.fontStyle = 'bold';
                    }
                    // Para outras linhas, colorir variações
                    else if ((data.column.dataKey === 'variacaoAbs' || data.column.dataKey === 'variacaoPerc') && rowData.tipo !== 'total' && rowData.tipo !== 'especie') {
                        if (rowData.variacaoNumero > 0) {
                            data.cell.styles.textColor = [0, 128, 0];    // Verde mais forte
                            data.cell.styles.fontStyle = 'bold';
                        } else if (rowData.variacaoNumero < 0) {
                            data.cell.styles.textColor = [220, 20, 60];  // Vermelho mais forte
                            data.cell.styles.fontStyle = 'bold';
                        }
                    }
                    
                    // Garantir alinhamento vertical ao centro para todas as células
                    data.cell.styles.valign = 'middle';
                }
            }
        });
        
        return pdf.lastAutoTable.finalY + 20;
    },
    
    // Extrair dados da tabela para PDF
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
                else if (linha.classList.contains('detalhamento')) tipo = 'detalhamento';
                else if (linha.classList.contains('total')) tipo = 'total';
                
                const codigo = celulas[0].textContent.trim().replace(/[🏛️🔧💰🏢🔄🏦├─]/g, '');
                const nome = celulas[1].textContent.trim();
                const valor2024 = celulas[2].textContent.trim();
                const valor2025 = celulas[3].textContent.trim();
                const variacaoAbs = celulas[4].textContent.trim();
                const variacaoPerc = celulas[5].textContent.trim();
                
                // Extrair número da variação para coloração
                let variacaoNumero = 0;
                const variacaoMatch = variacaoPerc.match(/([+-]?[\d,]+\.?\d*)/);
                if (variacaoMatch) {
                    variacaoNumero = parseFloat(variacaoMatch[1].replace(',', '.'));
                }
                
                dados.push({
                    tipo: tipo,
                    codigo: codigo,
                    nome: nome,
                    valor2024: valor2024,
                    valor2025: valor2025,
                    variacaoAbs: variacaoAbs,
                    variacaoPerc: variacaoPerc,
                    variacaoNumero: variacaoNumero
                });
            }
        });
        
        console.log(`✅ ${dados.length} linhas extraídas da tabela`);
        return dados;
    },
    
    // Adicionar outras seções ao PDF
    adicionarOutrasSecoesPDF: async function(pdf) {
        for (const secao of this.config.secoesPrincipais) {
            // Pular a tabela principal (já foi adicionada)
            if (secao.id === this.config.tabelaPrincipal) continue;
            
            const elemento = document.getElementById(secao.id);
            if (elemento) {
                // Adicionar nova página
                pdf.addPage('landscape');
                let posY = 20;
                
                // Título da seção
                pdf.setFontSize(14);
                pdf.setFont(undefined, 'bold');
                pdf.setTextColor(0, 51, 102);
                pdf.text(`${secao.icone || ''} ${secao.nome}`, 15, posY);
                posY += 15;
                
                try {
                    // Capturar seção como imagem
                    const canvas = await html2canvas(elemento, {
                        scale: 1.5,
                        useCORS: true,
                        backgroundColor: '#ffffff',
                        logging: false
                    });
                    
                    const imgData = canvas.toDataURL('image/png', 0.85);
                    const aspectRatio = canvas.height / canvas.width;
                    const larguraImg = 260; // Largura máxima em landscape
                    const alturaImg = Math.min(larguraImg * aspectRatio, 160);
                    
                    // Centralizar imagem
                    const xPos = (297 - larguraImg) / 2;
                    
                    pdf.addImage(imgData, 'PNG', xPos, posY, larguraImg, alturaImg);
                    
                    console.log(`✅ Seção ${secao.nome} adicionada ao PDF`);
                } catch (error) {
                    console.error(`❌ Erro ao capturar ${secao.nome}:`, error);
                    pdf.setFontSize(11);
                    pdf.setTextColor(220, 53, 69);
                    pdf.text('Erro ao capturar esta seção. Consulte a versão HTML.', 15, posY);
                }
            }
        }
    },
    
    // Adicionar rodapé ao PDF
    adicionarRodapePDF: function(pdf) {
        const totalPaginas = pdf.internal.getNumberOfPages();
        
        for (let i = 1; i <= totalPaginas; i++) {
            pdf.setPage(i);
            
            // Linha de separação
            pdf.setDrawColor(200, 200, 200);
            pdf.line(15, 195, 282, 195);
            
            // Rodapé
            pdf.setFontSize(8);
            pdf.setTextColor(120, 120, 120);
            pdf.text(this.config.metadados.autor, 15, 200);
            
            const agora = new Date().toLocaleString('pt-BR');
            pdf.text(`Gerado: ${agora}`, 148.5, 200, { align: 'center' });
            pdf.text(`Página ${i} de ${totalPaginas}`, 282, 200, { align: 'right' });
        }
    }
};

// Exportar globalmente
window.SistemaDownloads = SistemaDownloads;

// Auto-inicializar se houver configuração global
if (window.SistemaDownloadsConfig) {
    document.addEventListener('DOMContentLoaded', () => {
        SistemaDownloads.inicializar(window.SistemaDownloadsConfig);
    });
}