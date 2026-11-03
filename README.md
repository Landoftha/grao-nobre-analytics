# ☕ Grão Nobre — Business Analytics Platform

> Plataforma completa de analytics para a cafeteria e e-commerce de cafés especiais **Grão Nobre**.
> Projeto que percorre as disciplinas de Análise de Dados, Modelagem Dimensional (Star Schema), SQL Analítico, Business Intelligence (Power BI / DAX) e Engenharia de Dados.

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

```text
grao-nobre-analytics/
├── README.md                              # Este arquivo
├── docs/
│   ├── BUSINESS_RULES.md                  # Regras de negócio completas
│   ├── DATA_DICTIONARY.md                 # Dicionário de dados (Star Schema: 4 fatos e 6 dimensões)
│   ├── ARCHITECTURE.md                    # Arquitetura técnica
│   └── ROADMAP.md                         # Roadmap detalhado por fase
├── data/
│   └── raw/                               # CSVs do Star Schema (gerados por generate_data.py)
│       ├── dim_clientes.csv
│       ├── dim_produtos.csv
│       ├── dim_canais_marketing.csv
│       ├── dim_lojas.csv
│       ├── dim_campanhas.csv
│       ├── dim_calendario.csv
│       ├── fato_vendas.csv
│       ├── fato_marketing.csv
│       ├── fato_atendimento.csv
│       └── fato_estoque.csv
├── sql/
│   └── analise_kpis_star_schema.sql       # Consultas SQL analíticas (KPIs, MoM, Curva ABC, RFM, ROAS e Ruptura)
├── scripts/
│   ├── generate_data.py                   # Gerador de dados sintéticos realistas com sazonalidade
│   └── validate_data.py                   # Validação de integridade referencial e qualidade
└── powerbi/
    └── DAX_MEASURES.md                    # Catálogo de medidas DAX para o dashboard Power BI
```

---

## 📊 Consultas SQL Analíticas (`sql/analise_kpis_star_schema.sql`)

O diretório [`sql/analise_kpis_star_schema.sql`](sql/analise_kpis_star_schema.sql) contém consultas analíticas em PostgreSQL / DuckDB sobre o modelo **Star Schema**:

1. **KPIs Executivos por Canal e Loja:** Receita Bruta, Receita Líquida, Lucro Bruto, Margem Bruta (%) e Ticket Médio (`fato_vendas` + `dim_lojas`).
2. **Crescimento MoM (*Month-over-Month*) e Acumulado YTD:** Uso de *Window Functions* (`LAG`, `SUM() OVER`) com `dim_calendario`.
3. **Curva ABC (Pareto) de Produtos:** Classificação A/B/C de SKUs segundo participação acumulada no lucro bruto (`dim_produtos`).
4. **Segmentação RFM (Recência, Frequência e Valor Monetário):** Quintis via `NTILE(5)` classificando clientes em *Campeões*, *Clientes Fiéis*, *Potenciais Leais* e *Em Risco*.
5. **Performance de Mídia Paga (ROAS, CPA e CTR vs. Meta):** Avaliação de eficiência por canal (`fato_marketing` + `dim_canais_marketing`).
6. **Monitoramento de Ruptura e Cobertura de Estoque:** Dias em ruptura e giro diário por loja e SKU (`fato_estoque`).

---

## 🗺️ Roadmap (4 Fases)

### Fase 1 — Análise de Dados & BI
- [x] Modelagem dimensional (Star Schema: 4 tabelas fato e 6 dimensões)
- [x] Geração de dados sintéticos robustos e validação de qualidade (`scripts/`)
- [x] Consultas analíticas em SQL (`sql/analise_kpis_star_schema.sql`)
- [x] Catálogo de medidas DAX e estrutura para Power BI (`powerbi/`)
- [ ] Análise exploratória e RFM em notebooks Python

### Fase 2 — Ciência de Dados
- [ ] Modelo de previsão de churn
- [ ] Previsão de demanda (time series)
- [ ] Segmentação de clientes (clustering)

### Fase 3 — Engenharia de Dados
- [ ] Pipeline ETL automatizado e carga em PostgreSQL / DuckDB
- [ ] Testes automatizados de Data Quality

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Modelagem & SQL** | Star Schema (Kimball), SQL (PostgreSQL / DuckDB), Window Functions & CTEs |
| **BI & Visualização** | Power BI, DAX |
| **Engenharia & Scripts** | Python (Pandas, NumPy) |

---

*Desenvolvido por **Thays Yohana Costa** — [Portfólio](https://thays-portfolio-six.vercel.app) · [GitHub](https://github.com/Landoftha)*
