-- =============================================================================
-- GRÃO NOBRE ANALYTICS — Consultas Analíticas em SQL (Star Schema)
-- Dialeto: PostgreSQL / DuckDB
-- Autora: Thays Yohana Costa
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Receita Líquida, Lucro Bruto, Margem (%) e Ticket Médio por Canal e Loja
-- -----------------------------------------------------------------------------
SELECT
    l.tipo                                                AS tipo_canal,
    l.nome_loja                                           AS loja,
    l.cidade                                              AS cidade,
    COUNT(DISTINCT v.pedido_id)                           AS total_pedidos,
    SUM(v.quantidade)                                     AS unidades_vendidas,
    ROUND(SUM(v.valor_bruto), 2)                          AS receita_bruta_rs,
    ROUND(SUM(v.valor_liquido), 2)                        AS receita_liquida_rs,
    ROUND(SUM(v.lucro_bruto), 2)                          AS lucro_bruto_rs,
    ROUND(
        (SUM(v.lucro_bruto) / NULLIF(SUM(v.valor_liquido), 0)) * 100,
        2
    )                                                     AS margem_bruta_pct,
    ROUND(
        SUM(v.valor_liquido) / NULLIF(COUNT(DISTINCT v.pedido_id), 0),
        2
    )                                                     AS ticket_medio_pedido_rs
FROM fato_vendas v
INNER JOIN dim_lojas l
    ON v.loja_id = l.loja_id
WHERE v.status_pedido <> 'cancelado'
GROUP BY
    l.tipo,
    l.nome_loja,
    l.cidade
ORDER BY
    receita_liquida_rs DESC;

-- -----------------------------------------------------------------------------
-- 2. Evolução Mensal de Receita e Crescimento MoM (Month-over-Month) com Window Functions
-- -----------------------------------------------------------------------------
WITH receita_mensal AS (
    SELECT
        c.ano,
        c.mes,
        c.nome_mes,
        SUM(v.valor_liquido) AS receita_liquida,
        SUM(v.lucro_bruto)   AS lucro_bruto
    FROM fato_vendas v
    INNER JOIN dim_calendario c
        ON v.data_pedido = c.data
    WHERE v.status_pedido <> 'cancelado'
    GROUP BY
        c.ano,
        c.mes,
        c.nome_mes
)
SELECT
    ano,
    mes,
    nome_mes,
    ROUND(receita_liquida, 2) AS receita_liquida_rs,
    ROUND(
        LAG(receita_liquida) OVER (ORDER BY ano, mes),
        2
    ) AS receita_mes_anterior_rs,
    ROUND(
        (
            (receita_liquida - LAG(receita_liquida) OVER (ORDER BY ano, mes))
            / NULLIF(LAG(receita_liquida) OVER (ORDER BY ano, mes), 0)
        ) * 100,
        2
    ) AS crescimento_mom_pct,
    ROUND(
        SUM(receita_liquida) OVER (PARTITION BY ano ORDER BY mes),
        2
    ) AS receita_acumulada_ytd_rs
FROM receita_mensal
ORDER BY
    ano,
    mes;

-- -----------------------------------------------------------------------------
-- 3. Curva ABC (Pareto) de Produtos por Lucro Bruto
-- -----------------------------------------------------------------------------
WITH lucro_por_produto AS (
    SELECT
        p.produto_id,
        p.nome_produto,
        p.categoria,
        p.pontuacao_scaa,
        SUM(v.quantidade)    AS total_unidades,
        SUM(v.valor_liquido) AS receita_liquida,
        SUM(v.lucro_bruto)   AS lucro_bruto
    FROM fato_vendas v
    INNER JOIN dim_produtos p
        ON v.produto_id = p.produto_id
    WHERE v.status_pedido <> 'cancelado'
    GROUP BY
        p.produto_id,
        p.nome_produto,
        p.categoria,
        p.pontuacao_scaa
),
pareto AS (
    SELECT
        *,
        SUM(lucro_bruto) OVER (ORDER BY lucro_bruto DESC)
            / NULLIF(SUM(lucro_bruto) OVER (), 0) AS share_acumulado_lucro
    FROM lucro_por_produto
)
SELECT
    produto_id,
    nome_produto,
    categoria,
    pontuacao_scaa,
    total_unidades,
    ROUND(receita_liquida, 2)             AS receita_liquida_rs,
    ROUND(lucro_bruto, 2)                 AS lucro_bruto_rs,
    ROUND(share_acumulado_lucro * 100, 2) AS pct_acumulado_lucro,
    CASE
        WHEN share_acumulado_lucro <= 0.80 THEN 'Classe A (80% do Lucro)'
        WHEN share_acumulado_lucro <= 0.95 THEN 'Classe B (15% do Lucro)'
        ELSE 'Classe C (5% do Lucro)'
    END                                   AS classificacao_abc
