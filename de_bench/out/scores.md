## Score por modelo

| modelo | pass | tokens out (media) | latencia ms (media) | custo total USD |
|---|---|---|---|---|
| qwen3:8b | 9/11 (82%) | 75 | 2900 | 0.0000 |
| qwen3:8b+think | 10/11 (91%) | 938 | 25576 | 0.0000 |
| llama3.1:8b | 9/11 (82%) | 83 | 2879 | 0.0000 |
| claude-haiku-4-5 | 11/11 (100%) | 108 | 1962 | 0.0082 |
| claude-sonnet-5 | 11/11 (100%) | 136 | 2259 | 0.0216 |
| claude-opus-5 | 10/11 (91%) | 155 | 2956 | 0.0591 |

## Tarefa x modelo

| tarefa | qwen3:8b | qwen3:8b+think | llama3.1:8b | claude-haiku-4-5 | claude-sonnet-5 | claude-opus-5 |
|---|---|---|---|---|---|---|
| sql_total_by_country | pass | pass | pass | pass | pass | pass |
| sql_latest_order_per_customer | pass | pass | pass | pass | pass | pass |
| sql_running_total_by_month | FAIL (erro ao executar: BinderException: Binde) | pass | FAIL (resultado diferente: esperado 4 linhas, ) | pass | pass | FAIL (erro ao executar: BinderException: Binde) |
| sql_customers_without_completed_orders | FAIL (resultado diferente: esperado 2 linhas, ) | pass | pass | pass | pass | pass |
| sql_top2_orders_per_customer | pass | pass | pass | pass | pass | pass |
| sql_reconcile_order_totals | pass | FAIL (erro ao executar: BinderException: Binde) | pass | pass | pass | pass |
| sql_fix_duplicated_join | pass | pass | pass | pass | pass | pass |
| py_dedup_keep_latest | pass | pass | pass | pass | pass | pass |
| py_flatten_nested_orders | pass | pass | pass | pass | pass | pass |
| py_fix_date_parsing | pass | pass | FAIL (esperado datetime.datetime(2025, 9, 10, ) | pass | pass | pass |
| dq_rules_from_profile | pass | pass | pass | pass | pass | pass |
