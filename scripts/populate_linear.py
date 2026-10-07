"""Script para cadastrar tasks detalhadas no Linear para a plataforma Grão Nobre.

Cadastra tarefas para:
1. Dashboard Power BI - Visão Executiva (passo a passo dos visuais)
2. Dashboard Power BI - Vendas e Rentabilidade
3. Dashboard Power BI - Marketing e Aquisição
4. Dashboard Power BI - Clientes e Retenção
5. Ciência de Dados & Machine Learning (Churn, Prophet, K-Means, Markov)
"""

import os
import sys
import json
import urllib.request
import winreg

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def get_linear_token() -> str:
    """Recupera o token do Linear do ambiente ou do registro do Windows."""
    token = os.environ.get("LINEAR_API_KEY")
    if token:
        return token

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        token, _ = winreg.QueryValueEx(key, "LINEAR_API_KEY")
        winreg.CloseKey(key)
        return token
    except Exception:
        pass

    raise ValueError("LINEAR_API_KEY não encontrada nas variáveis de ambiente.")


def execute_graphql(token: str, query: str, variables: dict = None) -> dict:
    """Executa uma chamada GraphQL na API do Linear."""
    url = "https://api.linear.app/graphql"
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-Linear-Client"
        }
    )

    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        if "errors" in res:
            raise RuntimeError(f"Erro GraphQL: {res['errors']}")
        return res.get("data", {})


