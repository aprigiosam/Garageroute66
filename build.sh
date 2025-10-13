#!/usr/bin/env bash
# Build script MINIMALISTA para Render/Railway (Deploy Gratuito)

set -o errexit  # Exit on error

echo "🚀 Iniciando build MINIMALISTA do Oficina Pro..."

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

# Criar superusuário (se variáveis de ambiente estiverem definidas)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Criando superusuário..."
    python manage.py createsuperuser --no-input || echo "Superusuário já existe ou erro ao criar"
fi

echo "✅ Build concluído com sucesso!"
