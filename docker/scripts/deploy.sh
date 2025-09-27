#!/bin/bash
# Script de deploy do GarageRoute66

set -e

echo "🚀 Deploying GarageRoute66..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    error "Arquivo .env não encontrado!"
    warn "Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Verificar variáveis essenciais
check_env_var() {
    if [ -z "${!1}" ]; then
        error "Variável de ambiente $1 não está definida!"
        exit 1
    fi
}

# Carregar variáveis de ambiente
source .env

# Verificar variáveis essenciais
check_env_var "SECRET_KEY"
check_env_var "DB_PASSWORD"

# Definir ambiente
ENVIRONMENT=${1:-production}

log "Starting deployment for environment: $ENVIRONMENT"

# Parar containers se estiverem rodando
log "Stopping existing containers..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml down
else
    docker-compose down
fi

# Fazer backup do banco (apenas em produção)
if [ "$ENVIRONMENT" = "production" ]; then
    log "Creating database backup..."
    docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > backups/backup_$(date +%Y%m%d_%H%M%S).sql || warn "Backup failed - continuing deployment"
fi

# Build das imagens
log "Building Docker images..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml build
else
    docker-compose build
fi

# Subir serviços de infraestrutura primeiro
log "Starting infrastructure services..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml up -d db redis
else
    docker-compose up -d db redis
fi

# Aguardar serviços ficarem prontos
log "Waiting for services to be ready..."
sleep 10

# Subir aplicação
log "Starting application..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml up -d web
else
    docker-compose up -d web celery celery-beat
fi

# Aguardar aplicação ficar pronta
log "Waiting for application to be ready..."
sleep 15

# Subir nginx (apenas em produção)
if [ "$ENVIRONMENT" = "production" ]; then
    log "Starting nginx..."
    docker-compose up -d nginx
fi

# Verificar saúde dos serviços
log "Checking service health..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml ps
else
    docker-compose ps
fi

# Executar testes de saúde
log "Running health checks..."

# Verificar se banco está acessível
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web python manage.py check --database default
else
    docker-compose exec -T web python manage.py check --database default
fi

# Verificar se Redis está acessível
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping
else
    docker-compose exec -T redis redis-cli ping
fi

# Executar migrações
log "Running database migrations..."
if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web python manage.py migrate
else
    docker-compose exec -T web python manage.py migrate
fi

# Coletar arquivos estáticos (apenas produção)
if [ "$ENVIRONMENT" = "production" ]; then
    log "Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
fi

# Mostrar status final
log "✅ Deployment completed successfully!"
info "Services status:"

if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml ps
    info "Application available at: http://localhost:8001"
    info "Admin available at: http://localhost:8001/admin/"
else
    docker-compose ps
    info "Application available at: http://localhost"
    info "Admin available at: http://localhost/admin/"
fi

log "🎉 GarageRoute66 is now running!"

# Mostrar logs se solicitado
if [ "$2" = "--logs" ]; then
    log "Showing logs..."
    if [ "$ENVIRONMENT" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
fi