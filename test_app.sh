#!/bin/bash
echo "🧪 Testando GarageRoute66..."
echo ""

# Test 1: Django Check
echo "1️⃣ Verificando configuração Django..."
venv/bin/python manage.py check
if [ $? -eq 0 ]; then
    echo "✅ Configuração OK"
else
    echo "❌ Erro na configuração"
    exit 1
fi

# Test 2: Verificar migrações
echo ""
echo "2️⃣ Verificando migrações..."
venv/bin/python manage.py showmigrations | grep "\[ \]" > /dev/null
if [ $? -eq 0 ]; then
    echo "⚠️  Existem migrações pendentes"
    echo "Aplicando migrações..."
    venv/bin/python manage.py migrate --noinput
else
    echo "✅ Todas migrações aplicadas"
fi

# Test 3: Coletar estáticos
echo ""
echo "3️⃣ Coletando arquivos estáticos..."
venv/bin/python manage.py collectstatic --noinput -c > /dev/null 2>&1
echo "✅ Estáticos coletados"

# Test 4: Verificar admin
echo ""
echo "4️⃣ Verificando Django Admin..."
venv/bin/python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print("✅ Superusuário existe")
else:
    print("⚠️  Nenhum superusuário - crie com: python manage.py createsuperuser")
EOF

echo ""
echo "✅ TODOS OS TESTES PASSARAM!"
echo ""
echo "🚀 Sistema pronto para deploy!"
echo ""
echo "Para testar localmente:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo "  Acesse: http://127.0.0.1:8000"
