"""Script para sincronizar e atualizar PRDs de todas as tasks no Linear (Grão Nobre).

Atualiza as descrições (formato PRD) das issues existentes (YOH-5 a YOH-43),
configura o relacionamento pai-filho (parentId) das subtasks do Power BI e
cria as tasks faltantes da Fase 1 (1.2.7 a 1.3.5) com detalhamento completo.
"""

import json
import os
import sys
import urllib.request
import winreg
from typing import Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def get_linear_token() -> str:
    """Recupera o token do Linear do ambiente ou do registro do Windows.

    Returns:
        str: Token de autenticação da API do Linear.

    Raises:
        ValueError: Caso a variável LINEAR_API_KEY não seja encontrada.
    """
    token = os.environ.get("LINEAR_API_KEY")
    if token:
        return token

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        token, _ = winreg.QueryValueEx(key, "LINEAR_API_KEY")
        winreg.CloseKey(key)
        return str(token)
    except Exception:
        pass

    raise ValueError("LINEAR_API_KEY não encontrada nas variáveis de ambiente.")


def execute_graphql(
    token: str, query: str, variables: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Executa uma chamada GraphQL na API do Linear.

    Args:
        token: Chave de API do Linear.
        query: String contendo a query ou mutation GraphQL.
        variables: Dicionário opcional de variáveis GraphQL.

    Returns:
        dict[str, Any]: Campo `data` retornado pela API do Linear.

    Raises:
        RuntimeError: Caso a resposta contenha erros GraphQL.
    """
    url = "https://api.linear.app/graphql"
    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-Linear-Client",
        },
    )

    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        if "errors" in res:
            raise RuntimeError(f"Erro GraphQL: {res['errors']}")
        return res.get("data", {})


def fetch_existing_issues(token: str, team_id: str) -> dict[str, dict[str, Any]]:
    """Busca todas as issues existentes do time no Linear.

    Args:
        token: Chave de API do Linear.
        team_id: UUID do time no Linear.

    Returns:
        dict[str, dict[str, Any]]: Mapa de `identifier` (ex: 'YOH-16') para dados da issue.
    """
    query = """
    query GetTeamIssues($teamId: ID!) {
      issues(first: 150, filter: { team: { id: { eq: $teamId } } }) {
        nodes {
          id
          identifier
          title
        }
      }
    }
    """
    data = execute_graphql(token, query, {"teamId": team_id})
    nodes = data.get("issues", {}).get("nodes", [])
    return {node["identifier"]: node for node in nodes}


def update_issue(
    token: str,
    issue_id: str,
    description: str,
    title: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> dict[str, Any]:
    """Atualiza título, descrição PRD e parentId de uma issue existente no Linear.

    Args:
        token: Chave de API do Linear.
        issue_id: UUID da issue.
        description: Descrição em formato Markdown (PRD).
        title: Novo título opcional.
        parent_id: UUID opcional da issue mãe.

    Returns:
        dict[str, Any]: Dados da issue atualizada.
    """
    mutation = """
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          title
        }
      }
    }
    """
    input_data: dict[str, Any] = {"description": description}
    if title:
        input_data["title"] = title
    if parent_id:
        input_data["parentId"] = parent_id

    res = execute_graphql(token, mutation, {"id": issue_id, "input": input_data})
    return res.get("issueUpdate", {}).get("issue", {})


def create_issue(
    token: str,
    team_id: str,
    project_id: str,
    state_id: str,
    title: str,
    description: str,
    parent_id: Optional[str] = None,
) -> dict[str, Any]:
    """Cria uma nova issue no Linear com descrição PRD.

    Args:
        token: Chave de API do Linear.
        team_id: UUID do time.
        project_id: UUID do projeto.
        state_id: UUID do status inicial.
        title: Título da issue.
        description: Descrição completa em Markdown (PRD).
        parent_id: UUID opcional da issue mãe.

    Returns:
        dict[str, Any]: Dados da issue criada.
    """
    mutation = """
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
    input_data: dict[str, Any] = {
        "title": title,
        "description": description,
        "teamId": team_id,
        "projectId": project_id,
        "stateId": state_id,
    }
    if parent_id:
        input_data["parentId"] = parent_id

    res = execute_graphql(token, mutation, {"input": input_data})
    return res.get("issueCreate", {}).get("issue", {})


