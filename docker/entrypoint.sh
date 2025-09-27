#!/bin/bash
set -e

# Script de inicialização do GarageRoute66

echo "🚀 Iniciando GarageRoute66..."

# Aguardar banco de dados estar disponível
echo "⏳ Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Banco de dados conectado!"

# Aguardar Redis estar disponível
echo "⏳ Aguardando Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis conectado!"

# Aplicar migrações
echo "📊 Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@garageroute66.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superusuário '{username}' criado!")
else:
    print(f"ℹ️ Superusuário '{username}' já existe")
EOF

# Verificar saúde da aplicação
echo "🔍 Verificando configurações..."
python manage.py check --deploy

echo "🎉 GarageRoute66 pronto para uso!"

# Executar comando passado como argumento
exec "$@"