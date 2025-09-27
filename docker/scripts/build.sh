#!/bin/bash
# Script de build do GarageRoute66

set -e

echo "🏗️ Building GarageRoute66 Docker Images..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    error "Docker não está rodando!"
    exit 1
fi

# Verificar se docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose não está instalado!"
    exit 1
fi

# Definir ambiente (padrão: production)
ENVIRONMENT=${1:-production}

log "Building for environment: $ENVIRONMENT"

# Build baseado no ambiente
case $ENVIRONMENT in
    "dev"|"development")
        log "Building development environment..."
        docker-compose -f docker-compose.dev.yml build --no-cache
        ;;
    "prod"|"production")
        log "Building production environment..."
        docker-compose build --no-cache
        ;;
    *)
        error "Environment must be 'dev' or 'prod'"
        exit 1
        ;;
esac

# Verificar se build foi bem-sucedido
if [ $? -eq 0 ]; then
    log "✅ Build completed successfully!"

    # Mostrar imagens criadas
    log "Docker images created:"
    docker images | grep garage

    log "🚀 Ready to start with: docker-compose up"
else
    error "❌ Build failed!"
    exit 1
fi