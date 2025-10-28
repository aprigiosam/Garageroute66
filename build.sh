#!/usr/bin/env bash
# Build script para Render/Railway (Deploy Gratuito)

set -o errexit  # Exit on error

echo "🚀 Iniciando build do GarageRoute66..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios úteis
echo "📁 Criando diretórios necessários..."
mkdir -p logs

# Coletar arquivos estáticos
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Executar migrações
echo "🗄️  Executando migrações do banco de dados..."
python manage.py migrate --no-input

# Aviso sobre criação do superusuário
cat <<'EOF'
ℹ️  Build finalizado. Lembre-se de executar "python create_admin.py"
    manualmente (ou via job pós-deploy) com as variáveis de ambiente
    DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD
    definidas no Render.
EOF

echo "✅ Build concluído com sucesso!"
