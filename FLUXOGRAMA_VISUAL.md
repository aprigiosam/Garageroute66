# 🔄 FLUXOGRAMA VISUAL - GarageRoute66

---

## 📊 VISÃO GERAL DO SISTEMA

```
┌─────────────────────────────────────────────────────────────┐
│                    GARAGEROUTE66                            │
│                 Sistema de Gestão Completo                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   CADASTROS   │   │   OPERAÇÕES   │   │   CONTROLE    │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • Clientes    │   │ • Ordens de   │   │ • Estoque     │
│ • Veículos    │   │   Serviço     │   │ • Relatórios  │
│ • Peças       │   │ • Agendamentos│   │ • Dashboard   │
│ • Fornecedores│   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## 🎯 FLUXO PRINCIPAL: ATENDIMENTO AO CLIENTE

### **CENÁRIO 1: Cliente Novo**

```
🚗 Cliente chega na oficina
        │
        ▼
┌─────────────────────┐
│ 1. CADASTRAR CLIENTE│
│    • Nome           │
│    • CPF            │
│    • Telefone       │
│    • Endereço       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. CADASTRAR VEÍCULO│
│    • Placa          │
│    • Marca/Modelo   │
│    • Ano            │
│    • Chassi         │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. CRIAR OS         │
│    • Problema       │
│    • Prioridade     │
│    • Prazo          │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. DIAGNOSTICAR     │
│    (Mecânico avalia)│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 5. FAZER ORÇAMENTO  │
│    • Peças          │
│    • Mão de obra    │
│    • Terceiros      │
└─────────┬───────────┘
          │
          ▼
    Cliente aprova?
          │
    ┌─────┴─────┐
    │           │
   SIM         NÃO
    │           │
    ▼           ▼
┌─────────┐  ┌─────────┐
│APROVADA │  │CANCELADA│
└────┬────┘  └─────────┘
     │
     ▼
┌─────────────────────┐
│ 6. EXECUTAR SERVIÇO │
│    Status:          │
│    EM ANDAMENTO     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 7. CONCLUIR         │
│    Status:          │
│    CONCLUÍDA        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 8. ENTREGAR         │
│    • Receber $$$    │
│    • Status: ENTREGUE│
└─────────────────────┘
          │
          ▼
    ✅ FINALIZADO!
    (Entra no faturamento)
```

---

### **CENÁRIO 2: Cliente Já Cadastrado**

```
🚗 Cliente retorna
        │
        ▼
┌─────────────────────┐
│ 1. BUSCAR CLIENTE   │
│    (pelo nome/CPF)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. SELECIONAR VEÍCULO│
│    (da lista dele)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. CRIAR NOVA OS    │
│    (continua igual) │
└─────────────────────┘
```

---

### **CENÁRIO 3: Agendamento por Telefone**

```
📞 Cliente liga
        │
        ▼
┌─────────────────────┐
│ 1. BUSCAR CLIENTE   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. CRIAR AGENDAMENTO│
│    • Data/Hora      │
│    • Serviço        │
└─────────┬───────────┘
          │
          ▼
    ⏰ Aguardando...
          │
          ▼
┌─────────────────────┐
│ NO DIA DO AGENDAMENTO│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Cliente compareceu? │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
   SIM         NÃO
    │           │
    ▼           ▼
┌─────────┐  ┌─────────┐
│TRANSFORMAR│ │REMARCAR │
│EM OS    │  │ou       │
│         │  │CANCELAR │
└─────────┘  └─────────┘
```

---

## 📦 FLUXO DE ESTOQUE

### **Cadastro de Peça**

```
📋 Precisa cadastrar peça nova
        │
        ▼
┌─────────────────────┐
│ 1. TEM CATEGORIA?   │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
   NÃO         SIM
    │           │
    ▼           │
┌─────────┐     │
│ CRIAR   │     │
│CATEGORIA│     │
└────┬────┘     │
     │          │
     └────┬─────┘
          │
          ▼
┌─────────────────────┐
│ 2. TEM FORNECEDOR?  │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
   NÃO         SIM
    │           │
    ▼           │
┌──────────┐    │
│  CRIAR   │    │
│FORNECEDOR│    │
└─────┬────┘    │
      │         │
      └────┬────┘
           │
           ▼