def get_prd_updates() -> dict[str, dict[str, Any]]:
    """Retorna o mapeamento de issues existentes para seus PRDs detalhados.

    Returns:
        dict[str, dict[str, Any]]: Mapa de `identifier` para `title`, `desc` e `parent_key`.
    """
    return {
        # --- SPRINT 1.1: FUNDAÇÃO ---
        "YOH-5": {
            "title": "1.1.1 Definir regras de negócio",
            "desc": (
                "# 📋 PRD — 1.1.1 Definir Regras de Negócio\n\n"
                "## 1. Objetivo\n"
                "Documentar todas as regras de negócio da **Grão Nobre Cafés Especiais** como fonte única de verdade para dashboards, modelos de ML e pipelines.\n\n"
                "## 2. Escopo e Entregáveis\n"
                "- **Arquivo:** `docs/BUSINESS_RULES.md`\n"
                "- **Unidades de Negócio:** E-commerce (`WEB01`) + 3 Lojas Físicas (`LOJ01` Batel/PR, `LOJ02` Vila Madalena/SP, `LOJ03` Centro/SC).\n"
                "- **Categorias e Margens Alvo:** Grãos (55-60%), Moído (50-55%), Cápsulas (60-65%), Equipamentos (35-45%), Kits (50-55%), Assinatura (45-50%), Bebidas (70-80%), Alimentos (60-70%).\n"
                "- **Regras de Clientes:** Faixas de LTV (Bronze, Prata, Ouro, Diamante), matriz RFM (scores 1 a 5) e janelas de Churn (Ativo ≤60d, Em risco 61-120d, Inativo 121-180d, Churned >180d).\n"
                "- **Metas Globais:** Receita Bruta R$ 200k/mês, Margem Bruta ≥ 55%, ROAS ≥ 4,0x, CAC < R$ 45, LTV:CAC > 3:1, NPS ≥ 70.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] Regras financeiras, comerciais, de marketing, estoque e SLA de atendimento documentadas.\n"
                "- [x] Calendário de sazonalidade mensal mapeado."
            ),
        },
        "YOH-6": {
            "title": "1.1.2 Criar dicionário de dados",
            "desc": (
                "# 📋 PRD — 1.1.2 Criar Dicionário de Dados\n\n"
                "## 1. Objetivo\n"
                "Especificar o modelo dimensional **Star Schema** completo da plataforma analítica.\n\n"
                "## 2. Escopo e Entregáveis\n"
                "- **Arquivo:** `docs/DATA_DICTIONARY.md`\n"
                "- **6 Tabelas Dimensão:** `dim_clientes`, `dim_produtos`, `dim_canais_marketing`, `dim_campanhas`, `dim_lojas`, `dim_calendario`.\n"
                "- **4 Tabelas Fato:** `fato_vendas` (grain: item de pedido), `fato_marketing` (grain: canal/dia), `fato_atendimento` (grain: ocorrência), `fato_estoque` (grain: produto/loja/dia).\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] Tipos de dados, PKs, FKs, nulabilidade e exemplos documentados.\n"
                "- [x] Diagrama ER em Mermaid validado."
            ),
        },
        "YOH-7": {
            "title": "1.1.3 Criar arquitetura técnica",
            "desc": (
                "# 📋 PRD — 1.1.3 Criar Arquitetura Técnica\n\n"
                "## 1. Objetivo\n"
                "Definir a arquitetura técnica ponta a ponta das 4 fases do projeto (Análise, Ciência de Dados, Engenharia de Dados e Full-Stack).\n\n"
                "## 2. Escopo e Entregáveis\n"
                "- **Arquivo:** `docs/ARCHITECTURE.md`\n"
                "- **Diagramas:** Fluxo de dados da Fase 1, Arquitetura Medalhão (Bronze/Silver/Gold) com Airflow/dbt/PostgreSQL/MinIO e Arquitetura Web (FastAPI + Next.js).\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] Stack tecnológica, convenções de código (PEP 8, snake_case, Conventional Commits) e configuração de MCPs documentadas."
            ),
        },
        "YOH-8": {
            "title": "1.1.4 Criar repositório GitHub",
            "desc": (
                "# 📋 PRD — 1.1.4 Criar Repositório GitHub\n\n"
                "## 1. Objetivo\n"
                "Configurar o repositório público oficial no GitHub para versionamento e portfólio.\n\n"
                "## 2. Critérios de Aceite\n"
                "- [x] Repositório `Landoftha/grao-nobre-analytics` criado e estruturado com `.gitignore`, `README.md` e estrutura de pastas padronizada."
            ),
        },
        "YOH-9": {
            "title": "1.1.5 Configurar MCPs (GitHub + Linear)",
            "desc": (
                "# 📋 PRD — 1.1.5 Configurar MCPs (GitHub + Linear)\n\n"
                "## 1. Objetivo\n"
                "Integrar os servidores Model Context Protocol (MCP) do GitHub e Linear ao ambiente de desenvolvimento.\n\n"
                "## 2. Critérios de Aceite\n"
                "- [x] Conexão testada e operacional para criação de issues, branches e commits."
            ),
        },
        "YOH-10": {
            "title": "1.1.6 Criar projeto no Linear",
            "desc": (
                "# 📋 PRD — 1.1.6 Criar Projeto no Linear\n\n"
                "## 1. Objetivo\n"
                "Estruturar o projeto e backlog no Linear via API GraphQL (`scripts/populate_linear.py`).\n\n"
                "## 2. Critérios de Aceite\n"
                "- [x] Projeto criado e todas as tasks e subtasks sincronizadas com descrições em formato PRD."
            ),
        },
        "YOH-11": {
            "title": "1.1.7 Gerar dados sintéticos robustos",
            "desc": (
                "# 📋 PRD — 1.1.7 Gerar Dados Sintéticos Robustos\n\n"
                "## 1. Objetivo\n"
                "Gerar os 10 arquivos CSV em `data/raw/` via `scripts/generate_data.py` com `Faker (pt_BR)` respeitando todas as regras de negócio e sazonalidade.\n\n"
                "## 2. Requisitos de Volume e Regras\n"
                "- **Volume:** 550 clientes, 25+ produtos, 7.218 itens de venda, 365+ dias de marketing, estoque e atendimento.\n"
                "- **Padrões:** UTF-8, datas ISO 8601 (`YYYY-MM-DD`), valores monetários com 2 casas decimais e integridade referencial 100%.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] 10 CSVs gerados em `data/raw/` refletindo picos sazonais (Inverno, Black Friday, Natal, Dia das Mães)."
            ),
        },
        "YOH-12": {
            "title": "1.1.8 Criar script de validação de dados",
            "desc": (
                "# 📋 PRD — 1.1.8 Criar Script de Validação de Dados\n\n"
                "## 1. Objetivo\n"
                "Garantir a qualidade dos dados sintéticos através do script automatizado `scripts/validate_data.py`.\n\n"
                "## 2. Verificações Realizadas\n"
                "- Unicidade de PKs, integridade referencial de todas as FKs, ausência de `NULL` em campos obrigatórios e consistência de cálculos (`valor_liquido = valor_bruto - valor_desconto`).\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] 16.647 registros validados com 0 erros."
            ),
        },
        # --- SPRINT 1.2: POWER BI SETUP ---
        "YOH-13": {
            "title": "1.2.1 Importar dados no Power BI",
            "desc": (
                "# 📋 PRD — 1.2.1 Importar Dados no Power BI\n\n"
                "## 1. Objetivo\n"
                "Carregar e tipar os 10 arquivos CSV de `data/raw/` no Power BI Desktop aplicando o tema oficial `powerbi/grao_nobre_theme.json`.\n\n"
                "## 2. Critérios de Aceite\n"
                "- [x] Encoding UTF-8 e separador vírgula configurados.\n"
                "- [x] Colunas monetárias como Decimal Fixo, datas em ISO 8601 tipadas como Data e tema visual aplicado."
            ),
        },
        "YOH-14": {
            "title": "1.2.2 Criar modelo dimensional no PBI",
            "desc": (
                "# 📋 PRD — 1.2.2 Criar Modelo Dimensional no Power BI (Star Schema)\n\n"
                "## 1. Objetivo\n"
                "Configurar todos os relacionamentos `1:N` com filtro único entre as 6 dimensões e as 4 tabelas fato.\n\n"
                "## 2. Critérios de Aceite\n"
                "- [x] `dim_calendario` marcada como Tabela de Datas oficial.\n"
                "- [x] `nome_mes` ordenado por `mes` e FKs das tabelas fato ocultadas na visualização de relatório."
            ),
        },
        "YOH-15": {
            "title": "1.2.3 Criar medidas DAX",
            "desc": (
                "# 📋 PRD — 1.2.3 Criar Catálogo de Medidas DAX\n\n"
                "## 1. Objetivo\n"
                "Criar a tabela dedicada `_Medidas` no Power BI e implementar todas as medidas documentadas em `powerbi/medidas_dax.md`.\n\n"
                "## 2. Escopo de Áreas\n"
                "- **1. Vendas (`Vendas | ...`):** Receita Bruta, Descontos, Receita Líquida, Custo Total, Lucro Bruto, Margem Bruta %, Qtd Pedidos, Qtd Itens, Ticket Médio, Frete Total.\n"
                "- **2. Marketing (`Mkt | ...`):** Investimento Total, Impressões, Cliques, CTR %, CPC Médio, Conversões, CPA, Receita Atribuída, ROAS, Taxa de Conversão %, Sessões Site, Novos Leads, Bounce Rate Médio %.\n"
                "- **3. Clientes (`Clientes | ...`):** Total Base, Ativos, Em Risco, Inativos, Churned, Taxa de Churn %, CAC Médio, LTV Médio, LTV / CAC Ratio.\n"
                "- **4. Atendimento (`Atd | ...`):** Total Ocorrências, Tempo Médio Resposta, Tempo Médio Resolução, NPS Médio, NPS Score, % Tickets Resolvidos, % Dentro do SLA.\n"
                "- **5. Estoque (`Est | ...`):** Qtd em Estoque Atual, SKUs em Ruptura, SKUs Abaixo do Mínimo, Taxa de Ruptura %, Cobertura Média (Dias), Giro de Saída, Total Recebido.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [x] Todas as medidas criadas em `_Medidas` com formatação numérica correta e uso de `DIVIDE()`."
            ),
        },
        # --- PÁGINA 1: VISÃO EXECUTIVA (YOH-16 e Subtasks YOH-19 a YOH-23) ---
        "YOH-16": {
            "title": "1.2.4 Dashboard — Visão Executiva",
            "desc": (
                "# 📋 PRD — 1.2.4 Dashboard: Visão Executiva (Página 1)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "A página **Visão Executiva** é a porta de entrada (Página 1) do dashboard corporativo da **Grão Nobre Cafés Especiais** no Power BI. Fornece ao C-Level um panorama consolidado da saúde financeira, comercial, de marketing e de clientes da operação omnichannel (`WEB01` + `LOJ01`, `LOJ02`, `LOJ03`).\n\n"
                "## 2. Perguntas de Negócio Respondidas\n"
                "1. Estamos atingindo a meta de faturamento mensal (R$ 200.000) e de Margem Bruta (≥ 55%)?\n"
                "2. Qual é o ritmo de crescimento de receita e lucro ao longo dos meses (MoM) e como a sazonalidade impacta o resultado?\n"
                "3. Qual é a participação de cada canal (E-commerce vs. Lojas Físicas) e das categorias de produtos no faturamento?\n"
                "4. O investimento em marketing está gerando retorno sustentável (ROAS ≥ 4,0x e relação LTV/CAC > 3,0x)?\n\n"
                "## 3. Estrutura Visual e Subtasks\n"
                "- **YOH-19:** Cartões de KPIs Principais (`Receita Líquida`, `Margem Bruta %`, `Ticket Médio`, `ROAS`, `Clientes Ativos`).\n"
                "- **YOH-20:** Gráfico de Linhas — Evolução Temporal de Vendas (`Receita Líquida` vs. `Custo Total` e `Lucro Bruto`).\n"
                "- **YOH-21:** Gráfico de Barras — Receita e Margem por Categoria (`dim_produtos[categoria]`).\n"
                "- **YOH-22:** Gráfico Donut — Receita por Canal de Venda (`dim_lojas[tipo]` e `nome_loja`).\n"
                "- **YOH-23:** Barra Superior de Filtros e Segmentadores (`ano`, `nome_mes`, `regiao`, `nome_loja`).\n\n"
                "## 4. Diretrizes Visuais (Paleta Grão Nobre)\n"
                "- **Primária:** `#2D1810` | **Secundária:** `#C4956A` | **Acento:** `#E8B931` | **Sucesso:** `#2ECC71` | **Alerta:** `#E74C3C` | **Background:** `#F5F0EB`.\n\n"
                "## 5. Critérios de Aceite (DoD)\n"
                "- [ ] Todos os KPIs principais exibem os valores validados a partir da tabela `_Medidas`.\n"
                "- [ ] Eixo temporal ordenado cronologicamente por `dim_calendario[mes]`.\n"
                "- [ ] Indicadores visuais de meta (Margem ≥ 55%, ROAS ≥ 4,0x) com formatação condicional.\n"
                "- [ ] Filtros globais sincronizados em todos os visuais da página."
            ),
        },
        "YOH-19": {
            "title": "[PBI] Executivo: Cartões de KPIs Principais",
            "parent_key": "YOH-16",
            "desc": (
                "# 📋 PRD — [PBI] Executivo: Cartões de KPIs Principais\n\n"
                "## 1. Objetivo\n"
                "Exibir no topo da Página 1 (Visão Executiva) os Big Numbers estratégicos para tomada de decisão imediata da diretoria.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Novo Cartão (Card Visual) ou Cartão de Linha Múltipla.\n"
                "- **Medidas DAX (`_Medidas`):**\n"
                "  1. `[Vendas | Receita Líquida]` — Formato `R$ #,##0.00` (Referência de meta bruta: R$ 200k/mês)\n"
                "  2. `[Vendas | Margem Bruta %]` — Formato `0.0%` (Meta: **≥ 55,0%**)\n"
                "  3. `[Vendas | Ticket Médio]` — Formato `R$ #,##0.00` (Benchmark: R$ 120–180 Web | R$ 35–55 Loja)\n"
                "  4. `[Mkt | ROAS]` — Formato `0.00x` (Meta: **≥ 4,00x**)\n"
                "  5. `[Clientes | Ativos]` — Formato Inteiro `#,##0` (complementado por `[Clientes | LTV / CAC Ratio]` no subtítulo/tooltip)\n\n"
                "## 3. UI/UX & Formatação Condicional\n"
                "- Fundo dos cartões em `#FFFFFF` sobre canvas `#F5F0EB`, borda sutil `#C4956A` e cantos arredondados (`8px`).\n"
                "- Rótulo de valor em `#2D1810` e indicador de meta em verde (`#2ECC71`) quando atingir a meta ou vermelho (`#E74C3C`) quando abaixo.\n\n"
                "## 4. Critérios de Aceite\n"
                "- [ ] Todos os 5 cartões alinhados horizontalmente abaixo do cabeçalho.\n"
                "- [ ] Resposta imediata aos segmentadores de Ano, Mês, Região e Loja."
            ),
        },
        "YOH-20": {
            "title": "[PBI] Executivo: Gráfico de Linhas - Evolução Temporal de Vendas",
            "parent_key": "YOH-16",
            "desc": (
                "# 📋 PRD — [PBI] Executivo: Gráfico de Linhas — Evolução Temporal de Vendas\n\n"
                "## 1. Objetivo\n"
                "Demonstrar a evolução mensal de Receita Líquida vs. Custo Total (CPV) e evidenciar os picos de sazonalidade do calendário da Grão Nobre.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Linhas (ou Colunas Agrupadas e Linha).\n"
                "- **Eixo X:** Hierarquia `dim_calendario[ano]` > `dim_calendario[nome_mes]` (ordenado por `dim_calendario[mes]`).\n"
                "- **Eixo Y:** `[Vendas | Receita Líquida]` (cor `#2D1810`) e `[Vendas | Custo Total]` (cor `#C4956A`).\n"
                "- **Tooltips (Dicas de Ferramenta):** `[Vendas | Lucro Bruto]`, `[Vendas | Margem Bruta %]` e `[Vendas | Qtd Pedidos]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Meses ordenados de Janeiro a Dezembro.\n"
                "- [ ] Picos de Maio (Mães), Junho/Julho (Inverno), Novembro (Black Friday) e Dezembro (Natal) claramente visíveis."
            ),
        },
        "YOH-21": {
            "title": "[PBI] Executivo: Gráfico de Barras - Receita e Margem por Categoria",
            "parent_key": "YOH-16",
            "desc": (
                "# 📋 PRD — [PBI] Executivo: Gráfico de Barras — Receita e Margem por Categoria\n\n"
                "## 1. Objetivo\n"
                "Identificar o mix de categorias de produtos com maior participação na receita e comparar com suas margens de rentabilidade.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Barras Horizontais Agrupadas.\n"
                "- **Eixo Y:** `dim_produtos[categoria]`.\n"
                "- **Eixo X:** `[Vendas | Receita Líquida]`.\n"
                "- **Tooltips / Formatação Condicional:** `[Vendas | Margem Bruta %]`, `[Vendas | Lucro Bruto]` e `[Vendas | Qtd Itens Vendidos]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Categorias ordenadas decrescentemente por `[Vendas | Receita Líquida]`.\n"
                "- [ ] Rótulos de dados ativos em formato compacto (`R$ X mil`)."
            ),
        },
        "YOH-22": {
            "title": "[PBI] Executivo: Gráfico Donut - Receita por Canal de Venda",
            "parent_key": "YOH-16",
            "desc": (
                "# 📋 PRD — [PBI] Executivo: Gráfico Donut — Receita por Canal de Venda\n\n"
                "## 1. Objetivo\n"
                "Comparar a representatividade do E-commerce (`WEB01`) frente às 3 lojas físicas (`LOJ01` Batel, `LOJ02` Vila Madalena, `LOJ03` Florianópolis).\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Rosca (Donut Chart).\n"
                "- **Legenda:** `dim_lojas[tipo]` com drill-down habilitado para `dim_lojas[nome_loja]`.\n"
                "- **Valores:** `[Vendas | Receita Líquida]`.\n"
                "- **Tooltips:** `[Vendas | Qtd Pedidos]` e `[Vendas | Ticket Médio]`.\n"
                "- **Cores:** E-commerce em `#2D1810` e Lojas Físicas em `#C4956A` / `#E8B931`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Exibição de valor e percentual do total (`% GT`) nos rótulos de detalhe.\n"
                "- [ ] Drill-down funcionando de Tipo de Canal para Nome da Loja."
            ),
        },
        "YOH-23": {
            "title": "[PBI] Executivo: Barra Superior de Filtros e Segmentadores",
            "parent_key": "YOH-16",
            "desc": (
                "# 📋 PRD — [PBI] Executivo: Barra Superior de Filtros e Segmentadores\n\n"
                "## 1. Objetivo\n"
                "Permitir filtragem dinâmica de toda a Visão Executiva por recorte temporal, geográfico e operacional.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visuais:** Segmentadores de Dados (Slicers) suspensos (Dropdown) ou estilo bloco (Tile) no cabeçalho.\n"
                "- **Campos:**\n"
                "  1. `dim_calendario[ano]`\n"
                "  2. `dim_calendario[nome_mes]`\n"
                "  3. `dim_clientes[regiao]`\n"
                "  4. `dim_lojas[nome_loja]`\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Todos os segmentadores filtram os visuais da página sem quebrar o cálculo de ROAS quando o filtro for apenas de período."
            ),
        },
        # --- PÁGINA 2: VENDAS DETALHADO (YOH-17 e Subtasks YOH-24 a YOH-27) ---
        "YOH-17": {
            "title": "1.2.5 Dashboard — Vendas Detalhado",
            "desc": (
                "# 📋 PRD — 1.2.5 Dashboard: Vendas Detalhado (Página 2)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "Página analítica dedicada à performance comercial detalhada por produto (SKU), categoria, elasticidade preço x volume, distribuição regional e meios de pagamento.\n\n"
                "## 2. Perguntas de Negócio Respondidas\n"
                "1. Quais produtos e subcategorias geram maior lucro bruto e quais estão abaixo da margem alvo?\n"
                "2. Como se posicionam os SKUs na matriz Preço de Venda vs. Giro de Unidades?\n"
                "3. Quais estados e cidades concentram a maior receita e ticket médio?\n"
                "4. Qual é a participação de PIX, Cartão de Crédito, Débito e Boleto ao longo do ano?\n\n"
                "## 3. Subtasks Vinculadas\n"
                "- **YOH-24:** Matriz Hierárquica de Produtos e Margens.\n"
                "- **YOH-25:** Dispersão (Scatter Plot) — Preço vs. Volume vs. Lucro.\n"
                "- **YOH-26:** Desempenho Regional por Estado e Região.\n"
                "- **YOH-27:** Colunas Empilhadas — Distribuição por Meio de Pagamento.\n\n"
                "## 4. Critérios de Aceite\n"
                "- [ ] Drill-down completo por Categoria > Subcategoria > Produto e Região > Estado > Cidade.\n"
                "- [ ] Formatação condicional destacando margens abaixo de 50%."
            ),
        },
        "YOH-24": {
            "title": "[PBI] Vendas: Matriz Hierárquica de Produtos e Margens",
            "parent_key": "YOH-17",
            "desc": (
                "# 📋 PRD — [PBI] Vendas: Matriz Hierárquica de Produtos e Margens\n\n"
                "## 1. Objetivo\n"
                "Detalhar o DRE comercial por linha de produto até o nível de SKU.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Matriz (Matrix Visual).\n"
                "- **Linhas:** `dim_produtos[categoria]` > `dim_produtos[subcategoria]` > `dim_produtos[nome_produto]`.\n"
                "- **Valores:** `[Vendas | Qtd Itens Vendidos]`, `[Vendas | Receita Bruta]`, `[Vendas | Total Descontos]`, `[Vendas | Receita Líquida]`, `[Vendas | Custo Total]`, `[Vendas | Lucro Bruto]` e `[Vendas | Margem Bruta %]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Barras de dados aplicadas em `[Vendas | Receita Líquida]` e formatação condicional de fundo/fonte em `[Vendas | Margem Bruta %]`."
            ),
        },
        "YOH-25": {
            "title": "[PBI] Vendas: Dispersão (Scatter Plot) - Preço vs Volume vs Lucro",
            "parent_key": "YOH-17",
            "desc": (
                "# 📋 PRD — [PBI] Vendas: Dispersão (Scatter Plot) — Preço vs Volume vs Lucro\n\n"
                "## 1. Objetivo\n"
                "Classificar o portfólio de 25+ produtos em quadrantes estratégicos (Alto Giro/Alto Preço, Alto Giro/Baixo Preço, Nicho Premium e Baixa Tração).\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Dispersão.\n"
                "- **Valores/Detalhes:** `dim_produtos[nome_produto]`.\n"
                "- **Eixo X:** Média de `dim_produtos[preco_venda]`.\n"
                "- **Eixo Y:** `[Vendas | Qtd Itens Vendidos]`.\n"
                "- **Tamanho da Bolha:** `[Vendas | Lucro Bruto]`.\n"
                "- **Legenda:** `dim_produtos[categoria]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Linhas de média adicionadas nos eixos X e Y pelo painel de Análise do Power BI."
            ),
        },
        "YOH-26": {
            "title": "[PBI] Vendas: Desempenho Regional por Estado e Região",
            "parent_key": "YOH-17",
            "desc": (
                "# 📋 PRD — [PBI] Vendas: Desempenho Regional por Estado e Região\n\n"
                "## 1. Objetivo\n"
                "Analisar a penetração geográfica da Grão Nobre no Sul, Sudeste e demais regiões.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Barras Horizontais com Drill-Down (ou Mapa).\n"
                "- **Hierarquia Geográfica:** `dim_clientes[regiao]` > `dim_clientes[estado]` > `dim_clientes[cidade]`.\n"
                "- **Valores:** `[Vendas | Receita Líquida]`.\n"
                "- **Tooltips:** `[Vendas | Ticket Médio]`, `[Vendas | Qtd Pedidos]` e `[Vendas | Frete Total]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Navegação fluida entre Região, UF e Cidade."
            ),
        },
        "YOH-27": {
            "title": "[PBI] Vendas: Colunas Empilhadas - Distribuição por Meio de Pagamento",
            "parent_key": "YOH-17",
            "desc": (
                "# 📋 PRD — [PBI] Vendas: Colunas Empilhadas — Distribuição por Meio de Pagamento\n\n"
                "## 1. Objetivo\n"
                "Avaliar a preferência de pagamento dos clientes (PIX, Cartão de Crédito, Débito, Boleto) e seu impacto nas taxas financeiras e prazo de recebimento.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Colunas Empilhadas (ou 100% Empilhadas).\n"
                "- **Eixo X:** `dim_calendario[nome_mes]` (ordenado por `mes`).\n"
                "- **Eixo Y:** `[Vendas | Receita Líquida]`.\n"
                "- **Legenda:** `fato_vendas[meio_pagamento]`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Cores distintas da paleta para PIX, Crédito, Débito e Boleto."
            ),
        },
        # --- PÁGINA 3: MARKETING (YOH-18 e Subtasks YOH-28 a YOH-32) ---
        "YOH-18": {
            "title": "1.2.6 Dashboard — Marketing Performance",
            "desc": (
                "# 📋 PRD — 1.2.6 Dashboard: Marketing Performance (Página 3)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "Página dedicada à gestão de tráfego pago e orgânico (`fato_marketing`), funil de aquisição e retorno sobre o investimento mensal planejado de R$ 23.800.\n\n"
                "## 2. Perguntas de Negócio Respondidas\n"
                "1. Quais canais atingem o ROAS alvo e CPA alvo definidos em `dim_canais_marketing`?\n"
                "2. Onde ocorre a maior perda no funil Impressões ➔ Cliques ➔ Sessões ➔ Conversões?\n"
                "3. Qual é a relação diária entre aumento de verba e retorno (ROAS)?\n"
                "4. Quais campanhas sazonais trouxeram maior volume de conversões e receita atribuída?\n\n"
                "## 3. Subtasks Vinculadas\n"
                "- **YOH-28:** Cartões de KPIs de Mídia e Performance.\n"
                "- **YOH-29:** Funil de Conversão do Tráfego Digital.\n"
                "- **YOH-30:** Barras Agrupadas — Investimento vs. Receita por Canal.\n"
                "- **YOH-31:** Linhas Eixo Duplo — Investimento vs. ROAS Diário.\n"
                "- **YOH-32:** Tabela de Desempenho de Campanhas Sazonais."
            ),
        },
        "YOH-28": {
            "title": "[PBI] Marketing: Cartões de KPIs de Mídia e Performance",
            "parent_key": "YOH-18",
            "desc": (
                "# 📋 PRD — [PBI] Marketing: Cartões de KPIs de Mídia e Performance\n\n"
                "## 1. Objetivo\n"
                "Monitorar os indicadores vitais de eficiência de mídia no topo da Página 3.\n\n"
                "## 2. Medidas DAX (`_Medidas`)\n"
                "- `[Mkt | Investimento Total]` (Budget mensal referência: R$ 23.800)\n"
                "- `[Mkt | Receita Atribuída]`\n"
                "- `[Mkt | ROAS]` (Meta global: **≥ 4,00x**)\n"
                "- `[Clientes | CAC Médio]` (Meta: **< R$ 45,00**)\n"
                "- `[Mkt | CPA]`\n"
                "- `[Mkt | CTR %]` (Meta: **> 3,00%**)\n"
                "- `[Mkt | CPC Médio]` (Meta: **< R$ 1,50**)"
            ),
        },
        "YOH-29": {
            "title": "[PBI] Marketing: Funil de Conversão do Tráfego Digital",
            "parent_key": "YOH-18",
            "desc": (
                "# 📋 PRD — [PBI] Marketing: Funil de Conversão do Tráfego Digital\n\n"
                "## 1. Objetivo\n"
                "Medir a passagem dos usuários pelas etapas de atração, clique, navegação e compra.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Funil.\n"
                "- **Valores (em ordem):**\n"
                "  1. `[Mkt | Impressões]`\n"
                "  2. `[Mkt | Cliques]`\n"
                "  3. `[Mkt | Sessões Site]`\n"
                "  4. `[Mkt | Conversões]`"
            ),
        },
        "YOH-30": {
            "title": "[PBI] Marketing: Barras Agrupadas - Investimento vs Receita por Canal",
            "parent_key": "YOH-18",
            "desc": (
                "# 📋 PRD — [PBI] Marketing: Barras Agrupadas — Investimento vs Receita por Canal\n\n"
                "## 1. Objetivo\n"
                "Comparar lado a lado quanto cada canal consumiu de orçamento e quanto gerou de receita atribuída.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Barras Horizontais Agrupadas.\n"
                "- **Eixo Y:** `dim_canais_marketing[canal_nome]`.\n"
                "- **Eixo X:** `[Mkt | Investimento Total]` e `[Mkt | Receita Atribuída]`.\n"
                "- **Tooltips:** `[Mkt | ROAS]`, `AVERAGE(dim_canais_marketing[roas_alvo])`, `[Mkt | CPA]` e `AVERAGE(dim_canais_marketing[cpa_alvo])`."
            ),
        },
        "YOH-31": {
            "title": "[PBI] Marketing: Linhas Eixo Duplo - Investimento vs ROAS Diário",
            "parent_key": "YOH-18",
            "desc": (
                "# 📋 PRD — [PBI] Marketing: Linhas Eixo Duplo — Investimento vs ROAS Diário\n\n"
                "## 1. Objetivo\n"
                "Identificar a elasticidade diária do investimento e eventuais dias de saturação de mídia.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Colunas Agrupadas e Linha.\n"
                "- **Eixo X:** `dim_calendario[data]`.\n"
                "- **Eixo Y (Coluna):** `[Mkt | Investimento Total]`.\n"
                "- **Eixo Y Secundário (Linha):** `[Mkt | ROAS]` com linha constante de meta em `4,0x`."
            ),
        },
        "YOH-32": {
            "title": "[PBI] Marketing: Tabela de Desempenho de Campanhas Sazonais",
            "parent_key": "YOH-18",
            "desc": (
                "# 📋 PRD — [PBI] Marketing: Tabela de Desempenho de Campanhas Sazonais\n\n"
                "## 1. Objetivo\n"
                "Avaliar o retorno individual de cada campanha promocional e sazonal (`dim_campanhas`).\n\n"
                "## 2. Especificação Técnica\n"
                "- **Colunas:** `dim_campanhas[nome_campanha]`, `tipo_campanha`, `budget_campanha`, `[Mkt | Investimento Total]`, `[Mkt | Novos Leads]`, `[Mkt | Conversões]`, `[Mkt | CPA]`, `[Mkt | Receita Atribuída]` e `[Mkt | ROAS]`."
            ),
        },
        # --- PÁGINA 4: CLIENTES SUBTASKS (YOH-33 a YOH-36) ---
        "YOH-33": {
            "title": "[PBI] Clientes: Cartões de Saúde da Base (CRM & Churn)",
            "desc": (
                "# 📋 PRD — [PBI] Clientes: Cartões de Saúde da Base (CRM & Churn)\n\n"
                "## 1. Objetivo\n"
                "Exibir a fotografia de retenção e valor vitalício da base de clientes da Grão Nobre.\n\n"
                "## 2. Medidas DAX (`_Medidas`)\n"
                "- `[Clientes | Total Base]`\n"
                "- `[Clientes | Ativos]`\n"
                "- `[Clientes | Em Risco]`\n"
                "- `[Clientes | Churned]`\n"
                "- `[Clientes | Taxa de Churn %]`\n"
                "- `[Clientes | LTV Médio]`\n"
                "- `[Clientes | LTV / CAC Ratio]` (Meta: **> 3,0x**)"
            ),
        },
        "YOH-34": {
            "title": "[PBI] Clientes: Gráfico Donut - Distribuição de Churn",
            "desc": (
                "# 📋 PRD — [PBI] Clientes: Gráfico Donut — Distribuição de Churn\n\n"
                "## 1. Objetivo\n"
                "Visualizar a proporção da carteira por status de atividade (`Ativo` ≤60d, `Em risco` 61-120d, `Inativo` 121-180d, `Churned` >180d).\n\n"
                "## 2. Especificação Técnica\n"
                "- **Visual:** Gráfico de Rosca.\n"
                "- **Legenda:** `dim_clientes[status_churn]`.\n"
                "- **Valores:** `[Clientes | Total Base]`.\n"
                "- **Cores:** Ativo (`#2ECC71`), Em risco (`#E8B931`), Inativo (`#C4956A`), Churned (`#E74C3C`)."
            ),
        },
        "YOH-35": {
            "title": "[PBI] Clientes: Colunas 100% Empilhadas - Faixa Etária vs Segmento de Valor",
            "desc": (
                "# 📋 PRD — [PBI] Clientes: Colunas 100% Empilhadas — Faixa Etária vs Segmento de Valor\n\n"
                "## 1. Objetivo\n"
                "Cruzar o perfil etário da base com os tiers de fidelidade (`Bronze`, `Prata`, `Ouro`, `Diamante`).\n\n"
                "## 2. Especificação Técnica\n"
                "- **Eixo X:** `dim_clientes[faixa_etaria]`.\n"
                "- **Legenda:** `dim_clientes[segmento_valor]`.\n"
                "- **Valores:** `[Clientes | Total Base]`."
            ),
        },
        "YOH-36": {
            "title": "[PBI] Clientes: Barras Horizontais - LTV Médio e LTV/CAC por Canal",
            "desc": (
                "# 📋 PRD — [PBI] Clientes: Barras Horizontais — LTV Médio e LTV/CAC por Canal\n\n"
                "## 1. Objetivo\n"
                "Identificar quais canais de aquisição trazem clientes mais fiéis e rentáveis no longo prazo.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Eixo Y:** `dim_clientes[canal_aquisicao]`.\n"
                "- **Eixo X:** `[Clientes | LTV Médio]`.\n"
                "- **Tooltips:** `[Clientes | LTV / CAC Ratio]`, `[Clientes | Taxa de Churn %]` e `[Clientes | Total Base]`."
            ),
        },
        # --- FASE 2: MACHINE LEARNING (YOH-37 a YOH-43) ---
        "YOH-37": {
            "title": "[ML-01] Feature Engineering e Criação de Tabela RFM em Python",
            "desc": (
                "# 📋 PRD — [ML-01] Feature Engineering e Criação de Tabela RFM (`notebooks/05_feature_engineering.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Construir a *Analytical Base Table (ABT)* no nível cliente consolidando histórico de vendas e atendimento.\n\n"
                "## 2. Features Calculadas\n"
                "- **RFM:** `recencia_dias`, `frequencia_pedidos`, `monetario_total`.\n"
                "- **Comportamentais:** `ticket_medio_cliente`, `qtd_media_itens`, `pct_pedidos_com_desconto`, `frete_medio`, `diversidade_categorias`, `canal_preferido`, `tempo_medio_entre_compras`.\n"
                "- **Experiência (CX):** `qtd_tickets_atendimento`, `nota_nps_media`, `flag_reclamacao_qualidade`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Dataset exportado em `data/processed/customer_feature_store.csv` sem vazamento de dados (*data leakage*)."
            ),
        },
        "YOH-38": {
            "title": "[ML-02] Modelo 1: Classificação Preditiva de Churn (Scikit-Learn & XGBoost)",
            "desc": (
                "# 📋 PRD — [ML-02] Classificação Preditiva de Churn (`notebooks/06_churn_model.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Treinar modelo supervisionado para estimar a probabilidade de churn de cada cliente.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Algoritmos:** Logistic Regression (baseline), Random Forest e XGBoost/LightGBM.\n"
                "- **Validação:** `StratifiedKFold` (5 folds) + balanceamento via `SMOTE` ou `scale_pos_weight`.\n"
                "- **Meta de Performance:** `F1-Score > 0.80` e `ROC-AUC > 0.82`.\n\n"
                "## 3. Critérios de Aceite\n"
                "- [ ] Modelo serializado em `models/churn_model.pkl` com pipeline de pré-processamento acoplado."
            ),
        },
        "YOH-39": {
            "title": "[ML-03] Avaliação e Explicabilidade do Modelo de Churn (SHAP Values)",
            "desc": (
                "# 📋 PRD — [ML-03] Avaliação e Explicabilidade do Modelo de Churn (SHAP)\n\n"
                "## 1. Objetivo\n"
                "Traduzir as decisões do modelo de Churn em fatores acionáveis de negócio usando XAI (SHAP).\n\n"
                "## 2. Entregáveis\n"
                "- Curvas ROC e Precision-Recall, Matriz de Confusão com threshold ótimo de negócio.\n"
                "- SHAP Summary Plot (Beeswarm), Feature Importance Global e Waterfall Plot para clientes específicos em risco."
            ),
        },
        "YOH-40": {
            "title": "[ML-04] Modelo 2: Previsão de Demanda e Vendas Futuras (Time Series com Prophet)",
            "desc": (
                "# 📋 PRD — [ML-04] Previsão de Demanda com Prophet (`notebooks/07_demand_forecast.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Projetar vendas e demanda diária para os próximos 90 dias para planejamento de torra e estoque.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Algoritmo:** Meta Prophet / SARIMAX.\n"
                "- **Sazonalidades e Regressores:** Sazonalidade semanal, anual (inverno) e feriados/eventos comerciais (Dia das Mães, Namorados, Pais, Black Friday, Natal).\n"
                "- **Meta de Performance:** `MAPE < 15%` (alvo `< 10%`)."
            ),
        },
        "YOH-41": {
            "title": "[ML-05] Modelo 3: Clusterização Não Supervisionada de Clientes (K-Means)",
            "desc": (
                "# 📋 PRD — [ML-05] Clusterização de Clientes com K-Means (`notebooks/08_clustering.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Segmentar a carteira de clientes em personas comportamentais usando aprendizado não supervisionado.\n\n"
                "## 2. Especificação Técnica\n"
                "- **Pipeline:** `StandardScaler`/`MinMaxScaler` + `K-Means` + `PCA` (2D/3D).\n"
                "- **Métrica de Qualidade:** Escolha de $k$ via Elbow Method e `Silhouette Score > 0.50`."
            ),
        },
        "YOH-42": {
            "title": "[ML-06] Modelo 4: Modelo de Atribuição Multi-Touch com Cadeias de Markov",
            "desc": (
                "# 📋 PRD — [ML-06] Atribuição Multi-Touch com Cadeias de Markov (`notebooks/09_attribution.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Mensurar a contribuição real de cada canal de marketing ao longo da jornada de conversão via *Removal Effect*.\n\n"
                "## 2. Especificação Técnica\n"
                "- Comparativo entre *First Click*, *Last Click*, *Linear*, *Time Decay* e *Markov Chain*.\n"
                "- Proposta de realocação ótima do budget mensal de R$ 23.800."
            ),
        },
        "YOH-43": {
            "title": "[ML-07] Exportação dos Resultados de ML e Dashboard Preditivo no Power BI",
            "desc": (
                "# 📋 PRD — [ML-07] Exportação Preditiva e Integração com Power BI\n\n"
                "## 1. Objetivo\n"
                "Exportar os scores de probabilidade de churn, clusters de clientes e previsão de demanda de 90 dias para consumo no Power BI.\n\n"
                "## 2. Entregáveis\n"
                "- Arquivos CSV preditivos em `data/processed/`.\n"
                "- Aba **Visão Preditiva** no Power BI exibindo lista de clientes com risco de churn > 70% e curva de projeção de vendas com intervalo de confiança."
            ),
        },
    }


