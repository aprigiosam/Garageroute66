# Garage Route 66 - Gestão de Ordens de Serviço

Sistema web pensado para donos de oficina que também atuam na operação, permitindo abrir e acompanhar ordens de serviço de forma rápida.

## Recursos atuais

- Cadastro ágil de cliente e veículo diretamente da tela de nova OS.
- Geração automática de número da OS com base na data.
- Painel com indicadores essenciais (abertas, aguardando aprovação, em execução, finalizadas).
- Lista de ordens com filtros por status, prioridade e busca por cliente/placa.
- Detalhe da OS com resumo financeiro (itens, pagamentos e saldo) e histórico de status.
- Upload de fotos do veículo e anexos (ex.: cupons fiscais) diretamente durante o diagnóstico.
- Fluxo de aprovação com registro de canal, responsável e previsão de entrega após aceite.
- Link público de aprovação (com expiração e revogação) e envio automático por e-mail/WhatsApp.
- Gestão da execução (status, notas e fotos) e etapa final de pagamento/entrega com controle financeiro.
- Emissão de recibo detalhado da OS após liberação do veículo (com suporte à impressão).

## Como executar localmente

1. Crie um virtualenv e instale as dependências:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Aplique as migrações e crie um superusuário:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Execute o servidor de desenvolvimento:

   ```bash
   python manage.py runserver
   ```

4. Acesse `http://localhost:8000` e faça login com o usuário criado.
   Para visualizar anexos em desenvolvimento, os arquivos são servidos via `MEDIA_URL` (`/media/`).

## Próximos passos sugeridos

- Tela de edição da OS com atualização de status e itens.
- Registro de pagamentos direto na interface pública.
- Notificações (e-mail/WhatsApp) para clientes sobre andamento e aprovação.
- Exportação de relatórios e integração com aplicativos de contabilidade.
