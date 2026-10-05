# 📐 Dicionário de Medidas DAX — Grão Nobre Analytics

> Todas as medidas devem ser criadas dentro de uma tabela dedicada chamada `_Medidas` no Power BI.
> 
> **Como criar a tabela `_Medidas` no Power BI:**
> 1. Na aba **Página Inicial** > clique em **Inserir Dados**.
> 2. Dê o nome da tabela de `_Medidas` e clique em **Carregar**.
> 3. Crie as medidas abaixo dentro dela.

---

## 1. 💰 Vendas e Financeiro

### `Vendas | Receita Bruta`
```dax
Vendas | Receita Bruta = SUM(fato_vendas[valor_bruto])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Soma do valor faturado antes da dedução de descontos.

### `Vendas | Total Descontos`
```dax
Vendas | Total Descontos = SUM(fato_vendas[valor_desconto])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Total de descontos e cupons concedidos nas vendas.

### `Vendas | Receita Líquida`
```dax
Vendas | Receita Líquida = SUM(fato_vendas[valor_liquido])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Faturamento real após abatimento de descontos (`valor_bruto - valor_desconto`).

### `Vendas | Custo Total (CPV)`
```dax
Vendas | Custo Total = SUM(fato_vendas[custo_total])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Custo dos Produtos Vendidos (quantidade × custo unitário do café/acessório).

