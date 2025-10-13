# 🔒 SEGURANÇA DOS DADOS - GarageRoute66

## ⚠️ IMPORTANTE: LEIA ANTES DE POPULAR COM DADOS REAIS

---

## 📊 O QUE ACONTECE QUANDO O RENDER HIBERNA?

### **Plano Free do Render:**
- App **hiberna após 15 minutos** sem requisições
- Primeira visita após hibernação demora **30-60 segundos** (cold start)
- Isso é **normal e esperado** no plano gratuito

---

## 🔴 VERSÃO 1.0 (SQLite) - NÃO USE MAIS!

```
┌─────────────────────────────────┐
│   App Render (com SQLite)      │
│                                 │
│   ┌──────────────┐              │
│   │  db.sqlite3  │◄─── Aqui    │
│   └──────────────┘              │
│                                 │
│   Sistema de arquivos EFÊMERO  │
└─────────────────────────────────┘
         │
         ▼
    HIBERNAÇÃO
         │
         ▼
    🔴 TUDO APAGADO!
    (Container é destruído)
```

**Problema:**
- SQLite fica **dentro do container**
- Container é **efêmero** (temporário)
- Quando hiberna → **Container destruído** → **Dados perdidos**

---

## ✅ VERSÃO 2.0 (PostgreSQL) - USE ESTA!

```
┌───────────────────┐        ┌──────────────────────┐
│   App Render      │        │  PostgreSQL Database │
│                   │        │                      │
│   Django App      │◄──────►│  ┌────────────────┐ │
│                   │ Conecta│  │  Dados Salvos  │ │
│                   │        │  │  (Persistente) │ │
│                   │        │  └────────────────┘ │
└───────────────────┘        └──────────────────────┘
         │                             │
         ▼                             │
    HIBERNAÇÃO                         │
         │                             │
         ▼                             ▼
    App PARADO                   ✅ DADOS INTACTOS!
         │                             │
         ▼                             │
    PRIMEIRA VISITA                    │
         │                             │
         ▼                             │
    App ACORDA ──────── Reconecta ────►│
         │                             │
         ▼                             ▼
    ✅ DADOS CARREGADOS!         ✅ TUDO SALVO!
```

**Solução:**
- PostgreSQL é um **serviço separado**
- Tem **disco próprio persistente**
- **Nunca hiberna** (sempre ativo)
- Dados **100% seguros**

---

## 🎯 GARANTIAS COM POSTGRESQL

### ✅ Seus dados estão seguros:

| Situação | Dados Salvos? |
|----------|--------------|
| App hiberna após 15 min | ✅ SIM |
| App acorda (cold start) | ✅ SIM |
| Deploy novo do app | ✅ SIM |
| Atualização do código | ✅ SIM |
| Reinicialização do Render | ✅ SIM |
| Queda de energia do Render | ✅ SIM |
| 30 dias sem uso | ✅ SIM |

### ❌ Único jeito de perder dados:

| Situação | Dados Perdidos? |
|----------|----------------|
| Deletar o PostgreSQL database manualmente | ❌ SIM |
| Não renovar após 90 dias (avisa por email) | ❌ SIM |

---

## 🔐 CHECKLIST ANTES DE POPULAR COM DADOS REAIS

### **1. Verificar se PostgreSQL está configurado:**

```bash
# Acesse o Render Dashboard
# Vá no seu Web Service
# Clique em "Environment"
# Procure por:

DATABASE_URL=postgresql://...
```

✅ **TEM?** → Pode popular tranquilo!
❌ **NÃO TEM?** → Configure primeiro! (veja RENDER_DEPLOY.md)

---

### **2. Testar a persistência:**

**Teste prático:**

```
1. Acesse o sistema
2. Cadastre 1 cliente de teste (ex: "João Teste")
3. Espere 20 minutos (app vai hibernar)
4. Acesse novamente (vai demorar 30-60s)
5. Procure o cliente "João Teste"
```

✅ **Encontrou?** → PostgreSQL funcionando! Dados salvos!
❌ **Sumiu?** → Ainda está no SQLite! Configure PostgreSQL!

---

### **3. Verificar backup automático:**

O Render faz **backup automático** do PostgreSQL free:
- Backup diário
- Retém 7 dias
- Restauração via dashboard

**Para verificar:**
```
Render Dashboard → PostgreSQL → Info → Backups
```

---

## 💾 ESTRATÉGIAS DE BACKUP ADICIONAIS

### **Backup Manual (Recomendado para dados importantes):**

#### **Opção 1: Via Render Shell**

```bash
# 1. Acessar Shell do Web Service
Render Dashboard → Seu App → Shell

# 2. Fazer backup dos dados
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# 3. Baixar o arquivo
# Use o botão "Download" na interface
```

#### **Opção 2: Via Botão no Sistema**

```
No sistema GarageRoute66:
1. Faça login como admin
2. Menu lateral → "Backup DB"
3. Clique no botão
4. Backup salvo no banco PostgreSQL
```

#### **Opção 3: Script Automático**

Adicione ao `build.sh` (já tem):
```bash
# Backup antes de cada deploy
python manage.py dumpdata > backup_pre_deploy.json
```

---

## 📅 PLANO DE BACKUP RECOMENDADO

