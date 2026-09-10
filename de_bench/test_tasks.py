"""Sanidade: a resposta de referencia de cada tarefa deve passar no proprio verificador."""

import pytest

from de_bench import tasks as T

REFERENCE = {
    "sql_total_by_country": "```sql\nSELECT c.country, SUM(o.amount) total FROM orders o JOIN customers c USING (customer_id) WHERE o.status='completed' GROUP BY 1 ORDER BY 2 DESC\n```",
    "sql_latest_order_per_customer": "```sql\nSELECT customer_id, order_id, order_date FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) rn FROM orders) WHERE rn=1\n```",
    "sql_running_total_by_month": "```sql\nWITH m AS (SELECT DATE_TRUNC('month', order_date)::DATE AS month, SUM(amount) AS monthly_total FROM orders WHERE status='completed' GROUP BY 1) SELECT month, monthly_total, SUM(monthly_total) OVER (ORDER BY month) running_total FROM m ORDER BY 1\n```",
    "sql_customers_without_completed_orders": "```sql\nSELECT customer_id, name FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders WHERE status='completed')\n```",
    "sql_top2_orders_per_customer": "```sql\nSELECT customer_id, order_id, amount FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC, order_id) rn FROM orders) WHERE rn<=2\n```",
    "sql_reconcile_order_totals": "```sql\nSELECT o.order_id, o.amount, SUM(i.qty*i.unit_price) items_total FROM orders o JOIN order_items i USING (order_id) GROUP BY 1,2 HAVING o.amount <> SUM(i.qty*i.unit_price)\n```",
    "sql_fix_duplicated_join": "```sql\nSELECT c.country, SUM(i.qty) total_qty FROM customers c JOIN orders o ON o.customer_id=c.customer_id JOIN order_items i ON i.order_id=o.order_id GROUP BY 1\n```",
    "py_dedup_keep_latest": "```python\nimport pandas as pd\ndef dedup_latest(df):\n    return df.sort_values('updated_at').drop_duplicates('id', keep='last').reset_index(drop=True)\n```",
    "py_flatten_nested_orders": "```python\nimport pandas as pd\ndef flatten_orders(records):\n    rows=[{'order_id':r['order_id'],'customer_id':r['customer']['id'],'country':r['customer']['country'],'sku':i['sku'],'qty':i['qty']} for r in records for i in r['items']]\n    return pd.DataFrame(rows, columns=['order_id','customer_id','country','sku','qty'])\n```",
    "py_fix_date_parsing": "```python\nfrom datetime import datetime\ndef parse_date(s):\n    for fmt in ('%Y-%m-%d','%d/%m/%Y'):\n        try:\n            return datetime.strptime(s, fmt)\n        except ValueError:\n            pass\n    return None\n```",
    "dq_rules_from_profile": '```json\n[{"column":"order_id","rule":"not_null"},{"column":"order_id","rule":"unique"},{"column":"customer_id","rule":"not_null"},{"column":"order_date","rule":"not_null"},{"column":"status","rule":"accepted_values"},{"column":"amount","rule":"min"}]\n```',
}


@pytest.mark.parametrize("task", T.TASKS, ids=lambda t: t.id)
def test_reference_passes(task):
    passed, reason = task.check(REFERENCE[task.id])
    assert passed, reason


def test_wrong_sql_fails():
    passed, _ = T.T_SQL_GROUP.check("```sql\nSELECT 1\n```")
    assert not passed
