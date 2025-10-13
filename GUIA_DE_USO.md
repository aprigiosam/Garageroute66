# 📖 Guia Completo de Uso - GarageRoute66
## Sistema de Gestão para Oficinas Mecânicas

---

## 🎯 O QUE É O SISTEMA?

O **GarageRoute66** é um sistema completo para gerenciar sua oficina mecânica. Ele controla:

✅ **Clientes** - Cadastro de todos os clientes
✅ **Veículos** - Todos os carros/motos dos clientes
✅ **Ordens de Serviço** - Controle de todos os serviços
✅ **Agendamentos** - Agenda de serviços futuros
✅ **Estoque de Peças** - Controle de peças e valores
✅ **Relatórios** - Visualização de faturamento e desempenho

---

## 📱 COMO ACESSAR?

### No Computador:
1. Abra o navegador (Chrome, Edge, Firefox)
2. Digite: `https://seu-app.onrender.com`
3. Faça login com usuário e senha

### No Celular:
1. Abra o navegador no celular
2. Digite: `https://seu-app.onrender.com`
3. Faça login
4. **Clique em "Instalar App"** (botão azul que aparece)
5. Pronto! Agora tem um ícone na tela do celular

---

## 🔄 FLUXO DE TRABALHO COMPLETO

### **Passo 1: Cliente chega pela primeira vez**
```
Cliente novo → Cadastrar Cliente → Cadastrar Veículo → Criar Ordem de Serviço
```

### **Passo 2: Cliente já cadastrado retorna**
```
Buscar Cliente → Selecionar Veículo → Criar Ordem de Serviço
```

### **Passo 3: Cliente liga para agendar**
```
Buscar Cliente → Criar Agendamento → No dia: Transformar em Ordem de Serviço
```

---

## 📋 GUIA PASSO A PASSO DETALHADO

---

## 1️⃣ CADASTRAR CLIENTE NOVO

**Quando usar?** Sempre que um cliente chega pela primeira vez.

### Como fazer:

1. No menu lateral, clique em **"Clientes"**
2. Clique no botão verde **"+ Novo Cliente"**
3. Preencha os dados:
   - **Nome completo** (obrigatório)
   - **CPF** no formato: `123.456.789-00`
   - **Telefone** no formato: `(11) 99999-9999`
   - **E-mail** (ex: cliente@email.com)
   - **Endereço completo**
   - **Observações** (opcional - use para anotações importantes)
4. Clique em **"Salvar"**

✅ **Pronto!** Cliente cadastrado.

**💡 Dica:** Sempre preencha o telefone correto para contatos futuros!

---

## 2️⃣ CADASTRAR VEÍCULO DO CLIENTE

**Quando usar?** Logo após cadastrar o cliente OU quando ele traz um veículo novo.

### Como fazer:

1. No menu lateral, clique em **"Clientes"**
2. Procure o cliente e clique nele
3. Clique em **"+ Adicionar Veículo"**
4. Preencha os dados do veículo:
   - **Placa** (ex: ABC-1234 ou ABC1D23)
   - **Marca** (ex: Volkswagen, Fiat, Honda)
   - **Modelo** (ex: Gol, Civic, Uno)
   - **Ano** (ex: 2020)
   - **Cor** (ex: Prata)
   - **Chassi** (obrigatório - número único do veículo)
   - **Tipo** (Carro, Moto, Caminhão, Van)
   - **KM Atual** (quilometragem do veículo)
   - **Veículo batido?** (marque se for batido/acidentado)
   - **Observações** (ex: "Tem vazamento de óleo conhecido")
5. Clique em **"Salvar"**

✅ **Pronto!** Veículo cadastrado.

**💡 Dica:** Um cliente pode ter vários veículos cadastrados!

---

## 3️⃣ CRIAR ORDEM DE SERVIÇO (OS)

**Quando usar?** Sempre que um cliente deixa o veículo para manutenção.

### Como fazer:

