import logging
import json
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve

logger = logging.getLogger('core.audit')


class AuditMiddleware:
    """Middleware para auditoria de ações do usuário"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturar informações antes da requisição
        start_time = timezone.now()
        user = getattr(request, 'user', AnonymousUser())

        # Processar requisição
        response = self.get_response(request)

        # Log de auditoria apenas para ações importantes
        if self._should_audit(request):
            self._log_action(request, response, user, start_time)

        return response

    def _should_audit(self, request):
        """Determina se a requisição deve ser auditada"""
        # Auditar apenas métodos que modificam dados
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return False

        # Auditar apenas rotas específicas (não admin estático)
        if '/admin/jsi18n/' in request.path or '/static/' in request.path:
            return False

        return True

    def _log_action(self, request, response, user, start_time):
        """Registra a ação no log de auditoria"""
        try:
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()

            # Resolver o nome da view
            try:
                resolved = resolve(request.path)
                view_name = f"{resolved.namespace}:{resolved.url_name}" if resolved.namespace else resolved.url_name
            except:
                view_name = 'unknown'

            # Dados da auditoria
            audit_data = {
                'timestamp': start_time.isoformat(),
                'user': user.username if user.is_authenticated else 'anonymous',
                'user_id': user.id if user.is_authenticated else None,
                'method': request.method,
                'path': request.path,
                'view_name': view_name,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'status_code': response.status_code,
                'duration_seconds': round(duration, 3),
            }

            # Adicionar dados POST/PUT (sem senhas)
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'POST'):
                post_data = dict(request.POST)
                # Remover campos sensíveis
                sensitive_fields = ['password', 'password1', 'password2', 'csrfmiddlewaretoken']
                for field in sensitive_fields:
                    post_data.pop(field, None)
                audit_data['post_data'] = post_data

            # Log da auditoria
            logger.info(f"AUDIT: {json.dumps(audit_data, ensure_ascii=False)}")

        except Exception as e:
            logger.error(f"Erro na auditoria: {e}")

    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip