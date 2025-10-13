# 🚀 Deploy Gratuito - Oficina Pro

## Deploy em 10 MINUTOS no Render.com (100% GRÁTIS)

### Por que Render.com?
- ✅ **100% GRATUITO** (750 horas/mês - suficiente para uso contínuo)
- ✅ **SSL automático** (HTTPS)
- ✅ **Deploy automático do GitHub**
- ✅ **Banco SQLite incluído** (até 100GB)
- ✅ **Ótimo para mobile** (seu colega vai usar no celular)

---

## PASSO A PASSO

### 1️⃣ Preparar o Projeto (FAZER UMA VEZ)

```bash
# 1. Garantir que está usando os arquivos minimalistas
cp requirements-minimal.txt requirements.txt

# 2. Criar arquivo .env.production (copie o exemplo abaixo)
nano .env.production
```

**Conteúdo do `.env.production`:**
```bash
DEBUG=False
SECRET_KEY=cole-aqui-uma-chave-secreta-gerada
ALLOWED_HOSTS=seu-app.onrender.com,*.onrender.com
COMPANY_NAME=Oficina do João
```

**Gerar SECRET_KEY segura:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2️⃣ Criar build.sh (script de deploy)

Já está criado! Arquivo: `build.sh`

### 3️⃣ Commit e Push para GitHub

```bash
git add .
git commit -m "Configuração para deploy gratuito no Render"
git push origin main
```

---

## 4️⃣ Configurar no Render.com

### A. Criar conta
1. Acesse: https://render.com
2. Clique em "Get Started for Free"
3. Faça login com GitHub (mais fácil)

### B. Criar Web Service
1. No dashboard, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. Configure:

**Configurações Básicas:**
- **Name:** `oficina-pro` (ou qualquer nome)
- **Region:** `Oregon (US West)` (mais rápido)
- **Branch:** `main`
- **Root Directory:** deixe vazio
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  chmod +x build.sh && ./build.sh
  ```
- **Start Command:**
  ```bash
  gunicorn oficina.wsgi:application
  ```

**Instance Type:**
- Selecione: **"Free"** (grátis!)

### C. Variáveis de Ambiente
Clique em **"Advanced"** → **"Add Environment Variable"**

Adicione CADA UMA destas variáveis:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.0` |
| `DEBUG` | `False` |
| `SECRET_KEY` | _(cole a chave gerada)_ |
| `ALLOWED_HOSTS` | `*.onrender.com` |
| `DJANGO_SETTINGS_MODULE` | `oficina.settings_minimal` |
| `COMPANY_NAME` | `Oficina do João` |

### D. Deploy
1. Clique em **"Create Web Service"**
2. Aguarde 5-10 minutos (primeiro deploy demora)
3. Render vai:
   - Instalar dependências
   - Rodar migrações
   - Coletar arquivos estáticos
   - Subir o servidor

---

## 5️⃣ Criar Superusuário

Depois que o deploy terminar:

1. No dashboard do Render, vá em **"Shell"** (aba superior)
2. Execute:
```bash
python manage.py createsuperuser
```

3. Preencha:
   - **Username:** admin
   - **Email:** seu@email.com
   - **Password:** (escolha uma senha forte)

---

## 6️⃣ Acessar o Sistema

1. URL do app: `https://seu-app.onrender.com`
2. Login admin: `https://seu-app.onrender.com/admin`
3. Use as credenciais criadas acima

---

## 📱 Instalar como PWA no Celular do Seu Colega

### Android (Chrome):
1. Abra a URL no Chrome
2. Menu (3 pontos) → **"Adicionar à tela inicial"**
3. Aceitar
4. Ícone aparece na tela como app!

### iOS (Safari):
1. Abra a URL no Safari
2. Botão compartilhar → **"Adicionar à Tela Inicial"**
3. Aceitar
4. Ícone aparece como app!

---

## ⚠️ IMPORTANTE - LIMITAÇÕES DO PLANO GRATUITO

### Render Free Tier:
- ✅ **750 horas/mês** (suficiente para uso 24/7)
- ⚠️ **Hiberna após 15 min sem uso** (primeiro acesso demora ~30s)
- ✅ **100GB de espaço** (SQLite)
- ✅ **SSL/HTTPS automático**
- ⚠️ **Não tem backup automático** (faça backup manual do db.sqlite3)

### Como evitar hibernação:
Use um serviço de ping gratuito:
- https://uptimerobot.com (pinga a cada 5 minutos)
- Configure para pingar: `https://seu-app.onrender.com`

---

## 🔄 Fazer Backup do Banco de Dados

```bash
# No Shell do Render:
python manage.py dumpdata > backup.json

# Baixar o arquivo:
# 1. Vá em "Shell" do Render
# 2. Execute: cat backup.json
# 3. Copie e cole em um arquivo local
```

---

## 🚀 Próximos Passos (Quando Crescer)

Quando a oficina crescer e precisar de mais performance:

1. **Migrar para PostgreSQL gratuito:**
   - Railway.app (500MB grátis)
   - Supabase (500MB grátis)
   - Render PostgreSQL (90 dias grátis)

2. **Adicionar features:**
   - Relatórios PDF
   - Cache com Redis
   - API REST

3. **Upgrade para plano pago:**
   - Render: $7/mês (sem hibernação)
   - Railway: $5/mês

---

## 🆘 Problemas Comuns

### Deploy falhou?
1. Verifique os logs no Render: **"Logs"** (aba superior)
2. Erros comuns:
   - `SECRET_KEY not set` → Adicione variável de ambiente
   - `ALLOWED_HOSTS` → Adicione `*.onrender.com`
   - `Module not found` → Verifique requirements.txt

### App lento?
- Normal no primeiro acesso (hibernação)
- Configure UptimeRobot para manter ativo

### Não consigo fazer login?
```bash
# Reset senha do admin:
python manage.py changepassword admin
```

---

## 💡 Dicas Extras

1. **Domínio customizado (grátis):**
   - Configure em Render: Settings → Custom Domain
   - Use Freenom.com para domínio grátis (.tk, .ml, .ga)

2. **Monitoramento:**
   - Use Sentry.io (grátis até 5k eventos/mês)
   - Configure Google Analytics

3. **Performance Mobile:**
   - Sistema já está otimizado para celular
   - PWA permite uso offline parcial

---

## 🎯 RESUMO RÁPIDO

```bash
# 1. Preparar
cp requirements-minimal.txt requirements.txt
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Commit
git add .
git commit -m "Deploy config"
git push

# 3. Render.com
# - Criar conta
# - New Web Service
# - Conectar GitHub
# - Configurar variáveis
# - Deploy!

# 4. Criar admin
# No Shell do Render:
python manage.py createsuperuser

# PRONTO! 🎉
```

---

## 📞 Suporte

- **Documentação Render:** https://render.com/docs
- **Comunidade Django:** https://forum.djangoproject.com
- **Issues GitHub:** Abra issue no seu repositório

---

**Tempo total:** 10-15 minutos
**Custo:** R$ 0,00
**Escalabilidade:** Suporta centenas de OS/mês facilmente

Bom deploy! 🚀
