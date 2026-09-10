Crie um verificador de qualidade de dados em src/dq.py com:
- `check_not_null(rows, column) -> list[str]`: lista de mensagens de erro, uma por linha com valor None
- `check_unique(rows, column) -> list[str]`: uma mensagem por valor duplicado
- `run_checks(rows, config) -> dict` onde config e {"not_null": [cols], "unique": [cols]} e o retorno e
  {"passed": bool, "errors": [mensagens]}
E um CLI em src/cli.py com `main(argv) -> int` que le um JSON de linhas (--input), um JSON de config
(--config) e devolve 0 se passou, 1 se falhou, imprimindo cada erro em uma linha.
Rode `pytest -q` e garanta que todos os testes passam.
