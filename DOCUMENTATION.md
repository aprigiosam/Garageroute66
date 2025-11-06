# Garageroute66 - Sistema de Gestão de Oficina Mecânica

## Visão Geral

O **Garageroute66** é um sistema web moderno e completo para gerenciar oficinas mecânicas. Desenvolvido com **React 19**, **Node.js**, **Express** e **MySQL**, oferece funcionalidades robustas para controlar clientes, veículos, ordens de serviço, custos e finanças.

### Características Principais

- **Gestão de Clientes:** Cadastro completo com dados de contato e endereço
- **Gestão de Veículos:** Registro de veículos por cliente com marca, modelo, placa e VIN
- **Ordens de Serviço:** Criação e acompanhamento de OS com múltiplos status
- **Controle de Custos:** Registro de peças e serviços com custo interno (confidencial) e preço de venda
- **Orçamentos para Cliente:** Geração de orçamentos profissionais sem exposição de custos internos
- **Gestão Financeira:** Registro de receitas e despesas com categorização
- **Dashboard:** Resumo operacional com indicadores-chave
- **Autenticação:** Sistema de login seguro com OAuth

---

## Arquitetura Técnica

### Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| Frontend | React 19 + TypeScript + Tailwind CSS 4 |
| Backend | Node.js + Express 4 + tRPC 11 |
| Banco de Dados | MySQL com Drizzle ORM |
| Autenticação | Manus OAuth |
| UI Components | shadcn/ui |
| Styling | Tailwind CSS com temas personalizáveis |

### Estrutura de Pastas

```
garageroute66_app/
├── client/                    # Frontend React
│   ├── src/
│   │   ├── pages/            # Páginas do aplicativo
│   │   ├── components/       # Componentes reutilizáveis
│   │   ├── lib/              # Utilitários (tRPC client)
│   │   ├── contexts/         # React contexts
│   │   ├── App.tsx           # Roteamento principal
│   │   └── main.tsx          # Entrada da aplicação
│   └── public/               # Assets estáticos
├── server/                    # Backend Node.js
│   ├── routers.ts            # Definição das procedures tRPC
│   ├── db.ts                 # Helpers de banco de dados
│   └── _core/                # Infraestrutura (OAuth, contexto, etc)
├── drizzle/                  # Schema e migrações do banco
│   └── schema.ts             # Definição das tabelas
├── shared/                   # Código compartilhado
└── package.json              # Dependências do projeto
```

---

## Modelo de Dados

### Tabelas Principais

#### `users`
Tabela de usuários com autenticação OAuth.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| openId | varchar | Identificador OAuth único |
| name | text | Nome do usuário |
| email | varchar | Email |
| role | enum | `user` ou `admin` |
| createdAt | timestamp | Data de criação |

#### `clients`
Dados dos clientes da oficina.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| name | varchar | Nome do cliente |
| email | varchar | Email |
| phone | varchar | Telefone |
| cpf | varchar | CPF (único) |
| address | text | Endereço |
| city | varchar | Cidade |
| state | varchar | Estado (UF) |
| zipCode | varchar | CEP |

#### `vehicles`
Veículos dos clientes.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| clientId | int | FK para clients |
| brand | varchar | Marca (ex: Toyota) |
| model | varchar | Modelo (ex: Corolla) |
| year | int | Ano de fabricação |
| licensePlate | varchar | Placa (única) |
| vin | varchar | Número VIN |
| color | varchar | Cor |

#### `serviceOrders`
Ordens de serviço.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| clientId | int | FK para clients |
| vehicleId | int | FK para vehicles |
| orderNumber | varchar | Número da OS (único) |
| status | enum | `pending`, `in_progress`, `completed`, `paid`, `cancelled` |
| description | text | Descrição dos serviços |
| totalCost | decimal | Custo total (confidencial) |
| totalPrice | decimal | Preço total para cliente |
| createdAt | timestamp | Data de criação |
| completedAt | timestamp | Data de conclusão |
| paidAt | timestamp | Data de pagamento |

#### `serviceOrderItems`
Itens (peças e serviços) de cada OS.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| serviceOrderId | int | FK para serviceOrders |
| description | varchar | Descrição da peça/serviço |
| type | enum | `part` ou `service` |
| quantity | int | Quantidade |
| unitCost | decimal | Custo unitário (confidencial) |
| unitPrice | decimal | Preço unitário para cliente |

#### `transactions`
Registro de receitas e despesas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | ID único |
| type | enum | `revenue` ou `expense` |
| category | varchar | Categoria (ex: Serviços, Peças, Combustível) |
| description | text | Descrição |
| amount | decimal | Valor |
| serviceOrderId | int | FK opcional para serviceOrders |

---

## Funcionalidades por Página

### 1. Dashboard (`/`)
Página inicial com resumo operacional.

**Elementos:**
- Contagem de clientes cadastrados
- Total de ordens de serviço (com breakdown por status)
- Resumo financeiro (receitas, despesas, lucro)
- Ações rápidas para acessar funcionalidades principais
- Indicadores de ordens pendentes e lucro líquido

### 2. Gestão de Clientes (`/clients`)
Listagem e gerenciamento de clientes.

**Funcionalidades:**
- Listar todos os clientes cadastrados
- Criar novo cliente com formulário modal
- Editar dados do cliente
- Deletar cliente
- Visualizar detalhes do cliente (veículos e histórico de OS)

### 3. Detalhes do Cliente (`/clients/:id`)
Página com informações completas do cliente.

**Seções:**
- Dados do cliente (email, telefone, CPF, endereço)
- Lista de veículos com opção de adicionar novo
- Histórico de ordens de serviço

### 4. Ordens de Serviço (`/service-orders`)
Listagem de todas as ordens de serviço.

