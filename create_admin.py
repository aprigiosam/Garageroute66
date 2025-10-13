#!/usr/bin/env python
"""
Script para criar superusuário automaticamente
Rode: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oficina.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciais padrão (MUDE DEPOIS!)
username = 'admin'
email = 'admin@garageroute66.com'
password = 'Admin@2024!Change'  # MUDE essa senha após primeiro login!

# Criar admin se não existir
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'✅ Superusuário criado com sucesso!')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print('⚠️  IMPORTANTE: Mude a senha após primeiro login!')
else:
    print('ℹ️  Superusuário já existe')
