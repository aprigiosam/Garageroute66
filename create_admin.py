#!/usr/bin/env python
"""
Script para criar superusuário automaticamente
Usa variáveis de ambiente para credenciais persistentes
Rode: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oficina.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciais via variáveis de ambiente (define no Render)
missing = []
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

for var, value in (
    ('DJANGO_SUPERUSER_USERNAME', username),
    ('DJANGO_SUPERUSER_EMAIL', email),
    ('DJANGO_SUPERUSER_PASSWORD', password),
):
    if not value:
        missing.append(var)

if missing:
    vars_str = ", ".join(missing)
    raise SystemExit(
        f'❌ Variáveis ausentes: {vars_str}. '
        'Defina-as antes de executar create_admin.py.'
    )

# Verificar se admin já existe
if User.objects.filter(username=username).exists():
    print('ℹ️  Superusuário já existe')
    # Atualizar senha se mudou (útil quando você muda a senha no Render)
    admin = User.objects.get(username=username)
    admin.set_password(password)
    admin.email = email
    admin.save()
    print('✅ Credenciais do superusuário atualizadas!')
else:
    # Criar novo superusuário
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'✅ Superusuário criado com sucesso!')
    print(f'Username: {username}')
    print(f'Email: {email}')

# Exibir instruções
print('')
print('📝 IMPORTANTE:')
print('   Configure estas variáveis de ambiente no Render:')
print('   - DJANGO_SUPERUSER_USERNAME (seu nome de usuário)')
print('   - DJANGO_SUPERUSER_PASSWORD (sua senha segura)')
print('   - DJANGO_SUPERUSER_EMAIL (seu email)')
print('')
