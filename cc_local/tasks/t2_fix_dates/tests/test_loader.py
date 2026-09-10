from datetime import date
from src.loader import load_orders

CSV = "order_id,order_date,amount\n1,10/09/2025,100.5\n2,,20\n3,31/12/2024,7\n"

def test_brazilian_dates():
    rows = load_orders(CSV)
    assert rows[0]["order_date"] == date(2025, 9, 10)
    assert rows[2]["order_date"] == date(2024, 12, 31)

def test_empty_date_is_none():
    assert load_orders(CSV)[1]["order_date"] is None

def test_types():
    rows = load_orders(CSV)
    assert rows[0]["order_id"] == 1 and rows[1]["amount"] == 20.0
