# 🐳 GarageRoute66 - Guia Docker Completo

Este documento explica como executar o GarageRoute66 usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker 20.10 ou superior
- Docker Compose 2.0 ou superior
- 4GB de RAM livre
- 10GB de espaço em disco

### Instalação do Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Windows
Baixe e instale o [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### macOS
```bash
brew install --cask docker
```

## 🚀 Início Rápido

### 1. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Variáveis obrigatórias:**
- `SECRET_KEY`: Chave secreta do Django (gere uma nova!)
- `DB_PASSWORD`: Senha do banco PostgreSQL
- `ALLOWED_HOSTS`: Domínios permitidos

### 2. Executar em Desenvolvimento
```bash
# Build e start
docker-compose -f docker-compose.dev.yml up --build

# Em background
docker-compose -f docker-compose.dev.yml up -d --build
```

**Acesso:**
- Aplicação: http://localhost:8001
- Admin: http://localhost:8001/admin/
- Banco: localhost:5433
- Redis: localhost:6380

### 3. Executar em Produção
```bash
# Build e start
docker-compose up --build -d

# Verificar status
docker-compose ps
```

**Acesso:**
- Aplicação: http://localhost
- Admin: http://localhost/admin/
- Banco: localhost:5432
- Redis: localhost:6379

## 🏗️ Arquitetura dos Containers

### Serviços Disponíveis

| Serviço | Descrição | Porta | Ambiente |
|---------|-----------|-------|----------|
| **web** | Aplicação Django | 8000/8001 | dev/prod |
| **db** | PostgreSQL 15 | 5432/5433 | dev/prod |
| **redis** | Cache Redis | 6379/6380 | dev/prod |
| **nginx** | Proxy reverso | 80/443 | prod |
| **celery** | Worker assíncrono | - | prod |
| **celery-beat** | Agendador de tarefas | - | prod |

### Volumes Persistentes

```yaml
volumes:
  postgres_data:     # Dados do banco
  redis_data:        # Cache Redis
  static_volume:     # Arquivos estáticos
  media_volume:      # Uploads de usuário
  logs_volume:       # Logs da aplicação
```

## 🛠️ Comandos Úteis

### Gerenciamento Básico

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Reiniciar um serviço específico
docker-compose restart web

# Ver logs
docker-compose logs -f web

# Ver status dos containers
docker-compose ps
```

### Django Management

```bash
# Executar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic

# Shell Django
docker-compose exec web python manage.py shell

# Executar testes
docker-compose exec web python manage.py test
```

### Banco de Dados

```bash
# Conectar ao PostgreSQL
docker-compose exec db psql -U garage_user -d garageroute66

# Backup do banco
docker-compose exec db pg_dump -U garage_user garageroute66 > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U garage_user garageroute66 < backup.sql

# Ver logs do banco
docker-compose logs db
```

### Cache Redis

```bash
# Conectar ao Redis
docker-compose exec redis redis-cli

# Limpar cache
docker-compose exec redis redis-cli FLUSHALL

# Monitorar comandos
docker-compose exec redis redis-cli monitor
```

## 🔧 Scripts de Automação

### Build Automatizado

```bash
# Desenvolvimento
chmod +x docker/scripts/build.sh
./docker/scripts/build.sh dev

# Produção
./docker/scripts/build.sh prod
```

### Deploy Automatizado

```bash
# Desenvolvimento
chmod +x docker/scripts/deploy.sh
./docker/scripts/deploy.sh dev

# Produção
./docker/scripts/deploy.sh prod

# Com logs
./docker/scripts/deploy.sh prod --logs
```

## 🌍 Configuração de Ambientes

### Desenvolvimento

**Características:**
- Hot reload de código
- Debug mode ativado
- SQLite ou PostgreSQL
- Sem nginx
- Portas diferentes para evitar conflitos

**Arquivo:** `docker-compose.dev.yml`

### Produção

**Características:**
- Código otimizado
- Debug mode desativado
- PostgreSQL obrigatório
- Nginx como proxy
- SSL/HTTPS configurável
- Celery para tarefas assíncronas

**Arquivo:** `docker-compose.yml`

## 🔒 Configuração de Segurança

### Variáveis Sensíveis

**Nunca commite:**
- `SECRET_KEY`
- `DB_PASSWORD`
- Chaves de API
- Certificados SSL

### Headers de Segurança (Nginx)

```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=63072000";
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## 📊 Monitoramento

### Health Checks

Todos os serviços possuem health checks configurados:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logs

```bash
# Logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f web

# Últimas 100 linhas
docker-compose logs --tail=100 web
```

### Métricas

```bash
# Uso de recursos
docker stats

# Espaço usado pelos volumes
docker system df

# Informações detalhadas
docker-compose exec web python manage.py check --deploy
```

## 🚚 Backup e Restore

### Backup Completo

```bash
# Criar diretório de backup
mkdir -p backups

# Backup do banco
docker-compose exec db pg_dump -U garage_user garageroute66 > backups/db_$(date +%Y%m%d_%H%M%S).sql

# Backup dos volumes
docker run --rm -v garage_media_volume:/data -v $(pwd)/backups:/backup alpine tar czf /backup/media_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### Restore

```bash
# Restaurar banco
docker-compose exec -T db psql -U garage_user garageroute66 < backups/db_20240115_120000.sql

# Restaurar mídia
docker run --rm -v garage_media_volume:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/media_20240115_120000.tar.gz -C /data
```

## 🔧 Troubleshooting

### Problemas Comuns

#### Container não inicia

```bash
# Verificar logs
docker-compose logs web

# Verificar configuração
docker-compose config

# Rebuild sem cache
docker-compose build --no-cache web
```

#### Banco não conecta

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Verificar logs do banco
docker-compose logs db

# Testar conexão
docker-compose exec web python manage.py shell -c "from django.db import connection; connection.ensure_connection()"
```

#### Permissões de arquivo

```bash
# Corrigir permissões
sudo chown -R $USER:$USER .

# Recriar containers
docker-compose down
docker-compose up --build
```

#### Cache Redis não funciona

```bash
# Verificar Redis
docker-compose exec redis redis-cli ping

# Limpar cache
docker-compose exec redis redis-cli FLUSHALL

# Verificar configuração
docker-compose exec web python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'ok'); print(cache.get('test'))"
```

#### Nginx não serve arquivos estáticos

```bash
# Verificar volumes
docker volume ls | grep static

# Coletar estáticos novamente
docker-compose exec web python manage.py collectstatic --noinput

# Verificar configuração do nginx
docker-compose exec nginx nginx -t
```

### Comandos de Debug

```bash
# Entrar no container
docker-compose exec web bash

# Verificar variáveis de ambiente
docker-compose exec web env

# Verificar portas abertas
docker-compose exec web netstat -tlnp

# Verificar arquivos
docker-compose exec web ls -la /app/
```

## 📈 Performance

### Otimizações de Produção

#### Gunicorn

```bash
# Configurações otimizadas (já no Dockerfile)
--workers 3
--worker-class gthread
--worker-connections 1000
--max-requests 1000
--max-requests-jitter 100
```

#### PostgreSQL

```sql
-- Configurações no init.sql
shared_buffers = '256MB'
effective_cache_size = '1GB'
maintenance_work_mem = '64MB'
work_mem = '4MB'
```

#### Redis

```bash
# Configuração de memória
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Escalabilidade

```yaml
# Múltiplas instâncias da aplicação
web:
  deploy:
    replicas: 3

# Load balancer
nginx:
  depends_on:
    - web
```

## 🚀 Deploy em Produção

### Servidor VPS

1. **Instalar Docker no servidor**
2. **Clonar repositório**
3. **Configurar .env**
4. **Executar deploy**

```bash
# No servidor
git clone https://github.com/seu-usuario/garageroute66.git
cd garageroute66
cp .env.example .env
nano .env  # Configurar variáveis
./docker/scripts/deploy.sh prod
```

### Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Deploy da stack
docker stack deploy -c docker-compose.yml garage

# Verificar serviços
docker service ls
```

### Kubernetes

Ver arquivo `k8s/` para manifests do Kubernetes (criar separadamente se necessário).

## 📝 Manutenção

### Updates

```bash
# Atualizar código
git pull origin main

# Rebuild e redeploy
./docker/scripts/deploy.sh prod

# Verificar saúde
docker-compose ps
```

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Remover volumes órfãos
docker volume prune

# Limpeza completa (CUIDADO!)
docker system prune -a
```

---

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `docker-compose logs`
2. Consulte a documentação do Django
3. Abra uma issue no repositório

**GarageRoute66** - Sistema completo para gestão de oficinas mecânicas
*Agora com Docker para facilidade de deploy e escalabilidade*