def main():
    token = get_linear_token()
    team_id = "9701a6b3-6b83-4aba-982e-e239638acdf5"
    project_id = "6740b516-be4c-445e-8471-efb58720eae3"
    state_todo = "8fa2cade-08fe-4c93-b090-6849a0b1533b"

    tasks = [
        # --- PÁGINA 1: VISÃO EXECUTIVA ---
        {
            "title": "[PBI] Executivo: Cartões de KPIs Principais",
            "desc": (
                "**Objetivo:** Exibir os números macros para tomada de decisão da diretoria.\n\n"
                "- **Visuais recomendados:** Cartão de Linha Múltipla ou Novos Cartões (Card Visual)\n"
                "- **Medidas DAX:**\n"
                "  * `[Vendas | Receita Líquida]` (Formato: R$ 0,00)\n"
                "  * `[Vendas | Margem Bruta %]` (Meta: >= 55%)\n"
                "  * `[Vendas | Ticket Médio]` (Formato: R$ 0,00)\n"
                "  * `[Mkt | ROAS]` (Meta: >= 4.0x)\n"
                "  * `[Clientes | Ativos]` (Total de clientes em atividade)\n"
                "- **Design:** Background suave `#F5F0EB`, números em `#2D1810` e destaque de meta em `#2ECC71`."
            )
        },
        {
            "title": "[PBI] Executivo: Gráfico de Linhas - Evolução Temporal de Vendas",
            "desc": (
                "**Objetivo:** Acompanhar a curva de faturamento líquido contra o custo total mensal.\n\n"
                "- **Visual:** Gráfico de Linhas (Line Chart)\n"
                "- **Eixo X:** `dim_calendario[mes_ano]` (ou `dim_calendario[nome_mes]` ordenado pelo mês cronológico)\n"
                "- **Eixo Y (Linhas):** `[Vendas | Receita Líquida]` (cor `#2D1810`) e `[Vendas | Custo Total]` (cor `#C4956A`)\n"
                "- **Dica de Ferramenta (Tooltips):** `[Vendas | Lucro Bruto]` e `[Vendas | Qtd Pedidos]`\n"
                "- **Análise esperada:** Picos de venda em Maio (Mães), Junho (Namorados/Inverno) e Dezembro (Natal)."
            )
        },
        {
            "title": "[PBI] Executivo: Gráfico de Barras - Receita e Margem por Categoria",
            "desc": (
                "**Objetivo:** Identificar o mix de categorias mais rentável da Grão Nobre.\n\n"
                "- **Visual:** Gráfico de Barras Horizontais (Clustered Bar Chart)\n"
                "- **Eixo Y:** `dim_produtos[categoria]` (Grãos, Moído, Cápsulas, Métodos de Filtragem, Acessórios)\n"
                "- **Eixo X:** `[Vendas | Receita Líquida]`\n"
                "- **Cor condicional ou Tooltip:** `[Vendas | Margem Bruta %]`\n"
                "- **Insight:** Avaliar se produtos de maior faturamento também possuem as maiores margens."
            )
        },
        {
            "title": "[PBI] Executivo: Gráfico Donut - Receita por Canal de Venda",
            "desc": (
                "**Objetivo:** Comparar a representatividade do E-commerce frente às lojas físicas.\n\n"
                "- **Visual:** Gráfico de Rosca (Donut Chart)\n"
                "- **Legenda:** `dim_lojas[tipo]` (E-commerce / Loja Física) ou `dim_lojas[nome_loja]`\n"
                "- **Valores:** `[Vendas | Receita Líquida]`\n"
                "- **Cores:** E-commerce em tom café escuro (`#2D1810`) e lojas físicas em tons café com leite (`#C4956A`)."
            )
        },
        {
            "title": "[PBI] Executivo: Barra Superior de Filtros e Segmentadores",
            "desc": (
                "**Objetivo:** Permitir recorte dinâmico dos visuais executivos.\n\n"
                "- **Visual:** Segmentadores (Slicers) horizontais no cabeçalho\n"
                "- **Filtros:**\n"
                "  * `dim_calendario[ano]` (2025 / 2026)\n"
                "  * `dim_calendario[nome_mes]`\n"
                "  * `dim_clientes[regiao]` (Sul, Sudeste, etc.)\n"
                "  * `dim_lojas[nome_loja]`"
            )
        },

        # --- PÁGINA 2: VENDAS E RENTABILIDADE ---
        {
            "title": "[PBI] Vendas: Matriz Hierárquica de Produtos e Margens",
            "desc": (
                "**Objetivo:** Detalhamento fino da árvore de produtos da Grão Nobre.\n\n"
                "- **Visual:** Matriz (Matrix Visual)\n"
                "- **Linhas:** Hierarquia `dim_produtos[categoria]` > `dim_produtos[subcategoria]` > `dim_produtos[nome_produto]`\n"
                "- **Valores:**\n"
                "  * `[Vendas | Qtd Itens Vendidos]`\n"
                "  * `[Vendas | Receita Líquida]`\n"
                "  * `[Vendas | Custo Total]`\n"
                "  * `[Vendas | Lucro Bruto]`\n"
                "  * `[Vendas | Margem Bruta %]` (com barras de dados ou formatação condicional)"
            )
        },
        {
            "title": "[PBI] Vendas: Dispersão (Scatter Plot) - Preço vs Volume vs Lucro",
            "desc": (
                "**Objetivo:** Matriz de posicionamento de portfólio (produtos estrela, vacas leiteiras, oportunidades).\n\n"
                "- **Visual:** Gráfico de Dispersão (Scatter Plot)\n"
                "- **Detalhes:** `dim_produtos[nome_produto]`\n"
                "- **Eixo X:** `dim_produtos[preco_venda]` (Preço de Venda Médio)\n"
                "- **Eixo Y:** `[Vendas | Qtd Itens Vendidos]` (Volume de Saída)\n"
                "- **Tamanho da Bolha:** `[Vendas | Lucro Bruto]`\n"
                "- **Legenda:** `dim_produtos[categoria]`"
            )
        },
        {
            "title": "[PBI] Vendas: Desempenho Regional por Estado e Região",
            "desc": (
                "**Objetivo:** Identificar as praças com maior penetração de vendas.\n\n"
                "- **Visual:** Gráfico de Barras Horizontais com Drill-Down ou Mapa\n"
                "- **Eixo Y:** `dim_clientes[estado]` (Drill-down: `dim_clientes[cidade]`)\n"
                "- **Eixo X:** `[Vendas | Receita Líquida]`\n"
                "- **Dica de Ferramenta:** `[Vendas | Ticket Médio]` e `[Vendas | Qtd Pedidos]`"
            )
        },
        {
            "title": "[PBI] Vendas: Colunas Empilhadas - Distribuição por Meio de Pagamento",
            "desc": (
                "**Objetivo:** Analisar comportamento financeiro dos pedidos ao longo dos meses.\n\n"
                "- **Visual:** Gráfico de Colunas Empilhadas\n"
                "- **Eixo X:** `dim_calendario[nome_mes]`\n"
                "- **Eixo Y:** `[Vendas | Receita Líquida]`\n"
                "- **Legenda:** `fato_vendas[meio_pagamento]` (PIX, Crédito, Débito, Boleto)\n"
                "- **Insight:** Medir o crescimento da adoção de PIX frente a cartão."
            )
        },

        # --- PÁGINA 3: MARKETING E AQUISIÇÃO ---
        {
            "title": "[PBI] Marketing: Cartões de KPIs de Mídia e Performance",
            "desc": (
                "**Objetivo:** Monitorar eficiência do gasto de tráfego pago.\n\n"
                "- **Visuais:** Cartões de KPIs\n"
                "- **Medidas DAX:**\n"
                "  * `[Mkt | Investimento Total]`\n"
                "  * `[Mkt | ROAS]` (Meta: 4.0x)\n"
                "  * `[Clientes | CAC Médio]`\n"
                "  * `[Mkt | CTR %]` (Meta de engajamento do anúncio)\n"
                "  * `[Mkt | CPA]` (Custo por Aquisição / Conversão)"
            )
        },
        {
            "title": "[PBI] Marketing: Funil de Conversão do Tráfego Digital",
            "desc": (
                "**Objetivo:** Visualizar as etapas de atrito entre a visualização do anúncio e a compra.\n\n"
                "- **Visual:** Gráfico de Funil (Funnel Chart)\n"
                "- **Etapas do Funil:**\n"
                "  1. `[Mkt | Impressões]` (Topo do funil)\n"
                "  2. `[Mkt | Cliques]`\n"
                "  3. `[Mkt | Sessões Site]`\n"
                "  4. `[Mkt | Conversões]` (Fundo do funil / Vendas concluídas)"
            )
        },
        {
            "title": "[PBI] Marketing: Barras Agrupadas - Investimento vs Receita por Canal",
            "desc": (
                "**Objetivo:** Comparativo direto do retorno de cada fonte de tráfego.\n\n"
                "- **Visual:** Gráfico de Barras Clustered\n"
                "- **Eixo Y:** `dim_canais_marketing[canal_nome]` (Google Ads Search, Meta Ads, Orgânico, etc.)\n"
                "- **Eixo X:** `[Mkt | Investimento Total]` e `[Mkt | Receita Atribuída]`\n"
                "- **Rótulos de dados:** Exibir valores e o ROAS apurado de cada canal."
            )
        },
        {
            "title": "[PBI] Marketing: Linhas Eixo Duplo - Investimento vs ROAS Diário",
            "desc": (
                "**Objetivo:** Descobrir pontos de saturação de investimento em anúncios.\n\n"
                "- **Visual:** Gráfico de Linhas e Colunas Agrupadas (Line and Clustered Column Chart)\n"
                "- **Eixo X:** `dim_calendario[data]`\n"
                "- **Eixo Y da Coluna:** `[Mkt | Investimento Total]`\n"
                "- **Eixo Y da Linha:** `[Mkt | ROAS]` (Adicionar linha constante de meta em 4.0x)"
            )
        },
        {
            "title": "[PBI] Marketing: Tabela de Desempenho de Campanhas Sazonais",
            "desc": (
                "**Objetivo:** Comparar o sucesso das campanhas Black Friday, Dia das Mães, etc.\n\n"
                "- **Visual:** Tabela com ordenação por ROAS\n"
                "- **Colunas:**\n"
                "  * `dim_campanhas[nome_campanha]`\n"
                "  * `dim_campanhas[tipo_campanha]`\n"
                "  * `dim_campanhas[budget_campanha]`\n"
                "  * `[Mkt | Conversões]`\n"
                "  * `[Mkt | CPA]`\n"
                "  * `[Mkt | Receita Atribuída]`\n"
                "  * `[Mkt | ROAS]`"
            )
        },

        # --- PÁGINA 4: CLIENTES E RETENÇÃO ---
        {
            "title": "[PBI] Clientes: Cartões de Saúde da Base (CRM & Churn)",
            "desc": (
                "**Objetivo:** Radiografia rápida do estado de fidelidade dos clientes.\n\n"
                "- **Visuais:** Cartões\n"
                "- **Medidas DAX:**\n"
                "  * `[Clientes | Total Base]` (550 clientes cadastrados)\n"
                "  * `[Clientes | Ativos]`\n"
                "  * `[Clientes | Em Risco]`\n"
                "  * `[Clientes | Churned]`\n"
                "  * `[Clientes | Taxa de Churn %]`"
            )
        },
        {
            "title": "[PBI] Clientes: Gráfico Donut - Distribuição de Churn",
            "desc": (
                "**Objetivo:** Visualizar a fatia de clientes retidos versus perdidos.\n\n"
                "- **Visual:** Gráfico de Rosca (Donut)\n"
                "- **Legenda:** `dim_clientes[status_churn]` (Ativo, Em risco, Inativo, Churned)\n"
                "- **Valores:** `[Clientes | Total Base]`\n"
                "- **Cores:** Ativo em verde (`#2ECC71`), Em risco em amarelo/dourado (`#E8B931`) e Churned em vermelho (`#E74C3C`)."
            )
        },
        {
            "title": "[PBI] Clientes: Colunas 100% Empilhadas - Faixa Etária vs Segmento de Valor",
            "desc": (
                "**Objetivo:** Descobrir qual perfil demográfico concentra os clientes Ouro e Diamante.\n\n"
                "- **Visual:** Gráfico de Colunas 100% Empilhadas\n"
                "- **Eixo X:** `dim_clientes[faixa_etaria]` (18-24, 25-30, 31-40, 41-50, 50+)\n"
                "- **Legenda:** `dim_clientes[segmento_valor]` (Bronze, Prata, Ouro, Diamante)\n"
                "- **Valores:** `[Clientes | Total Base]`"
            )
        },
        {
            "title": "[PBI] Clientes: Barras Horizontais - LTV Médio e LTV/CAC por Canal",
            "desc": (
                "**Objetivo:** Avaliar quais canais de aquisição geram os clientes com maior valor vitalício.\n\n"
                "- **Visual:** Gráfico de Barras Horizontais\n"
                "- **Eixo Y:** `dim_clientes[canal_aquisicao]` (Google Ads, Meta Ads, Indicação, etc.)\n"
                "- **Eixo X:** `[Clientes | LTV Médio]`\n"
                "- **Dica de Ferramenta / Rótulo:** `[Clientes | LTV / CAC Ratio]`"
            )
        },

        # --- FASE 2: CIÊNCIA DE DADOS & MACHINE LEARNING ---
        {
            "title": "[ML-01] Feature Engineering e Criação de Tabela RFM em Python",
            "desc": (
                "**Objetivo:** Transformar o histórico de compras em variáveis preditivas por cliente.\n\n"
                "- **Notebook:** `notebooks/05_feature_engineering.ipynb`\n"
                "- **Features calculadas:**\n"
                "  * **Recência:** dias desde a última compra (`data_referencia - max(data_pedido)`)\n"
                "  * **Frequência:** total de compras nos últimos 12 meses\n"
                "  * **Monetário:** soma da receita líquida gerada por cliente (LTV histórico)\n"
                "  * **Comportamentais:** ticket médio pessoal, % de compras com cupom de desconto, canal preferido, categorias de café favoritas\n"
                "- **Saída:** Dataset consolidado pronto para algoritmos de ML."
            )
        },
        {
            "title": "[ML-02] Modelo 1: Classificação Preditiva de Churn (Scikit-Learn & XGBoost)",
            "desc": (
                "**Objetivo:** Treinar modelo supervisionado para prever probabilidade de evasão de cada cliente.\n\n"
                "- **Notebook:** `notebooks/06_churn_model.ipynb`\n"
                "- **Target:** Variável binária de Churn (1 = Churned/Em risco, 0 = Ativo)\n"
                "- **Pré-processamento:** Imputação, One-Hot Encoding em variáveis categóricas, StandardScaler, SMOTE para classes desbalanceadas\n"
                "- **Algoritmos avaliados:** Regressão Logística, Random Forest e XGBoost / LightGBM\n"
                "- **Validação:** Validação Cruzada Estratificada (Stratified K-Fold)."
            )
        },
        {
            "title": "[ML-03] Avaliação e Explicabilidade do Modelo de Churn (SHAP Values)",
            "desc": (
                "**Objetivo:** Explicar detalhadamente para o negócio o que faz um cliente parar de comprar.\n\n"
                "- **Métricas avaliadas:** ROC-AUC (> 0.82), Precision-Recall, F1-Score e Brier Score\n"
                "- **Interpretabilidade (XAI):** SHAP (SHapley Additive exPlanations) Beeswarm Plot e Feature Importance\n"
                "- **Entregável:** Matriz de confusão, limiar de corte otimizado e lista dos 5 fatores de maior impacto no churn."
            )
        },
        {
            "title": "[ML-04] Modelo 2: Previsão de Demanda e Vendas Futuras (Time Series com Prophet)",
            "desc": (
                "**Objetivo:** Prever faturamento e unidades vendidas nos próximos 90 dias para apoiar planejamento de estoque.\n\n"
                "- **Notebook:** `notebooks/07_demand_forecast.ipynb`\n"
                "- **Algoritmo:** Prophet (Meta) ou AutoARIMA\n"
                "- **Componentes:** Tendência linear/não-linear, sazonalidade semanal (pico em sábados/domingos) e anual\n"
                "- **Regressores exógenos:** Calendário de feriados brasileiros e picos de datas comemorativas (Black Friday, Dia das Mães, etc.)\n"
                "- **Métricas de erro:** MAPE (< 10%) e RMSE."
            )
        },
        {
            "title": "[ML-05] Modelo 3: Clusterização Não Supervisionada de Clientes (K-Means)",
            "desc": (
                "**Objetivo:** Agrupar a carteira de clientes em personas analíticas para CRM hiperpersonalizado.\n\n"
                "- **Notebook:** `notebooks/08_clustering.ipynb`\n"
                "- **Técnicas:** Normalização MinMax + K-Means Clustering + PCA para visualização 2D/3D\n"
                "- **Otimização:** Método do Cotovelo (Elbow Method) e Silhouette Score para selecionar k ideal\n"
                "- **Clusters esperados:**\n"
                "  * Cluster 1: Apaixonados por Café (VIP / Alto LTV)\n"
                "  * Cluster 2: Compradores Casuais / Presenteadores\n"
                "  * Cluster 3: Caçadores de Ofertas (Compram só com cupom)\n"
                "  * Cluster 4: Clientes Frios / Em Risco de Abandono."
            )
        },
        {
            "title": "[ML-06] Modelo 4: Modelo de Atribuição Multi-Touch com Cadeias de Markov",
            "desc": (
                "**Objetivo:** Descobrir o real peso de cada canal de marketing na jornada de conversão.\n\n"
                "- **Notebook:** `notebooks/09_attribution.ipynb`\n"
                "- **Metodologia:** Markov Chain Attribution Model com cálculo do Efeito de Remoção (Removal Effect)\n"
                "- **Comparativo:** Comparação lado a lado com os modelos Last-Touch (Último Clique) e First-Touch\n"
                "- **Recomendação de Mídia:** Redirecionamento de verba para os canais de maior impacto indireto."
            )
        },
        {
            "title": "[ML-07] Exportação dos Resultados de ML e Dashboard Preditivo no Power BI",
            "desc": (
                "**Objetivo:** Conectar a Ciência de Dados de volta ao Power BI em uma página 'Visão Preditiva'.\n\n"
                "- **Pipeline de Exportação:** Salvar CSV/tabela com probabilidades de churn por cliente e projeções de demanda\n"
                "- **Visuais no Power BI:**\n"
                "  * Tabela com Alerta de Risco: Clientes com probabilidade de churn > 70% com contato e canal recomendado\n"
                "  * Gráfico de Projeção de Faturamento Futuro com faixa de incerteza (80% e 95%)\n"
                "  * Segmentador por Persona/Cluster do K-Means."
            )
        }
    ]

    print("=" * 60)
    print("🚀 CADASTRANDO TASKS DETALHADAS NO LINEAR 🚀")
    print(f"Total de tasks a cadastrar: {len(tasks)}")
    print("=" * 60)

    mutation_query = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
        }
      }
    }
    """

    for i, t in enumerate(tasks, 1):
        variables = {
            "input": {
                "title": t["title"],
                "description": t["desc"],
                "teamId": team_id,
                "projectId": project_id,
                "stateId": state_todo
            }
        }
        res = execute_graphql(token, mutation_query, variables)
        issue = res.get("issueCreate", {}).get("issue", {})
        print(f"[{i:02d}/{len(tasks):02d}] ✓ {issue.get('identifier')}: {issue.get('title')}")

    print("\n✅ Todas as tasks foram cadastradas com sucesso no Linear!")


if __name__ == "__main__":
    main()
