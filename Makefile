# GarageRoute66 - Makefile para automação Docker

.PHONY: help build up down logs shell test migrate collectstatic backup restore clean

# Variáveis
COMPOSE_FILE_DEV = docker-compose.dev.yml
COMPOSE_FILE_PROD = docker-compose.yml
BACKUP_DIR = backups

# Comando padrão
help: ## Mostrar ajuda
	@echo "🚗 GarageRoute66 - Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========================================
# DESENVOLVIMENTO
# ========================================

dev-build: ## Build para desenvolvimento
	@echo "🏗️ Building development environment..."
	docker-compose -f $(COMPOSE_FILE_DEV) build

dev-up: ## Iniciar desenvolvimento
	@echo "🚀 Starting development environment..."
	docker-compose -f $(COMPOSE_FILE_DEV) up -d
	@echo "✅ Development environment started!"
	@echo "📱 Application: http://localhost:8001"
	@echo "⚡ Admin: http://localhost:8001/admin/"

dev-down: ## Parar desenvolvimento
	@echo "🛑 Stopping development environment..."
	docker-compose -f $(COMPOSE_FILE_DEV) down

dev-logs: ## Ver logs desenvolvimento
	docker-compose -f $(COMPOSE_FILE_DEV) logs -f

dev-shell: ## Shell do container desenvolvimento
	docker-compose -f $(COMPOSE_FILE_DEV) exec web bash

dev-migrate: ## Executar migrações desenvolvimento
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python manage.py migrate

dev-test: ## Executar testes desenvolvimento
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python manage.py test

dev-superuser: ## Criar superusuário desenvolvimento
	docker-compose -f $(COMPOSE_FILE_DEV) exec web python manage.py createsuperuser

# ========================================
# PRODUÇÃO
# ========================================

build: ## Build para produção
	@echo "🏗️ Building production environment..."
	docker-compose -f $(COMPOSE_FILE_PROD) build

up: ## Iniciar produção
	@echo "🚀 Starting production environment..."
	docker-compose -f $(COMPOSE_FILE_PROD) up -d
	@echo "✅ Production environment started!"
	@echo "🌐 Application: http://localhost"
	@echo "⚡ Admin: http://localhost/admin/"

down: ## Parar produção
	@echo "🛑 Stopping production environment..."
	docker-compose -f $(COMPOSE_FILE_PROD) down

logs: ## Ver logs produção
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f

shell: ## Shell do container produção
	docker-compose -f $(COMPOSE_FILE_PROD) exec web bash

restart: ## Reiniciar produção
	@echo "🔄 Restarting production environment..."
	docker-compose -f $(COMPOSE_FILE_PROD) restart

# ========================================
# BANCO DE DADOS
# ========================================

migrate: ## Executar migrações
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py migrate

makemigrations: ## Criar migrações
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py makemigrations

db-shell: ## Shell do PostgreSQL
	docker-compose -f $(COMPOSE_FILE_PROD) exec db psql -U garage_user -d garageroute66

db-backup: ## Backup do banco
	@echo "💾 Creating database backup..."
	@mkdir -p $(BACKUP_DIR)
	docker-compose -f $(COMPOSE_FILE_PROD) exec db pg_dump -U garage_user garageroute66 > $(BACKUP_DIR)/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in $(BACKUP_DIR)/"

db-restore: ## Restaurar banco (uso: make db-restore FILE=backup.sql)
	@echo "🔄 Restoring database from $(FILE)..."
	docker-compose -f $(COMPOSE_FILE_PROD) exec -T db psql -U garage_user garageroute66 < $(FILE)
	@echo "✅ Database restored!"

# ========================================
# DJANGO
# ========================================

collectstatic: ## Coletar arquivos estáticos
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py collectstatic --noinput

test: ## Executar testes
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py test

superuser: ## Criar superusuário
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py createsuperuser

check: ## Verificar configurações Django
	docker-compose -f $(COMPOSE_FILE_PROD) exec web python manage.py check --deploy

# ========================================
# CACHE
# ========================================

cache-clear: ## Limpar cache Redis
	docker-compose -f $(COMPOSE_FILE_PROD) exec redis redis-cli FLUSHALL

cache-shell: ## Shell do Redis
	docker-compose -f $(COMPOSE_FILE_PROD) exec redis redis-cli

# ========================================
# MONITORAMENTO
# ========================================

ps: ## Status dos containers
	docker-compose -f $(COMPOSE_FILE_PROD) ps

stats: ## Estatísticas dos containers
	docker stats

logs-web: ## Logs apenas da aplicação
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f web

logs-db: ## Logs apenas do banco
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f db

logs-nginx: ## Logs apenas do nginx
	docker-compose -f $(COMPOSE_FILE_PROD) logs -f nginx

# ========================================
# MANUTENÇÃO
# ========================================

clean: ## Limpeza geral do Docker
	@echo "🧹 Cleaning Docker resources..."
	docker container prune -f
	docker image prune -f
	docker volume prune -f
	docker network prune -f
	@echo "✅ Cleanup completed!"

clean-all: ## Limpeza completa (CUIDADO!)
	@echo "⚠️ This will remove ALL unused Docker resources!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a -f; \
		echo "✅ Complete cleanup done!"; \
	else \
		echo "❌ Cleanup cancelled."; \
	fi

update: ## Atualizar e redeploy
	@echo "🔄 Updating GarageRoute66..."
	git pull origin main
	docker-compose -f $(COMPOSE_FILE_PROD) build
	docker-compose -f $(COMPOSE_FILE_PROD) up -d
	@echo "✅ Update completed!"

# ========================================
# BACKUP COMPLETO
# ========================================

backup-full: ## Backup completo (banco + mídia)
	@echo "💾 Creating full backup..."
	@mkdir -p $(BACKUP_DIR)
	$(MAKE) db-backup
	docker run --rm -v garage_media_volume:/data -v $(shell pwd)/$(BACKUP_DIR):/backup alpine tar czf /backup/media_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "✅ Full backup completed!"

restore-full: ## Restaurar backup completo
	@echo "🔄 Restoring full backup..."
	@echo "Please specify backup files:"
	@echo "make restore-full DB_FILE=backup_db.sql MEDIA_FILE=media_backup.tar.gz"

# ========================================
# SCRIPTS PERSONALIZADOS
# ========================================

deploy-dev: ## Deploy completo desenvolvimento
	chmod +x docker/scripts/deploy.sh
	./docker/scripts/deploy.sh dev

deploy-prod: ## Deploy completo produção
	chmod +x docker/scripts/deploy.sh
	./docker/scripts/deploy.sh prod

build-script: ## Build usando script
	chmod +x docker/scripts/build.sh
	./docker/scripts/build.sh prod

# ========================================
# INFORMAÇÕES
# ========================================

info: ## Informações do sistema
	@echo "📊 GarageRoute66 System Information"
	@echo "=================================="
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker Compose version:"
	@docker-compose --version
	@echo ""
	@echo "Running containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Docker disk usage:"
	@docker system df

env-check: ## Verificar variáveis de ambiente
	@echo "🔍 Checking environment variables..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "📋 Copy .env.example to .env and configure it"; \
	else \
		echo "✅ .env file found"; \
		echo "📋 Key variables:"; \
		grep -E "^(DEBUG|SECRET_KEY|DB_|ALLOWED_HOSTS)" .env || echo "❌ Missing key variables"; \
	fi

# Comando padrão quando apenas 'make' é executado
.DEFAULT_GOAL := help