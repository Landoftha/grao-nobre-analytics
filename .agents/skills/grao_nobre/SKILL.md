---
name: grao-nobre-analytics
description: >
  Skill para o projeto Grão Nobre Analytics Platform. Contém contexto sobre o negócio fictício
  de cafés especiais, regras de negócio, modelagem dimensional, KPIs e convenções do projeto.
  Ative esta skill quando trabalhar em qualquer task relacionada ao projeto business-analytics.
---

# Grão Nobre Analytics Platform — Skill

## Contexto do Projeto

A **Grão Nobre** é uma empresa fictícia de cafés especiais brasileira que opera via e-commerce e 3 lojas físicas.
Este é um projeto educacional de portfólio que percorre 4 fases:

1. **Análise de Dados** — Power BI + Python (Pandas)
2. **Ciência de Dados** — ML (Scikit-learn, Prophet)
3. **Engenharia de Dados** — Airflow, dbt, PostgreSQL
4. **Full-Stack** — FastAPI + Next.js

## Documentação de Referência

Antes de executar qualquer task, consulte:

| Documento | Caminho | Conteúdo |
|-----------|---------|----------|
| **Regras de Negócio** | `docs/BUSINESS_RULES.md` | Todas as regras do negócio |
| **Dicionário de Dados** | `docs/DATA_DICTIONARY.md` | Tabelas, colunas, tipos, FKs |
| **Arquitetura** | `docs/ARCHITECTURE.md` | Stack, diagramas, MCPs |
| **Roadmap** | `docs/ROADMAP.md` | Tasks e critérios de conclusão |

## Regras Obrigatórias

### Dados
- **Star Schema** com tabelas `dim_*` (dimensões) e `fato_*` (fatos)
- IDs seguem padrão: `CLI###`, `PRD##`, `PED####`, `CAM###`, `LOJ##`, `CAN##`
- Datas em ISO 8601: `YYYY-MM-DD`
- Valores monetários: `DECIMAL(10,2)` — sempre 2 casas decimais
- Encoding: UTF-8
- CSVs com separador vírgula

### Métricas-Chave

#### Vendas
```
receita_bruta = SUM(valor_bruto)
receita_liquida = SUM(valor_liquido)
ticket_medio = receita_liquida / COUNT(DISTINCT pedido_id)
margem_bruta_pct = SUM(lucro_bruto) / SUM(valor_liquido) × 100
taxa_conversao = conversoes / sessoes × 100
```

#### Marketing
```
CAC = investimento_total / novos_clientes
ROAS = receita_atribuida / investimento
CPC = investimento / cliques
CTR = (cliques / impressoes) × 100
CPA = investimento / conversoes
LTV_CAC_ratio = LTV_medio / CAC
```

#### Clientes
```
LTV = SUM(valor_liquido) por cliente nos últimos 12 meses
Churn = última compra > 180 dias
NPS = %Promotores - %Detratores
```

### Sazonalidade
Sempre considerar o calendário de sazonalidade:
- **Alta temporada:** Maio (Mães), Junho (Namorados+Inverno), Julho (Inverno), Agosto (Pais), Novembro (Black Friday), Dezembro (Natal)
- **Baixa temporada:** Janeiro (pós-festas), Fevereiro

### Convenções de Código
- Python: PEP 8, type hints, Google docstrings
- SQL: snake_case, CTEs preferidas sobre subqueries
- Git: Conventional Commits em PT-BR (`feat:`, `fix:`, `docs:`, `data:`)
- Notebooks: numerados sequencialmente (`01_`, `02_`, ...)

### Power BI
- Todas as medidas em uma tabela separada chamada `_Medidas`
- Nomes de medidas em português com prefixo da área: `Vendas | Receita Líquida`, `Mkt | ROAS`
- Cores da marca:
  - Primária: `#2D1810` (marrom escuro café)
  - Secundária: `#C4956A` (café com leite)
  - Acento: `#E8B931` (dourado)
  - Sucesso: `#2ECC71`
  - Alerta: `#E74C3C`
  - Background: `#F5F0EB` (creme)

## Geração de Dados

Ao gerar dados sintéticos:
1. Usar a biblioteca `Faker` com locale `pt_BR`
2. Respeitar a sazonalidade definida nas regras de negócio
3. Gerar no mínimo: 500 clientes, 25 produtos, 2000+ vendas, 365 dias de marketing
4. Aplicar distribuições realistas (não uniformes)
5. Garantir integridade referencial entre fatos e dimensões
6. Incluir dados de anomalias/outliers controlados (para exercícios de análise)

## Workflow Padrão

1. Ler os docs de referência antes de qualquer implementação
2. Validar dados contra as regras de qualidade do dicionário
3. Commitar com conventional commits
4. Atualizar o roadmap conforme tasks são concluídas
5. Documentar decisões e insights em notebooks/relatórios
