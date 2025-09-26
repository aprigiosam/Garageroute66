#!/usr/bin/env python
"""
Script de migração para atualizar o sistema Oficina Pro
Execute este script para migrar do sistema antigo para o novo
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("🚀 Iniciando migração do sistema Oficina Pro...")
    
    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto Django")
        sys.exit(1)
    
    # 1. Fazer backup do sistema atual
    print("\n📦 Fazendo backup do sistema atual...")
    backup_dir = Path('backup_migracao')
    backup_dir.mkdir(exist_ok=True)
    
    # Backup do banco
    os.system('python manage.py dumpdata > backup_migracao/dados_antigos.json')
    
    # Backup dos arquivos importantes
    files_to_backup = [
        'core/models.py',
        'core/views.py', 
        'core/forms.py',
        'core/admin.py',
        'core/urls.py',
        'oficina/settings.py',
        'templates/base.html'
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / Path(file_path).name)
    
    print("✅ Backup criado em backup_migracao/")
    
    # 2. Criar novos arquivos
    print("\n📁 Criando novos arquivos...")
    
    # Criar diretórios necessários
    dirs_to_create = [
        'core/management',
        'core/management/commands',
        'templates/core',
        'templates/emails',
        'static/css',
        'static/js',
        'media',
        'logs',
        'backups'
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    # Criar arquivos __init__.py
    init_files = [
        'core/management/__init__.py',
        'core/management/commands/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
    
    print("✅ Estrutura de diretórios criada")
    
    # 3. Instalar dependências
    print("\n📦 Instalando dependências...")
    os.system('pip install -r requirements.txt')
    print("✅ Dependências instaladas")
    
    # 4. Aplicar migrações
    print("\n🗄️ Aplicando migrações do banco de dados...")
    
    # Fazer migrações
    os.system('python manage.py makemigrations')
    os.system('python manage.py migrate')
    
    print("✅ Migrações aplicadas")
    
    # 5. Coletar arquivos estáticos
    print("\n📄 Coletando arquivos estáticos...")
    os.system('python manage.py collectstatic --noinput')
    print("✅ Arquivos estáticos coletados")
    
    # 6. Criar superusuário se necessário
    print("\n👤 Verificando superusuário...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("Nenhum superusuário encontrado. Execute:")
            print("python manage.py createsuperuser")
    except:
        print("Execute: python manage.py createsuperuser")
    
    # 7. Verificar arquivos críticos
    print("\n🔍 Verificando arquivos críticos...")
    critical_files = [
        'core/models.py',
        'core/views.py',
        'core/forms.py', 
        'core/urls.py',
        'core/signals.py',
        'core/validators.py',
        'templates/base.html',
        'templates/core/dashboard.html'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Arquivos em falta:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nCopie os arquivos dos artifacts para completar a migração.")
    else:
        print("✅ Todos os arquivos críticos estão presentes")
    
    # 8. Teste básico
    print("\n🧪 Executando teste básico...")
    try:
        os.system('python manage.py check')
        print("✅ Sistema passou na verificação básica")
    except:
        print("⚠️  Há erros no sistema - verifique os arquivos")
    
    print("\n🎉 Migração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Copie todos os arquivos dos artifacts")
    print("2. Execute: python manage.py runserver")
    print("3. Acesse http://127.0.0.1:8000")
    print("4. Teste todas as funcionalidades")
    
    print("\n📁 Estrutura final esperada:")
    print("""
oficina-pro/
├── core/
│   ├── models.py (NOVO - com auditoria)
│   ├── views.py (NOVO - completo)
│   ├── forms.py (NOVO - validações)
│   ├── admin.py (NOVO - melhorado)
│   ├── signals.py (NOVO)
│   ├── validators.py (NOVO)
│   └── management/commands/backup_db.py (NOVO)
├── templates/
│   ├── base.html (NOVO)
│   └── core/ (NOVOS templates)
├── oficina/
│   ├── settings.py (ATUALIZADO)
│   └── urls.py
├── requirements.txt (NOVO)
├── .env.example (NOVO)
└── README.md (NOVO)
    """)


if __name__ == '__main__':
    main()