1. No menu lateral, clique em **"Ordens de Serviço"**
2. Clique em **"+ Nova Ordem de Serviço"**
3. **DADOS BÁSICOS:**
   - **Cliente**: Selecione o cliente na lista
   - **Veículo**: Selecione o veículo do cliente
   - **Descrição do Problema**: Escreva o que o cliente relatou
     - Ex: "Barulho no motor ao acelerar"
   - **KM na Entrada**: Quilometragem atual do veículo
   - **Prioridade**:
     - 🟢 **Baixa** - Pode esperar
     - 🟡 **Normal** - Serviço comum
     - 🟠 **Alta** - Cliente precisa logo
     - 🔴 **Urgente** - Cliente esperando
   - **Prazo de Entrega**: Data e hora combinadas
   - **Responsável Técnico**: Mecânico que vai fazer

4. Clique em **"Salvar"**

✅ **OS Criada!** O sistema gera automaticamente um número (ex: 2025-000001)

---

## 4️⃣ ADICIONAR SERVIÇOS E PEÇAS NA OS

**Quando usar?** Depois de diagnosticar o problema e decidir o que vai fazer.

### Como fazer:

1. Abra a Ordem de Serviço criada
2. Clique em **"Adicionar Item/Serviço"**

### **OPÇÃO A: Adicionar SERVIÇO (mão de obra)**
- **Tipo**: Serviço
- **Descrição**: Ex: "Troca de óleo e filtro"
- **Quantidade**: 1
- **Valor Unitário**: R$ 80,00
- Clique em **"Adicionar"**

### **OPÇÃO B: Adicionar PEÇA do estoque**
- **Tipo**: Peça
- **Selecionar Peça**: Escolha da lista (ex: "Óleo 15W40")
- **Quantidade**: 4 (litros)
- **Valor Unitário**: Já vem preenchido automaticamente
- **Dar baixa no estoque**: ✅ (deixe marcado)
- Clique em **"Adicionar"**

### **OPÇÃO C: Adicionar serviço TERCEIRIZADO**
- **Tipo**: Terceiro
- **Descrição**: Ex: "Funilaria - Serviço externo"
- **Quantidade**: 1
- **Valor Unitário**: R$ 500,00
- Clique em **"Adicionar"**

3. **VALORES AUTOMÁTICOS:**
   - O sistema soma automaticamente:
     - Valor de Mão de Obra (serviços)
     - Valor de Peças
     - Valor de Terceiros
   - Você pode adicionar **DESCONTO** se negociar com o cliente
   - **TOTAL** é calculado automaticamente

✅ **Itens adicionados!** O orçamento está pronto.

---

## 5️⃣ CONTROLAR STATUS DA OS

**O QUE É STATUS?** É a etapa em que a OS está. Use para acompanhar o progresso.

### **FLUXO NORMAL:**

```
1. ABERTA          → OS criada, ainda não orçada
      ↓
2. ORÇAMENTO       → Orçamento pronto, aguardando aprovação do cliente
      ↓
3. APROVADA        → Cliente aprovou, pode começar a trabalhar
      ↓
4. EM ANDAMENTO    → Mecânico está trabalhando no veículo
      ↓
5. AGUARDANDO PEÇA → Esperando peça chegar (se necessário)
      ↓
6. CONCLUÍDA       → Serviço terminado, aguardando cliente buscar
      ↓
7. ENTREGUE        → Cliente pegou o veículo e pagou
```

### Como mudar o status:

1. Abra a Ordem de Serviço
2. Clique em **"Mudar Status"**
3. Selecione o novo status
4. Adicione uma observação (opcional)
5. Clique em **"Salvar"**

**💡 Dica:** O sistema registra automaticamente:
- Data e hora de cada mudança
- Quem mudou o status
- Todo o histórico fica salvo!

---

## 6️⃣ FINALIZAR E ENTREGAR A OS

**Quando usar?** Quando o cliente vem buscar o veículo.

### Como fazer:

1. Abra a Ordem de Serviço
2. Verifique se está tudo certo:
   - ✅ Todos os serviços feitos
   - ✅ Todas as peças adicionadas
   - ✅ Valores corretos
3. Mude o status para **"CONCLUÍDA"**
4. Quando o cliente chegar:
   - Mostre a OS para ele
   - Receba o pagamento
   - Mude o status para **"ENTREGUE"**

✅ **OS Finalizada!** Entra no faturamento.

**💡 Dica:** Só OS com status **"ENTREGUE"** contam no faturamento!

---

## 7️⃣ CRIAR AGENDAMENTO

**Quando usar?** Cliente liga para marcar um serviço futuro.

