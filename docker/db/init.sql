-- Script de inicialização do PostgreSQL para GarageRoute66

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurações de performance (comentadas para evitar erros)
-- ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
-- ALTER SYSTEM SET pg_stat_statements.track = 'all';
-- ALTER SYSTEM SET log_statement = 'all';
-- ALTER SYSTEM SET log_duration = 'on';
-- ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Configurações de memória (ajuste conforme recursos disponíveis)
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '4MB';

-- Configurações de WAL
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

-- Recarregar configurações
SELECT pg_reload_conf();

-- Criar usuário e database se não existirem (redundância)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'garage_user') THEN
        CREATE ROLE garage_user WITH LOGIN PASSWORD 'garage_password';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'garageroute66') THEN
        CREATE DATABASE garageroute66 OWNER garage_user;
    END IF;
END
$$;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE garageroute66 TO garage_user;

\echo 'Database initialization completed for GarageRoute66!'