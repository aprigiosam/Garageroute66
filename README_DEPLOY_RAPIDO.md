# 🚀 DEPLOY RÁPIDO - 3 COMANDOS

## Você quer colocar no ar AGORA? Siga isto:

### 1️⃣ Preparar (LOCAL)

```bash
# Gerar SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copie a chave gerada! Vai usar daqui a pouco
```

### 2️⃣ Commit (LOCAL)

```bash
git add .
git commit -m "Config deploy minimalista"
git push origin main
```

### 3️⃣ Deploy (RENDER.COM)

1. **Criar conta:** https://render.com
2. **New Web Service** → Conectar GitHub
3. **Configurar:**

```
Build Command: chmod +x build.sh && ./build.sh
Start Command: gunicorn oficina.wsgi:application
```

4. **Environment Variables (adicione TODAS):**

```
PYTHON_VERSION=3.12.0
DEBUG=False
SECRET_KEY=COLE-A-CHAVE-GERADA-NO-PASSO-1
ALLOWED_HOSTS=*.onrender.com
DJANGO_SETTINGS_MODULE=oficina.settings_minimal
COMPANY_NAME=Nome da Oficina
```

5. **Create Web Service** → Aguarde 5-10 min

### 4️⃣ Criar Admin (SHELL DO RENDER)

No Render, vá em "Shell" e execute:

```bash
python manage.py createsuperuser
```

---

## ✅ PRONTO!

- **URL:** https://seu-app.onrender.com
- **Admin:** https://seu-app.onrender.com/admin

---

## 📱 Instalar no Celular

**Android:** Chrome → Menu → "Adicionar à tela inicial"
**iOS:** Safari → Compartilhar → "Adicionar à tela inicial"

---

## 📚 Quer mais detalhes?

Leia: `DEPLOY_GRATIS.md`

---

**Tempo:** 10 minutos | **Custo:** R$ 0,00
