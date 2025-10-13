# Oficina Pro 🔧

Sistema web completo para gestão de oficinas mecânicas, otimizado para uso mobile.

## 🚀 Deploy Gratuito em 10 Minutos

**Quer colocar no ar AGORA?** → [README_DEPLOY_RAPIDO.md](README_DEPLOY_RAPIDO.md)

**Precisa de mais detalhes?** → [DEPLOY_GRATIS.md](DEPLOY_GRATIS.md)

### Por que este projeto é ideal para oficinas pequenas?

- ✅ **100% Gratuito** - Deploy no Render.com (750h/mês)
- ✅ **Otimizado para Mobile** - Seu time usa direto do celular
- ✅ **PWA** - Instala como app no celular
- ✅ **Simples** - Sem complexidade desnecessária
- ✅ **Rápido** - Deploy em 10 minutos

---

## 📱 Funcionalidades

### Gestão Completa
- **Clientes** - Cadastro com CPF, telefone, endereço
- **Veículos** - Placa, marca, modelo, chassi, quilometragem
- **Ordens de Serviço** - Fluxo completo de abertura até entrega
- **Agendamentos** - Organize os serviços do dia
- **Peças** - Controle de estoque com categorias e fornecedores

### Dashboard
- Ordens abertas, em andamento e concluídas
- Faturamento do período
- Agendamentos do dia
- Gráficos visuais

### Mobile First
- Interface adaptada para celular
- Navegação bottom bar no mobile
- Formulários otimizados para toque
- PWA instalável

---

## 💻 Desenvolvimento Local

### Requisitos
- Python 3.10+
- Git

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/garageroute.git
cd garageroute

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar .env
echo "DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1
COMPANY_NAME=Minha Oficina" > .env

# 5. Configurar banco de dados
python manage.py migrate

# 6. Criar superusuário
python manage.py createsuperuser

# 7. Rodar servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

---

## 📦 Estrutura do Projeto

```
garageroute/
├── core/              # App principal
│   ├── models.py      # Modelos (Cliente, Veiculo, OS, Peca, etc)
│   ├── views.py       # Views principais
│   ├── forms.py       # Formulários
│   ├── urls.py        # URLs do app
│   └── admin.py       # Configuração do admin
├── oficina/           # Configurações do Django
│   ├── settings.py    # Settings simplificado
│   ├── urls.py        # URLs principais
│   └── wsgi.py        # WSGI para produção
├── templates/         # Templates HTML
│   ├── base.html      # Template base (PWA)
│   └── core/          # Templates do app
├── static/            # Arquivos estáticos (criado automaticamente)
├── db.sqlite3         # Banco de dados SQLite
├── manage.py          # Django management
├── requirements.txt   # Dependências
├── build.sh           # Script de build (Render)
├── Procfile           # Comando de start (Render)
└── runtime.txt        # Versão do Python
```

---

## 🛠️ Comandos Úteis

```bash
# Criar novas migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Rodar testes
python manage.py test
```

---

## 🌐 Deploy em Produção

### Opção 1: Render.com (Recomendado - Gratuito)

Siga o guia: [README_DEPLOY_RAPIDO.md](README_DEPLOY_RAPIDO.md)

**Tempo:** 10 minutos | **Custo:** R$ 0,00

### Opção 2: Railway.app

1. Conecte seu GitHub
2. Configure variáveis de ambiente
3. Deploy automático

### Opção 3: Fly.io ou Heroku

Compatível com Procfile e build.sh incluídos

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Segurança
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=seu-dominio.com,*.onrender.com

# Aplicação
COMPANY_NAME=Nome da Oficina
OS_PREFIX=OS

# Opcional
COMPANY_PHONE=(11) 99999-9999
COMPANY_EMAIL=contato@oficina.com
```

---

## 📊 Tecnologias

- **Backend:** Django 5.2
- **Banco:** SQLite (pode migrar para PostgreSQL)
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **Charts:** Chart.js
- **PWA:** Service Worker + Manifest
- **Deploy:** Whitenoise (static files) + Gunicorn

---

## 🆘 Problemas Comuns

### ImportError ao rodar projeto
```bash
# Certifique-se que o venv está ativo
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Erro de SECRET_KEY
```bash
# Gere uma nova chave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Erro de migração
```bash
# Delete o banco e recrie
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Próximos Passos (Quando Crescer)

- Migrar para PostgreSQL
- Adicionar relatórios PDF
- Implementar API REST
- Adicionar notificações por email/SMS
- Sistema de backup automático
- Cache com Redis

---

## 📝 Licença

Este projeto é de código aberto. Use, modifique e distribua livremente.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

---

## 📞 Suporte

- **Documentação Django:** https://docs.djangoproject.com
- **Render Docs:** https://render.com/docs
- **Issues:** Abra uma issue neste repositório

---

**Desenvolvido com ❤️ para oficinas que querem simplicidade e eficiência.**

**Tempo de setup:** 10 minutos | **Custo inicial:** R$ 0,00 | **Escalável:** Sim
