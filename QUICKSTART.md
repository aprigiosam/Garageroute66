# Garageroute66 - Guia Rápido de Início

## Instalação

### 1. Pré-requisitos

- Node.js 22+
- pnpm (gerenciador de pacotes)
- MySQL 8+

### 2. Clonar o Repositório

```bash
git clone https://github.com/aprigiosam/Garageroute66.git
cd garageroute66_app
```

### 3. Instalar Dependências

```bash
pnpm install
```

### 4. Configurar Banco de Dados

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=mysql://root:senha@localhost:3306/garageroute66
JWT_SECRET=sua_chave_secreta_super_segura_aqui_123456
VITE_APP_ID=seu_app_id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://portal.manus.im
OWNER_OPEN_ID=seu_open_id
OWNER_NAME=Seu Nome
```

### 5. Criar Banco de Dados

```bash
# Aplicar migrações
pnpm db:push
```

### 6. Iniciar o Servidor

```bash
# Modo desenvolvimento
pnpm dev

# O servidor estará disponível em http://localhost:3000
```

---

## Primeiro Uso

### 1. Fazer Login

- Acesse `http://localhost:3000`
- Clique em "Fazer Login"
- Autentique com suas credenciais OAuth

### 2. Criar Primeiro Cliente

1. Clique em **Gerenciar Clientes** no dashboard
2. Clique em **Novo Cliente**
3. Preencha os dados:
   - Nome (obrigatório)
   - Email
   - Telefone
   - CPF
   - Endereço
4. Clique em **Criar Cliente**

### 3. Adicionar Veículo

1. Clique no cliente criado
2. Clique em **Novo Veículo**
3. Preencha:
   - Marca (ex: Toyota)
   - Modelo (ex: Corolla)
   - Ano
   - Placa (obrigatório)
   - Cor
   - VIN (opcional)
4. Clique em **Criar Veículo**

### 4. Criar Ordem de Serviço

1. Clique em **Ordens de Serviço** no menu
2. Clique em **Nova Ordem**
3. Selecione:
   - Cliente
   - Veículo
   - Número da OS (ex: OS-001)
   - Descrição (opcional)
4. Clique em **Criar Ordem**

### 5. Adicionar Itens à OS

1. Abra a OS criada
2. Clique em **Adicionar Item**
3. Preencha:
   - **Descrição:** Nome da peça/serviço
   - **Tipo:** Peça ou Serviço
   - **Quantidade:** Quantas unidades
   - **Custo Unitário:** Quanto você paga (confidencial)
   - **Preço Unitário:** Quanto o cliente paga
4. Clique em **Adicionar Item**
5. Repita para adicionar mais itens

### 6. Gerar Orçamento para Cliente

1. Na página da OS, clique em **Gerar Orçamento**
2. Uma página profissional será aberta mostrando:
   - Dados do cliente
   - Dados do veículo
   - Itens com preços (SEM custos internos)
   - Total
3. Clique em **Imprimir / Salvar PDF** para gerar documento

### 7. Registrar Transações Financeiras

1. Clique em **Financeiro** no menu
2. Clique em **Nova Transação**
3. Selecione:
   - **Tipo:** Receita ou Despesa
   - **Categoria:** Escolha uma categoria
   - **Descrição:** Detalhes (opcional)
   - **Valor:** Quantia
4. Clique em **Registrar Transação**

---

## Dicas de Uso

### Numeração de OS

Use um padrão consistente para os números de OS:
- `OS-001`, `OS-002`, etc. (sequencial)
- `OS-2024-001` (com ano)
- `OS-NOV-001` (com mês)

### Categorias de Transações

**Receitas:**
- Serviços
- Peças
- Outros

**Despesas:**
- Peças
- Combustível
- Aluguel
- Salários
- Utilidades
- Manutenção
- Outros

### Acompanhar Lucro

No dashboard, você verá:
- **Receitas:** Total de dinheiro que entrou
- **Despesas:** Total de custos operacionais
- **Lucro Líquido:** Receitas - Despesas

---

## Troubleshooting

### Erro: "Database connection failed"

- Verifique se MySQL está rodando
- Confira a string `DATABASE_URL` no `.env`
- Certifique-se que o banco de dados existe

### Erro: "OAuth not configured"

- Verifique as variáveis de ambiente
- Confirme que `VITE_APP_ID` e `OAUTH_SERVER_URL` estão corretos

### Página em branco após login

- Limpe o cache do navegador (Ctrl+Shift+Delete)
- Reinicie o servidor (`pnpm dev`)
- Verifique o console do navegador (F12) para erros

---

## Próximos Passos

1. Customize o nome da empresa em **Settings → General**
2. Configure o logo da empresa
3. Crie vários clientes e ordens para testar o fluxo
4. Explore o relatório financeiro
5. Teste a geração de orçamentos

---

## Documentação Completa

Para mais detalhes sobre funcionalidades, arquitetura e segurança, consulte [DOCUMENTATION.md](./DOCUMENTATION.md).

---

**Boa sorte com seu sistema de gestão de oficina! 🚗**
