import json
from src.dq import check_not_null, check_unique, run_checks
from src.cli import main

ROWS = [{"id": 1, "email": "a@x"}, {"id": 2, "email": None}, {"id": 2, "email": "b@x"}]

def test_not_null():
    assert len(check_not_null(ROWS, "email")) == 1 and check_not_null(ROWS, "id") == []

def test_unique():
    assert len(check_unique(ROWS, "id")) == 1 and check_unique(ROWS, "email") == []

def test_run_checks():
    result = run_checks(ROWS, {"not_null": ["email"], "unique": ["id"]})
    assert result["passed"] is False and len(result["errors"]) == 2
    assert run_checks(ROWS, {"not_null": ["id"], "unique": []})["passed"] is True

def test_cli(tmp_path, capsys):
    inp, cfg = tmp_path / "rows.json", tmp_path / "cfg.json"
    inp.write_text(json.dumps(ROWS)); cfg.write_text(json.dumps({"not_null": ["email"], "unique": ["id"]}))
    assert main(["--input", str(inp), "--config", str(cfg)]) == 1
    assert len(capsys.readouterr().out.strip().splitlines()) == 2
    cfg.write_text(json.dumps({"not_null": ["id"], "unique": []}))
    assert main(["--input", str(inp), "--config", str(cfg)]) == 0
