#!/bin/bash
# Script para testar o sistema localmente antes do deploy

echo "🧪 Testando GarageRoute66 localmente..."
echo ""

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment não encontrado"
    echo "📦 Criando virtual environment..."
    python3 -m venv venv
fi

# Ativar venv
echo "🔄 Ativando virtual environment..."
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Verificar Django
echo ""
echo "✅ Verificando configuração Django..."
python manage.py check

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Criando arquivo .env..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1
COMPANY_NAME=GarageRoute66
EOF
    echo "✅ Arquivo .env criado"
fi

# Migrações
echo ""
echo "🗄️  Aplicando migrações..."
python manage.py migrate --noinput

# Verificar se há superusuário
echo ""
echo "👤 Verificando superusuário..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('✅ Superusuário existe' if User.objects.filter(is_superuser=True).exists() else '❌ Nenhum superusuário encontrado')"

# Coletar estáticos
echo ""
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput -c

echo ""
echo "✅ Sistema pronto para rodar!"
echo ""
echo "📋 Para testar:"
echo "   1. python manage.py createsuperuser (se necessário)"
echo "   2. python manage.py runserver"
echo "   3. Acesse: http://127.0.0.1:8000"
echo ""
echo "🔐 Admin: http://127.0.0.1:8000/admin"
echo ""
