# Como Gerar Ícones PWA

## Opção 1: Online (Mais Fácil)

1. Acesse: https://realfavicongenerator.net/
2. Faça upload de uma logo da sua oficina (mínimo 512x512px)
3. Configure as opções PWA
4. Baixe o pacote completo
5. Extraia os ícones nesta pasta

> **Logo atual**: o arquivo `static/img/logo-garageroute66.jpg` foi adicionado como referência visual e está sendo reutilizado temporariamente em todos os tamanhos `.jpg`. Gere versões otimizadas em PNG sempre que possível para melhorar a nitidez.

## Opção 2: Temporário (Para Teste)

Use ícones placeholder até ter o logo oficial:

```bash
# Criar ícones simples com ImageMagick
convert -size 512x512 xc:#c1272d -fill white -pointsize 200 -gravity center -annotate +0+0 "GR" icon-512x512.png
convert icon-512x512.png -resize 384x384 icon-384x384.png
convert icon-512x512.png -resize 192x192 icon-192x192.png
convert icon-512x512.png -resize 152x152 icon-152x152.png
convert icon-512x512.png -resize 144x144 icon-144x144.png
convert icon-512x512.png -resize 128x128 icon-128x128.png
convert icon-512x512.png -resize 96x96 icon-96x96.png
convert icon-512x512.png -resize 72x72 icon-72x72.png
```

## Opção 3: Usar Logo Existente

Se você já tem um logo:

```bash
# Com ImageMagick instalado
convert seu-logo.png -resize 512x512 -background none -gravity center -extent 512x512 icon-512x512.png
# Repita para os outros tamanhos
```

## Tamanhos Necessários

- 72x72
- 96x96
- 128x128
- 144x144
- 152x152
- 192x192
- 384x384
- 512x512

## Nota

Enquanto os ícones oficiais não são gerados, o PWA usará as cópias `.jpg` do logo em todos os tamanhos. Substitua-os por PNG dimensionados corretamente assim que tiver as versões definitivas.
