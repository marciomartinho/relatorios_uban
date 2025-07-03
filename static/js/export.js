// Função genérica para exportar uma tabela para PDF usando jsPDF-AutoTable
function exportarTabelaParaPDF(titulo, dadosPDF, dadosTiposDeLinha) {
    alert('Gerando PDF de alta qualidade...');
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'pt', 'a4'); // Força retrato para padronizar

    // Adiciona o título
    doc.setFontSize(16);
    doc.text(titulo, doc.internal.pageSize.getWidth() / 2, 40, { align: 'center' });

    // Gera a tabela
    doc.autoTable({
        head: dadosPDF.head,
        body: dadosPDF.body,
        startY: 60,
        theme: 'grid',
        headStyles: {
            fillColor: [0, 51, 102], // Azul escuro
            textColor: [255, 255, 255],
            halign: 'center'
        },
        styles: {
            fontSize: 8,
            cellPadding: 4,
        },
        // Estilização condicional das linhas
        willDrawCell: function (data) {
            // Se dadosTiposDeLinha for fornecido, usa para colorir
            if (dadosTiposDeLinha && dadosTiposDeLinha[data.row.index]) {
                const tipo = dadosTiposDeLinha[data.row.index].tipo;
                if (tipo === 'principal' || tipo === 'total') {
                    doc.setFillColor(204, 229, 255); // Azul claro
                    doc.setFont(undefined, 'bold');
                }
            }
        },
        // Alinhamento das colunas
        didParseCell: function(data) {
            if (data.row.section === 'body' && data.column.index > 0) {
                data.cell.styles.halign = 'right';
            }
        }
    });

    doc.save(`${titulo}.pdf`);
}

// Função genérica para "fotografar" um elemento HTML e baixar como JPG
function exportarElementoParaJPG(idElemento, nomeArquivo) {
    alert(`Gerando imagem JPG de '${nomeArquivo}'...`);
    const elemento = document.getElementById(idElemento);

    html2canvas(elemento, { scale: 2 }).then(canvas => {
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/jpeg', 0.9);
        link.download = `${nomeArquivo}.jpg`;
        link.click();
    });
}