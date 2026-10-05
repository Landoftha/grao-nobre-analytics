# 📘 Regras de Negócio — Grão Nobre

> Este documento define TODAS as regras de negócio da empresa fictícia Grão Nobre.
> É a fonte de verdade para dashboards, modelos e pipelines.

---

## 1. Visão Geral da Empresa

### 1.1 Identidade
| Atributo | Valor |
|----------|-------|
| **Nome** | Grão Nobre Cafés Especiais |
| **CNPJ (fictício)** | 45.123.789/0001-00 |
| **Fundação** | Janeiro de 2025 |
| **Sede** | Curitiba, PR |
| **Setor** | Varejo de Cafés Especiais |
| **Canais de venda** | E-commerce + 3 Lojas Físicas |
| **Público-alvo** | Classes A e B, 25-55 anos, apreciadores de café |

### 1.2 Missão
Democratizar o acesso a cafés especiais de alta qualidade, conectando produtores brasileiros a consumidores exigentes por meio de experiência premium no digital e no presencial.

### 1.3 Unidades de Negócio

| Loja ID | Nome | Cidade | Estado | Abertura | Capacidade |
|---------|------|--------|--------|----------|------------|
| LOJ01 | Grão Nobre — Batel | Curitiba | PR | 2025-01-15 | 40 lugares |
| LOJ02 | Grão Nobre — Vila Madalena | São Paulo | SP | 2025-06-01 | 55 lugares |
| LOJ03 | Grão Nobre — Centro | Florianópolis | SC | 2025-09-15 | 35 lugares |
| WEB01 | E-commerce | Nacional | BR | 2025-01-15 | — |

---

## 2. Regras de Produtos

### 2.1 Categorias de Produto

| Categoria | Descrição | Margem Alvo |
|-----------|-----------|-------------|
| **Café em Grãos** | Cafés especiais em grãos, torrados | 55-60% |
| **Café Moído** | Cafés moídos sob demanda | 50-55% |
| **Cápsulas** | Cápsulas compatíveis com Nespresso | 60-65% |
| **Equipamentos** | Moedores, cafeteiras, acessórios | 35-45% |
| **Kits Especiais** | Combos e presentes | 50-55% |
| **Assinatura** | Planos mensais de café | 45-50% |
| **Bebidas (loja)** | Espresso, cappuccino, etc. | 70-80% |
| **Alimentos (loja)** | Pães, bolos, salgados | 60-70% |

### 2.2 Regras de Precificação

```
preco_venda = custo_unitario / (1 - margem_desejada)
preco_com_desconto = preco_venda * (1 - percentual_desconto)
```

- **Desconto máximo permitido:** 25%
- **Desconto progressivo:**
  - 2-4 unidades: 5%
  - 5-9 unidades: 10%
  - 10+ unidades: 15%
- **Frete grátis:** pedidos acima de R$ 150,00
- **Frete fixo:** R$ 15,90 (Sul/Sudeste), R$ 22,90 (demais regiões)

### 2.3 Regras de Estoque

- **Estoque mínimo:** 20 unidades por SKU
- **Ponto de reposição:** quando estoque ≤ 30% da capacidade
- **Validade café torrado:** 6 meses após torra
- **FIFO obrigatório** (primeiro a entrar, primeiro a sair)
- **Ruptura (stockout):** gera alerta automático quando estoque = 0

---

## 3. Regras de Clientes

### 3.1 Segmentação por Faixa de Valor (LTV)

| Segmento | LTV Anual | Benefícios |
|----------|-----------|------------|
| **Bronze** | < R$ 500 | Programa de pontos básico |
| **Prata** | R$ 500 — R$ 1.500 | 5% desconto + frete grátis acima de R$ 100 |
| **Ouro** | R$ 1.500 — R$ 5.000 | 10% desconto + frete grátis + acesso antecipado |
| **Diamante** | > R$ 5.000 | 15% desconto + frete grátis + experiências exclusivas |

### 3.2 Análise RFM (Recency, Frequency, Monetary)

| Métrica | Cálculo | Score 5 | Score 1 |
|---------|---------|---------|---------|
| **Recency** | Dias desde última compra | ≤ 14 dias | > 180 dias |
| **Frequency** | Nº pedidos em 12 meses | ≥ 12 pedidos | 1 pedido |
| **Monetary** | Valor total em 12 meses | ≥ R$ 2.000 | < R$ 100 |

### 3.3 Regras de Churn

| Status | Definição |
|--------|-----------|
| **Ativo** | Comprou nos últimos 60 dias |
| **Em risco** | Última compra entre 61-120 dias |
| **Inativo** | Última compra entre 121-180 dias |
| **Churned** | Sem compra há mais de 180 dias |

### 3.4 Jornada do Cliente

```
Visitante → Lead → Primeira Compra → Cliente Recorrente → Fiel → Embaixador
```

