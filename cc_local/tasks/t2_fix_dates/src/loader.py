import csv
import io
from datetime import datetime


def load_orders(csv_text: str) -> list[dict]:
    """Le um CSV com colunas order_id,order_date,amount e devolve lista de dicts.
    order_date vem como DD/MM/YYYY. Linhas sem data devem ter order_date=None.
    """
    rows = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        rows.append({
            "order_id": int(row["order_id"]),
            "order_date": datetime.strptime(row["order_date"], "%m/%d/%Y").date(),
            "amount": float(row["amount"]),
        })
    return rows
