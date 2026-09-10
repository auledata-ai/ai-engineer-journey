"""Tarefas de engenharia de dados com verificacao automatica.

Cada tarefa tem: id, categoria, prompt, e um verificador que recebe o texto do modelo
e devolve (passou, motivo). Sem juiz humano nem LLM: a resposta roda e e comparada.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from de_bench.data import DDL, fresh_connection

SYSTEM = (
    "Voce e um engenheiro de dados senior. Responda apenas com o codigo pedido, "
    "dentro de um unico bloco de codigo com a linguagem indicada. Sem explicacoes."
)


def extract_code(text: str, lang: str) -> str:
    blocks = re.findall(r"```(?:\w+)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def sql_matches(model_sql: str, expected_sql: str) -> tuple[bool, str]:
    con = fresh_connection()
    try:
        expected = con.execute(expected_sql).fetchall()
        got = con.execute(model_sql).fetchall()
    except Exception as e:  # noqa: BLE001 - qualquer erro do SQL do modelo e uma falha da tarefa
        return False, f"erro ao executar: {type(e).__name__}: {str(e)[:120]}"
    finally:
        con.close()
    norm = lambda rows: sorted(tuple(str(v) for v in r) for r in rows)  # noqa: E731
    if norm(got) == norm(expected):
        return True, "ok"
    return False, f"resultado diferente: esperado {len(expected)} linhas, obtido {len(got)}"


def run_python(code: str, func_name: str) -> Callable:
    namespace: dict = {}
    exec(code, namespace)  # noqa: S102 - benchmark local, codigo do modelo roda de proposito
    if func_name not in namespace:
        raise NameError(f"funcao {func_name} nao definida")
    return namespace[func_name]


@dataclass
class Task:
    id: str
    category: str
    lang: str
    prompt: str
    check: Callable[[str], tuple[bool, str]]
    max_tokens: int = 1024
    tags: list[str] = field(default_factory=list)


def _sql_task(id: str, question: str, expected_sql: str, tags=None) -> Task:
    prompt = f"Schema DuckDB:\n{DDL}\nEscreva uma query SQL que responda: {question}"
    return Task(
        id=id, category="sql", lang="sql", prompt=prompt, tags=tags or [],
        check=lambda text: sql_matches(extract_code(text, "sql"), expected_sql),
    )


def _python_check(func_name: str, cases: list[tuple[tuple, object]]) -> Callable[[str], tuple[bool, str]]:
    def check(text: str) -> tuple[bool, str]:
        try:
            fn = run_python(extract_code(text, "python"), func_name)
            for args, expected in cases:
                got = fn(*args)
                if isinstance(expected, pd.DataFrame):
                    pd.testing.assert_frame_equal(
                        got.sort_values(list(got.columns)).reset_index(drop=True),
                        expected.sort_values(list(expected.columns)).reset_index(drop=True),
                        check_dtype=False,
                    )
                elif got != expected:
                    return False, f"esperado {expected!r}, obtido {got!r}"
        except Exception as e:  # noqa: BLE001
            return False, f"{type(e).__name__}: {str(e)[:120]}"
        return True, "ok"
    return check


# ---------- SQL ----------

T_SQL_GROUP = _sql_task(
    "sql_total_by_country",
    "o valor total (amount) de pedidos com status 'completed' por pais do cliente, "
    "colunas country e total, ordenado por total decrescente.",
    "SELECT c.country, SUM(o.amount) AS total FROM orders o JOIN customers c USING (customer_id) "
    "WHERE o.status='completed' GROUP BY c.country ORDER BY total DESC",
    tags=["join", "aggregate"],
)

T_SQL_LATEST = _sql_task(
    "sql_latest_order_per_customer",
    "para cada cliente, o pedido mais recente (order_date). Colunas: customer_id, order_id, order_date. "
    "Considere todos os status.",
    "SELECT customer_id, order_id, order_date FROM (SELECT *, ROW_NUMBER() OVER "
    "(PARTITION BY customer_id ORDER BY order_date DESC) rn FROM orders) WHERE rn=1",
    tags=["window"],
)

T_SQL_RUNNING = _sql_task(
    "sql_running_total_by_month",
    "o total mensal de pedidos 'completed' e o acumulado ao longo dos meses. "
    "Colunas: month (primeiro dia do mes, tipo DATE), monthly_total, running_total, ordenado por month.",
    "SELECT month, monthly_total, SUM(monthly_total) OVER (ORDER BY month) AS running_total FROM "
    "(SELECT DATE_TRUNC('month', order_date)::DATE AS month, SUM(amount) AS monthly_total FROM orders "
    "WHERE status='completed' GROUP BY 1) ORDER BY month",
    tags=["window", "date"],
)

T_SQL_ANTI = _sql_task(
    "sql_customers_without_completed_orders",
    "clientes que nao tem nenhum pedido com status 'completed'. Colunas: customer_id, name.",
    "SELECT customer_id, name FROM customers c WHERE NOT EXISTS "
    "(SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id AND o.status='completed')",
    tags=["anti-join"],
)

T_SQL_TOPN = _sql_task(
    "sql_top2_orders_per_customer",
    "os 2 pedidos de maior amount de cada cliente. Colunas: customer_id, order_id, amount. "
    "Em caso de empate, escolha o menor order_id.",
    "SELECT customer_id, order_id, amount FROM (SELECT *, ROW_NUMBER() OVER "
    "(PARTITION BY customer_id ORDER BY amount DESC, order_id) rn FROM orders) WHERE rn<=2",
    tags=["window", "top-n"],
)

T_SQL_RECONCILE = _sql_task(
    "sql_reconcile_order_totals",
    "pedidos cujo amount na tabela orders e diferente da soma de qty*unit_price em order_items. "
    "Colunas: order_id, amount, items_total.",
    "SELECT o.order_id, o.amount, i.items_total FROM orders o JOIN "
    "(SELECT order_id, SUM(qty*unit_price) items_total FROM order_items GROUP BY order_id) i USING (order_id) "
    "WHERE o.amount <> i.items_total",
    tags=["join", "data-quality"],
)

T_SQL_FIX = Task(
    id="sql_fix_duplicated_join",
    category="sql-fix",
    lang="sql",
    tags=["debug", "join"],
    prompt=(
        f"Schema DuckDB:\n{DDL}\n"
        "A query abaixo deveria devolver o total de itens (soma de qty) por pais, mas os numeros estao "
        "inflados porque o join multiplica linhas. Corrija a query mantendo as colunas country e total_qty.\n\n"
        "```sql\nSELECT c.country, SUM(i.qty) AS total_qty\nFROM customers c\n"
        "JOIN orders o ON o.customer_id = c.customer_id\nJOIN order_items i ON i.order_id = o.order_id\n"
        "JOIN orders o2 ON o2.customer_id = c.customer_id\nGROUP BY c.country\n```"
    ),
    check=lambda text: sql_matches(
        extract_code(text, "sql"),
        "SELECT c.country, SUM(i.qty) total_qty FROM customers c JOIN orders o ON o.customer_id=c.customer_id "
        "JOIN order_items i ON i.order_id=o.order_id GROUP BY c.country",
    ),
)

# ---------- Python / pandas ----------

_dedup_in = pd.DataFrame({
    "id": [1, 1, 2, 3, 3, 3],
    "value": ["a", "b", "c", "d", "e", "f"],
    "updated_at": pd.to_datetime(["2025-01-01", "2025-01-05", "2025-02-01", "2025-03-01", "2025-03-03", "2025-03-02"]),
})
_dedup_out = pd.DataFrame({
    "id": [1, 2, 3], "value": ["b", "c", "e"],
    "updated_at": pd.to_datetime(["2025-01-05", "2025-02-01", "2025-03-03"]),
})

T_PY_DEDUP = Task(
    id="py_dedup_keep_latest",
    category="python",
    lang="python",
    tags=["pandas", "dedup"],
    prompt=(
        "Escreva uma funcao Python `dedup_latest(df: pd.DataFrame) -> pd.DataFrame` usando pandas. "
        "O DataFrame tem colunas id, value, updated_at (datetime). Devolva uma linha por id, "
        "mantendo a de updated_at mais recente. Preserve as tres colunas. Inclua o import de pandas."
    ),
    check=_python_check("dedup_latest", [((_dedup_in.copy(),), _dedup_out)]),
)

_flat_in = [
    {"order_id": 1, "customer": {"id": 10, "country": "PT"}, "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]},
    {"order_id": 2, "customer": {"id": 11, "country": "BR"}, "items": [{"sku": "C", "qty": 5}]},
]
_flat_out = pd.DataFrame({
    "order_id": [1, 1, 2], "customer_id": [10, 10, 11], "country": ["PT", "PT", "BR"],
    "sku": ["A", "B", "C"], "qty": [2, 1, 5],
})

T_PY_FLATTEN = Task(
    id="py_flatten_nested_orders",
    category="python",
    lang="python",
    tags=["json", "flatten"],
    prompt=(
        "Escreva uma funcao Python `flatten_orders(records: list[dict]) -> pd.DataFrame`. "
        "Cada registro tem o formato {'order_id': int, 'customer': {'id': int, 'country': str}, "
        "'items': [{'sku': str, 'qty': int}, ...]}. Devolva um DataFrame com uma linha por item e as colunas, "
        "nesta ordem: order_id, customer_id, country, sku, qty. Inclua o import de pandas."
    ),
    check=_python_check("flatten_orders", [((_flat_in,), _flat_out)]),
)

T_PY_FIX = Task(
    id="py_fix_date_parsing",
    category="python-fix",
    lang="python",
    tags=["debug", "dates"],
    prompt=(
        "A funcao abaixo quebra em producao com `ValueError: time data '2025-13-01' does not match format`. "
        "As datas chegam como 'YYYY-MM-DD' ou 'DD/MM/YYYY' e algumas sao invalidas. "
        "Corrija a funcao para: aceitar os dois formatos, devolver `None` para datas invalidas, "
        "e manter a assinatura `parse_date(s: str) -> datetime | None`. Inclua os imports.\n\n"
        "```python\nfrom datetime import datetime\n\ndef parse_date(s: str) -> datetime:\n"
        "    return datetime.strptime(s, '%Y-%m-%d')\n```"
    ),
    check=_python_check("parse_date", [
        (("2025-09-10",), __import__("datetime").datetime(2025, 9, 10)),
        (("10/09/2025",), __import__("datetime").datetime(2025, 9, 10)),
        (("2025-13-01",), None),
        (("abc",), None),
    ]),
)


def _dq_check(text: str) -> tuple[bool, str]:
    raw = extract_code(text, "json")
    try:
        rules = json.loads(raw)
        got = {(r["column"], r["rule"]) for r in rules}
    except Exception as e:  # noqa: BLE001
        return False, f"JSON invalido: {type(e).__name__}"
    expected = {("order_id", "not_null"), ("order_id", "unique"), ("customer_id", "not_null"),
                ("status", "accepted_values"), ("amount", "min")}
    missing = expected - got
    return (not missing), ("ok" if not missing else f"faltam {sorted(missing)}")


T_DQ_RULES = Task(
    id="dq_rules_from_profile",
    category="data-quality",
    lang="json",
    tags=["structured-output", "dq"],
    prompt=(
        "Tabela orders com o perfil abaixo. Gere regras de qualidade como um JSON: lista de objetos "
        "com as chaves column e rule. Use apenas os valores de rule: not_null, unique, accepted_values, min. "
        "Inclua exatamente as regras que o perfil justifica.\n\n"
        "order_id: inteiro, 0% nulos, 100% valores distintos, chave primaria\n"
        "customer_id: inteiro, 0% nulos, chave estrangeira para customers\n"
        "order_date: data, 0% nulos\n"
        "status: texto, valores observados: completed, cancelled, pending\n"
        "amount: decimal, minimo observado 50.00, sem valores negativos permitidos"
    ),
    check=_dq_check,
)

TASKS: list[Task] = [
    T_SQL_GROUP, T_SQL_LATEST, T_SQL_RUNNING, T_SQL_ANTI, T_SQL_TOPN, T_SQL_RECONCILE, T_SQL_FIX,
    T_PY_DEDUP, T_PY_FLATTEN, T_PY_FIX, T_DQ_RULES,
]
