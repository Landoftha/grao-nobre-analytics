# 🏗️ Arquitetura Técnica — Grão Nobre Analytics Platform

> Visão completa da arquitetura do projeto em todas as suas fases.

---

## Visão Geral

```mermaid
flowchart TB
    subgraph "Fase 1 — Análise de Dados"
        CSV["📄 CSVs (Raw Data)"] --> PBI["📊 Power BI"]
        CSV --> PYTHON["🐍 Python (Pandas)"]
        PYTHON --> NOTEBOOKS["📓 Jupyter Notebooks"]
    end

    subgraph "Fase 2 — Ciência de Dados"
        PYTHON --> ML["🤖 Scikit-learn"]
        PYTHON --> STATS["📈 Statsmodels"]
        ML --> MODELS["Modelos Preditivos"]
        STATS --> MODELS
    end

    subgraph "Fase 3 — Engenharia de Dados"
        CSV --> LAKE["🪣 Data Lake (MinIO)"]
        LAKE --> ETL["⚙️ Airflow/dbt"]
        ETL --> DW["🏢 PostgreSQL (DW)"]
        DW --> PBI
    end

    subgraph "Fase 4 — Full-Stack"
        DW --> API["🔌 FastAPI"]
        API --> FRONT["🌐 Next.js"]
        API --> AUTH["🔐 Auth"]
    end
```

---

## Fase 1 — Análise de Dados (ATUAL)

### Stack

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Dados | CSV (UTF-8) | — |
| Geração de dados | Python + Faker | 3.11+ |
| Análise | Pandas, NumPy | — |
| Visualização | Matplotlib, Seaborn, Plotly | — |
| Dashboard | Power BI Desktop | Última estável |
| Versionamento | Git + GitHub | — |
| Tasks | Linear | — |

### Fluxo de Dados

```mermaid
flowchart LR
    GEN["generate_data.py"] --> RAW["data/raw/*.csv"]
    RAW --> VALIDATE["validate_data.py"]
    VALIDATE --> CLEAN["data/processed/*.csv"]
    CLEAN --> PBI["Power BI (.pbix)"]
    CLEAN --> NB["Notebooks (EDA)"]
```

### Dashboard Power BI — Páginas Planejadas

| Página | Conteúdo Principal |
|--------|-------------------|
| **Visão Executiva** | KPIs principais, receita, margem, tendências MoM |
| **Vendas Detalhado** | Vendas por produto, canal, região, loja, ticket médio |
| **Marketing Performance** | ROAS, CPA, CTR, CPC por canal e campanha |
| **Clientes** | Segmentação RFM, LTV, cohort analysis, churn |
| **Estoque** | Níveis, rupturas, cobertura, alertas |
| **Atendimento** | NPS, SLA, tickets, satisfação |

---

## Fase 2 — Ciência de Dados

### Modelos Planejados

| Modelo | Tipo | Target | Features Principais |
|--------|------|--------|---------------------|
| **Previsão de Churn** | Classificação (XGBoost) | `is_churned` (0/1) | RFM scores, dias_inativo, ticket_medio, canal |
| **Previsão de Demanda** | Séries Temporais (Prophet) | `vendas_diarias` | Sazonalidade, feriados, promoções |
| **Segmentação** | Clustering (K-Means) | Cluster label | RFM, LTV, categorias compradas |
| **Propensão de Compra** | Classificação (LogReg) | `compra_proximos_30d` | Histórico, navegação, email opens |
| **Atribuição** | Markov Chain | Contribuição por canal | Touchpoints da jornada |

### Métricas de Avaliação

| Modelo | Métrica Principal | Meta |
|--------|------------------|------|
| Churn | F1-Score | > 0.80 |
| Demanda | MAPE | < 15% |
| Segmentação | Silhouette Score | > 0.50 |
| Propensão | AUC-ROC | > 0.75 |

---

## Fase 3 — Engenharia de Dados

### Arquitetura do Data Warehouse

```mermaid
flowchart TB
    subgraph "Sources"
        CSV_S["📄 CSVs"]
        API_S["🔌 APIs Externas"]
        DB_S["🗄️ App DB"]
    end

    subgraph "Ingestion"
        AIR["Airflow DAGs"]
    end

    subgraph "Storage"
        BRONZE["🥉 Bronze (Raw)"]
        SILVER["🥈 Silver (Cleaned)"]
        GOLD["🥇 Gold (Aggregated)"]
    end

    subgraph "Serving"
        PBI_S["Power BI"]
        API_SERVE["FastAPI"]
        NB_S["Notebooks"]
    end

    CSV_S --> AIR
    API_S --> AIR
    DB_S --> AIR
    AIR --> BRONZE
    BRONZE --> |"dbt models"| SILVER
    SILVER --> |"dbt models"| GOLD
    GOLD --> PBI_S
    GOLD --> API_SERVE
    SILVER --> NB_S
```