| Etapa | Gatilho de transição |
|-------|---------------------|
| Visitante → Lead | Cadastro no site ou newsletter |
| Lead → Primeira Compra | Primeiro pedido concluído |
| Primeira Compra → Recorrente | 2ª compra em até 90 dias |
| Recorrente → Fiel | 6+ compras no ano |
| Fiel → Embaixador | Indicação que gera conversão |

---

## 4. Regras de Vendas

### 4.1 Funil de Vendas (E-commerce)

```
Sessões → Visualizações de Produto → Adicionou ao Carrinho → Iniciou Checkout → Pagamento → Pedido Concluído
```

| Métrica | Benchmark |
|---------|-----------|
| Taxa de conversão geral | 2.5 - 3.5% |
| Taxa de abandono de carrinho | 65 - 75% |
| Ticket médio e-commerce | R$ 120 - R$ 180 |
| Ticket médio loja física | R$ 35 - R$ 55 |

### 4.2 Status do Pedido

| Status | Descrição |
|--------|-----------|
| `pendente` | Pedido criado, aguardando pagamento |
| `pago` | Pagamento confirmado |
| `em_separacao` | Em processo de picking |
| `enviado` | Despachado para transportadora |
| `entregue` | Entrega confirmada |
| `cancelado` | Cancelado (pelo cliente ou estoque) |
| `devolvido` | Devolução processada |

### 4.3 Regras de Cancelamento e Devolução

- **Cancelamento grátis:** até 2h após o pedido
- **Devolução:** até 7 dias após recebimento (CDC)
- **Reembolso:** processado em até 10 dias úteis
- **Taxa de cancelamento aceitável:** < 8%
- **Taxa de devolução aceitável:** < 3%

### 4.4 Formas de Pagamento

| Meio | Taxa | Prazo de Recebimento |
|------|------|---------------------|
| PIX | 0.99% | D+0 |
| Cartão de Crédito | 3.49% | D+30 |
| Cartão de Débito | 1.99% | D+1 |
| Boleto | R$ 3,49 fixo | D+2 |

### 4.5 Sazonalidade

| Período | Impacto nas Vendas |
|---------|-------------------|
| **Janeiro** | -20% (pós-festas) |
| **Fevereiro** | -10% |
| **Março-Abril** | Baseline |
| **Maio** | +30% (Dia das Mães) |
| **Junho** | +50% (Dia dos Namorados + Inverno) |
| **Julho** | +40% (Inverno — pico de café) |
| **Agosto** | +25% (Dia dos Pais) |
| **Setembro** | Baseline |
| **Outubro** | +15% (Dia das Crianças — kits) |
| **Novembro** | +80% (Black Friday) |
| **Dezembro** | +60% (Natal — kits presentes) |

---

## 5. Regras de Marketing

### 5.1 Canais de Aquisição

| Canal | Budget Mensal | CPA Alvo | ROAS Alvo |
|-------|--------------|----------|-----------|
| **Google Ads (Search)** | R$ 6.000 | R$ 35 | 4.0x |
| **Google Ads (Shopping)** | R$ 4.000 | R$ 28 | 5.0x |
| **Meta Ads (Instagram)** | R$ 5.000 | R$ 40 | 3.5x |
| **Meta Ads (Facebook)** | R$ 3.000 | R$ 45 | 3.0x |
| **Email Marketing** | R$ 800 | R$ 8 | 10.0x |
| **Orgânico (SEO)** | R$ 2.000 | R$ 15 | 8.0x |
| **Influenciadores** | R$ 3.000 | R$ 50 | 3.0x |
| **Direto** | R$ 0 | R$ 0 | ∞ |

**Budget mensal total de marketing:** R$ 23.800

### 5.2 KPIs de Marketing

| KPI | Fórmula | Meta |
|-----|---------|------|
| **CAC** | Investimento Total / Novos Clientes | < R$ 45 |
| **ROAS** | Receita Atribuída / Investimento | > 4.0x |
| **CPC** | Investimento / Cliques | < R$ 1,50 |
| **CTR** | Cliques / Impressões × 100 | > 3.0% |
| **Taxa de Conversão** | Conversões / Cliques × 100 | > 2.5% |
| **CPM** | (Investimento / Impressões) × 1000 | < R$ 15 |
| **LTV:CAC** | LTV Médio / CAC | > 3:1 |

### 5.3 Modelo de Atribuição

**Modelo padrão:** Último clique (Last Click)

**Modelos para análise comparativa (Fase 2 — Data Science):**
- First Click
- Linear
- Time Decay
- Data-Driven (Markov Chain)

### 5.4 Regras de Campanha

| Tipo | Duração | Desconto Max | Canal Primário |
|------|---------|-------------|----------------|
| **Sazonal** | 7-15 dias | 25% | Multi-canal |
| **Flash Sale** | 24-48h | 30% | Email + Instagram |
| **Lançamento** | 30 dias | 10% | Google + Instagram |
| **Remarketing** | Contínuo | 15% | Google + Meta |
| **Fidelidade** | Contínuo | Variável | Email |

