"""
Gerador de dados sintéticos para o projeto Grão Nobre Analytics.

Gera dados realistas respeitando as regras de negócio documentadas em
docs/BUSINESS_RULES.md e docs/DATA_DICTIONARY.md.

Uso:
    python scripts/generate_data.py

Saída:
    data/raw/*.csv (10 arquivos CSV)
"""

import csv
import os
import random
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
from faker import Faker

# Configuração
fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Diretório de saída
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Constantes do Negócio ---

DATA_INICIO = date(2025, 1, 15)  # Fundação da empresa
DATA_FIM = date(2026, 9, 30)  # Dados até setembro 2026

ESTADOS_BRASIL: dict[str, str] = {
    "PR": "Sul", "SC": "Sul", "RS": "Sul",
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
    "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "GO": "Centro-Oeste", "DF": "Centro-Oeste", "MT": "Centro-Oeste",
    "PA": "Norte", "AM": "Norte",
}

CIDADES_POR_ESTADO: dict[str, list[str]] = {
    "PR": ["Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel"],
    "SC": ["Florianópolis", "Joinville", "Blumenau", "Chapecó"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Santa Maria"],
    "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba"],
    "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis"],
    "MG": ["Belo Horizonte", "Uberlândia", "Juiz de Fora"],
    "ES": ["Vitória", "Vila Velha"],
    "BA": ["Salvador", "Feira de Santana"],
    "PE": ["Recife", "Olinda"],
    "CE": ["Fortaleza"],
    "MA": ["São Luís"],
    "GO": ["Goiânia", "Anápolis"],
    "DF": ["Brasília"],
    "MT": ["Cuiabá"],
    "PA": ["Belém"],
    "AM": ["Manaus"],
}

# Peso de distribuição dos estados (Sul/Sudeste dominam, realista para café especial)
PESO_ESTADOS: dict[str, float] = {
    "SP": 0.22, "PR": 0.15, "RJ": 0.10, "MG": 0.10, "SC": 0.08, "RS": 0.08,
    "BA": 0.05, "PE": 0.04, "CE": 0.03, "DF": 0.04, "GO": 0.03,
    "ES": 0.02, "MA": 0.01, "MT": 0.01, "PA": 0.02, "AM": 0.02,
}

FAIXAS_ETARIAS = ["18-24", "25-30", "31-40", "41-50", "51-60", "60+"]
PESO_FAIXAS = [0.08, 0.25, 0.30, 0.20, 0.12, 0.05]

CANAIS_AQUISICAO = [
    "Google Ads", "Meta Ads", "Orgânico", "Indicação",
    "Email Marketing", "Influenciador", "Direto",
]
PESO_CANAIS_AQUISICAO = [0.25, 0.20, 0.18, 0.12, 0.10, 0.08, 0.07]

# Sazonalidade mensal (multiplicador sobre baseline)
SAZONALIDADE: dict[int, float] = {
    1: 0.80, 2: 0.90, 3: 1.00, 4: 1.00,
    5: 1.30, 6: 1.50, 7: 1.40, 8: 1.25,
    9: 1.00, 10: 1.15, 11: 1.80, 12: 1.60,
}

# Sazonalidade dia da semana (seg=0 ... dom=6)
SAZONALIDADE_DIA_SEMANA = [0.85, 0.90, 1.00, 1.05, 1.15, 1.20, 0.85]


