# Grão Nobre Analytics — Agent Rules

## Contexto
Este workspace contém o projeto **Grão Nobre Analytics Platform**, um projeto educacional completo
de analytics para uma empresa fictícia de cafés especiais.

## Regras Gerais

1. **Sempre consulte a skill `grao_nobre`** antes de trabalhar em qualquer task do projeto.
2. **Responda em português brasileiro** (PT-BR), a menos que o código ou nomes técnicos exijam inglês.
3. **Siga as convenções** documentadas em `docs/ARCHITECTURE.md` para nomes de arquivos, branches e commits.
4. **Valide dados** contra as regras em `docs/DATA_DICTIONARY.md` após qualquer geração ou transformação.
5. **Atualize o roadmap** em `docs/ROADMAP.md` quando concluir tasks.

## Regras de Dados
- Nunca gere dados com valores NULL em campos obrigatórios.
- Sempre use UTF-8 e ISO 8601 para datas.
- Mantenha integridade referencial entre fatos e dimensões.
- Valores monetários sempre com 2 casas decimais.

## Regras de Código
- Python: PEP 8, type hints, Google docstrings.
- SQL: snake_case, CTEs sobre subqueries.
- DAX: medidas numa tabela `_Medidas` com prefixo de área.
- Commits: Conventional Commits em PT-BR.

## Regras de Documentação
- Mantenha todos os docs em `docs/` atualizados.
- Notebooks devem ter markdown cells explicando cada análise.
- Todo insight deve ter visualização correspondente.
