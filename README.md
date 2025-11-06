# Garageroute66 - Sistema Moderno de Gestão de Oficina

Um sistema web completo e profissional para gerenciar oficinas mecânicas, desenvolvido com as tecnologias mais modernas.

## 🚀 Características

- ✅ **Gestão de Clientes:** Cadastro completo com dados de contato
- ✅ **Gestão de Veículos:** Registro de veículos por cliente
- ✅ **Ordens de Serviço:** Criação e acompanhamento com múltiplos status
- ✅ **Controle de Custos:** Peças e serviços com custo interno (confidencial) e preço de venda
- ✅ **Orçamentos Profissionais:** Geração de orçamentos sem exposição de custos
- ✅ **Gestão Financeira:** Receitas e despesas com categorização
- ✅ **Dashboard:** Resumo operacional com indicadores-chave
- ✅ **Autenticação Segura:** Sistema de login com OAuth
- ✅ **Interface Responsiva:** Funciona em desktop, tablet e mobile

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| Frontend | React 19 + TypeScript + Tailwind CSS 4 |
| Backend | Node.js + Express 4 + tRPC 11 |
| Banco de Dados | MySQL com Drizzle ORM |
| Autenticação | Manus OAuth |
| UI Components | shadcn/ui |

## 📦 Instalação Rápida

### 1. Clonar e Instalar

```bash
git clone https://github.com/aprigiosam/Garageroute66.git
cd garageroute66_app
pnpm install
```

### 2. Configurar Banco de Dados

Crie um arquivo `.env`:

```env
DATABASE_URL=mysql://root:senha@localhost:3306/garageroute66
JWT_SECRET=sua_chave_secreta_aqui
VITE_APP_ID=seu_app_id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://portal.manus.im
OWNER_OPEN_ID=seu_open_id
OWNER_NAME=Seu Nome
```

### 3. Executar

```bash
# Aplicar migrações
pnpm db:push

# Iniciar servidor
pnpm dev
```

Acesse `http://localhost:3000`

## 📖 Documentação

- **[Guia Rápido](./QUICKSTART.md)** - Como começar em 5 minutos
- **[Documentação Completa](./DOCUMENTATION.md)** - Detalhes técnicos e funcionalidades

## 🎯 Fluxo Principal

1. **Criar Cliente** → Adicionar dados de contato
2. **Adicionar Veículo** → Registrar veículo do cliente
3. **Criar Ordem de Serviço** → Abrir nova OS
4. **Adicionar Itens** → Peças e serviços com custos
5. **Gerar Orçamento** → Documento profissional para cliente (sem custos)
6. **Registrar Financeiro** → Receitas e despesas
7. **Acompanhar Dashboard** → Visualizar indicadores

## 🔒 Segurança

- **Custos Confidenciais:** Apenas usuários internos veem os custos
- **Orçamentos Públicos:** Clientes veem apenas preços de venda
- **Autenticação OAuth:** Login seguro com tokens JWT
- **Banco de Dados:** MySQL com senhas criptografadas

## 📊 Páginas Disponíveis

| Página | URL | Descrição |
|--------|-----|-----------|
| Dashboard | `/` | Resumo operacional |
| Clientes | `/clients` | Listagem de clientes |
| Detalhes Cliente | `/clients/:id` | Veículos e histórico |
| Ordens de Serviço | `/service-orders` | Listagem de OS |
| Detalhes OS | `/service-orders/:id` | Itens e custos |
| Orçamento | `/quote/:id` | Documento para cliente |
| Financeiro | `/financial` | Receitas e despesas |

## 🚀 Próximos Passos

- [ ] Geração de recibos após pagamento
- [ ] Notificações por email/WhatsApp
- [ ] Relatórios em PDF/Excel
- [ ] Upload de fotos do veículo
- [ ] Sistema de agendamento
- [ ] Integração com contabilidade

## 📝 Licença

Este projeto é de código aberto e pode ser usado livremente.

## 👨‍💻 Desenvolvido com ❤️

Para oficinas mecânicas que querem gerenciar seus negócios de forma profissional e eficiente.

---

**Comece agora:** [Guia Rápido](./QUICKSTART.md)