┌─────────────────────┐
│ 3. CADASTRAR PEÇA   │
│    • Código         │
│    • Nome           │
│    • Categoria      │
│    • Fornecedor     │
│    • Preços         │
│    • Estoque        │
└─────────────────────┘
           │
           ▼
     ✅ CADASTRADO!
```

---

### **Movimentação de Estoque**

```
┌─────────────────────┐
│   MOVIMENTAÇÕES     │
└─────────┬───────────┘
          │
    ┌─────┴─────────────────┐
    │                       │
    ▼                       ▼
┌─────────┐         ┌─────────────┐
│ENTRADA  │         │   SAÍDA     │
│• Compra │         │ • Uso em OS │
│• Devolução│       │ • Perda     │
└────┬────┘         └──────┬──────┘
     │                     │
     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐
│ Estoque AUMENTA │  │ Estoque DIMINUI │
└─────────────────┘  └─────────────────┘
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Sistema atualiza     │
        │  automaticamente      │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Estoque < Mínimo?     │
        └───────────┬───────────┘
                    │
              ┌─────┴─────┐
              │           │
             SIM         NÃO
              │           │
              ▼           ▼
        🔴 ALERTA!    ✅ OK
        Comprar!
```

---

## 💰 FLUXO FINANCEIRO DA OS

```
┌─────────────────────────────────────────────┐
│              ORDEM DE SERVIÇO               │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  MÃO DE │+│ PEÇAS   │+│TERCEIROS│
│  OBRA   │ │         │ │         │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └─────┬─────┴─────┬─────┘
           │           │
           ▼           ▼
      ┌────────┐  ┌─────────┐
      │SUBTOTAL│- │DESCONTO │
      └───┬────┘  └────┬────┘
          │            │
          └──────┬─────┘
                 │
                 ▼
        ┌────────────────┐
        │  TOTAL FINAL   │
        └────────────────┘
                 │
                 ▼
        Status = ENTREGUE?
                 │
           ┌─────┴─────┐
           │           │
          SIM         NÃO
           │           │
           ▼           ▼
    ┌──────────┐  ┌──────────┐
    │ ENTRA NO │  │NÃO ENTRA │
    │FATURAMENTO│  │FATURAMENTO│
    └──────────┘  └──────────┘
```

---

## 📊 ESTADOS DE UMA OS

```
     ABERTA
       │ (OS criada)
       ▼
    ORÇAMENTO
       │ (Valores definidos)
       ▼
    APROVADA
       │ (Cliente OK)
       ▼
  EM ANDAMENTO
       │ (Mecânico trabalhando)
       ▼
AGUARDANDO PEÇA? ──[NÃO]──┐
       │                   │
      [SIM]                │
       │                   │
       ▼                   │
  AGUARDANDO PEÇA         │
       │                   │
   (Peça chegou?)         │
       │                   │
       └───────┬───────────┘
               │
               ▼
          CONCLUÍDA
               │ (Serviço pronto)
               ▼
           ENTREGUE
               │ (Cliente pegou)
               ▼
          💰 PAGO!

[Qualquer momento]
       │
       ▼
    CANCELADA
       │
       ▼
  Não fatura
```

---

## 🎯 INDICADORES DO DASHBOARD

```
┌────────────────────────────────────────────┐
│           DASHBOARD PRINCIPAL              │
├────────────────────────────────────────────┤
│                                            │
│  📊 OS ABERTAS         ┌─────────┐        │
│     Status atual       │   15    │        │
│                        └─────────┘        │
│                                            │
│  💰 FATURAMENTO MÊS    ┌─────────┐        │
│     Só OS ENTREGUE     │ R$ 45k  │        │
│                        └─────────┘        │
│                                            │
│  🚗 VEÍCULOS ATENDIDOS ┌─────────┐        │
│     Únicos no mês      │   78    │        │
│                        └─────────┘        │
│                                            │
│  ⏰ OS ATRASADAS       ┌─────────┐        │
│     Prazo vencido      │   3     │        │
│                        └─────────┘        │
│                                            │
│  📈 GRÁFICO MENSAL                        │
│     ┌──┐                                  │
│     │██│  ┌──┐  ┌──┐                     │
│     │██│  │██│  │██│  ┌──┐              │
│  ┌──┤██├──┤██├──┤██├──┤██│              │
│  └──┴──┴──┴──┴──┴──┴──┴──┘              │
│    Jan  Fev  Mar  Abr                     │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🔍 BUSCA E FILTROS

