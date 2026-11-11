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
Vendas | Receita Líquida = 
CALCULATE(
    SUM(fato_vendas[valor_liquido]),
    fato_vendas[status_pedido] = "entregue"
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Faturamento real após descontos, devoluções e cancelamentos. Considera apenas pedidos entregues, conforme a DRE em `docs/BUSINESS_RULES.md`.

### `Vendas | Custo Total (CPV)`
```dax
Vendas | Custo Total = 
CALCULATE(
    SUM(fato_vendas[custo_total]),
    fato_vendas[status_pedido] = "entregue"
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Custo dos Produtos Vendidos (quantidade × custo unitário do café/acessório) dos pedidos entregues.

### `Vendas | Lucro Bruto`
```dax
Vendas | Lucro Bruto = 
CALCULATE(
    SUM(fato_vendas[lucro_bruto]),
    fato_vendas[status_pedido] = "entregue"
)
```
* **Formato:** Moeda (R$ 0,00)
* **Descrição:** Receita Líquida deduzido o Custo Total dos produtos, considerando apenas pedidos entregues.

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
Vendas | Qtd Pedidos = 
CALCULATE(
    DISTINCTCOUNT(fato_vendas[pedido_id]),
    fato_vendas[status_pedido] = "entregue"
)
```
* **Formato:** Número Inteiro
* **Descrição:** Volume único de pedidos entregues.

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
* **Descrição:** Click-Through Rate. Eficiência de atratividade dos anúncios. Meta: > 3,0%.

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
* **Descrição:** Custo Médio por Clique. Meta: < R$ 1,50.

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

### `Mkt | Sessões Site`
```dax
Mkt | Sessões Site = SUM(fato_marketing[sessoes_site])
```
* **Formato:** Número Inteiro
* **Descrição:** Total de sessões iniciadas no e-commerce originadas pelos canais de marketing.

### `Mkt | Novos Leads`
```dax
Mkt | Novos Leads = SUM(fato_marketing[novos_leads])
```
* **Formato:** Número Inteiro
* **Descrição:** Total de novos leads captados nas campanhas e canais digitais.

### `Mkt | Bounce Rate Médio %`
```dax
Mkt | Bounce Rate Médio % = DIVIDE(AVERAGE(fato_marketing[bounce_rate]), 100, 0)
```
* **Formato:** Porcentagem (0,0%)
* **Descrição:** Taxa média de rejeição das páginas de destino.

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

### `Clientes | Inativos`
```dax
Clientes | Inativos = 
CALCULATE(
    [Clientes | Total Base],
    dim_clientes[status_churn] = "Inativo"
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
* **Descrição:** Custo de Aquisição por Cliente da base. Meta: < R$ 45,00.

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

### `Atd | NPS Score`
```dax
Atd | NPS Score = 
VAR TotalAvaliacoes = 
    CALCULATE(
        COUNTROWS(fato_atendimento),
        NOT(ISBLANK(fato_atendimento[nota_nps]))
    )
VAR Promotores = 
    CALCULATE(
        COUNTROWS(fato_atendimento),
        fato_atendimento[nota_nps] >= 9
    )
VAR Detratores = 
    CALCULATE(
        COUNTROWS(fato_atendimento),
        fato_atendimento[nota_nps] <= 6
    )
RETURN
    DIVIDE(Promotores - Detratores, TotalAvaliacoes, 0) * 100
```
* **Formato:** Número Decimal (0,0)
* **Descrição:** Net Promoter Score oficial (`% Promotores - % Detratores`). Meta da Grão Nobre: ≥ 70.

### `Atd | % Tickets Resolvidos`
```dax
Atd | % Tickets Resolvidos = 
VAR Resolvidos = 
    CALCULATE(
        [Atd | Total Ocorrências],
        fato_atendimento[status] = "Resolvido"
    )
RETURN
    DIVIDE(Resolvidos, [Atd | Total Ocorrências], 0)
```
* **Formato:** Porcentagem (0,0%)
* **Descrição:** Proporção de chamados já solucionados pela equipe de atendimento.

### `Atd | % Dentro do SLA`
```dax
Atd | % Dentro do SLA = 
VAR TicketsNoSLA = 
    COUNTROWS(
        FILTER(
            fato_atendimento,
            SWITCH(
                fato_atendimento[canal_atendimento],
                "Telefone", fato_atendimento[tempo_resposta_min] <= 1,
                "Chat no site", fato_atendimento[tempo_resposta_min] <= 2,
                "WhatsApp", fato_atendimento[tempo_resposta_min] <= 15,
                "Instagram DM", fato_atendimento[tempo_resposta_min] <= 30,
                "Email", fato_atendimento[tempo_resposta_min] <= 240,
                fato_atendimento[tempo_resposta_min] <= 30
            )
        )
    )
RETURN
    DIVIDE(TicketsNoSLA, [Atd | Total Ocorrências], 0)
```
* **Formato:** Porcentagem (0,0%)
* **Descrição:** Percentual de atendimentos cuja primeira resposta ocorreu dentro do SLA definido nas regras de negócio por canal.

---

## 5. 📦 Estoque e Operações

### `Est | Qtd em Estoque Atual`
```dax
Est | Qtd em Estoque Atual = 
VAR UltimaData = LASTDATE(fato_estoque[data])
RETURN
    CALCULATE(
        SUM(fato_estoque[qtd_estoque]),
        fato_estoque[data] = UltimaData
    )
```
* **Formato:** Número Inteiro
* **Descrição:** Saldo semi-aditivo de unidades em estoque na última data disponível no contexto de filtro.

### `Est | SKUs em Ruptura`
```dax
Est | SKUs em Ruptura = 
VAR UltimaData = LASTDATE(fato_estoque[data])
RETURN
    CALCULATE(
        DISTINCTCOUNT(fato_estoque[produto_id]),
        fato_estoque[data] = UltimaData,
        fato_estoque[is_ruptura] = TRUE()
    )
```
* **Formato:** Número Inteiro
* **Descrição:** Quantidade de produtos distintos com estoque zerado (`qtd_estoque = 0`) na data mais recente do período selecionado.

### `Est | SKUs Abaixo do Mínimo`
```dax
Est | SKUs Abaixo do Mínimo = 
VAR UltimaData = LASTDATE(fato_estoque[data])
RETURN
    CALCULATE(
        DISTINCTCOUNT(fato_estoque[produto_id]),
        fato_estoque[data] = UltimaData,
        fato_estoque[is_abaixo_minimo] = TRUE()
    )
```
* **Formato:** Número Inteiro
* **Descrição:** Quantidade de produtos distintos com estoque abaixo do mínimo de segurança (`< 20 unidades`) na data mais recente do período.

### `Est | Taxa de Ruptura %`
```dax
Est | Taxa de Ruptura % = 
VAR UltimaData = LASTDATE(fato_estoque[data])
VAR TotalSKUs = 
    CALCULATE(
        DISTINCTCOUNT(fato_estoque[produto_id]),
        fato_estoque[data] = UltimaData
    )
RETURN
    DIVIDE([Est | SKUs em Ruptura], TotalSKUs, 0)
```
* **Formato:** Porcentagem (0,0%)
* **Descrição:** Percentual do catálogo ativo que se encontra em ruptura de estoque.

### `Est | Cobertura Média (Dias)`
```dax
Est | Cobertura Média (Dias) = 
VAR UltimaData = LASTDATE(fato_estoque[data])
RETURN
    CALCULATE(
        AVERAGE(fato_estoque[dias_cobertura]),
        fato_estoque[data] = UltimaData
    )
```
* **Formato:** Número Inteiro (0 dias)
* **Descrição:** Média de dias que o estoque atual suporta com base no giro diário de vendas.

### `Est | Giro de Saída (Unidades Vendidas)`
```dax
Est | Giro de Saída = SUM(fato_estoque[qtd_vendida_dia])
```
* **Formato:** Número Inteiro
* **Descrição:** Total de unidades baixadas do estoque por venda no período filtrado.

### `Est | Total Recebido (Reposição)`
```dax
Est | Total Recebido = SUM(fato_estoque[qtd_recebida_dia])
```
* **Formato:** Número Inteiro
* **Descrição:** Total de unidades entradas por reposição de torra/fornecedores no período filtrado.

---

## Comparativos e destaque da Visão Executiva
> `Comp | *` compara a seleção atual com o mesmo intervalo do ano anterior, usando apenas as datas que têm base de comparação.

### `Vendas | Receita Último Mês`
```dax
Vendas | Receita Último Mês = 
VAR U = CALCULATE(MAX(fato_vendas[data_pedido]), ALLSELECTED(dim_calendario))
RETURN IF(MAX(dim_calendario[AnoMes]) = YEAR(U) * 100 + MONTH(U), [Vendas | Receita Líquida])
```

### `Vendas | Receita Var. Mês %`
```dax
Vendas | Receita Var. Mês % = 
VAR A = SELECTEDVALUE(dim_calendario[AnoMes])
VAR Ant = IF(MOD(A, 100) = 1, A - 89, A - 1)
VAR R = CALCULATE([Vendas | Receita Líquida], REMOVEFILTERS(dim_calendario), dim_calendario[AnoMes] = Ant)
RETURN IF(NOT ISBLANK(A), DIVIDE([Vendas | Receita Líquida] - R, R))
```

### `Vendas | Destaque Último Mês`
```dax
Vendas | Destaque Último Mês = 
VAR U = CALCULATE(MAX(fato_vendas[data_pedido]), ALLSELECTED(dim_calendario))
VAR A = YEAR(U) * 100 + MONTH(U)
VAR Ant = IF(MONTH(U) = 1, A - 89, A - 1)
VAR DataAnt = DATE(YEAR(U), MONTH(U) - 1, 1)
VAR RU = CALCULATE([Vendas | Receita Líquida], REMOVEFILTERS(dim_calendario), dim_calendario[AnoMes] = A)
VAR RA = CALCULATE([Vendas | Receita Líquida], REMOVEFILTERS(dim_calendario), dim_calendario[AnoMes] = Ant)
VAR Delta = DIVIDE(RU - RA, RA)
RETURN FORMAT(U, "mmm/yy") & ": R$ " & FORMAT(RU, "#,0") & IF(ISBLANK(Delta), "", " (" & IF(Delta >= 0, "↑ ", "↓ ") & FORMAT(ABS(Delta), "0.0%") & " vs. " & FORMAT(DataAnt, "mmm/yy") & ")")
```

### `Comp | Receita`
```dax
Comp | Receita = 
VAR Prim = CALCULATE(MIN(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Ult = CALCULATE(MAX(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Atual = FILTER(VALUES(dim_calendario[data]), EDATE(dim_calendario[data], -12) >= Prim && dim_calendario[data] <= Ult)
VAR Base = TREATAS(SELECTCOLUMNS(Atual, "d", EDATE(dim_calendario[data], -12)), dim_calendario[data])
VAR Ini = MINX(Atual, EDATE(dim_calendario[data], -12))
VAR Fim = MAXX(Atual, EDATE(dim_calendario[data], -12))
VAR Rotulo = IF(FORMAT(Ini, "yyyymm") = FORMAT(Fim, "yyyymm"), FORMAT(Fim, "mmm/yy"), FORMAT(Ini, "mmm") & "–" & FORMAT(Fim, "mmm/yy"))
VAR vAtual = CALCULATE([Vendas | Receita Líquida], Atual)
VAR vBase = CALCULATE([Vendas | Receita Líquida], REMOVEFILTERS(dim_calendario), Base)
VAR Delta = DIVIDE(vAtual - vBase, vBase)
RETURN IF(ISBLANK(Delta), "sem base de comparação", IF(Delta >= 0, "↑ ", "↓ ") & FORMAT(ABS(Delta), "0.0%") & " vs. " & Rotulo)
```

### `Comp | Margem`
```dax
Comp | Margem = 
VAR Prim = CALCULATE(MIN(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Ult = CALCULATE(MAX(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Atual = FILTER(VALUES(dim_calendario[data]), EDATE(dim_calendario[data], -12) >= Prim && dim_calendario[data] <= Ult)
VAR Base = TREATAS(SELECTCOLUMNS(Atual, "d", EDATE(dim_calendario[data], -12)), dim_calendario[data])
VAR Ini = MINX(Atual, EDATE(dim_calendario[data], -12))
VAR Fim = MAXX(Atual, EDATE(dim_calendario[data], -12))
VAR Rotulo = IF(FORMAT(Ini, "yyyymm") = FORMAT(Fim, "yyyymm"), FORMAT(Fim, "mmm/yy"), FORMAT(Ini, "mmm") & "–" & FORMAT(Fim, "mmm/yy"))
VAR vAtual = CALCULATE([Vendas | Margem Bruta %], Atual)
VAR vBase = CALCULATE([Vendas | Margem Bruta %], REMOVEFILTERS(dim_calendario), Base)
VAR Delta = (vAtual - vBase) * 100
RETURN IF(ISBLANK(vAtual) || ISBLANK(vBase), "sem base de comparação", IF(Delta >= 0, "↑ ", "↓ ") & FORMAT(ABS(Delta), "0.0") & " p.p. vs. " & Rotulo)
```

### `Comp | Ticket`
```dax
Comp | Ticket = 
VAR Prim = CALCULATE(MIN(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Ult = CALCULATE(MAX(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Atual = FILTER(VALUES(dim_calendario[data]), EDATE(dim_calendario[data], -12) >= Prim && dim_calendario[data] <= Ult)
VAR Base = TREATAS(SELECTCOLUMNS(Atual, "d", EDATE(dim_calendario[data], -12)), dim_calendario[data])
VAR Ini = MINX(Atual, EDATE(dim_calendario[data], -12))
VAR Fim = MAXX(Atual, EDATE(dim_calendario[data], -12))
VAR Rotulo = IF(FORMAT(Ini, "yyyymm") = FORMAT(Fim, "yyyymm"), FORMAT(Fim, "mmm/yy"), FORMAT(Ini, "mmm") & "–" & FORMAT(Fim, "mmm/yy"))
VAR vAtual = CALCULATE([Vendas | Ticket Médio], Atual)
VAR vBase = CALCULATE([Vendas | Ticket Médio], REMOVEFILTERS(dim_calendario), Base)
VAR Delta = DIVIDE(vAtual - vBase, vBase)
RETURN IF(ISBLANK(Delta), "sem base de comparação", IF(Delta >= 0, "↑ ", "↓ ") & FORMAT(ABS(Delta), "0.0%") & " vs. " & Rotulo)
```

### `Comp | ROAS`
```dax
Comp | ROAS = 
VAR Prim = CALCULATE(MIN(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Ult = CALCULATE(MAX(fato_vendas[data_pedido]), REMOVEFILTERS())
VAR Atual = FILTER(VALUES(dim_calendario[data]), EDATE(dim_calendario[data], -12) >= Prim && dim_calendario[data] <= Ult)
VAR Base = TREATAS(SELECTCOLUMNS(Atual, "d", EDATE(dim_calendario[data], -12)), dim_calendario[data])
VAR Ini = MINX(Atual, EDATE(dim_calendario[data], -12))
VAR Fim = MAXX(Atual, EDATE(dim_calendario[data], -12))
VAR Rotulo = IF(FORMAT(Ini, "yyyymm") = FORMAT(Fim, "yyyymm"), FORMAT(Fim, "mmm/yy"), FORMAT(Ini, "mmm") & "–" & FORMAT(Fim, "mmm/yy"))
VAR vAtual = CALCULATE([Mkt | ROAS], Atual)
VAR vBase = CALCULATE([Mkt | ROAS], REMOVEFILTERS(dim_calendario), Base)
VAR Delta = DIVIDE(vAtual - vBase, vBase)
RETURN IF(ISBLANK(Delta), "sem base de comparação", IF(Delta >= 0, "↑ ", "↓ ") & FORMAT(ABS(Delta), "0.0%") & " vs. " & Rotulo)
```

### `Comp | Clientes`
```dax
Comp | Clientes = 
FORMAT(DIVIDE([Clientes | Ativos], [Clientes | Total Base]), "0.0%") & " da base"
```
