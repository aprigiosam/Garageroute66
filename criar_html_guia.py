#!/usr/bin/env python3
"""
Script para converter guias Markdown para HTML formatado
Uso: python criar_html_guia.py
"""
import markdown
import os

# CSS profissional
CSS = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background: #f5f5f5;
    }
    .container {
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 {
        color: #0066cc;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 10px;
    }
    h2 {
        color: #004d99;
        margin-top: 30px;
        border-left: 4px solid #0066cc;
        padding-left: 15px;
    }
    h3 {
        color: #0066cc;
        margin-top: 20px;
    }
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    pre {
        background: #2d2d2d;
        color: #f8f8f8;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
    }
    pre code {
        background: transparent;
        color: #f8f8f8;
        padding: 0;
    }
    ul, ol {
        margin-left: 20px;
    }
    li {
        margin: 8px 0;
    }
    .emoji {
        font-size: 1.2em;
    }
    blockquote {
        border-left: 4px solid #0066cc;
        padding-left: 20px;
        margin-left: 0;
        color: #666;
        font-style: italic;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #0066cc;
        color: white;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .print-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #0066cc;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .print-btn:hover {
        background: #004d99;
    }
    @media print {
        body {
            background: white;
        }
        .container {
            box-shadow: none;
        }
        .print-btn {
            display: none;
        }
    }
    .checklist {
        background: #f0f8ff;
        border: 1px solid #0066cc;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .warning {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .success {
        background: #d4edda;
        border: 1px solid #28a745;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
"""

def converter_arquivo(arquivo_md, arquivo_html, titulo):
    """Converte um arquivo Markdown para HTML formatado"""

    print(f"📄 Convertendo {arquivo_md}...")

    # Ler conteúdo Markdown
    with open(arquivo_md, 'r', encoding='utf-8') as f:
        conteudo_md = f.read()

    # Converter para HTML
    html_content = markdown.markdown(
        conteudo_md,
        extensions=['fenced_code', 'tables', 'nl2br']
    )

    # Template HTML completo
    html_completo = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    {CSS}
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ Imprimir PDF</button>
    <div class="container">
        {html_content}
        <hr style="margin-top: 50px; border: none; border-top: 2px solid #ddd;">
        <p style="text-align: center; color: #999; font-size: 0.9em;">
            <strong>GarageRoute66</strong> - Sistema de Gestão para Oficinas Mecânicas<br>
            Versão 2.0.0 - 2025
        </p>
    </div>
    <script>
        // Melhorar aparência de checkboxes
        document.querySelectorAll('li').forEach(li => {{
            if (li.textContent.trim().startsWith('[ ]') || li.textContent.trim().startsWith('[x]')) {{
                li.style.listStyle = 'none';
                li.style.marginLeft = '-20px';
            }}
        }});
    </script>
</body>
</html>
    """

    # Salvar HTML
    with open(arquivo_html, 'w', encoding='utf-8') as f:
        f.write(html_completo)

    print(f"✅ Criado: {arquivo_html}")

def main():
    print("🚀 Iniciando conversão dos guias...")
    print()

    # Criar diretório de saída
    os.makedirs('documentacao_html', exist_ok=True)

    # Converter os arquivos
    arquivos = [
        ('GUIA_DE_USO.md', 'documentacao_html/Guia_de_Uso.html', 'GarageRoute66 - Guia de Uso'),
        ('FLUXOGRAMA_VISUAL.md', 'documentacao_html/Fluxogramas.html', 'GarageRoute66 - Fluxogramas'),
    ]

    for md, html, titulo in arquivos:
        if os.path.exists(md):
            converter_arquivo(md, html, titulo)
        else:
            print(f"⚠️  Arquivo não encontrado: {md}")

    print()
    print("=" * 60)
    print("✅ CONVERSÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("📁 Arquivos criados em: documentacao_html/")
    print()
    print("📖 Como usar:")
    print("   1. Abra os arquivos .html no navegador")
    print("   2. Clique em 'Imprimir PDF' para salvar como PDF")
    print("   3. Ou compartilhe os arquivos HTML direto")
    print()
    print("📤 Como enviar:")
    print("   • WhatsApp: Envie os arquivos HTML")
    print("   • Email: Anexe os arquivos HTML")
    print("   • Impressão: Abra e imprima direto")
    print()

if __name__ == '__main__':
    main()