### Como fazer:

1. No menu lateral, clique em **"Agendamentos"**
2. Clique em **"+ Novo Agendamento"**
3. Preencha:
   - **Cliente**: Selecione o cliente
   - **Veículo**: Selecione o veículo (opcional)
   - **Data e Hora**: Quando ele vai vir
   - **Serviço Solicitado**: O que ele quer fazer
     - Ex: "Revisão dos 10.000 km"
   - **Observações**: Anotações importantes
4. Clique em **"Salvar"**

### No dia do agendamento:

1. Vá em **"Agendamentos"**
2. Encontre o agendamento
3. Clique em **"Transformar em OS"**
4. Pronto! O sistema cria automaticamente uma OS com os dados

✅ **Agendamento controlado!**

**💡 Dica:** Marque "Confirmado" quando o cliente confirmar a presença por telefone.

---

## 8️⃣ CONTROLAR ESTOQUE DE PEÇAS

### **CADASTRAR CATEGORIA (primeiro passo)**

1. Clique em **"Categorias"**
2. Clique em **"+ Nova Categoria"**
3. Digite o nome (ex: "Óleos e Lubrificantes", "Filtros", "Freios")
4. Salve

### **CADASTRAR FORNECEDOR**

1. Clique em **"Fornecedores"**
2. Clique em **"+ Novo Fornecedor"**
3. Preencha os dados da empresa fornecedora
4. Salve

### **CADASTRAR PEÇA**

1. Clique em **"Peças"**
2. Clique em **"+ Nova Peça"**
3. Preencha:
   - **Código**: Código interno (ex: "OL-001")
   - **Nome**: Nome da peça (ex: "Óleo Lubrax 15W40")
   - **Categoria**: Selecione (ex: "Óleos")
   - **Fornecedor**: Selecione
   - **Quantidade em Estoque**: 20
   - **Estoque Mínimo**: 5 (sistema avisa quando ficar baixo)
   - **Unidade de Medida**: UN, L, KG, etc.
   - **Preço de Custo**: R$ 25,00 (quanto você paga)
   - **Preço de Venda**: R$ 40,00 (quanto você cobra)
   - **Localização**: "Prateleira A1" (onde está guardada)
4. Salve

✅ **Peça cadastrada!** O sistema calcula automaticamente a margem de lucro.

### **DAR ENTRADA NO ESTOQUE**

Quando você compra mais peças:

1. Vá na peça
2. Clique em **"Entrada de Estoque"**
3. Preencha:
   - **Quantidade**: Quanto chegou
   - **Valor Unitário**: Preço que pagou
   - **Nota Fiscal**: Número da NF
   - **Motivo**: "Compra de fornecedor"
4. Salve

✅ O sistema atualiza o estoque automaticamente!

### **ALERTAS AUTOMÁTICOS:**

🟡 **Estoque Baixo**: Quando chega no estoque mínimo
🔴 **Estoque Crítico**: Quando está com 50% do estoque mínimo

---

## 9️⃣ CONSULTAR RELATÓRIOS

**Quando usar?** Para ver o desempenho da oficina.

### Como fazer:

1. Clique em **"Relatórios"**
2. Selecione o período (últimos 7 dias, 30 dias, etc.)
3. Veja os dados:

### **DASHBOARD:**
- 📊 Total de OS abertas
- 💰 Faturamento do mês
- 🚗 Veículos atendidos
- ⏰ OS atrasadas
- 📈 Gráfico de faturamento
- 🏆 Peças mais vendidas
- ⭐ Melhores clientes

### **RELATÓRIO DE OS:**
- Lista todas as OS do período
- Filtre por status, cliente, etc.
- Exporte para impressão

### **RELATÓRIO DE ESTOQUE:**
- Peças em estoque baixo
- Valor total do estoque
- Movimentações recentes

---

## 🔍 DICAS E MACETES

### ✅ **BOAS PRÁTICAS:**

1. **Sempre atualize o status da OS**
   - Assim você sabe em que ponto está cada serviço

2. **Registre TUDO na OS**
   - Peças usadas, serviços feitos, observações
   - Isso ajuda no histórico do veículo

3. **Mantenha o estoque atualizado**
   - Sempre dê baixa quando usar uma peça
   - Faça entrada quando comprar

