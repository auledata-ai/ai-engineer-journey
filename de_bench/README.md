# DE-Bench: tarefas de engenharia de dados para comparar LLMs

Benchmark de tarefas reais de engenharia de dados (SQL, pandas, debugging, qualidade de dados)
com **verificação por execução**: a resposta do modelo roda contra DuckDB ou pandas e é comparada
ao resultado esperado. Sem juiz humano nem LLM.

Resultado mais recente em [out/scores.md](out/scores.md).

## Por que existe
Responder, com números, onde um modelo local de 8B basta e onde um modelo pago compensa,
nas tarefas que eu faço no dia a dia. Também é o golden dataset dos projetos seguintes
(regressão em CI, juiz calibrado).

## Como rodar
```bash
uv sync
ollama pull qwen3:8b llama3.1:8b
uv run pytest de_bench/test_tasks.py      # sanidade: referências passam no verificador
uv run python -m de_bench.runner          # roda tudo, escreve out/scores.md
```
Com `ANTHROPIC_API_KEY` no `.env`, os modelos Claude entram automaticamente.

## Tarefas
| id | categoria | o que testa |
|---|---|---|
| sql_total_by_country | sql | join + agregação |
| sql_latest_order_per_customer | sql | window (ROW_NUMBER) |
| sql_running_total_by_month | sql | window acumulada + truncar data |
| sql_customers_without_completed_orders | sql | anti-join |
| sql_top2_orders_per_customer | sql | top-N por grupo com desempate |
| sql_reconcile_order_totals | sql | reconciliação header vs itens |
| sql_fix_duplicated_join | sql-fix | achar e remover join que multiplica linhas |
| py_dedup_keep_latest | python | dedup mantendo o mais recente |
| py_flatten_nested_orders | python | achatar JSON aninhado |
| py_fix_date_parsing | python-fix | corrigir parser para 2 formatos + inválidos |
| dq_rules_from_profile | data-quality | gerar regras como JSON estruturado |

## Decisões
- **Verificação por execução, não por string.** Duas queries diferentes que dão o mesmo resultado são ambas corretas.
- **Comparação por valor.** `200` e `200.00`, `DATE` e `TIMESTAMP` à meia-noite contam como iguais.
- **Temperatura 0.** Reprodutibilidade acima de criatividade.
- **Referência testada.** Cada tarefa tem uma resposta gabarito que precisa passar no próprio verificador. Se o gabarito falha, o bug é do benchmark.

## O que não funcionou (e virou lição)
- Prompt "total mensal de pedidos" foi lido como contagem por um modelo e como soma por outro. Prompt ambíguo gera falso negativo. Reescrito para "soma de amount".
- Comparar `str(valor)` reprovou `DATE` vs `TIMESTAMP`. Comparador reescrito por valor.
- Endpoint compatível com OpenAI do Ollama não desliga o raciocínio do Qwen3. Usado o endpoint nativo.
