## Score por modelo

| modelo | pass | tokens out (media) | latencia ms (media) | custo total USD |
|---|---|---|---|---|
| qwen3:8b | 9/11 (82%) | 75 | 2952 | 0.0000 |
| qwen3:8b+think | 10/11 (91%) | 938 | 24949 | 0.0000 |
| llama3.1:8b | 9/11 (82%) | 83 | 2795 | 0.0000 |

## Tarefa x modelo

| tarefa | qwen3:8b | qwen3:8b+think | llama3.1:8b |
|---|---|---|---|
| sql_total_by_country | pass | pass | pass |
| sql_latest_order_per_customer | pass | pass | pass |
| sql_running_total_by_month | FAIL (erro ao executar: BinderException: Binde) | pass | FAIL (resultado diferente: esperado 4 linhas, ) |
| sql_customers_without_completed_orders | FAIL (resultado diferente: esperado 2 linhas, ) | pass | pass |
| sql_top2_orders_per_customer | pass | pass | pass |
| sql_reconcile_order_totals | pass | FAIL (erro ao executar: BinderException: Binde) | pass |
| sql_fix_duplicated_join | pass | pass | pass |
| py_dedup_keep_latest | pass | pass | pass |
| py_flatten_nested_orders | pass | pass | pass |
| py_fix_date_parsing | pass | pass | FAIL (esperado datetime.datetime(2025, 9, 10, ) |
| dq_rules_from_profile | pass | pass | pass |
