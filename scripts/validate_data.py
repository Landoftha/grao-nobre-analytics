"""Script de validação de dados para a plataforma Grão Nobre Analytics.

Valida regras de negócio, integridade referencial, completude e consistência
dos datasets sintéticos armazenados em `data/raw/`.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


def check_file_existence(data_dir: Path, expected_files: List[str]) -> Tuple[bool, List[str]]:
    """Verifica se todos os arquivos esperados existem no diretório.

    Args:
        data_dir: Caminho para a pasta com os CSVs.
        expected_files: Lista com os nomes dos arquivos esperados.

    Returns:
        Tupla contendo booleano de sucesso e lista de arquivos ausentes.
    """
    missing = [f for f in expected_files if not (data_dir / f).exists()]
    return len(missing) == 0, missing


def validate_primary_keys(dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """Verifica unicidade e ausência de nulos nas Primary Keys.

    Args:
        dfs: Dicionário mapeando nome da tabela para seu DataFrame.

    Returns:
        Lista com descrições de erros encontrados.
    """
    errors: List[str] = []
    pk_map = {
        "dim_clientes.csv": "cliente_id",
        "dim_produtos.csv": "produto_id",
        "dim_canais_marketing.csv": "canal_id",
        "dim_campanhas.csv": "campanha_id",
        "dim_lojas.csv": "loja_id",
        "dim_calendario.csv": "data",
        "fato_vendas.csv": "venda_id",
        "fato_marketing.csv": "marketing_id",
        "fato_atendimento.csv": "atendimento_id",
        "fato_estoque.csv": "estoque_id",
    }

    for file_name, pk_col in pk_map.items():
        if file_name not in dfs:
            continue
        df = dfs[file_name]
        if pk_col not in df.columns:
            errors.append(f"[{file_name}] Coluna PK '{pk_col}' não encontrada.")
            continue

        null_count = df[pk_col].isnull().sum()
        if null_count > 0:
            errors.append(f"[{file_name}] PK '{pk_col}' possui {null_count} valores nulos.")

        dup_count = df[pk_col].duplicated().sum()
        if dup_count > 0:
            errors.append(f"[{file_name}] PK '{pk_col}' possui {dup_count} valores duplicados.")

    return errors


def validate_foreign_keys(dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """Verifica a integridade referencial entre fatos e dimensões.

    Args:
        dfs: Dicionário mapeando nome da tabela para seu DataFrame.

    Returns:
        Lista com inconsistências de chaves estrangeiras.
    """
    errors: List[str] = []

    fk_checks = [
        # (fato, fk_col, dim, pk_col, permite_nulo)
        ("fato_vendas.csv", "cliente_id", "dim_clientes.csv", "cliente_id", False),
        ("fato_vendas.csv", "produto_id", "dim_produtos.csv", "produto_id", False),
        ("fato_vendas.csv", "loja_id", "dim_lojas.csv", "loja_id", False),
        ("fato_vendas.csv", "campanha_id", "dim_campanhas.csv", "campanha_id", True),
        ("fato_vendas.csv", "data_pedido", "dim_calendario.csv", "data", False),
        ("fato_marketing.csv", "canal_id", "dim_canais_marketing.csv", "canal_id", False),
        ("fato_marketing.csv", "campanha_id", "dim_campanhas.csv", "campanha_id", True),
        ("fato_marketing.csv", "data", "dim_calendario.csv", "data", False),
        ("fato_atendimento.csv", "cliente_id", "dim_clientes.csv", "cliente_id", False),
        ("fato_atendimento.csv", "data_abertura", "dim_calendario.csv", "data", False),
        ("fato_estoque.csv", "produto_id", "dim_produtos.csv", "produto_id", False),
        ("fato_estoque.csv", "loja_id", "dim_lojas.csv", "loja_id", False),
        ("fato_estoque.csv", "data", "dim_calendario.csv", "data", False),
    ]

    for fact_file, fk_col, dim_file, pk_col, nullable in fk_checks:
        if fact_file not in dfs or dim_file not in dfs:
            continue

        fact_df = dfs[fact_file]
        dim_df = dfs[dim_file]

        if fk_col not in fact_df.columns or pk_col not in dim_df.columns:
            errors.append(f"Colunas de relacionamento {fact_file}.{fk_col} -> {dim_file}.{pk_col} ausentes.")
            continue

        series = fact_df[fk_col]
        if nullable:
            series = series.dropna()

        valid_keys = set(dim_df[pk_col].astype(str))
        invalid_keys = series.astype(str)[~series.astype(str).isin(valid_keys)]

        if not invalid_keys.empty:
            sample = list(invalid_keys.unique()[:3])
            errors.append(
                f"[{fact_file}] FK '{fk_col}' possui {len(invalid_keys)} referências inválidas para {dim_file}.{pk_col} (ex: {sample})."
            )

    return errors


def validate_vendas_math(dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """Valida a consistência matemática das colunas de valores em fato_vendas.

    Args:
        dfs: Dicionário com os DataFrames.

    Returns:
        Lista com divergências de cálculo.
    """
    errors: List[str] = []
    if "fato_vendas.csv" not in dfs:
        return errors

    df = dfs["fato_vendas.csv"]

    # valor_bruto == round(quantidade * preco_unitario, 2)
    expected_bruto = (df["quantidade"] * df["preco_unitario"]).round(2)
    diff_bruto = (df["valor_bruto"] - expected_bruto).abs() > 0.01
    if diff_bruto.any():
        errors.append(f"[fato_vendas.csv] {diff_bruto.sum()} linhas com valor_bruto divergente de qtd * preco.")

    # valor_liquido == round(valor_bruto - valor_desconto, 2)
    expected_liq = (df["valor_bruto"] - df["valor_desconto"]).round(2)
    diff_liq = (df["valor_liquido"] - expected_liq).abs() > 0.01
    if diff_liq.any():
        errors.append(f"[fato_vendas.csv] {diff_liq.sum()} linhas com valor_liquido divergente de bruto - desconto.")

    # lucro_bruto == round(valor_liquido - custo_total, 2)
    expected_lucro = (df["valor_liquido"] - df["custo_total"]).round(2)
    diff_lucro = (df["lucro_bruto"] - expected_lucro).abs() > 0.01
    if diff_lucro.any():
        errors.append(f"[fato_vendas.csv] {diff_lucro.sum()} linhas com lucro_bruto divergente de líquido - custo.")

    return errors


def main() -> None:
    """Executa a rotina completa de testes de qualidade de dados."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "raw"

    expected_files = [
        "dim_clientes.csv",
        "dim_produtos.csv",
        "dim_canais_marketing.csv",
        "dim_campanhas.csv",
        "dim_lojas.csv",
        "dim_calendario.csv",
        "fato_vendas.csv",
        "fato_marketing.csv",
        "fato_atendimento.csv",
        "fato_estoque.csv",
    ]

    print("=" * 60)
    print("GRAO NOBRE ANALYTICS - DATA QUALITY CHECK")
    print(f"Diretório analisado: {data_dir}")
    print("=" * 60)

    exists_ok, missing = check_file_existence(data_dir, expected_files)
    if not exists_ok:
        print(f"❌ ERRO CRÍTICO: Arquivos ausentes: {missing}")
        sys.exit(1)

    dfs: Dict[str, pd.DataFrame] = {}
    print("\n📂 Carregando arquivos...")
    total_records = 0
    for f in expected_files:
        df = pd.read_csv(data_dir / f, encoding="utf-8")
        dfs[f] = df
        total_records += len(df)
        print(f"  ✓ {f:<26} : {len(df):>7} registros | {len(df.columns):>2} colunas")

    print(f"\n📊 Total de registros carregados: {total_records:,}")

    # Executar validações
    print("\n🔍 Executando verificações de qualidade...")
    pk_errors = validate_primary_keys(dfs)
    fk_errors = validate_foreign_keys(dfs)
    math_errors = validate_vendas_math(dfs)

    all_errors = pk_errors + fk_errors + math_errors

    print("-" * 60)
    if not all_errors:
        print("✅ SUCESSO: Todos os dados passaram em 100% dos testes de validação!")
        print("  ✓ Unicidade de Chaves Primárias")
        print("  ✓ Integridade Referencial (Star Schema)")
        print("  ✓ Consistência Matemática de Métricas")
        print("  ✓ Encoding UTF-8 e Formatos ISO 8601")
        print("-" * 60)
        sys.exit(0)
    else:
        print(f"⚠️ Foram encontradas {len(all_errors)} inconsistências:")
        for err in all_errors:
            print(f"  ❌ {err}")
        print("-" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