def gerar_dim_produtos() -> list[dict[str, Any]]:
    """Gera a dimensão de produtos com 25 SKUs."""
    produtos = [
        # Café em Grãos
        {"produto_id": "PRD01", "nome_produto": "Café Arábica Especial Notas de Chocolate (250g)",
         "categoria": "Café em Grãos", "subcategoria": "Origem Única",
         "preco_venda": 45.00, "custo_unitario": 18.00, "peso_g": 250,
         "pontuacao_scaa": 85.0, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD02", "nome_produto": "Café Exótico Geisha Microlote (250g)",
         "categoria": "Café em Grãos", "subcategoria": "Microlote",
         "preco_venda": 95.00, "custo_unitario": 40.00, "peso_g": 250,
         "pontuacao_scaa": 92.0, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD03", "nome_produto": "Blend da Casa Torra Média (500g)",
         "categoria": "Café em Grãos", "subcategoria": "Blend",
         "preco_venda": 78.00, "custo_unitario": 30.00, "peso_g": 500,
         "pontuacao_scaa": 84.0, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD04", "nome_produto": "Café Bourbon Amarelo Cerrado (250g)",
         "categoria": "Café em Grãos", "subcategoria": "Origem Única",
         "preco_venda": 52.00, "custo_unitario": 20.00, "peso_g": 250,
         "pontuacao_scaa": 86.5, "data_lancamento": "2025-03-01"},
        {"produto_id": "PRD05", "nome_produto": "Café Catuaí Vermelho Natural (250g)",
         "categoria": "Café em Grãos", "subcategoria": "Origem Única",
         "preco_venda": 48.00, "custo_unitario": 19.00, "peso_g": 250,
         "pontuacao_scaa": 85.5, "data_lancamento": "2025-04-15"},
        # Café Moído
        {"produto_id": "PRD06", "nome_produto": "Café Moído Premium Torra Escura (250g)",
         "categoria": "Café Moído", "subcategoria": "Premium",
         "preco_venda": 38.00, "custo_unitario": 16.00, "peso_g": 250,
         "pontuacao_scaa": 83.0, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD07", "nome_produto": "Café Moído Orgânico Mantiqueira (250g)",
         "categoria": "Café Moído", "subcategoria": "Orgânico",
         "preco_venda": 55.00, "custo_unitario": 24.00, "peso_g": 250,
         "pontuacao_scaa": 87.0, "data_lancamento": "2025-06-01"},
        # Cápsulas
        {"produto_id": "PRD08", "nome_produto": "Cápsulas Intenso (10un)",
         "categoria": "Cápsulas", "subcategoria": "Intenso",
         "preco_venda": 32.00, "custo_unitario": 11.00, "peso_g": 55,
         "pontuacao_scaa": None, "data_lancamento": "2025-02-01"},
        {"produto_id": "PRD09", "nome_produto": "Cápsulas Suave Floral (10un)",
         "categoria": "Cápsulas", "subcategoria": "Suave",
         "preco_venda": 32.00, "custo_unitario": 11.00, "peso_g": 55,
         "pontuacao_scaa": None, "data_lancamento": "2025-02-01"},
        {"produto_id": "PRD10", "nome_produto": "Cápsulas Descafeinado (10un)",
         "categoria": "Cápsulas", "subcategoria": "Descafeinado",
         "preco_venda": 35.00, "custo_unitario": 13.00, "peso_g": 55,
         "pontuacao_scaa": None, "data_lancamento": "2025-05-01"},
        # Equipamentos
        {"produto_id": "PRD11", "nome_produto": "Moedor de Café Manual em Aço Inox",
         "categoria": "Equipamentos", "subcategoria": "Moedores",
         "preco_venda": 165.00, "custo_unitario": 70.00, "peso_g": 450,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD12", "nome_produto": "Cafeteira Prensa Francesa 800ml",
         "categoria": "Equipamentos", "subcategoria": "Cafeteiras",
         "preco_venda": 130.00, "custo_unitario": 50.00, "peso_g": 600,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD13", "nome_produto": "Cafeteira Hario V60 Kit Completo",
         "categoria": "Equipamentos", "subcategoria": "Cafeteiras",
         "preco_venda": 189.00, "custo_unitario": 78.00, "peso_g": 550,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD14", "nome_produto": "Balança Digital de Precisão 0.1g",
         "categoria": "Equipamentos", "subcategoria": "Acessórios",
         "preco_venda": 120.00, "custo_unitario": 45.00, "peso_g": 300,
         "pontuacao_scaa": None, "data_lancamento": "2025-03-15"},
        {"produto_id": "PRD15", "nome_produto": "Chaleira Bico de Ganso 700ml",
         "categoria": "Equipamentos", "subcategoria": "Acessórios",
         "preco_venda": 210.00, "custo_unitario": 85.00, "peso_g": 650,
         "pontuacao_scaa": None, "data_lancamento": "2025-02-01"},
        {"produto_id": "PRD16", "nome_produto": "Moedor Elétrico Cônico Profissional",
         "categoria": "Equipamentos", "subcategoria": "Moedores",
         "preco_venda": 450.00, "custo_unitario": 180.00, "peso_g": 1800,
         "pontuacao_scaa": None, "data_lancamento": "2025-06-01"},
        # Kits Especiais
        {"produto_id": "PRD17", "nome_produto": "Kit Completo Barista Iniciante",
         "categoria": "Kits Especiais", "subcategoria": "Kit Iniciante",
         "preco_venda": 320.00, "custo_unitario": 130.00, "peso_g": 2000,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD18", "nome_produto": "Kit Degustação 4 Origens (4x100g)",
         "categoria": "Kits Especiais", "subcategoria": "Degustação",
         "preco_venda": 89.00, "custo_unitario": 35.00, "peso_g": 400,
         "pontuacao_scaa": None, "data_lancamento": "2025-04-01"},
        {"produto_id": "PRD19", "nome_produto": "Kit Presente Premium Caixa Madeira",
         "categoria": "Kits Especiais", "subcategoria": "Presente",
         "preco_venda": 280.00, "custo_unitario": 110.00, "peso_g": 1500,
         "pontuacao_scaa": None, "data_lancamento": "2025-05-01"},
        # Assinatura
        {"produto_id": "PRD20", "nome_produto": "Assinatura Mensal Descoberta (250g/mês)",
         "categoria": "Assinatura", "subcategoria": "Mensal",
         "preco_venda": 42.00, "custo_unitario": 20.00, "peso_g": 250,
         "pontuacao_scaa": None, "data_lancamento": "2025-03-01"},
        {"produto_id": "PRD21", "nome_produto": "Assinatura Mensal Premium (2x250g/mês)",
         "categoria": "Assinatura", "subcategoria": "Mensal",
         "preco_venda": 75.00, "custo_unitario": 32.00, "peso_g": 500,
         "pontuacao_scaa": None, "data_lancamento": "2025-03-01"},
        # Bebidas (loja)
        {"produto_id": "PRD22", "nome_produto": "Espresso Duplo",
         "categoria": "Bebidas (loja)", "subcategoria": "Espresso",
         "preco_venda": 12.00, "custo_unitario": 2.50, "peso_g": None,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD23", "nome_produto": "Cappuccino Tradicional",
         "categoria": "Bebidas (loja)", "subcategoria": "Leite",
         "preco_venda": 16.00, "custo_unitario": 4.00, "peso_g": None,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
        {"produto_id": "PRD24", "nome_produto": "Cold Brew 350ml",
         "categoria": "Bebidas (loja)", "subcategoria": "Gelado",
         "preco_venda": 18.00, "custo_unitario": 4.50, "peso_g": None,
         "pontuacao_scaa": None, "data_lancamento": "2025-06-01"},
        # Alimentos (loja)
        {"produto_id": "PRD25", "nome_produto": "Bolo de Cenoura com Cobertura de Chocolate",
         "categoria": "Alimentos (loja)", "subcategoria": "Doces",
         "preco_venda": 14.00, "custo_unitario": 4.20, "peso_g": None,
         "pontuacao_scaa": None, "data_lancamento": "2025-01-15"},
    ]

    for p in produtos:
        margem = round((p["preco_venda"] - p["custo_unitario"]) / p["preco_venda"] * 100, 2)
        p["margem_percentual"] = margem
        p["ativo"] = True

    return produtos


def gerar_dim_lojas() -> list[dict[str, Any]]:
    """Gera a dimensão de lojas."""
    return [
        {"loja_id": "LOJ01", "nome_loja": "Grão Nobre — Batel", "tipo": "Física",
         "cidade": "Curitiba", "estado": "PR", "data_abertura": "2025-01-15",
         "capacidade_lugares": 40, "ativa": True},
        {"loja_id": "LOJ02", "nome_loja": "Grão Nobre — Vila Madalena", "tipo": "Física",
         "cidade": "São Paulo", "estado": "SP", "data_abertura": "2025-06-01",
         "capacidade_lugares": 55, "ativa": True},
        {"loja_id": "LOJ03", "nome_loja": "Grão Nobre — Centro", "tipo": "Física",
         "cidade": "Florianópolis", "estado": "SC", "data_abertura": "2025-09-15",
         "capacidade_lugares": 35, "ativa": True},
        {"loja_id": "WEB01", "nome_loja": "E-commerce", "tipo": "E-commerce",
         "cidade": "Nacional", "estado": "BR", "data_abertura": "2025-01-15",
         "capacidade_lugares": None, "ativa": True},
    ]


def gerar_dim_canais_marketing() -> list[dict[str, Any]]:
    """Gera a dimensão de canais de marketing."""
    return [
        {"canal_id": "CAN01", "canal_nome": "Google Ads (Search)", "canal_grupo": "Paid Search",
         "canal_tipo": "Pago", "plataforma": "Google",
         "budget_mensal": 6000.00, "cpa_alvo": 35.00, "roas_alvo": 4.00},
        {"canal_id": "CAN02", "canal_nome": "Google Ads (Shopping)", "canal_grupo": "Paid Search",
         "canal_tipo": "Pago", "plataforma": "Google",
         "budget_mensal": 4000.00, "cpa_alvo": 28.00, "roas_alvo": 5.00},
        {"canal_id": "CAN03", "canal_nome": "Meta Ads (Instagram)", "canal_grupo": "Paid Social",
         "canal_tipo": "Pago", "plataforma": "Meta",
         "budget_mensal": 5000.00, "cpa_alvo": 40.00, "roas_alvo": 3.50},
        {"canal_id": "CAN04", "canal_nome": "Meta Ads (Facebook)", "canal_grupo": "Paid Social",
         "canal_tipo": "Pago", "plataforma": "Meta",
         "budget_mensal": 3000.00, "cpa_alvo": 45.00, "roas_alvo": 3.00},
        {"canal_id": "CAN05", "canal_nome": "Email Marketing", "canal_grupo": "Email",
         "canal_tipo": "Próprio", "plataforma": "Email",
         "budget_mensal": 800.00, "cpa_alvo": 8.00, "roas_alvo": 10.00},
        {"canal_id": "CAN06", "canal_nome": "Orgânico (SEO)", "canal_grupo": "Organic Search",
         "canal_tipo": "Orgânico", "plataforma": "Google",
         "budget_mensal": 2000.00, "cpa_alvo": 15.00, "roas_alvo": 8.00},
        {"canal_id": "CAN07", "canal_nome": "Influenciadores", "canal_grupo": "Influencer",
         "canal_tipo": "Pago", "plataforma": "Multi",
         "budget_mensal": 3000.00, "cpa_alvo": 50.00, "roas_alvo": 3.00},
        {"canal_id": "CAN08", "canal_nome": "Direto", "canal_grupo": "Direct",
         "canal_tipo": "Orgânico", "plataforma": "Direto",
         "budget_mensal": 0.00, "cpa_alvo": 0.00, "roas_alvo": 0.00},
    ]


def gerar_dim_campanhas(canais: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Gera campanhas de marketing ao longo do período."""
    campanhas = []
    templates = [
        ("Dia das Mães 2025", "CAN03", "Sazonal", "2025-04-28", "2025-05-11", 3000.00, 15.00),
        ("Inverno Café 2025", "CAN01", "Sazonal", "2025-06-01", "2025-07-31", 5000.00, 10.00),
        ("Dia dos Pais 2025", "CAN03", "Sazonal", "2025-08-01", "2025-08-10", 2500.00, 15.00),
        ("Black Friday 2025", "CAN01", "Sazonal", "2025-11-20", "2025-11-30", 8000.00, 25.00),
        ("Natal 2025", "CAN03", "Sazonal", "2025-12-01", "2025-12-25", 6000.00, 20.00),
        ("Lançamento Bourbon", "CAN02", "Lançamento", "2025-03-01", "2025-03-31", 2000.00, 10.00),
        ("Lançamento Cold Brew", "CAN03", "Lançamento", "2025-06-01", "2025-06-30", 1500.00, 5.00),
        ("Remarketing Q1", "CAN04", "Remarketing", "2025-01-15", "2025-03-31", 3000.00, 10.00),
        ("Remarketing Q2", "CAN04", "Remarketing", "2025-04-01", "2025-06-30", 3000.00, 10.00),
        ("Flash Sale Aniversário", "CAN05", "Flash Sale", "2025-07-15", "2025-07-16", 500.00, 30.00),
        ("Dia das Mães 2026", "CAN03", "Sazonal", "2026-04-27", "2026-05-10", 4000.00, 15.00),
        ("Inverno Café 2026", "CAN01", "Sazonal", "2026-06-01", "2026-07-31", 6000.00, 10.00),
        ("Dia dos Pais 2026", "CAN03", "Sazonal", "2026-08-01", "2026-08-09", 3000.00, 15.00),
        ("Black Friday 2026 (early)", "CAN01", "Sazonal", "2026-09-01", "2026-09-30", 4000.00, 15.00),
        ("Remarketing Q3 2026", "CAN04", "Remarketing", "2026-07-01", "2026-09-30", 3500.00, 10.00),
        ("Fidelidade Ouro", "CAN05", "Fidelidade", "2026-01-01", "2026-09-30", 2000.00, 10.00),
    ]

    for i, (nome, canal, tipo, ini, fim, budget, desc) in enumerate(templates, 1):
        dt_fim = datetime.strptime(fim, "%Y-%m-%d").date()
        status = "Finalizada" if dt_fim < DATA_FIM else "Ativa"
        campanhas.append({
            "campanha_id": f"CAM{i:03d}",
            "nome_campanha": nome,
            "canal_id": canal,
            "tipo_campanha": tipo,
            "data_inicio": ini,
            "data_fim": fim,
            "budget_campanha": budget,
            "desconto_percentual": desc,
            "status": status,
        })

    return campanhas


def gerar_dim_clientes(n: int = 550) -> list[dict[str, Any]]:
    """Gera n clientes com distribuição realista."""
    clientes = []
    estados = list(PESO_ESTADOS.keys())
    pesos_estados = list(PESO_ESTADOS.values())

    for i in range(1, n + 1):
        estado = random.choices(estados, weights=pesos_estados, k=1)[0]
        cidade = random.choice(CIDADES_POR_ESTADO[estado])
        regiao = ESTADOS_BRASIL[estado]
        faixa = random.choices(FAIXAS_ETARIAS, weights=PESO_FAIXAS, k=1)[0]
        canal = random.choices(CANAIS_AQUISICAO, weights=PESO_CANAIS_AQUISICAO, k=1)[0]
        genero = random.choices(["M", "F", "N"], weights=[0.42, 0.52, 0.06], k=1)[0]

        # Data de cadastro distribuída ao longo do tempo (mais novos = mais recentes)
        dias_desde_inicio = (DATA_FIM - DATA_INICIO).days
        # Distribuição que favorece cadastros mais recentes
        dia_cadastro = int(np.random.beta(2, 3) * dias_desde_inicio)
        data_cadastro = DATA_INICIO + timedelta(days=dia_cadastro)

        nome = fake.name_male() if genero == "M" else fake.name_female() if genero == "F" else fake.name()
        email = fake.ascii_email()
        telefone = fake.msisdn()[:13]

        clientes.append({
            "cliente_id": f"CLI{i:03d}",
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cidade": cidade,
            "estado": estado,
            "regiao": regiao,
            "data_cadastro": data_cadastro.isoformat(),
            "faixa_etaria": faixa,
            "genero": genero,
            "canal_aquisicao": canal,
            "segmento_valor": "Bronze",  # Será atualizado depois
            "status_churn": "Ativo",  # Será atualizado depois
            "aceita_marketing": random.choices([True, False], weights=[0.82, 0.18], k=1)[0],
        })

    return clientes


def gerar_dim_calendario() -> list[dict[str, Any]]:
    """Gera tabela calendário de DATA_INICIO até DATA_FIM."""
    MESES_PT = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    DIAS_PT = {
        0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
        3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo",
    }
    FERIADOS = {
        (1, 1): "Confraternização Universal",
        (4, 21): "Tiradentes",
        (5, 1): "Dia do Trabalho",
        (9, 7): "Independência do Brasil",
        (10, 12): "Nossa Senhora Aparecida",
        (11, 2): "Finados",
        (11, 15): "Proclamação da República",
        (12, 25): "Natal",
    }

    calendario = []
    current = DATA_INICIO
    while current <= DATA_FIM:
        mes = current.month
        feriado_key = (current.month, current.day)
        is_feriado = feriado_key in FERIADOS
        nome_feriado = FERIADOS.get(feriado_key, "")

        saz = SAZONALIDADE.get(mes, 1.0)
        if saz >= 1.3:
            sazonalidade_label = "Alta"
        elif saz <= 0.9:
            sazonalidade_label = "Baixa"
        else:
            sazonalidade_label = "Média"

        calendario.append({
            "data": current.isoformat(),
            "ano": current.year,
            "mes": mes,
            "dia": current.day,
            "trimestre": (mes - 1) // 3 + 1,
            "semestre": 1 if mes <= 6 else 2,
            "nome_mes": MESES_PT[mes],
            "nome_dia_semana": DIAS_PT[current.weekday()],
            "dia_semana_num": current.weekday() + 1,
            "semana_ano": current.isocalendar()[1],
            "is_fim_semana": current.weekday() >= 5,
            "is_feriado": is_feriado,
            "nome_feriado": nome_feriado,
            "sazonalidade": sazonalidade_label,
        })
        current += timedelta(days=1)

    return calendario


def gerar_fato_vendas(
    clientes: list[dict[str, Any]],
    produtos: list[dict[str, Any]],
    lojas: list[dict[str, Any]],
    campanhas: list[dict[str, Any]],
    canais: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Gera vendas realistas com sazonalidade e distribuições não-uniformes."""
    vendas = []
    venda_counter = 0
    pedido_counter = 0

    # Produtos disponíveis por canal
    produtos_ecommerce = [p for p in produtos if p["categoria"] not in ["Bebidas (loja)", "Alimentos (loja)"]]
    produtos_loja_fisica = produtos  # Todos disponíveis na loja

    canais_mkt_nomes = [c["canal_nome"] for c in canais]
    canais_mkt_pesos = [0.22, 0.15, 0.20, 0.10, 0.08, 0.12, 0.05, 0.08]

    meios_pagamento = ["PIX", "Cartão de Crédito", "Cartão de Débito", "Boleto"]
    pesos_pagamento = [0.40, 0.35, 0.15, 0.10]

    status_distribuicao = ["entregue", "entregue", "entregue", "entregue", "entregue",
                           "entregue", "entregue", "entregue",
                           "cancelado", "devolvido"]  # ~80% entregue, 10% cancelado, 10% devolvido

    # Vendas diárias baseline: ~5 pedidos/dia no início, crescendo
    current_date = DATA_INICIO
    while current_date <= DATA_FIM:
        # Não vender em datas anteriores ao lançamento do produto
        mes = current_date.month
        dia_semana = current_date.weekday()
        dias_operacao = (current_date - DATA_INICIO).days

        # Crescimento orgânico: mais vendas com o tempo
        growth_factor = 1.0 + (dias_operacao / 365) * 0.8  # +80% ao ano

        # Baseline de pedidos por dia
        baseline_pedidos = 3.5 * growth_factor
        saz_mensal = SAZONALIDADE.get(mes, 1.0)
        saz_dia = SAZONALIDADE_DIA_SEMANA[dia_semana]

        n_pedidos = max(0, int(np.random.poisson(baseline_pedidos * saz_mensal * saz_dia)))

        for _ in range(n_pedidos):
            pedido_counter += 1
            pedido_id = f"PED{pedido_counter:04d}"

            # Selecionar cliente (clientes mais antigos compram mais)
            clientes_validos = [c for c in clientes
                                if c["data_cadastro"] <= current_date.isoformat()]
            if not clientes_validos:
                continue

            # Peso por recência do cadastro (clientes mais recentes são mais ativos)
            pesos_cli = []
            for c in clientes_validos:
                dias_como_cliente = (current_date - date.fromisoformat(c["data_cadastro"])).days
                peso = max(0.1, 10 - dias_como_cliente / 60)  # Mais recentes = mais peso
                pesos_cli.append(peso)

            cliente = random.choices(clientes_validos, weights=pesos_cli, k=1)[0]

            # Determinar loja (70% e-commerce, 30% lojas físicas proporcionais)
            lojas_abertas = [lj for lj in lojas
                            if lj["data_abertura"] <= current_date.isoformat()]
            lojas_fisicas = [lj for lj in lojas_abertas if lj["tipo"] == "Física"]
            ecommerce = [lj for lj in lojas_abertas if lj["tipo"] == "E-commerce"]

            if random.random() < 0.70 or not lojas_fisicas:
                loja = ecommerce[0] if ecommerce else lojas_abertas[0]
                prod_pool = produtos_ecommerce
            else:
                loja = random.choice(lojas_fisicas)
                prod_pool = produtos_loja_fisica

            # Produtos disponíveis nesta data
            prod_disponiveis = [p for p in prod_pool
                                if p["data_lancamento"] <= current_date.isoformat()]
            if not prod_disponiveis:
                pedido_counter -= 1
                continue

            # Número de itens por pedido (1-4, maioria 1-2)
            n_itens = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05], k=1)[0]

            canal_atribuicao = random.choices(canais_mkt_nomes, weights=canais_mkt_pesos, k=1)[0]

            # Verificar se alguma campanha está ativa nesta data
            campanha_ativa = None
            for camp in campanhas:
                if camp["data_inicio"] <= current_date.isoformat() <= camp["data_fim"]:
                    campanha_ativa = camp
                    break

            meio_pgto = random.choices(meios_pagamento, weights=pesos_pagamento, k=1)[0]
            status = random.choice(status_distribuicao)

            # Datas de envio e entrega
            if status in ["entregue", "devolvido"]:
                data_envio = current_date + timedelta(days=random.randint(1, 3))
                regiao_cliente = ESTADOS_BRASIL.get(cliente["estado"], "Sudeste")
                if regiao_cliente in ["Sul", "Sudeste"]:
                    dias_entrega = random.randint(2, 6)
                else:
                    dias_entrega = random.randint(5, 12)
                data_entrega = data_envio + timedelta(days=dias_entrega)
            else:
                data_envio = None
                data_entrega = None

            for item_idx in range(n_itens):
                venda_counter += 1
                produto = random.choices(
                    prod_disponiveis,
                    weights=[1.5 if p["categoria"] in ["Café em Grãos", "Cápsulas"]
                             else 0.8 if p["categoria"] in ["Bebidas (loja)"]
                             else 1.0 for p in prod_disponiveis],
                    k=1,
                )[0]

                quantidade = random.choices([1, 2, 3, 4, 5],
                                            weights=[0.50, 0.25, 0.13, 0.07, 0.05], k=1)[0]

                preco = produto["preco_venda"]
                custo = produto["custo_unitario"]

                # Desconto progressivo
                if quantidade >= 10:
                    desc_pct = 15.00
                elif quantidade >= 5:
                    desc_pct = 10.00
                elif quantidade >= 2:
                    desc_pct = 5.00
                else:
                    desc_pct = 0.00

                # Desconto adicional de campanha
                if campanha_ativa and random.random() < 0.6:
                    desc_pct = max(desc_pct, campanha_ativa["desconto_percentual"])

                valor_bruto = round(quantidade * preco, 2)
                valor_desconto = round(valor_bruto * desc_pct / 100, 2)
                valor_liquido = round(valor_bruto - valor_desconto, 2)
                custo_total = round(quantidade * custo, 2)
                lucro_bruto = round(valor_liquido - custo_total, 2)

                # Frete
                regiao_cli = ESTADOS_BRASIL.get(cliente["estado"], "Sudeste")
                if loja["tipo"] == "Física":
                    frete = 0.00
                elif valor_liquido >= 150:
                    frete = 0.00
                elif regiao_cli in ["Sul", "Sudeste"]:
                    frete = 15.90
                else:
                    frete = 22.90

                vendas.append({
                    "venda_id": f"VEN{venda_counter:05d}",
                    "pedido_id": pedido_id,
                    "data_pedido": current_date.isoformat(),
                    "cliente_id": cliente["cliente_id"],
                    "produto_id": produto["produto_id"],
                    "loja_id": loja["loja_id"],
                    "campanha_id": campanha_ativa["campanha_id"] if campanha_ativa and random.random() < 0.6 else "",
                    "canal_atribuicao": canal_atribuicao,
                    "quantidade": quantidade,
                    "preco_unitario": preco,
                    "desconto_percentual": desc_pct,
                    "valor_desconto": valor_desconto,
                    "valor_bruto": valor_bruto,
                    "valor_liquido": valor_liquido,
                    "custo_total": custo_total,
                    "lucro_bruto": lucro_bruto,
                    "frete": frete,
                    "meio_pagamento": meio_pgto,
                    "status_pedido": status,
                    "data_envio": data_envio.isoformat() if data_envio else "",
                    "data_entrega": data_entrega.isoformat() if data_entrega else "",
                })

        current_date += timedelta(days=1)

    return vendas


