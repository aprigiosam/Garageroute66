# Deploy no Render.com - GarageRoute66

## Problema Resolvido: Reset de Credenciais

O Render.com free tier **hiberna** seu app após inatividade e **APAGA** o banco SQLite.
Solução: Migrar para PostgreSQL (persistente e gratuito).

---

## 🚀 Passo a Passo Completo

### 1. Criar PostgreSQL no Render

1. Acesse https://dashboard.render.com/
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `garageroute66-db`
   - **Database**: `garageroute66`
   - **User**: (deixe o padrão)
   - **Region**: `Oregon (US West)` ou mais próximo
   - **Plan**: **FREE** (100 MB, 90 dias - depois renova grátis)
4. Clique em **"Create Database"**
5. Aguarde a criação (1-2 minutos)

### 2. Copiar DATABASE_URL

Após criar o banco:
1. Clique no banco criado
2. Na aba **"Info"**, copie a **"Internal Database URL"**
   - Exemplo: `postgresql://user:pass@host/dbname`

### 3. Configurar Web Service

1. Vá em seu Web Service no Render
2. Clique em **"Environment"**
3. Adicione estas variáveis:

```bash
# Database (OBRIGATÓRIO)
DATABASE_URL=postgresql://user:pass@host/dbname
# Cole a URL copiada acima ☝️

# Credenciais Admin (DEFINA SUAS PRÓPRIAS!)
DJANGO_SUPERUSER_USERNAME=seu_usuario_aqui
DJANGO_SUPERUSER_PASSWORD=SuaSenhaSegura123!
DJANGO_SUPERUSER_EMAIL=seu@email.com

# Outras configurações existentes (mantenha)
SECRET_KEY=sua-secret-key-super-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=*.onrender.com
```

### 4. Fazer Deploy

Após configurar as variáveis:
1. Clique em **"Manual Deploy"** → **"Deploy latest commit"**
2. Aguarde o build (3-5 minutos)
3. O sistema irá:
   - ✅ Instalar dependências (incluindo PostgreSQL)
   - ✅ Criar tabelas no PostgreSQL
   - ✅ Criar superusuário com SUAS credenciais
   - ✅ Coletar arquivos estáticos

### 5. Acessar o Sistema

1. Acesse: `https://seu-app.onrender.com/admin/`
2. Login com:
   - **Usuário**: O que você definiu em `DJANGO_SUPERUSER_USERNAME`
   - **Senha**: O que você definiu em `DJANGO_SUPERUSER_PASSWORD`

---

## ✅ Vantagens do PostgreSQL

- ✅ **Persistente**: Dados não são perdidos quando o app hiberna
- ✅ **Gratuito**: 100 MB no Render (suficiente para começar)
- ✅ **Credenciais seguras**: Definidas por você via variáveis de ambiente
- ✅ **Escalável**: Fácil upgrade para plano pago depois
- ✅ **Backups**: Render faz backup automático

---

## 🔄 Como Mudar a Senha Admin

Se quiser mudar a senha depois:

1. Vá em **Environment** no Render
2. Edite `DJANGO_SUPERUSER_PASSWORD`
3. Faça **Manual Deploy**
4. O script `create_admin.py` atualizará a senha automaticamente

---

## 🆘 Troubleshooting

### Erro: "relation does not exist"
- Solução: O banco não foi migrado. Rode no deploy:
  ```bash
  python manage.py migrate
  ```

### App retorna 502/503
- Espere 30-60 segundos (cold start)
- Verifique logs: **"Logs"** no Render

### Não consigo fazer login
- Verifique se definiu `DJANGO_SUPERUSER_USERNAME` e `DJANGO_SUPERUSER_PASSWORD`
- Verifique logs do último deploy

---

## 📊 Monitoramento

- **Uso do banco**: Veja em PostgreSQL → "Metrics"
- **Logs da aplicação**: Web Service → "Logs"
- **Status**: Web Service → "Events"

---

## 🔐 Segurança

- ✅ Use senha forte (mínimo 12 caracteres, letras, números, símbolos)
- ✅ Não compartilhe suas credenciais
- ✅ Mude a senha padrão imediatamente
- ✅ Mantenha `DEBUG=False` em produção
- ✅ Use `ALLOWED_HOSTS` correto

---

## 💡 Dicas

1. **Hibernação**: App hiberna após 15 min de inatividade (plano free)
   - Primeira requisição pode demorar 30-60s (cold start)

2. **Renovação do banco**: PostgreSQL free expira em 90 dias
   - Render avisa por email antes
   - Basta criar novo banco e migrar dados

3. **Upgrade**: Se precisar de mais recursos
   - PostgreSQL: $7/mês (256 MB + backups)
   - Web Service: $7/mês (sem hibernação)

---

## 🎯 Próximos Passos

Após deploy bem-sucedido:

1. ✅ Faça login no admin
2. ✅ Mude a senha (se usou padrão)
3. ✅ Configure dados da empresa
4. ✅ Comece a usar o sistema

---

**Dúvidas?** Verifique os logs no Render: Dashboard → Seu App → Logs
