# ☕ Grão Nobre — Business Analytics Platform

> Plataforma completa de analytics para a cafeteria e e-commerce de cafés especiais **Grão Nobre**.
> Projeto educacional que percorre todas as disciplinas de dados: Análise, Ciência, Engenharia de Dados e Desenvolvimento Full-Stack.

---

## 🏢 O Negócio

A **Grão Nobre** é uma empresa brasileira de cafés especiais que opera em dois canais:

| Canal | Descrição |
|-------|-----------|
| **E-commerce** | Loja online com vendas B2C para todo o Brasil |
| **Lojas Físicas** | 3 cafeterias (Curitiba, São Paulo, Florianópolis) |

**Fundação:** Janeiro de 2025  
**Sede:** Curitiba, PR  
**Faturamento anual projetado:** R$ 2,4 milhões  
**Funcionários:** 32  

---

## 📂 Estrutura do Projeto

```
business-analytics/
├── README.md                          # Este arquivo
├── docs/
│   ├── BUSINESS_RULES.md              # Regras de negócio completas
│   ├── DATA_DICTIONARY.md             # Dicionário de dados
│   ├── ARCHITECTURE.md                # Arquitetura técnica
│   └── ROADMAP.md                     # Roadmap detalhado por fase
├── data/
│   ├── raw/                           # CSVs originais (fonte de verdade)
│   │   ├── dim_clientes.csv
│   │   ├── dim_produtos.csv
│   │   ├── dim_canais_marketing.csv
│   │   ├── dim_lojas.csv
│   │   ├── dim_campanhas.csv
│   │   ├── dim_calendario.csv
│   │   ├── fato_vendas.csv
│   │   ├── fato_marketing.csv
│   │   ├── fato_atendimento.csv
│   │   └── fato_estoque.csv
│   ├── processed/                     # Dados limpos e transformados
│   └── analytics/                     # Dados agregados para dashboards
├── scripts/
│   ├── generate_data.py               # Gerador de dados sintéticos
│   └── validate_data.py               # Validação de qualidade
├── notebooks/
│   ├── 01_eda_vendas.ipynb            # Análise exploratória de vendas
│   ├── 02_eda_marketing.ipynb         # Análise exploratória de marketing
│   ├── 03_cohort_analysis.ipynb       # Análise de coorte
│   ├── 04_rfm_analysis.ipynb          # Segmentação RFM
│   └── 05_predictive_models.ipynb     # Modelos preditivos
├── dashboards/
│   └── powerbi/                       # Arquivos .pbix
├── backend/                           # API (fase futura)
├── frontend/                          # Site (fase futura)
├── pipelines/                         # ETL/ELT (fase futura)
└── .agents/
    ├── AGENTS.md                      # Regras gerais do agente
    └── skills/
        └── grao_nobre/
            └── SKILL.md               # Skill do projeto
```

---

## 🗺️ Roadmap (4 Fases)

### Fase 1 — Análise de Dados (ATUAL)
- [x] Modelagem dimensional (Star Schema)
- [ ] Geração de dados sintéticos robustos (+2000 registros)
- [ ] Dashboard Power BI: Vendas & Marketing
- [ ] Análise exploratória (EDA) com Python
- [ ] Análise de coorte e RFM

### Fase 2 — Ciência de Dados
- [ ] Modelo de previsão de churn
- [ ] Previsão de demanda (time series)
- [ ] Segmentação de clientes (clustering)
- [ ] Modelo de atribuição de marketing
- [ ] A/B Testing framework

### Fase 3 — Engenharia de Dados
- [ ] Pipeline ETL com Airflow/Prefect
- [ ] Data Lake (MinIO/S3)
- [ ] Data Warehouse (PostgreSQL/DuckDB)
- [ ] Orquestração e monitoramento
- [ ] Data Quality com Great Expectations

### Fase 4 — Full-Stack Application
- [ ] API REST (FastAPI)
- [ ] Frontend dashboard (Next.js)
- [ ] Autenticação e autorização
- [ ] Deploy e CI/CD

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Análise** | Power BI, Python (Pandas, Matplotlib, Seaborn) |
| **Ciência** | Scikit-learn, Statsmodels, Prophet |
| **Engenharia** | PostgreSQL, DuckDB, Airflow, dbt |
| **Backend** | FastAPI, SQLAlchemy, Alembic |
| **Frontend** | Next.js, TypeScript, Recharts |
| **DevOps** | Docker, GitHub Actions, Linear |

---

## 🔌 Integrações MCP

O projeto utiliza MCP (Model Context Protocol) para:
- **GitHub** — Versionamento e CI/CD
- **Linear** — Gestão de tasks e sprints
- **PostgreSQL** — Banco de dados de produção
- **Filesystem** — Acesso ao projeto local

---

*Projeto educacional de portfólio por Thays.*
