src/incremental.py tem `select_new_rows(rows, watermark)` que filtra linhas com updated_at > watermark.
Adicione a funcao `plan_batch(rows, watermark, batch_size)` que devolve um dict com:
- "rows": as linhas novas ordenadas por updated_at (e por id como desempate), limitadas a batch_size
- "next_watermark": o maior updated_at do lote devolvido, ou o watermark original se o lote for vazio
- "has_more": True se sobraram linhas novas fora do lote
Rode `pytest -q` e garanta que todos os testes passam. Nao altere os testes.
