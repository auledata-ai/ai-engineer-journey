from datetime import datetime


def select_new_rows(rows: list[dict], watermark: datetime) -> list[dict]:
    return [r for r in rows if r["updated_at"] > watermark]