def get_missing_phase1_tasks() -> list[dict[str, Any]]:
    """Retorna as tasks faltantes da Fase 1 no Linear (1.2.7, 1.2.8, 1.2.9 e Sprint 1.3).

    Returns:
        list[dict[str, Any]]: Lista de definições de issues a criar caso ainda não existam.
    """
    return [
        {
            "title": "1.2.7 Dashboard — Clientes",
            "link_children": ["YOH-33", "YOH-34", "YOH-35", "YOH-36"],
            "desc": (
                "# 📋 PRD — 1.2.7 Dashboard: Clientes & Retenção (Página 4)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "Página dedicada à gestão de CRM, fidelidade, LTV, CAC e monitoramento de Churn dos 550 clientes da Grão Nobre.\n\n"
                "## 2. Perguntas de Negócio Respondidas\n"
                "1. Qual percentual da base está Ativa, Em Risco, Inativa ou Churned?\n"
                "2. Qual perfil demográfico concentra os clientes Ouro e Diamante?\n"
                "3. Quais canais de aquisição trazem clientes com maior LTV e relação LTV/CAC > 3,0x?\n\n"
                "## 3. Subtasks Vinculadas\n"
                "- **YOH-33:** Cartões de Saúde da Base (CRM & Churn).\n"
                "- **YOH-34:** Gráfico Donut — Distribuição de Churn.\n"
                "- **YOH-35:** Colunas 100% Empilhadas — Faixa Etária vs. Segmento de Valor.\n"
                "- **YOH-36:** Barras Horizontais — LTV Médio e LTV/CAC por Canal."
            ),
        },
        {
            "title": "1.2.8 Dashboard — Estoque",
            "desc": (
                "# 📋 PRD — 1.2.8 Dashboard: Estoque & Operações (Página 5)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "Página operacional para controle diário de inventário (`fato_estoque`), prevenção de rupturas (*stockout*), alerta de estoque mínimo (< 20 unidades) e dias de cobertura por SKU e loja.\n\n"
                "## 2. Medidas DAX Utilizadas (`_Medidas`)\n"
                "- `[Est | Qtd em Estoque Atual]` (saldo semi-aditivo via `LASTDATE`)\n"
                "- `[Est | SKUs em Ruptura]`\n"
                "- `[Est | SKUs Abaixo do Mínimo]`\n"
                "- `[Est | Taxa de Ruptura %]`\n"
                "- `[Est | Cobertura Média (Dias)]`\n"
                "- `[Est | Giro de Saída]` e `[Est | Total Recebido]`\n\n"
                "## 3. Visuais Obrigatórios\n"
                "1. **Cartões de Alerta de Estoque:** Estoque Atual, SKUs em Ruptura (`#E74C3C`), SKUs Abaixo do Mínimo (`#E8B931`) e Cobertura Média.\n"
                "2. **Matriz Crítica de Reposição (SKU x Loja):** Quantidade atual, cobertura em dias e status visual de alerta.\n"
                "3. **Gráfico de Linhas:** Evolução diária do saldo em estoque vs. saídas e recebimentos.\n"
                "4. **Gráfico de Barras Agrupadas:** Dias de cobertura por Categoria e Loja (`WEB01`, `LOJ01`, `LOJ02`, `LOJ03`)."
            ),
        },
        {
            "title": "1.2.9 Dashboard — Atendimento",
            "desc": (
                "# 📋 PRD — 1.2.9 Dashboard: Atendimento & CX (Página 6)\n\n"
                "## 1. Visão Geral e Contexto\n"
                "Página de monitoramento da experiência do cliente (`fato_atendimento`), cumprimento de SLA de primeira resposta/resolução por canal e Net Promoter Score (NPS).\n\n"
                "## 2. Medidas DAX Utilizadas (`_Medidas`)\n"
                "- `[Atd | Total Ocorrências]`\n"
                "- `[Atd | NPS Score]` (Meta: **≥ 70**) e `[Atd | NPS Médio]`\n"
                "- `[Atd | Tempo Médio Resposta (min)]` e `[Atd | Tempo Médio Resolução (min)]`\n"
                "- `[Atd | % Tickets Resolvidos]` e `[Atd | % Dentro do SLA]` (WhatsApp ≤15m, Chat ≤2m, Telefone ≤1m, Instagram ≤30m, Email ≤4h)\n\n"
                "## 3. Visuais Obrigatórios\n"
                "1. **Cartões de CX & SLA:** Total de Ocorrências, NPS Score, % Dentro do SLA, Tempo Médio de Resposta e Resolução.\n"
                "2. **Gráfico de Barras Horizontais:** Ocorrências e tempo médio de resolução por `tipo_ocorrencia` (destacando `Atraso na entrega` e `Reclamação de qualidade`).\n"
                "3. **Matriz por Canal de Atendimento:** Volume, SLA Alvo vs. Realizado e `% Dentro do SLA`.\n"
                "4. **Colunas 100% Empilhadas + Linha:** Evolução mensal de Promotores, Neutros e Detratores com curva do NPS Score."
            ),
        },
        {
            "title": "1.3.1 EDA de Vendas (notebooks/01_eda_vendas.ipynb)",
            "desc": (
                "# 📋 PRD — 1.3.1 Análise Exploratória de Vendas (`notebooks/01_eda_vendas.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Conduzir análise estatística e visual profunda sobre o faturamento, margens, sazonalidade, descontos e mix de produtos da Grão Nobre.\n\n"
                "## 2. Análises Obrigatórias\n"
                "- Distribuição do Ticket Médio (E-commerce vs. Lojas Físicas) e testes estatísticos.\n"
                "- Decomposição da série temporal de vendas (tendência e sazonalidade mensal/semanal).\n"
                "- Curva ABC (Pareto) de SKUs por Receita Líquida e por Lucro Bruto.\n"
                "- Impacto de descontos e frete grátis na margem líquida.\n"
                "- Detecção e documentação de outliers/anomalias."
            ),
        },
        {
            "title": "1.3.2 EDA de Marketing (notebooks/02_eda_marketing.ipynb)",
            "desc": (
                "# 📋 PRD — 1.3.2 Análise Exploratória de Marketing (`notebooks/02_eda_marketing.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Avaliar a eficiência de alocação do budget de marketing (R$ 23.800/mês) entre canais pagos e orgânicos.\n\n"
                "## 2. Análises Obrigatórias\n"
                "- Performance real vs. metas (`roas_alvo`, `cpa_alvo`) por canal.\n"
                "- Curva de saturação e retorno marginal decrescente (Investimento diário vs. Receita atribuída).\n"
                "- Eficiência do funil de tráfego (Impressões, Cliques, Sessões, Bounce Rate, Leads e Conversões).\n"
                "- ROI das campanhas sazonais e flash sales."
            ),
        },
        {
            "title": "1.3.3 Análise de Coorte (notebooks/03_cohort_analysis.ipynb)",
            "desc": (
                "# 📋 PRD — 1.3.3 Análise de Coorte / Retenção (`notebooks/03_cohort_analysis.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Mensurar a retenção mensal de clientes e receita por safra de aquisição (*Cohort Analysis*).\n\n"
                "## 2. Análises Obrigatórias\n"
                "- Heatmap de retenção percentual de clientes (`cohort_month` x `cohort_index`).\n"
                "- Retenção líquida de receita (*Net Dollar Retention*) por safra.\n"
                "- Comparação de retenção entre safras adquiridas em campanhas promocionais (ex: Black Friday) vs. meses regulares."
            ),
        },
        {
            "title": "1.3.4 Segmentação RFM (notebooks/04_rfm_analysis.ipynb)",
            "desc": (
                "# 📋 PRD — 1.3.4 Segmentação RFM (`notebooks/04_rfm_analysis.ipynb`)\n\n"
                "## 1. Objetivo\n"
                "Classificar os 550 clientes da base nas dimensões Recência, Frequência e Monetário (scores 1 a 5).\n\n"
                "## 2. Análises e Entregáveis\n"
                "- Cálculo de R, F e M nos últimos 12 meses conforme regras de `docs/BUSINESS_RULES.md`.\n"
                "- Agrupamento em segmentos acionáveis (*Campeões*, *Fiéis*, *Potenciais Fiéis*, *Em Risco*, *Não Posso Perder*, *Hibernando*).\n"
                "- Exportação de `data/processed/clientes_rfm.csv` e matriz de recomendações de CRM por segmento."
            ),
        },
        {
            "title": "1.3.5 Relatório final da Fase 1 (docs/FASE1_REPORT.md)",
            "desc": (
                "# 📋 PRD — 1.3.5 Relatório Executivo Final da Fase 1 (`docs/FASE1_REPORT.md`)\n\n"
                "## 1. Objetivo\n"
                "Consolidar todos os aprendizados, métricas do Power BI e descobertas estatísticas dos 4 notebooks de EDA em um relatório executivo.\n\n"
                "## 2. Estrutura do Documento\n"
                "- Sumário Executivo para o C-Level.\n"
                "- Diagnóstico de Vendas, Marketing, Clientes, Estoque e Atendimento.\n"
                "- Top 10 Insights acionáveis com impacto financeiro estimado.\n"
                "- Recomendações e hipóteses para os modelos preditivos da Fase 2."
            ),
        },
    ]


