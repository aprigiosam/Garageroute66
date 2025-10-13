# Changelog - GarageRoute66

## [2.0.0] - 2025-01-13

### 🔥 CORREÇÕES CRÍTICAS

#### ✅ Problema de Reset de Credenciais - RESOLVIDO
- **Problema**: No Render free tier, quando o app hibernava, o banco SQLite era apagado e as credenciais voltavam ao padrão
- **Solução**:
  - Migração de SQLite para PostgreSQL (persistente e gratuito)
  - Credenciais admin via variáveis de ambiente
  - Script atualizado para criar/atualizar admin automaticamente

#### ✅ Interface Mobile - MELHORADA
- **Problema**: Navegação difícil no celular
- **Soluções**:
  - Navbar movida para a parte inferior (bottom navigation)
  - Apenas itens principais visíveis no mobile
  - Tabelas responsivas com scroll horizontal
  - Botões e textos otimizados para toque
  - Padding reduzido para aproveitar melhor o espaço
  - iOS safe area support

---

## 🚀 Como Atualizar no Render

### 1. Criar PostgreSQL Database
1. Dashboard Render → **"New +"** → **"PostgreSQL"**
2. Configure:
   - Name: `garageroute66-db`
   - Database: `garageroute66`
   - Region: Oregon (US West)
   - Plan: **FREE**
3. Copie a **"Internal Database URL"**

### 2. Configurar Variáveis de Ambiente
No seu Web Service, adicione:

```bash
# Database (obrigatório)
DATABASE_URL=postgresql://user:pass@host/dbname

# Suas credenciais admin (mude!)
DJANGO_SUPERUSER_USERNAME=seu_usuario
DJANGO_SUPERUSER_PASSWORD=SuaSenhaForte123!
DJANGO_SUPERUSER_EMAIL=seu@email.com

# Outras (mantenha)
SECRET_KEY=sua-secret-key
DEBUG=False
ALLOWED_HOSTS=*.onrender.com
```

### 3. Fazer Deploy
1. **Manual Deploy** → **"Deploy latest commit"**
2. Aguarde 3-5 minutos
3. Acesse `/admin/` com suas novas credenciais

---

## 📱 Melhorias Mobile

### Navegação Bottom Bar (< 768px)
- Dashboard
- Clientes
- Peças
- Ordens
- Agendamentos

**Acesso rápido aos itens mais usados!**

### Itens ocultos no mobile (acesse via desktop):
- Veículos (acesse via Clientes)
- Categorias e Fornecedores (acesse via Peças)
- Relatórios
- Backup DB

### Gestos Touch
- **Pull to Refresh**: Arraste para baixo no topo para recarregar
- **Scroll horizontal**: Tabelas grandes podem ser roladas

---

## 🔧 Mudanças Técnicas

### Banco de Dados
- ✅ Suporte a PostgreSQL via `DATABASE_URL`
- ✅ Fallback para SQLite em desenvolvimento local
- ✅ Connection pooling (600s)
- ✅ Health checks habilitados

### Dependências Adicionadas
```txt
psycopg2-binary==2.9.9
dj-database-url==2.1.0
```

### Settings.py
- Auto-detecta PostgreSQL via `DATABASE_URL`
- Mantém SQLite para desenvolvimento local
- Zero configuração manual necessária

### create_admin.py
- Lê credenciais de variáveis de ambiente
- Atualiza senha se já existe admin
- Cria novo admin se não existe
- Mais seguro e flexível

---

## 📊 Vantagens da Nova Arquitetura

### Persistência de Dados
- ✅ Dados mantidos após hibernação
- ✅ Credenciais não resetam mais
- ✅ PostgreSQL gratuito (100 MB)
- ✅ Backups automáticos pelo Render

### Segurança
- ✅ Senhas via variáveis de ambiente
- ✅ Não mais hardcoded no código
- ✅ Fácil rotação de credenciais
- ✅ Sem exposição acidental

### Mobile First
- ✅ Interface otimizada para celular
- ✅ Navegação intuitiva (bottom bar)
- ✅ Touch targets adequados (44px mínimo)
- ✅ PWA ready

---

## 🆘 Troubleshooting

### Ainda vejo senha antiga no Render
1. Verifique se definiu `DJANGO_SUPERUSER_PASSWORD` correto
2. Faça novo deploy manual
3. Limpe cache do navegador
4. Tente login novamente

### Mobile navbar não aparece embaixo
- Limpe cache do navegador
- Force refresh (Ctrl+Shift+R)
- Verifique se está em tela < 768px

### Erro: "relation does not exist"
- Aguarde migração completar no deploy
- Veja logs: Render Dashboard → Logs
- Se persistir, rode: `python manage.py migrate`

---

## 📝 Notas de Migração

### De SQLite para PostgreSQL

**Dados locais**: Seu banco SQLite local continua funcionando.

**Dados em produção (Render)**:
- Dados antigos do SQLite não são migrados automaticamente
- Será criado banco PostgreSQL novo e vazio
- Recadastre dados importantes após deploy

**Para migrar dados**:
```bash
# Local
python manage.py dumpdata > backup.json

# Render Shell
python manage.py loaddata backup.json
```

---

## 🎯 Próximas Melhorias Sugeridas

- [ ] Export/Import de dados via admin
- [ ] Backup automático agendado
- [ ] Notificações push mobile
- [ ] Modo offline completo (PWA)
- [ ] Dark mode
- [ ] Filtros avançados nas listagens

---

## 📚 Documentação

- **Deploy**: `RENDER_DEPLOY.md`
- **Config Render**: `RENDER_CONFIG.txt`
- **README**: `README.md`

---

## 👨‍💻 Desenvolvido para

Sistema de gestão completo para oficinas mecânicas
- Ordens de Serviço
- Clientes e Veículos
- Estoque de Peças
- Agendamentos
- Relatórios

**Free tier friendly**: Funciona perfeitamente no plano gratuito do Render.com

---

**Versão**: 2.0.0
**Data**: 13 de Janeiro de 2025
**Status**: Stable - Production Ready ✅