### `Vendas | Lucro Bruto`
```dax
Vendas | Lucro Bruto = SUM(fato_vendas[lucro_bruto])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Receita Líquida deduzido o Custo Total dos produtos.

### `Vendas | Margem Bruta %`
```dax
Vendas | Margem Bruta % = 
DIVIDE(
    [Vendas | Lucro Bruto],
    [Vendas | Receita Líquida],
    0
)
```
* **Formato:** Porcentagem (0,0%)
* **Descrição:** Percentual de rentabilidade sobre a receita líquida. Meta da Grão Nobre: ≥ 55%.

### `Vendas | Qtd Pedidos`
```dax
Vendas | Qtd Pedidos = DISTINCTCOUNT(fato_vendas[pedido_id])
```
* **Formato:** Número Inteiro
* **Descrição:** Volume único de transações/pedidos efetuados.

### `Vendas | Qtd Itens Vendidos`
```dax
Vendas | Qtd Itens Vendidos = SUM(fato_vendas[quantidade])
```
* **Formato:** Número Inteiro
* **Descrição:** Total de pacotes de café ou produtos comercializados.

### `Vendas | Ticket Médio`
```dax
Vendas | Ticket Médio = 
DIVIDE(
    [Vendas | Receita Líquida],
    [Vendas | Qtd Pedidos],
    0
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Gasto médio por transação de cliente.

### `Vendas | Frete Total`
```dax
Vendas | Frete Total = SUM(fato_vendas[frete])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Valor total arrecadado com taxas de envio no e-commerce.

---

## 2. 📢 Marketing e Performance

### `Mkt | Investimento Total`
```dax
Mkt | Investimento Total = SUM(fato_marketing[investimento_reais])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Verba total investida em canais de mídia paga e campanhas.

### `Mkt | Impressões`
```dax
Mkt | Impressões = SUM(fato_marketing[impressoes])
```
* **Formato:** Número Inteiro

### `Mkt | Cliques`
```dax
Mkt | Cliques = SUM(fato_marketing[cliques])
```
* **Formato:** Número Inteiro

### `Mkt | CTR %`
```dax
Mkt | CTR % = 
DIVIDE(
    [Mkt | Cliques],
    [Mkt | Impressões],
    0
)
```
* **Formato:** Porcentagem (0,00%)
* **Descrição:** Click-Through Rate. Eficiência de atratividade dos anúncios.

### `Mkt | CPC Médio`
```dax
Mkt | CPC Médio = 
DIVIDE(
    [Mkt | Investimento Total],
    [Mkt | Cliques],
    0
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Custo Médio por Clique.

### `Mkt | Conversões`
```dax
Mkt | Conversões = SUM(fato_marketing[conversoes])
```
* **Formato:** Número Inteiro
* **Descrição:** Número de aquisições de vendas originadas pelos canais de marketing.

### `Mkt | CPA`
```dax
Mkt | CPA = 
DIVIDE(
    [Mkt | Investimento Total],
    [Mkt | Conversões],
    0
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Custo por Aquisição / Conversão.

### `Mkt | Receita Atribuída`
```dax
Mkt | Receita Atribuída = SUM(fato_marketing[receita_atribuida])
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Receita gerada rastreada diretamente pelas campanhas.

### `Mkt | ROAS`
```dax
Mkt | ROAS = 
DIVIDE(
    [Mkt | Receita Atribuída],
    [Mkt | Investimento Total],
    0
)
```
* **Formato:** Decimal (0,00x)
* **Descrição:** Return on Ad Spend (Retorno sobre Gasto em Anúncios). Meta: ≥ 4.0x.

### `Mkt | Taxa de Conversão %`
```dax
Mkt | Taxa de Conversão % = 
DIVIDE(
    [Mkt | Conversões],
    [Mkt | Cliques],
    0
)
```
* **Formato:** Porcentagem (0,00%)

---

## 3. 👥 Clientes, LTV e Churn

### `Clientes | Total Base`
```dax
Clientes | Total Base = COUNTROWS(dim_clientes)
```
* **Formato:** Número Inteiro
* **Descrição:** Número total de clientes únicos cadastrados no CRM da Grão Nobre.

### `Clientes | Ativos`
```dax
Clientes | Ativos = 
CALCULATE(
    [Clientes | Total Base],
    dim_clientes[status_churn] = "Ativo"
)
```
* **Formato:** Número Inteiro

### `Clientes | Em Risco`
```dax
Clientes | Em Risco = 
CALCULATE(
    [Clientes | Total Base],
    dim_clientes[status_churn] = "Em risco"
)
```
* **Formato:** Número Inteiro

### `Clientes | Churned`
```dax
Clientes | Churned = 
CALCULATE(
    [Clientes | Total Base],
    dim_clientes[status_churn] = "Churned"
)
```
* **Formato:** Número Inteiro

### `Clientes | Taxa de Churn %`
```dax
Clientes | Taxa de Churn % = 
DIVIDE(
    [Clientes | Churned],
    [Clientes | Total Base],
    0
)
```
* **Formato:** Porcentagem (0,0%)

### `Clientes | CAC Médio`
```dax
Clientes | CAC Médio = 
DIVIDE(
    [Mkt | Investimento Total],
    [Clientes | Total Base],
    0
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Custo de Aquisição por Cliente da base.

### `Clientes | LTV Médio`
```dax
Clientes | LTV Médio = 
DIVIDE(
    [Vendas | Receita Líquida],
    [Clientes | Total Base],
    0
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Lifetime Value médio histórico por cliente.

### `Clientes | LTV / CAC Ratio`
```dax
Clientes | LTV / CAC Ratio = 
DIVIDE(
    [Clientes | LTV Médio],
    [Clientes | CAC Médio],
    0
)
```
* **Formato:** Decimal (0,00x)
* **Descrição:** Relação LTV/CAC. Meta saudável de SaaS/e-commerce: > 3.0x.

---

## 4. 🎧 Atendimento e Logística

### `Atd | Total Ocorrências`
```dax
Atd | Total Ocorrências = COUNTROWS(fato_atendimento)
```
* **Formato:** Número Inteiro

### `Atd | Tempo Médio Resposta (min)`
```dax
Atd | Tempo Médio Resposta (min) = AVERAGE(fato_atendimento[tempo_resposta_min])
```
* **Formato:** Decimal (0,0 min)

### `Atd | Tempo Médio Resolução (min)`
```dax
Atd | Tempo Médio Resolução (min) = AVERAGE(fato_atendimento[tempo_resolucao_min])
```
* **Formato:** Decimal (0,0 min)

### `Atd | NPS Médio`
```dax
Atd | NPS Médio = AVERAGE(fato_atendimento[nota_nps])
```
* **Formato:** Decimal (0,0)
* **Descrição:** Média de satisfação nas avaliações pós-atendimento.
