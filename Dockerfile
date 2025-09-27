# GarageRoute66 - Multi-stage Dockerfile

# =================================
# Stage 1: Base
# =================================
FROM python:3.11-slim as base

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN groupadd -r garage && useradd -r -g garage garage

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =================================
# Stage 2: Development
# =================================
FROM base as development

# Instalar dependências adicionais para desenvolvimento
RUN pip install \
    django-debug-toolbar \
    ipdb \
    pytest-django \
    pytest-cov

# Copiar código da aplicação
COPY . .

# Ajustar permissões
RUN chown -R garage:garage /app && \
    chmod +x /app/docker/entrypoint.sh

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R garage:garage /app

# Expor porta
EXPOSE 8000

# Mudar para usuário não-root
USER garage

# Definir entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Comando padrão para desenvolvimento
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =================================
# Stage 3: Production
# =================================
FROM base as production

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R garage:garage /app

# Ajustar permissões
RUN chown -R garage:garage /app && \
    chmod +x /app/docker/entrypoint.sh

# Expor porta
EXPOSE 8000

# Mudar para usuário não-root
USER garage

# Definir entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Comando padrão para produção
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "gthread", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "oficina.wsgi:application"]