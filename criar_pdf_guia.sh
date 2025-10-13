#!/bin/bash
# Script para criar PDF dos guias
# Requer: pandoc e wkhtmltopdf instalados

echo "🔄 Criando PDFs dos guias..."

# Criar diretório de saída
mkdir -p documentacao_pdf

# Converter Guia de Uso
if command -v pandoc &> /dev/null; then
    echo "📄 Convertendo Guia de Uso..."
    pandoc GUIA_DE_USO.md \
        -o documentacao_pdf/GarageRoute66_Guia_de_Uso.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=2cm \
        -V fontsize=11pt \
        --toc \
        --metadata title="GarageRoute66 - Guia de Uso" \
        --metadata author="Sistema de Gestão" \
        --metadata date="2025"

    echo "📊 Convertendo Fluxogramas..."
    pandoc FLUXOGRAMA_VISUAL.md \
        -o documentacao_pdf/GarageRoute66_Fluxogramas.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=2cm \
        -V fontsize=10pt \
        -V monofont="Courier New" \
        --metadata title="GarageRoute66 - Fluxogramas" \
        --metadata author="Sistema de Gestão" \
        --metadata date="2025"

    echo "✅ PDFs criados em: documentacao_pdf/"
    echo "📁 Arquivos:"
    ls -lh documentacao_pdf/
else
    echo "❌ Pandoc não instalado."
    echo "📝 Para instalar:"
    echo "   Ubuntu/Debian: sudo apt install pandoc texlive-xetex"
    echo "   Mac: brew install pandoc basictex"
    echo "   Windows: https://pandoc.org/installing.html"
fi
