from datetime import datetime as dt
from src.incremental import plan_batch, select_new_rows

ROWS = [
    {"id": 3, "updated_at": dt(2025, 1, 3)}, {"id": 1, "updated_at": dt(2025, 1, 1)},
    {"id": 2, "updated_at": dt(2025, 1, 2)}, {"id": 4, "updated_at": dt(2025, 1, 3)},
    {"id": 5, "updated_at": dt(2025, 1, 5)},
]

def test_select_new_rows_still_works():
    assert {r["id"] for r in select_new_rows(ROWS, dt(2025, 1, 2))} == {3, 4, 5}

def test_plan_batch_orders_and_limits():
    plan = plan_batch(ROWS, dt(2024, 12, 31), batch_size=3)
    assert [r["id"] for r in plan["rows"]] == [1, 2, 3]
    assert plan["next_watermark"] == dt(2025, 1, 3)
    assert plan["has_more"] is True

def test_plan_batch_last_batch():
    plan = plan_batch(ROWS, dt(2025, 1, 3), batch_size=10)
    assert [r["id"] for r in plan["rows"]] == [5]
    assert plan["has_more"] is False

def test_plan_batch_empty_keeps_watermark():
    plan = plan_batch(ROWS, dt(2025, 1, 5), batch_size=10)
    assert plan["rows"] == [] and plan["next_watermark"] == dt(2025, 1, 5) and plan["has_more"] is False