def atualizar_segmentos_clientes(
    clientes: list[dict[str, Any]],
    vendas: list[dict[str, Any]],
) -> None:
    """Atualiza segmento_valor e status_churn dos clientes baseado nas vendas."""
    # Calcular LTV e última compra por cliente
    cliente_stats: dict[str, dict[str, Any]] = {}
    for v in vendas:
        cid = v["cliente_id"]
        if v["status_pedido"] in ["cancelado", "devolvido"]:
            continue
        if cid not in cliente_stats:
            cliente_stats[cid] = {"total": 0.0, "ultima_compra": v["data_pedido"]}
        cliente_stats[cid]["total"] += v["valor_liquido"]
        if v["data_pedido"] > cliente_stats[cid]["ultima_compra"]:
            cliente_stats[cid]["ultima_compra"] = v["data_pedido"]

    for c in clientes:
        cid = c["cliente_id"]
        if cid in cliente_stats:
            ltv = cliente_stats[cid]["total"]
            ultima = date.fromisoformat(cliente_stats[cid]["ultima_compra"])
            dias_inativo = (DATA_FIM - ultima).days

            # Segmento
            if ltv >= 5000:
                c["segmento_valor"] = "Diamante"
            elif ltv >= 1500:
                c["segmento_valor"] = "Ouro"
            elif ltv >= 500:
                c["segmento_valor"] = "Prata"
            else:
                c["segmento_valor"] = "Bronze"

            # Churn
            if dias_inativo <= 60:
                c["status_churn"] = "Ativo"
            elif dias_inativo <= 120:
                c["status_churn"] = "Em risco"
            elif dias_inativo <= 180:
                c["status_churn"] = "Inativo"
            else:
                c["status_churn"] = "Churned"
        else:
            c["segmento_valor"] = "Bronze"
            c["status_churn"] = "Churned"