### **Para oficina pequena (até 50 OS/mês):**
```
□ Backup automático Render (7 dias) ✅ Já tem
□ Backup manual mensal via botão
□ Guardar em Google Drive/Dropbox
```

### **Para oficina média (50-200 OS/mês):**
```
□ Backup automático Render (7 dias) ✅ Já tem
□ Backup manual semanal via botão
□ Guardar em 2 lugares (Drive + Dropbox)
□ Testar restauração 1x/mês
```

### **Para oficina grande (200+ OS/mês):**
```
□ Upgrade PostgreSQL para pago ($7/mês)
  → Backup 30 dias em vez de 7
  → 256 MB em vez de 100 MB
□ Backup automático diário via script
□ Guardar em 3 lugares
□ Testar restauração 1x/semana
```

---

## 🆘 COMO RESTAURAR BACKUP (SE NECESSÁRIO)

### **Se algo der errado:**

#### **1. Restaurar do backup do Render:**

```
Render Dashboard
  → PostgreSQL
  → Backups
  → Selecione o backup
  → "Restore"
```

#### **2. Restaurar de arquivo JSON:**

```bash
# Via Shell do Render
python manage.py loaddata backup_20250113.json
```

---

## ⏰ RENOVAÇÃO DO POSTGRESQL FREE

### **IMPORTANTE:**

O PostgreSQL free do Render **expira em 90 dias**.

**O que fazer:**

```
📧 30 dias antes → Render envia email avisando
📧 15 dias antes → Render envia email avisando
📧 7 dias antes → Render envia email avisando

Opções:
1. Renovar grátis (cria novo banco, migra dados)
2. Upgrade para pago ($7/mês - sem expiração)
```

**Como renovar grátis:**

```
1. Criar novo PostgreSQL database (free)
2. Fazer backup do banco antigo:
   python manage.py dumpdata > backup.json
3. Atualizar DATABASE_URL para novo banco
4. Restaurar dados:
   python manage.py migrate
   python manage.py loaddata backup.json
5. Deletar banco antigo
```

---

## 📊 MONITORAMENTO DE SAÚDE

### **Verifique periodicamente:**

```
□ Render Dashboard
  □ PostgreSQL Status: ✅ Running
  □ Storage Used: __/100 MB
  □ Days until renewal: __/90

□ No seu sistema
  □ Dados carregando normalmente
  □ Novos cadastros salvando
  □ Relatórios funcionando

□ Emails do Render
  □ Sem alertas de problema
  □ Sem avisos de expiração próxima
```

---

## 💡 DICAS DE SEGURANÇA

### **Para dormir tranquilo:**

✅ **Configure PostgreSQL ANTES de popular**
```
Siga: RENDER_DEPLOY.md
```

✅ **Faça teste de persistência**
```
Cadastre 1 dado → Espere hibernar → Verifique se voltou
```

✅ **Configure backups mensais**
```
Todo dia 1º do mês: Clique em "Backup DB"
Baixe e guarde no Drive
```

✅ **Monitore os emails do Render**
```
Fique atento aos avisos de expiração
```

✅ **Teste restauração 1x**
```
Para saber que funciona quando precisar
```

---

## 🎯 CHECKLIST FINAL

Antes de colocar em produção com dados reais:

- [ ] PostgreSQL criado e configurado
- [ ] DATABASE_URL definida no Render
- [ ] Credenciais admin via env vars
- [ ] Teste de persistência feito (passou!)
- [ ] Primeiro backup manual criado
- [ ] Backup salvo em lugar seguro (Drive/Dropbox)
- [ ] Email do Render cadastrado corretamente
- [ ] Equipe treinada sobre backups

✅ **TUDO OK?** → Pode popular com dados reais!

---

## 📞 PERGUNTAS FREQUENTES

### **"E se o Render falir?"**
- Você tem os backups JSON
- Pode migrar para outro serviço facilmente
- Django é portátil (funciona em qualquer lugar)

### **"E se eu esquecer de renovar após 90 dias?"**
- Render envia 3 avisos por email
- Mesmo expirado, dados ficam mais alguns dias
- Tempo de migrar antes de perder

### **"Quanto custa o PostgreSQL pago?"**
- $7/mês (R$ 35-40 dependendo do dólar)
- 256 MB de espaço
- Backups por 30 dias
- Sem expiração

### **"100 MB é suficiente?"**
- Para 1000 clientes: ~10 MB
- Para 5000 OS: ~50 MB
- Para 10000 peças: ~20 MB
- **Total**: Tranquilamente 1-2 anos de uso

### **"Preciso pagar o Render?"**
- Não! O free tier é suficiente para pequenas/médias oficinas
- Único inconveniente: Hibernação (30-60s primeiro acesso)
- PostgreSQL free funciona perfeitamente

---

## ✅ CONCLUSÃO

### **COM POSTGRESQL CONFIGURADO:**

```
┌──────────────────────────────────────┐
│  SEUS DADOS ESTÃO 100% SEGUROS! ✅   │
├──────────────────────────────────────┤
│                                      │
│  • Persistem após hibernação         │
│  • Backup automático (7 dias)        │
│  • Restauração fácil                 │
│  • Totalmente gratuito               │
│                                      │
│  Pode popular com dados reais!       │
│                                      │
└──────────────────────────────────────┘
```

---

**Última atualização:** 13/01/2025
**Versão:** 2.0.0
**Status:** ✅ Seguro para Produção