### **Buscar Cliente**

```
Digite: "João"
    │
    ▼
Sistema busca por:
    • Nome
    • CPF
    • Telefone
    • Email
    │
    ▼
Resultados encontrados
    │
    ▼
Clique no cliente
    │
    ▼
Ver detalhes:
    • Dados cadastrais
    • Veículos
    • Histórico de OS
    • Total gasto
```

---

### **Filtrar OS**

```
Filtros disponíveis:
    │
    ├─ Por Status
    │  • Abertas
    │  • Em Andamento
    │  • Concluídas
    │  • etc.
    │
    ├─ Por Cliente
    │  • Selecione da lista
    │
    ├─ Por Período
    │  • Hoje
    │  • Últimos 7 dias
    │  • Último mês
    │  • Personalizado
    │
    ├─ Por Prioridade
    │  • Urgente
    │  • Alta
    │  • Normal
    │  • Baixa
    │
    └─ Por Responsável
       • Mecânico específico
```

---

## 🎨 LEGENDA DE CORES

```
🟢 Verde     → Tudo OK / Concluído / Ativo
🟡 Amarelo   → Atenção / Aguardando / Baixo
🟠 Laranja   → Importante / Alta Prioridade
🔴 Vermelho  → Urgente / Crítico / Atrasado
🔵 Azul      → Em Andamento / Normal
⚪ Cinza     → Cancelado / Inativo
```

---

## 📱 NAVEGAÇÃO MOBILE vs DESKTOP

### **DESKTOP (Tela grande)**

```
┌──────────────────────────────────────┐
│  [Logo] GarageRoute66        [User] │
├────────┬─────────────────────────────┤
│        │                             │
│ MENU   │      CONTEÚDO PRINCIPAL    │
│ LATERAL│                             │
│        │                             │
│ • Home │                             │
│ • Clientes                           │
│ • Veículos                           │
│ • OS   │                             │
│ • Peças│                             │
│ • Etc. │                             │
│        │                             │
└────────┴─────────────────────────────┘
```

### **MOBILE (Celular)**

```
┌──────────────────────────┐
│  [≡] GarageRoute66  [⚙] │
├──────────────────────────┤
│                          │
│                          │
│   CONTEÚDO PRINCIPAL     │
│   (Tela cheia)           │
│                          │
│                          │
│                          │
├──────────────────────────┤
│  [🏠] [👥] [🔧] [📋] [📅] │
│  Home Cli  Peças OS  Agenda│
└──────────────────────────┘
           ↑
    MENU NA PARTE DE BAIXO
```

---

## 🔔 ALERTAS AUTOMÁTICOS

```
Sistema monitora:

┌─────────────────────┐
│ ESTOQUE BAIXO       │
│ Peça X: 2 unidades  │
│ Mínimo: 5           │
│ 🔴 COMPRAR!         │
└─────────────────────┘

┌─────────────────────┐
│ OS ATRASADA         │
│ OS #2025-000123     │
│ Prazo: Ontem        │
│ ⏰ URGENTE!         │
└─────────────────────┘

┌─────────────────────┐
│ AGENDAMENTO HOJE    │
│ João Silva - 14h    │
│ Revisão             │
│ 📅 LEMBRETE         │
└─────────────────────┘
```

---

## ✅ CHECKLIST DIÁRIO

```
TODO INÍCIO DO DIA:
  [ ] Verificar OS abertas
  [ ] Ver agendamentos do dia
  [ ] Conferir OS atrasadas
  [ ] Checar estoque baixo

TODO FIM DO DIA:
  [ ] Atualizar status das OS
  [ ] Confirmar agendamentos de amanhã
  [ ] Verificar faturamento do dia
  [ ] Fazer backup (automático)
```

---

**🎓 DICA FINAL:**

```
┌──────────────────────────────────────────┐
│                                          │
│  "Use o sistema TODOS OS DIAS!"         │
│                                          │
│  Quanto mais você usa:                   │
│  ✅ Mais organizado fica                 │
│  ✅ Mais rápido você trabalha            │
│  ✅ Mais profissional você fica          │
│  ✅ Mais controle você tem               │
│                                          │
│  Em 1 semana você está EXPERT!          │
│                                          │
└──────────────────────────────────────────┘
```

---

**GarageRoute66** - Sistema Visual e Intuitivo
Versão 2.0.0 - 2025