4. **Use as observações**
   - Anote problemas recorrentes
   - Anote acordos com o cliente
   - Anote defeitos que não foram arrumados

5. **Configure o estoque mínimo**
   - Assim você não fica sem peças importantes

6. **Agende clientes recorrentes**
   - Revisões periódicas podem ser agendadas

### ⚠️ **O QUE NÃO FAZER:**

❌ **NÃO delete clientes ou veículos** - Desative em vez de deletar
❌ **NÃO esqueça de dar baixa no estoque** - Senão fica errado
❌ **NÃO deixe OS sem status** - Sempre atualize
❌ **NÃO use a mesma placa para veículos diferentes**

---

## 📱 USANDO NO CELULAR

### **Menu Inferior:**

No celular, o menu fica na parte de baixo da tela com 5 botões principais:

```
[Dashboard] [Clientes] [Peças] [Ordens] [Agenda]
```

### **Ações Rápidas:**

- **Puxar para baixo** no topo = Recarrega a página
- **Rolar tabelas** = Deslize o dedo para os lados
- **Voltar** = Use a seta ← no topo

### **Instalando como App:**

1. Acesse o site no celular
2. Clique no botão azul **"Instalar App"**
3. Confirme
4. Pronto! Agora tem ícone na tela inicial

✅ **Funciona offline** para consultar dados já carregados!

---

## 🆘 RESOLUÇÃO DE PROBLEMAS

### **"O site está lento"**
- O Render hiberna após 15 min sem uso
- Primeira visita demora 30-60 segundos (normal)
- Depois fica rápido

### **"Esqueci minha senha"**
- Entre em contato com o administrador do sistema
- Ele pode redefinir no painel admin

### **"Não consigo adicionar peças na OS"**
- Verifique se a peça está cadastrada
- Verifique se tem quantidade em estoque
- Verifique se a peça está marcada como "Ativa"

### **"O estoque ficou negativo"**
- Vá na peça
- Clique em "Ajustar Estoque"
- Corrija a quantidade manualmente
- Anote o motivo

### **"Quero cancelar uma OS"**
- Abra a OS
- Mude o status para "CANCELADA"
- Explique o motivo nas observações
- OS canceladas não entram no faturamento

---

## 📞 SUPORTE

Dúvidas? Problemas? Entre em contato:

- **Email**: seu-email-suporte@email.com
- **WhatsApp**: (11) 99999-9999

---

## 🎓 TREINAMENTO RÁPIDO

### **Para o recepcionista:**
1. Cadastrar clientes e veículos
2. Criar agendamentos
3. Abrir Ordens de Serviço

### **Para o mecânico:**
1. Ver ordens de serviço atribuídas a ele
2. Atualizar status da OS
3. Adicionar observações técnicas
4. Dar baixa nas peças usadas

### **Para o gerente:**
1. Tudo que os outros fazem +
2. Aprovar orçamentos
3. Dar descontos
4. Ver relatórios e faturamento
5. Gerenciar estoque e compras

---

## ✨ VANTAGENS DO SISTEMA

✅ **Organização Total**
- Tudo em um só lugar
- Nada se perde
- Histórico completo de cada veículo

✅ **Controle Financeiro**
- Sabe quanto fatura
- Controla custos
- Vê a margem de lucro

✅ **Profissionalismo**
- Cliente vê que você é organizado
- Orçamentos impressos
- Histórico de serviços

✅ **Economia de Tempo**
- Menos papel
- Menos retrabalho
- Busca rápida de clientes

✅ **Controle de Estoque**
- Nunca fica sem peças
- Sabe o que tem
- Evita perdas

---

## 🚀 COMEÇANDO HOJE!

### **Checklist do Primeiro Dia:**

- [ ] Acessar o sistema e fazer login
- [ ] Cadastrar 3 clientes existentes
- [ ] Cadastrar os veículos desses clientes
- [ ] Cadastrar 5 peças principais do estoque
- [ ] Criar 1 ordem de serviço de teste
- [ ] Adicionar itens na OS
- [ ] Finalizar a OS
- [ ] Ver o relatório

✅ **Depois desse treino, você já sabe usar!**

---

**GarageRoute66** - Gestão Profissional para Oficinas Mecânicas
Versão 2.0.0 - 2025