### Medalion Architecture (Bronze / Silver / Gold)

| Camada | Descrição | Formato | Exemplo |
|--------|-----------|---------|---------|
| **Bronze** | Dados brutos, sem transformação | Parquet/CSV | `fato_vendas_raw` |
| **Silver** | Dados limpos, tipados, deduplicados | Parquet | `fato_vendas_clean` |
| **Gold** | Agregações prontas para consumo | Parquet/Views | `vendas_mensal_por_canal` |

### dbt Models (planejados)

```
models/
├── staging/
│   ├── stg_vendas.sql
│   ├── stg_clientes.sql
│   ├── stg_produtos.sql
│   └── stg_marketing.sql
├── intermediate/
│   ├── int_vendas_com_margem.sql
│   ├── int_clientes_rfm.sql
│   └── int_marketing_metricas.sql
└── marts/
    ├── mart_vendas_diario.sql
    ├── mart_marketing_performance.sql
    ├── mart_clientes_360.sql
    └── mart_executivo.sql
```

---

## Fase 4 — Full-Stack Application

### Arquitetura da Aplicação

```mermaid
flowchart TB
    subgraph "Frontend (Next.js)"
        PAGES["Pages (SSR/SSG)"]
        CHARTS["Recharts / D3.js"]
        AUTH_FE["Auth (NextAuth)"]
    end

    subgraph "Backend (FastAPI)"
        ROUTES["API Routes"]
        SERVICES["Business Logic"]
        ORM["SQLAlchemy"]
        AUTH_BE["JWT Auth"]
    end

    subgraph "Data Layer"
        PG["PostgreSQL"]
        REDIS["Redis (Cache)"]
    end

    PAGES --> ROUTES
    CHARTS --> ROUTES
    AUTH_FE --> AUTH_BE
    ROUTES --> SERVICES
    SERVICES --> ORM
    ORM --> PG
    ROUTES --> REDIS
```

### API Endpoints (planejados)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/vendas/resumo` | KPIs de vendas |
| GET | `/api/v1/vendas/por-periodo` | Vendas por período |
| GET | `/api/v1/marketing/performance` | Performance por canal |
| GET | `/api/v1/clientes/segmentos` | Distribuição de segmentos |
| GET | `/api/v1/clientes/{id}/perfil` | Perfil 360 do cliente |
| GET | `/api/v1/estoque/alertas` | Alertas de estoque |
| POST | `/api/v1/previsao/demanda` | Previsão de demanda |
| POST | `/api/v1/previsao/churn` | Score de churn |

---

## Integrações MCP

### Configuração de MCPs

| MCP Server | Uso | Fase |
|------------|-----|------|
| **GitHub** | Repositório, PRs, CI/CD | 1-4 |
| **Linear** | Tasks, sprints, roadmap | 1-4 |
| **PostgreSQL** | Data warehouse | 3-4 |
| **Filesystem** | Acesso local ao projeto | 1-4 |

### Setup MCP — GitHub

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<SEU_TOKEN>"
      }
    }
  }
}
```

### Setup MCP — Linear

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@linear/mcp-server"],
      "env": {
        "LINEAR_API_KEY": "<SEU_TOKEN>"
      }
    }
  }
}
```

### Setup MCP — PostgreSQL (Fase 3+)

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@localhost:5432/grao_nobre"
      ]
    }
  }
}
```

---

## Convenções do Projeto

### Git

- **Branch principal:** `main`
- **Feature branches:** `feat/nome-da-feature`
- **Fix branches:** `fix/nome-do-bug`
- **Commits:** Conventional Commits em PT-BR
  - `feat: adiciona dashboard de vendas`
  - `fix: corrige cálculo de margem`
  - `docs: atualiza dicionário de dados`
  - `data: regenera dados sintéticos`

### Código Python

- **Style:** PEP 8
- **Docstrings:** Google style
- **Type hints:** obrigatórios
- **Linting:** Ruff
- **Formatter:** Black

### Nomes de Arquivos

- Snake_case para tudo: `fato_vendas.csv`, `generate_data.py`
- Notebooks numerados: `01_eda_vendas.ipynb`
- Docs em UPPERCASE: `BUSINESS_RULES.md`, `ARCHITECTURE.md`

---

*Última atualização: 2026-10-02*
