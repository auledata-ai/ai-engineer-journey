"""Claude Code com modelos locais vs Anthropic: mesmo harness, mesmas tarefas, medir o que muda.

Para cada (modelo, tarefa): copia a tarefa para um diretorio temporario, roda
`claude -p` nao interativo, depois roda pytest. Registra sucesso, turnos, tempo, tokens, custo.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
TASKS_DIR = HERE / "tasks"
OUT = HERE / "out"
PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]


@dataclass
class ModelConfig:
    label: str
    env: dict = field(default_factory=dict)  # variaveis extras para o claude
    model_flag: str | None = None  # --model


OLLAMA = {"ANTHROPIC_BASE_URL": "http://localhost:11434", "ANTHROPIC_AUTH_TOKEN": "ollama"}

MODELS = [
    ModelConfig("claude-sonnet-5", model_flag="claude-sonnet-5"),
    ModelConfig("qwen3-coder:30b", env={**OLLAMA, "ANTHROPIC_MODEL": "qwen3-coder:30b",
                                         "ANTHROPIC_SMALL_FAST_MODEL": "qwen3-coder:30b"}),
    ModelConfig("glm-4.7-flash", env={**OLLAMA, "ANTHROPIC_MODEL": "glm-4.7-flash",
                                       "ANTHROPIC_SMALL_FAST_MODEL": "glm-4.7-flash"}),
]

MAX_TURNS = 25
TIMEOUT_S = 900


@dataclass
class Run:
    model: str
    task: str
    passed: bool
    tests: str
    num_turns: int
    duration_s: float
    tokens_in: int
    tokens_out: int
    cost_usd: float
    is_error: bool
    note: str


def run_one(cfg: ModelConfig, task_dir: Path) -> Run:
    prompt = (task_dir / "TASK.md").read_text()
    with tempfile.TemporaryDirectory(prefix=f"cc_{task_dir.name}_") as tmp:
        work = Path(tmp) / task_dir.name
        shutil.copytree(task_dir, work)
        env = {**os.environ, **cfg.env, "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
        cmd = ["claude", "-p", prompt, "--output-format", "json", "--max-turns", str(MAX_TURNS),
               "--dangerously-skip-permissions"]
        if cfg.model_flag:
            cmd += ["--model", cfg.model_flag]
        start = time.perf_counter()
        note, data = "", {}
        try:
            proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=TIMEOUT_S)
            raw = proc.stdout.strip().splitlines()
            data = json.loads(raw[-1]) if raw else {}
            if proc.returncode != 0 and not data:
                note = f"exit {proc.returncode}: {proc.stderr.strip()[-200:]}"
        except subprocess.TimeoutExpired:
            note = f"timeout apos {TIMEOUT_S}s"
        except json.JSONDecodeError:
            note = "saida nao era JSON"
        duration = time.perf_counter() - start

        test = subprocess.run(PYTEST, cwd=work, capture_output=True, text=True)
        summary = test.stdout.strip().splitlines()[-1] if test.stdout.strip() else "sem saida"
        usage = data.get("usage", {})
        return Run(
            model=cfg.label, task=task_dir.name, passed=test.returncode == 0, tests=summary,
            num_turns=data.get("num_turns", 0), duration_s=round(duration, 1),
            tokens_in=usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0),
            tokens_out=usage.get("output_tokens", 0), cost_usd=round(data.get("total_cost_usd", 0.0), 4),
            is_error=bool(data.get("is_error", False)), note=note or str(data.get("result", ""))[:100],
        )


def summarize(runs: list[Run]) -> str:
    models = list(dict.fromkeys(r.model for r in runs))
    tasks = list(dict.fromkeys(r.task for r in runs))
    lines = ["## Score por modelo", "", "| modelo | tarefas ok | turnos (media) | tempo medio | custo total |", "|---|---|---|---|---|"]
    for m in models:
        rs = [r for r in runs if r.model == m]
        lines.append(f"| {m} | {sum(r.passed for r in rs)}/{len(rs)} | {sum(r.num_turns for r in rs)/len(rs):.1f} | "
                     f"{sum(r.duration_s for r in rs)/len(rs):.0f}s | ${sum(r.cost_usd for r in rs):.2f} |")
    lines += ["", "## Tarefa x modelo", "", "| tarefa | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    for t in tasks:
        cells = []
        for m in models:
            r = next(x for x in runs if x.model == m and x.task == t)
            cells.append(("pass" if r.passed else "FAIL") + f" ({r.num_turns}t, {r.duration_s:.0f}s)")
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main(only: list[str] | None = None) -> None:
    tasks = sorted(p for p in TASKS_DIR.iterdir() if p.is_dir())
    configs = [c for c in MODELS if not only or c.label in only]
    runs: list[Run] = []
    for cfg in configs:
        for task in tasks:
            r = run_one(cfg, task)
            runs.append(r)
            print(f"{r.model:16} {r.task:20} {'pass' if r.passed else 'FAIL':4} turns={r.num_turns:3} "
                  f"{r.duration_s:6.0f}s ${r.cost_usd:.3f}  {r.tests[:40]}  {r.note[:60]}", flush=True)
    OUT.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    with open(OUT / f"runs-{stamp}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Run.__dataclass_fields__))
        w.writeheader()
        w.writerows(asdict(r) for r in runs)
    (OUT / "scores.md").write_text(summarize(runs))
    print("\n" + summarize(runs))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