def gerar_fato_marketing(
    canais: list[dict[str, Any]],
    campanhas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Gera dados de marketing diários por canal."""
    marketing = []
    mkt_counter = 0

    # Canais pagos (excluir Direto)
    canais_pagos = [c for c in canais if c["canal_tipo"] != "Orgânico" or c["canal_id"] == "CAN06"]
    canais_ativos = [c for c in canais if c["canal_id"] != "CAN08"]  # Excluir Direto

    current_date = DATA_INICIO
    while current_date <= DATA_FIM:
        mes = current_date.month
        saz = SAZONALIDADE.get(mes, 1.0)

        for canal in canais_ativos:
            mkt_counter += 1

            budget_diario = canal["budget_mensal"] / 30
            investimento = round(budget_diario * saz * random.uniform(0.85, 1.15), 2)

            if canal["canal_tipo"] == "Orgânico":
                investimento = round(budget_diario * random.uniform(0.7, 1.3), 2)

            # Métricas variam por canal
            if "Google" in canal["canal_nome"]:
                impressoes = int(investimento * random.uniform(40, 55))
                ctr_base = random.uniform(0.06, 0.09)
            elif "Meta" in canal["canal_nome"]:
                impressoes = int(investimento * random.uniform(80, 120))
                ctr_base = random.uniform(0.025, 0.04)
            elif "Email" in canal["canal_nome"]:
                impressoes = int(random.uniform(800, 2500))  # Lista de email
                ctr_base = random.uniform(0.15, 0.25)
            elif "Influenciador" in canal["canal_nome"]:
                impressoes = int(investimento * random.uniform(60, 100))
                ctr_base = random.uniform(0.02, 0.04)
            else:  # SEO
                impressoes = int(random.uniform(3000, 8000) * saz)
                ctr_base = random.uniform(0.03, 0.06)

            cliques = max(1, int(impressoes * ctr_base * random.uniform(0.8, 1.2)))
            taxa_conversao = random.uniform(0.015, 0.04)
            conversoes = max(0, int(cliques * taxa_conversao))

            # Receita atribuída
            ticket_medio = random.uniform(80, 160)
            receita_atribuida = round(conversoes * ticket_medio, 2)

            novos_leads = max(0, int(conversoes * random.uniform(1.5, 3.0)))
            sessoes = max(cliques, int(cliques * random.uniform(0.9, 1.3)))
            bounce_rate = round(random.uniform(30, 65), 2)

            # Verificar campanha ativa
            campanha_id = ""
            for camp in campanhas:
                if (camp["canal_id"] == canal["canal_id"]
                        and camp["data_inicio"] <= current_date.isoformat() <= camp["data_fim"]):
                    campanha_id = camp["campanha_id"]
                    # Boost de campanha
                    investimento = round(investimento * 1.5, 2)
                    impressoes = int(impressoes * 1.4)
                    cliques = int(cliques * 1.3)
                    conversoes = int(conversoes * 1.4)
                    receita_atribuida = round(receita_atribuida * 1.4, 2)
                    break

            marketing.append({
                "marketing_id": f"MKT{mkt_counter:05d}",
                "data": current_date.isoformat(),
                "canal_id": canal["canal_id"],
                "campanha_id": campanha_id,
                "investimento_reais": investimento,
                "impressoes": impressoes,
                "cliques": cliques,
                "conversoes": conversoes,
                "receita_atribuida": receita_atribuida,
                "novos_leads": novos_leads,
                "sessoes_site": sessoes,
                "bounce_rate": bounce_rate,
            })

        current_date += timedelta(days=1)

    return marketing


def gerar_fato_atendimento(
    clientes: list[dict[str, Any]],
    vendas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Gera ocorrências de atendimento."""
    atendimentos = []
    atd_counter = 0

    canais_atendimento = ["WhatsApp", "Email", "Chat no site", "Instagram DM", "Telefone"]
    pesos_canais_atd = [0.35, 0.20, 0.20, 0.15, 0.10]

    tipos_ocorrencia = [
        "Dúvida sobre produto", "Atraso na entrega", "Troca/Devolução",
        "Reclamação de qualidade", "Elogio/Sugestão", "Problema no pagamento",
        "Informação sobre rastreio",
    ]
    pesos_tipos = [0.25, 0.20, 0.10, 0.08, 0.12, 0.10, 0.15]

    prioridade_por_tipo = {
        "Dúvida sobre produto": "Baixa",
        "Atraso na entrega": "Alta",
        "Troca/Devolução": "Média",
        "Reclamação de qualidade": "Alta",
        "Elogio/Sugestão": "Baixa",
        "Problema no pagamento": "Alta",
        "Informação sobre rastreio": "Baixa",
    }

    # Para cada venda, chance de gerar atendimento
    pedidos_unicos = {}
    for v in vendas:
        if v["pedido_id"] not in pedidos_unicos:
            pedidos_unicos[v["pedido_id"]] = v

    for ped_id, venda in pedidos_unicos.items():
        # ~15% dos pedidos geram atendimento
        if random.random() > 0.15:
            continue

        atd_counter += 1
        tipo = random.choices(tipos_ocorrencia, weights=pesos_tipos, k=1)[0]
        canal = random.choices(canais_atendimento, weights=pesos_canais_atd, k=1)[0]
        prioridade = prioridade_por_tipo[tipo]

        # Tempo de resposta varia por canal
        sla_canal = {"WhatsApp": 15, "Email": 240, "Chat no site": 2,
                     "Instagram DM": 30, "Telefone": 1}
        base_resposta = sla_canal[canal]
        tempo_resposta = max(1, int(np.random.exponential(base_resposta * 0.8)))

        # Status e resolução
        if random.random() < 0.85:
            status = "Resolvido"
            tempo_resolucao = max(tempo_resposta, int(np.random.exponential(
                120 if prioridade == "Baixa" else 240 if prioridade == "Média" else 360
            )))
        elif random.random() < 0.5:
            status = "Em andamento"
            tempo_resolucao = None
        else:
            status = "Aberto"
            tempo_resolucao = None

        # NPS (promotores mais comuns se resolvido)
        if status == "Resolvido":
            nota_nps = random.choices(
                list(range(0, 11)),
                weights=[1, 1, 1, 2, 2, 3, 4, 8, 12, 18, 25],
                k=1,
            )[0]
        else:
            nota_nps = random.choices(
                list(range(0, 11)),
                weights=[5, 4, 5, 6, 7, 8, 10, 12, 10, 8, 5],
                k=1,
            )[0]

        if nota_nps >= 9:
            satisfacao = "Satisfeito"
        elif nota_nps >= 7:
            satisfacao = "Neutro"
        else:
            satisfacao = "Insatisfeito"

        data_abertura_dt = date.fromisoformat(venda["data_pedido"]) + timedelta(
            days=random.randint(1, 10)
        )
        if data_abertura_dt > DATA_FIM:
            data_abertura_dt = DATA_FIM

        atendimentos.append({
            "atendimento_id": f"ATD{atd_counter:04d}",
            "data_abertura": data_abertura_dt.isoformat(),
            "cliente_id": venda["cliente_id"],
            "pedido_id": ped_id,
            "canal_atendimento": canal,
            "tipo_ocorrencia": tipo,
            "prioridade": prioridade,
            "status": status,
            "tempo_resposta_min": tempo_resposta,
            "tempo_resolucao_min": tempo_resolucao if tempo_resolucao else "",
            "nota_nps": nota_nps,
            "satisfacao": satisfacao,
        })

    return atendimentos


def gerar_fato_estoque(
    produtos: list[dict[str, Any]],
    lojas: list[dict[str, Any]],
    vendas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Gera snapshots diários de estoque (amostra mensal para não ficar gigante)."""
    estoque = []
    est_counter = 0

    # Calcular vendas por produto/loja/dia
    vendas_por_dia: dict[str, dict[str, int]] = {}
    for v in vendas:
        if v["status_pedido"] == "cancelado":
            continue
        key = f"{v['data_pedido']}_{v['produto_id']}_{v['loja_id']}"
        vendas_por_dia[key] = vendas_por_dia.get(key, 0) + v["quantidade"]

    # Gerar snapshot no 1º e 15º dia de cada mês
    current_date = DATA_INICIO
    while current_date <= DATA_FIM:
        if current_date.day not in [1, 15]:
            current_date += timedelta(days=1)
            continue

        for loja in lojas:
            if loja["data_abertura"] > current_date.isoformat():
                continue

            # Produtos disponíveis na loja
            if loja["tipo"] == "E-commerce":
                prods = [p for p in produtos
                         if p["categoria"] not in ["Bebidas (loja)", "Alimentos (loja)"]
                         and p["data_lancamento"] <= current_date.isoformat()]
            else:
                prods = [p for p in produtos
                         if p["data_lancamento"] <= current_date.isoformat()]

            for prod in prods:
                est_counter += 1

                # Simular nível de estoque
                base_estoque = random.randint(30, 200)
                key = f"{current_date.isoformat()}_{prod['produto_id']}_{loja['loja_id']}"
                qtd_vendida = vendas_por_dia.get(key, random.randint(0, 8))

                # Chance de recebimento
                qtd_recebida = 0
                if random.random() < 0.15:
                    qtd_recebida = random.randint(50, 200)

                qtd_estoque = max(0, base_estoque - qtd_vendida + qtd_recebida)
                is_ruptura = qtd_estoque == 0
                is_abaixo_minimo = qtd_estoque < 20

                media_vendas_diaria = max(1, qtd_vendida if qtd_vendida > 0 else 3)
                dias_cobertura = qtd_estoque // media_vendas_diaria

                estoque.append({
                    "estoque_id": f"EST{est_counter:05d}",
                    "data": current_date.isoformat(),
                    "produto_id": prod["produto_id"],
                    "loja_id": loja["loja_id"],
                    "qtd_estoque": qtd_estoque,
                    "qtd_vendida_dia": qtd_vendida,
                    "qtd_recebida_dia": qtd_recebida,
                    "is_ruptura": is_ruptura,
                    "is_abaixo_minimo": is_abaixo_minimo,
                    "dias_cobertura": dias_cobertura,
                })

        current_date += timedelta(days=1)

    return estoque


def salvar_csv(dados: list[dict[str, Any]], nome_arquivo: str) -> str:
    """Salva uma lista de dicionários como CSV."""
    if not dados:
        print(f"  ⚠️  {nome_arquivo}: sem dados para salvar")
        return ""

    filepath = os.path.join(OUTPUT_DIR, nome_arquivo)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

    print(f"  ✅ {nome_arquivo}: {len(dados)} registros")
    return filepath


def main() -> None:
    """Função principal de geração de dados."""
    print("=" * 60)
    print("☕ Grão Nobre — Gerador de Dados Sintéticos")
    print("=" * 60)
    print(f"Período: {DATA_INICIO} até {DATA_FIM}")
    print(f"Saída: {OUTPUT_DIR}")
    print()

    # 1. Dimensões
    print("📦 Gerando dimensões...")
    produtos = gerar_dim_produtos()
    salvar_csv(produtos, "dim_produtos.csv")

    lojas = gerar_dim_lojas()
    salvar_csv(lojas, "dim_lojas.csv")

    canais = gerar_dim_canais_marketing()
    salvar_csv(canais, "dim_canais_marketing.csv")

    campanhas = gerar_dim_campanhas(canais)
    salvar_csv(campanhas, "dim_campanhas.csv")

    clientes = gerar_dim_clientes(550)
    # Clientes serão salvos depois de atualizar segmentos

    calendario = gerar_dim_calendario()
    salvar_csv(calendario, "dim_calendario.csv")

    # 2. Fatos
    print("\n📊 Gerando fatos...")
    vendas = gerar_fato_vendas(clientes, produtos, lojas, campanhas, canais)
    salvar_csv(vendas, "fato_vendas.csv")

    # Atualizar segmentos dos clientes baseado nas vendas
    atualizar_segmentos_clientes(clientes, vendas)
    salvar_csv(clientes, "dim_clientes.csv")

    marketing = gerar_fato_marketing(canais, campanhas)
    salvar_csv(marketing, "fato_marketing.csv")

    atendimentos = gerar_fato_atendimento(clientes, vendas)
    salvar_csv(atendimentos, "fato_atendimento.csv")

    estoque = gerar_fato_estoque(produtos, lojas, vendas)
    salvar_csv(estoque, "fato_estoque.csv")

    # 3. Resumo
    print("\n" + "=" * 60)
    print("📋 Resumo da Geração")
    print("=" * 60)
    print(f"  Clientes:     {len(clientes)}")
    print(f"  Produtos:     {len(produtos)}")
    print(f"  Lojas:        {len(lojas)}")
    print(f"  Canais Mkt:   {len(canais)}")
    print(f"  Campanhas:    {len(campanhas)}")
    print(f"  Calendário:   {len(calendario)} dias")
    print(f"  Vendas:       {len(vendas)} itens")
    n_pedidos = len(set(v["pedido_id"] for v in vendas))
    print(f"  Pedidos:      {n_pedidos} únicos")
    print(f"  Marketing:    {len(marketing)} registros")
    print(f"  Atendimento:  {len(atendimentos)} tickets")
    print(f"  Estoque:      {len(estoque)} snapshots")

    # Stats de vendas
    receita_total = sum(v["valor_liquido"] for v in vendas if v["status_pedido"] == "entregue")
    print(f"\n  💰 Receita total (entregue): R$ {receita_total:,.2f}")

    # Distribuição de segmentos
    segmentos = {}
    for c in clientes:
        seg = c["segmento_valor"]
        segmentos[seg] = segmentos.get(seg, 0) + 1
    print(f"\n  👥 Segmentos de clientes:")
    for seg, count in sorted(segmentos.items()):
        print(f"     {seg}: {count}")

    print("\n✅ Geração concluída com sucesso!")


if __name__ == "__main__":
    main()