FROM pareto
ORDER BY
    lucro_bruto DESC;

-- -----------------------------------------------------------------------------
-- 4. Segmentação RFM (Recência, Frequência e Valor Monetário) de Clientes
-- -----------------------------------------------------------------------------
WITH base_rfm AS (
    SELECT
        c.cliente_id,
        c.nome,
        c.segmento_valor,
        c.canal_aquisicao,
        MAX(v.data_pedido)                          AS ultima_compra,
        (CURRENT_DATE - MAX(v.data_pedido))         AS recencia_dias,
        COUNT(DISTINCT v.pedido_id)                 AS frequencia_pedidos,
        ROUND(SUM(v.valor_liquido), 2)              AS valor_monetario_total
    FROM dim_clientes c
    INNER JOIN fato_vendas v
        ON c.cliente_id = v.cliente_id
    WHERE v.status_pedido <> 'cancelado'
    GROUP BY
        c.cliente_id,
        c.nome,
        c.segmento_valor,
        c.canal_aquisicao
),
scores_rfm AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recencia_dias DESC)       AS r_score,
        NTILE(5) OVER (ORDER BY frequencia_pedidos ASC)   AS f_score,
        NTILE(5) OVER (ORDER BY valor_monetario_total ASC) AS m_score
    FROM base_rfm
)
SELECT
    cliente_id,
    nome,
    segmento_valor,
    canal_aquisicao,
    ultima_compra,
    recencia_dias,
    frequencia_pedidos,
    valor_monetario_total,
    r_score,
    f_score,
    m_score,
    (r_score * 100 + f_score * 10 + m_score) AS rfm_codigo,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Campeões'
        WHEN r_score >= 3 AND f_score >= 3                  THEN 'Clientes Fiéis'
        WHEN r_score <= 2 AND f_score >= 3                  THEN 'Em Risco (Reativar)'
        WHEN r_score <= 2 AND f_score <= 2                  THEN 'Inativos / Hibernando'
        ELSE 'Potenciais Leais'
    END AS segmento_rfm
FROM scores_rfm
ORDER BY
    valor_monetario_total DESC;

-- -----------------------------------------------------------------------------
-- 5. Performance de Marketing Digital: ROAS, CPA, CTR e Conversão vs. Metas
-- -----------------------------------------------------------------------------
SELECT
    cm.canal_id,
    cm.canal_nome,
    cm.canal_tipo,
    cm.plataforma,
    ROUND(SUM(m.investimento_reais), 2)                                 AS investimento_total_rs,
    SUM(m.impressoes)                                                   AS total_impressoes,
    SUM(m.cliques)                                                      AS total_cliques,
    SUM(m.conversoes)                                                   AS total_conversoes,
    ROUND(SUM(m.receita_atribuida), 2)                                  AS receita_atribuida_rs,
    ROUND((SUM(m.cliques)::NUMERIC / NULLIF(SUM(m.impressoes), 0)) * 100, 2) AS ctr_pct,
    ROUND(SUM(m.investimento_reais) / NULLIF(SUM(m.conversoes), 0), 2)  AS cpa_real_rs,
    cm.cpa_alvo                                                         AS cpa_meta_rs,
    ROUND(SUM(m.receita_atribuida) / NULLIF(SUM(m.investimento_reais), 0), 2) AS roas_real,
    cm.roas_alvo                                                        AS roas_meta
FROM fato_marketing m
INNER JOIN dim_canais_marketing cm
    ON m.canal_id = cm.canal_id
GROUP BY
    cm.canal_id,
    cm.canal_nome,
    cm.canal_tipo,
    cm.plataforma,
    cm.cpa_alvo,
    cm.roas_alvo
ORDER BY
    roas_real DESC NULLS LAST;

-- -----------------------------------------------------------------------------
-- 6. Monitoramento de Ruptura de Estoque e Giro por Produto e Loja
-- -----------------------------------------------------------------------------
SELECT
    l.nome_loja,
    p.nome_produto,
    p.categoria,
    COUNT(*)                                                AS dias_monitorados,
    SUM(CASE WHEN e.is_ruptura THEN 1 ELSE 0 END)           AS dias_em_ruptura,
    SUM(CASE WHEN e.is_abaixo_minimo THEN 1 ELSE 0 END)     AS dias_abaixo_estoque_minimo,
    ROUND(AVG(e.dias_cobertura), 1)                         AS media_dias_cobertura,
    SUM(e.qtd_vendida_dia)                                  AS total_unidades_vendidas
FROM fato_estoque e
INNER JOIN dim_lojas l
    ON e.loja_id = l.loja_id
INNER JOIN dim_produtos p
    ON e.produto_id = p.produto_id
GROUP BY
    l.nome_loja,
    p.nome_produto,
    p.categoria
ORDER BY
    dias_em_ruptura DESC,
    dias_abaixo_estoque_minimo DESC;
