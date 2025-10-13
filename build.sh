#!/usr/bin/env bash
# Build script para Render/Railway (Deploy Gratuito)

set -o errexit  # Exit on error

echo "🚀 Iniciando build do GarageRoute66..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório de logs
echo "📁 Criando diretórios necessários..."
mkdir -p logs

# Coletar arquivos estáticos
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Executar migrações
echo "🗄️  Executando migrações do banco de dados..."
python manage.py migrate --no-input

# Criar superusuário automaticamente
echo "👤 Criando superusuário automaticamente..."
python create_admin.py

echo "✅ Build concluído com sucesso!"