def main() -> None:
    """Executa a sincronização completa de PRDs e tasks no Linear."""
    token = get_linear_token()
    team_id = "9701a6b3-6b83-4aba-982e-e239638acdf5"
    project_id = "6740b516-be4c-445e-8471-efb58720eae3"
    state_todo = "8fa2cade-08fe-4c93-b090-6849a0b1533b"

    print("=" * 65)
    print("🔄 BUSCANDO ISSUES EXISTENTES NO LINEAR...")
    existing = fetch_existing_issues(token, team_id)
    existing_by_title = {v["title"]: v for v in existing.values()}
    print(f"Encontradas {len(existing)} issues no time.")
    print("=" * 65)

    prd_updates = get_prd_updates()
    total_updates = len(prd_updates)

    for idx, (identifier, spec) in enumerate(prd_updates.items(), 1):
        if identifier not in existing:
            print(f"[{idx:02d}/{total_updates:02d}] ⚠️ {identifier} não encontrada, pulando...")
            continue

        issue_id = existing[identifier]["id"]
        parent_id = None
        parent_key = spec.get("parent_key")
        if parent_key and parent_key in existing:
            parent_id = existing[parent_key]["id"]

        updated = update_issue(
            token=token,
            issue_id=issue_id,
            description=spec["desc"],
            title=spec.get("title"),
            parent_id=parent_id,
        )
        print(
            f"[{idx:02d}/{total_updates:02d}] ✓ Atualizada {updated.get('identifier')}: {updated.get('title')}"
        )

    print("\n" + "=" * 65)
    print("➕ VERIFICANDO / CRIANDO TASKS COMPLEMENTARES DA FASE 1...")
    print("=" * 65)

    missing_tasks = get_missing_phase1_tasks()
    for idx, task in enumerate(missing_tasks, 1):
        title = task["title"]
        if title in existing_by_title:
            issue_node = existing_by_title[title]
            updated = update_issue(
                token=token,
                issue_id=issue_node["id"],
                description=task["desc"],
                title=title,
            )
            parent_uuid = issue_node["id"]
            print(f"[{idx:02d}/{len(missing_tasks):02d}] ↻ Atualizada {updated.get('identifier')}: {title}")
        else:
            created = create_issue(
                token=token,
                team_id=team_id,
                project_id=project_id,
                state_id=state_todo,
                title=title,
                description=task["desc"],
            )
            parent_uuid = created.get("id")
            print(f"[{idx:02d}/{len(missing_tasks):02d}] ✨ Criada {created.get('identifier')}: {title}")

        for child_key in task.get("link_children", []):
            if child_key in existing and parent_uuid:
                child_node = existing[child_key]
                update_issue(
                    token=token,
                    issue_id=child_node["id"],
                    description=prd_updates[child_key]["desc"],
                    parent_id=parent_uuid,
                )
                print(f"    └─ Vinculada subtask {child_key} à task mãe {title}")

    print("\n✅ Sincronização de PRDs concluída com sucesso no Linear!")


if __name__ == "__main__":
    main()
