# GarageRoute66 🔧

Sistema web completo para gestão de oficinas mecânicas, otimizado para uso mobile.

[![Deploy](https://img.shields.io/badge/deploy-render-46E3B7)](https://render.com)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 🎯 Funcionalidades

- **Gestão de Clientes** - Cadastro completo com CPF, telefone e histórico
- **Controle de Veículos** - Placa, marca, modelo, chassi e quilometragem
- **Ordens de Serviço** - Fluxo completo de abertura até entrega
- **Estoque de Peças** - Controle com categorias, fornecedores e movimentações
- **Agendamentos** - Organize os serviços programados
- **Dashboard** - Visão geral com métricas e gráficos
- **PWA** - Instalável como app no celular

## 🚀 Deploy Rápido

### Render.com (Gratuito)

1. **Fork** este repositório
2. Acesse [Render.com](https://render.com) e conecte seu GitHub
3. **New Web Service** → Selecione seu fork
4. Configure:
   - Build: `chmod +x build.sh && ./build.sh`
   - Start: `gunicorn oficina.wsgi:application`
   - Instance: **Free**
5. Adicione variáveis de ambiente:
   ```
   PYTHON_VERSION=3.12.0
   DEBUG=False
   SECRET_KEY=<gere-uma-chave-secreta>
   ALLOWED_HOSTS=*.onrender.com
   COMPANY_NAME=Sua Oficina
   ```
6. Deploy! ⏱️ ~10 minutos

**Gerar SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Criar admin (no Shell do Render):**
```bash
python manage.py createsuperuser
```

## 💻 Desenvolvimento Local

### Requisitos
- Python 3.10+
- Git

### Instalação

```bash
# Clonar
git clone https://github.com/aprigiosam/Garageroute66.git
cd Garageroute66

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependências
pip install -r requirements.txt

# Configurar .env
cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1
COMPANY_NAME=Minha Oficina
EOF

# Banco de dados
python manage.py migrate

# Admin
python manage.py createsuperuser

# Rodar
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 📦 Stack Tecnológica

- **Backend:** Django 5.2
- **Database:** SQLite (migre para PostgreSQL em produção)
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **Charts:** Chart.js
- **PWA:** Service Worker + Manifest
- **Server:** Gunicorn + Whitenoise

## 📱 PWA - Instalação no Celular

**Android (Chrome):**
Menu → "Adicionar à tela inicial"

**iOS (Safari):**
Compartilhar → "Adicionar à Tela Inicial"

## 🏗️ Estrutura do Projeto

```
garageroute/
├── core/              # App principal
│   ├── models.py      # Cliente, Veiculo, OS, Peca
│   ├── views.py       # Views principais
│   ├── forms.py       # Formulários
│   └── admin.py       # Admin personalizado
├── oficina/           # Settings Django
├── templates/         # Templates HTML
├── static/            # CSS, JS, ícones
├── requirements.txt   # Dependências
├── build.sh           # Script de build
└── manage.py          # CLI Django
```

## 🛠️ Comandos Úteis

```bash
# Migrações
python manage.py makemigrations
python manage.py migrate

# Admin
python manage.py createsuperuser

# Testes
python manage.py test

# Collectstatic (produção)
python manage.py collectstatic
```

## 🔧 Configuração

### Variáveis de Ambiente

```env
DEBUG=False
SECRET_KEY=sua-chave-secreta
ALLOWED_HOSTS=seudominio.com,*.onrender.com
COMPANY_NAME=Nome da Oficina
OS_PREFIX=OS
```

## 📊 Roadmap

- [x] Sistema de OS completo
- [x] Controle de estoque
- [x] PWA mobile-first
- [x] Dashboard com gráficos
- [ ] Relatórios em PDF
- [ ] API REST
- [ ] Notificações por email/SMS
- [ ] Backup automático

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

Samuel Aprigio - [@aprigiosam](https://github.com/aprigiosam)

## 🙏 Agradecimentos

- Django Framework
- Bootstrap
- Comunidade open source

---

**GarageRoute66** - Gestão de oficinas simplificada e eficiente 🚗💨
