# Oficina Pro

Plataforma web para gestao de oficinas mecanicas construida com Django. O projeto reune cadastro de clientes, veiculos, ordens de servico, agendamentos e relatorios em uma interface unica pensada para equipes operacionais.

## Visao geral
- Autenticacao segura com Django Admin para gestao interna.
- Dashboard com indicadores de ordens, faturamento e agenda diaria.
- Fluxo completo de ordens de servico (abertura, acompanhamento, historico e faturamento).
- Modulo de agendamentos integrado a abertura de OS.
- Relatorios exportaveis com filtros por periodo e tipo de informacao.

## Arquitetura do projeto
- oficina/ - configuracoes centrais do Django (settings, urls, wsgi/asgi).
- core/ - app principal com models, forms, views, sinais e comandos customizados.
- templates/ - layout base e paginas da aplicacao (Bootstrap 5 e Bootstrap Icons).
- static/ (opcional) - assets locais quando necessarios.
- logs/ - saida padrao de logs configurada em producao/desenvolvimento.

### Dependencias principais
- Django 5.2, Django Debug Toolbar (ambiente de desenvolvimento).
- Celery e Redis (opcionais) para filas e cache.
- WeasyPrint e ReportLab para relatorios PDF.
- Sentry SDK para monitoramento.
- Gunicorn ou Daphne para deploy em ambientes WSGI/ASGI.

## Requisitos
- Python 3.10 ou superior.
- Pip e Virtualenv.
- Banco SQLite (desenvolvimento) ou PostgreSQL (producao).
- Redis (opcional) quando cache ou filas forem ativados.
## Preparando o ambiente de desenvolvimento
1. Clonar o repositorio:
   - Comando: `git clone https://github.com/seu-usuario/oficina-pro.git`
   - Em seguida: `cd oficina-pro`.

2. Criar e ativar o virtualenv:
   - Linux, macOS ou WSL: `python3 -m venv venv && source venv/bin/activate`.
   - Windows (PowerShell): `python -m venv venv; .\venv\Scripts\Activate.ps1`.

3. Instalar dependencias:
   - `pip install --upgrade pip`
   - `pip install -r requirements.txt`
   - Atualize o arquivo sempre que adicionar bibliotecas novas.

4. Configurar variaveis de ambiente:
   - Copie `env_example.txt` para `.env`.
   - Ajuste SECRET_KEY, DEBUG, ALLOWED_HOSTS e integracoes (SMTP, Redis, Sentry).
   - Para PostgreSQL informe DB_NAME, DB_USER, DB_PASSWORD, DB_HOST e DB_PORT.

5. Preparar o banco de dados:
   - Execute `python manage.py migrate`.

6. Criar usuario administrativo:
   - Execute `python manage.py createsuperuser`.

7. Rodar o servidor local:
   - Execute `python manage.py runserver` e acesse http://127.0.0.1:8000/.

## Comandos uteis
- `python manage.py makemigrations` - gerar novas migracoes.
- `python manage.py loaddata arquivo.json` - importar fixtures.
- `python manage.py backup_db --cleanup` - rotina de backup (quando habilitada).
- `python manage.py check_prazos` - verificar ordens com prazo vencido.
- `python manage.py send_reminders` - enviar lembretes ativos.

## Testes e qualidade
- Testes unitarios e integrados: `python manage.py test`.
- Cobertura de codigo: `coverage run manage.py test` e depois `coverage html`.
- Debug Toolbar fica ativa quando DEBUG=True e o IP aparece em INTERNAL_IPS.

## Deploy
1. Ajuste variaveis sensiveis (DEBUG=False, ALLOWED_HOSTS, credenciais, chaves de API).
2. Rode as migracoes no ambiente final.
3. Coletar estaticos: `python manage.py collectstatic --noinput`.
4. Configurar servidor de aplicacao (Gunicorn para WSGI ou Daphne/uvicorn para ASGI).
5. Ativar HTTPS, cabecalhos de seguranca e monitoramento (Sentry, logs).
6. Agendar rotinas de backup (`backup_db`) e limpeza de logs.

## Solucao de problemas
- ImportError de Django: confirme se o virtualenv esta ativo e se as dependencias foram instaladas.
- TemplateSyntaxError: confira se blocos {% for %}/{% if %} possuem {% endfor %}/{% endif %}.
- Avisos de timezone: utilize django.utils.timezone.now() ou timezone.make_aware ao salvar DateTimeField.
- Debug Toolbar sem aparecer: inclua o IP da maquina em INTERNAL_IPS (especialmente para WSL/Docker).

## Proximos passos sugeridos
- Criar fixtures com dados de exemplo para demonstracoes.
- Adicionar testes para agendamentos e relatorios.
- Configurar pipelines de CI/CD para validar build e testes automaticamente.

---

Contribuicoes sao bem-vindas. Abra um issue ou envie um pull request com melhorias.