**Funcionalidades:**
- Listar todas as OS com status visual
- Criar nova OS (selecionando cliente e veículo)
- Visualizar detalhes da OS
- Mudar status da OS

### 5. Detalhes da OS (`/service-orders/:id`)
Página completa de gerenciamento da ordem de serviço.

**Seções:**
- Informações da OS (cliente, veículo, status)
- Tabela de itens com custo e preço
- Adicionar/editar/deletar itens
- Resumo financeiro (custo total, preço total, lucro)
- Botão para gerar orçamento para o cliente

### 6. Orçamento para Cliente (`/quote/:id`)
Página de visualização de orçamento (sem custos internos).

**Características:**
- Design profissional e imprimível
- Mostra apenas preços de venda (sem custos)
- Informações do cliente e veículo
- Tabela de itens com preços
- Total do orçamento
- Botão para imprimir/salvar como PDF
- Válido por 7 dias

### 7. Gestão Financeira (`/financial`)
Registro e acompanhamento de receitas e despesas.

**Funcionalidades:**
- Registrar nova transação (receita ou despesa)
- Categorizar transações (Serviços, Peças, Combustível, etc)
- Visualizar resumo de receitas e despesas
- Listar todas as transações com datas
- Calcular lucro líquido

---

## Procedures tRPC

### Clientes
```typescript
trpc.clients.list()                    // Listar todos
trpc.clients.get({ id })              // Obter um
trpc.clients.create({ ...data })      // Criar
trpc.clients.update({ id, ...data })  // Atualizar
trpc.clients.delete({ id })           // Deletar
```

### Veículos
```typescript
trpc.vehicles.listByClient({ clientId })      // Listar por cliente
trpc.vehicles.get({ id })                     // Obter um
trpc.vehicles.create({ ...data })             // Criar
trpc.vehicles.update({ id, ...data })        // Atualizar
trpc.vehicles.delete({ id })                 // Deletar
```

### Ordens de Serviço
```typescript
trpc.serviceOrders.list()                     // Listar todas
trpc.serviceOrders.get({ id })               // Obter uma
trpc.serviceOrders.listByClient({ clientId }) // Listar por cliente
trpc.serviceOrders.create({ ...data })       // Criar
trpc.serviceOrders.updateStatus({ id, status }) // Mudar status
```

### Itens de OS
```typescript
trpc.serviceOrderItems.list({ serviceOrderId })    // Listar
trpc.serviceOrderItems.create({ ...data })         // Criar
trpc.serviceOrderItems.update({ id, ...data })    // Atualizar
trpc.serviceOrderItems.delete({ id, serviceOrderId }) // Deletar
```

### Transações Financeiras
```typescript
trpc.transactions.list()           // Listar todas
trpc.transactions.create({ ...data }) // Criar
```

---

## Fluxo de Uso Típico

### Criar uma Ordem de Serviço

1. **Acesse Ordens de Serviço** → Clique em "Nova Ordem"
2. **Selecione Cliente** → Se novo, crie na página de Clientes
3. **Selecione Veículo** → Se novo, crie na página de Detalhes do Cliente
4. **Preencha Dados da OS** → Número e descrição
5. **Adicione Itens** → Clique em "Adicionar Item"
   - Descrição (ex: "Óleo de motor 5W30")
   - Tipo (Peça ou Serviço)
   - Quantidade
   - **Custo Unitário** (preço que você paga)
   - **Preço Unitário** (preço para o cliente)
6. **Gere Orçamento** → Clique em "Gerar Orçamento"
   - O cliente vê apenas os preços, não os custos
   - Pode imprimir ou salvar como PDF

### Acompanhar Financeiro

1. **Acesse Financeiro**
2. **Registre Receitas** → Quando cliente paga
3. **Registre Despesas** → Custos operacionais
4. **Visualize Resumo** → Dashboard mostra lucro líquido

---

## Segurança e Confidencialidade

### Proteção de Custos

- **Custos internos** (`unitCost`, `totalCost`) são armazenados no banco de dados
- **Orçamentos para cliente** (`/quote/:id`) mostram apenas preços de venda
- **Relatórios internos** (Dashboard, Detalhes da OS) mostram custos apenas para usuários autenticados
- Não há acesso público aos custos

### Autenticação

- Sistema usa **OAuth Manus** para autenticação segura
- Apenas usuários autenticados podem acessar dados
- Cookies de sessão com JWT

---

## Deployment

### Requisitos

- Node.js 22+
- MySQL 8+
- Variáveis de ambiente configuradas

### Variáveis de Ambiente

```env
DATABASE_URL=mysql://user:password@host:3306/garageroute66
JWT_SECRET=sua_chave_secreta_aqui
VITE_APP_ID=seu_app_id_oauth
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://portal.manus.im
```

### Executar Localmente

```bash
# Instalar dependências
pnpm install

# Criar/atualizar banco de dados
pnpm db:push

# Iniciar servidor de desenvolvimento
pnpm dev
```

---

## Próximos Passos Sugeridos

1. **Geração de Recibos:** Criar recibos detalhados após pagamento
2. **Notificações:** Enviar orçamentos por email/WhatsApp
3. **Relatórios Avançados:** Exportar relatórios em PDF/Excel
4. **Integração com Contabilidade:** Sincronizar com sistemas contábeis
5. **Histórico de Fotos:** Adicionar upload de fotos do veículo
6. **Agendamento:** Sistema de agendamento de serviços
7. **Backup Automático:** Backup regular do banco de dados
8. **Mobile App:** Aplicativo mobile para gerenciamento em campo

---

## Suporte e Contribuição

Para dúvidas ou sugestões, entre em contato com o desenvolvedor.

**Desenvolvido com ❤️ para oficinas mecânicas**