---

## 6. Regras de Atendimento

### 6.1 Canais de Atendimento

| Canal | SLA Resposta | Horário |
|-------|-------------|---------|
| **WhatsApp** | 15 min | 8h-20h |
| **Email** | 4h | 8h-18h |
| **Chat no site** | 2 min | 8h-22h |
| **Instagram DM** | 30 min | 8h-20h |
| **Telefone** | 1 min | 8h-18h |

### 6.2 Tipos de Ocorrência

| Tipo | Prioridade | SLA Resolução |
|------|-----------|--------------|
| Reclamação de qualidade | Alta | 24h |
| Atraso na entrega | Alta | 48h |
| Troca/Devolução | Média | 72h |
| Dúvida sobre produto | Baixa | 4h |
| Elogio/Sugestão | Baixa | 24h |

### 6.3 NPS (Net Promoter Score)

- **Promotor:** nota 9-10
- **Neutro:** nota 7-8
- **Detrator:** nota 0-6
- **Meta NPS:** ≥ 70

---

## 7. Métricas Financeiras

### 7.1 DRE Simplificada (Mensal)

```
(+) Receita Bruta
(-) Devoluções e Cancelamentos
(=) Receita Líquida
(-) CMV (Custo da Mercadoria Vendida)
(=) Lucro Bruto
(-) Despesas de Marketing
(-) Despesas Operacionais (pessoal, aluguel, etc.)
(-) Taxas de Pagamento
(=) EBITDA
(-) Depreciação
(=) Lucro Operacional
```

### 7.2 Metas Financeiras

| Métrica | Meta Mensal |
|---------|-------------|
| **Receita Bruta** | R$ 200.000 |
| **Margem Bruta** | ≥ 55% |
| **Margem EBITDA** | ≥ 20% |
| **Taxa de Inadimplência** | < 2% |
| **Custo de Marketing / Receita** | ≤ 12% |

---

## 8. Regras de Dados

### 8.1 Modelagem Dimensional (Star Schema)

```
                    ┌──────────────┐
                    │ dim_calendario│
                    └──────┬───────┘
                           │
┌────────────┐    ┌────────┴────────┐    ┌──────────────┐
│dim_clientes│────│  fato_vendas    │────│ dim_produtos  │
└────────────┘    └────────┬────────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  dim_lojas   │
                    └──────────────┘

┌───────────────────┐    ┌────────────────────┐
│ dim_canais_mktg   │────│  fato_marketing    │
└───────────────────┘    └────────────────────┘

                         ┌────────────────────┐
                         │  fato_atendimento  │
                         └────────────────────┘

                         ┌────────────────────┐
                         │  fato_estoque      │
                         └────────────────────┘
```

### 8.2 Grain (Granularidade)

| Tabela Fato | Grain |
|-------------|-------|
| `fato_vendas` | Uma linha por item de pedido |
| `fato_marketing` | Uma linha por canal por dia |
| `fato_atendimento` | Uma linha por ocorrência |
| `fato_estoque` | Uma linha por produto por dia (snapshot) |

### 8.3 Regras de Qualidade de Dados

- **Nenhum campo chave pode ser NULL** (PKs e FKs)
- **Datas futuras não são permitidas** em fatos
- **Valores monetários:** sempre 2 casas decimais
- **Percentuais:** 0.00 a 100.00
- **IDs seguem padrão:** CLI###, PRD##, PED####, CAM###, LOJ##
- **Encoding:** UTF-8
- **Separador CSV:** vírgula
- **Formato de data:** YYYY-MM-DD (ISO 8601)

---

## 9. Glossário

| Termo | Definição |
|-------|-----------|
| **CAC** | Custo de Aquisição de Cliente |
| **LTV** | Lifetime Value — valor total que um cliente gera |
| **ROAS** | Return on Ad Spend — retorno sobre investimento em ads |
| **CPC** | Custo por Clique |
| **CTR** | Click-Through Rate — taxa de cliques |
| **CPM** | Custo por Mil impressões |
| **NPS** | Net Promoter Score |
| **RFM** | Recency, Frequency, Monetary (segmentação) |
| **GMV** | Gross Merchandise Value — valor bruto de mercadorias |
| **AOV** | Average Order Value — ticket médio |
| **MoM** | Month over Month — comparação mês a mês |
| **YoY** | Year over Year — comparação ano a ano |
| **SKU** | Stock Keeping Unit — código do produto |
| **FIFO** | First In, First Out |
| **CMV** | Custo da Mercadoria Vendida |
| **EBITDA** | Lucro antes de juros, impostos, depreciação e amortização |

---

*Última atualização: 2026-10-02*
