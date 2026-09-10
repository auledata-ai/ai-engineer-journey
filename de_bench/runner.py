"""Roda todas as tarefas em todos os modelos e escreve out/scores.md e out/runs.csv."""

import csv
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from common.llm import ModelSpec, complete
from de_bench.tasks import SYSTEM, TASKS, Task

OUT = Path(__file__).parent / "out"

MODELS = [
    ModelSpec("qwen3:8b", "qwen3:8b", "ollama"),
    ModelSpec("qwen3:8b+think", "qwen3:8b", "ollama", think=True),
    ModelSpec("llama3.1:8b", "llama3.1:8b", "ollama"),
    # Precos USD/1M tokens, docs Anthropic set/2026. Ativos apenas com ANTHROPIC_API_KEY.
    ModelSpec("claude-haiku-4-5", "claude-haiku-4-5", "anthropic", 1.00, 5.00),
    ModelSpec("claude-sonnet-5", "claude-sonnet-5", "anthropic", 2.00, 10.00),
]


@dataclass
class Run:
    model: str
    task: str
    category: str
    passed: bool
    reason: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    stop_reason: str
    output: str


def run_task(spec: ModelSpec, task: Task) -> Run:
    max_tokens = task.max_tokens * (4 if spec.think else 1)
    start = time.perf_counter()
    text, tin, tout, stop = complete(spec, task.prompt, system=SYSTEM, max_tokens=max_tokens)
    latency = round((time.perf_counter() - start) * 1000)
    passed, reason = task.check(text)
    return Run(spec.label, task.id, task.category, passed, reason, tin, tout,
               round(spec.cost(tin, tout), 6), latency, stop, text)


def summarize(runs: list[Run]) -> str:
    models = list(dict.fromkeys(r.model for r in runs))
    lines = ["## Score por modelo", "", "| modelo | pass | tokens out (media) | latencia ms (media) | custo total USD |", "|---|---|---|---|---|"]
    for m in models:
        rs = [r for r in runs if r.model == m]
        n_pass = sum(r.passed for r in rs)
        lines.append(f"| {m} | {n_pass}/{len(rs)} ({100*n_pass/len(rs):.0f}%) | "
                     f"{sum(r.tokens_out for r in rs)/len(rs):.0f} | {sum(r.latency_ms for r in rs)/len(rs):.0f} | "
                     f"{sum(r.cost_usd for r in rs):.4f} |")
    lines += ["", "## Tarefa x modelo", "", "| tarefa | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    for t in TASKS:
        cells = []
        for m in models:
            r = next(x for x in runs if x.model == m and x.task == t.id)
            cells.append("pass" if r.passed else f"FAIL ({r.reason[:40]})")
        lines.append(f"| {t.id} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    active = [m for m in MODELS if m.provider == "ollama" or os.getenv("ANTHROPIC_API_KEY")]
    runs: list[Run] = []
    for spec in active:
        for task in TASKS:
            r = run_task(spec, task)
            runs.append(r)
            print(f"{spec.label:16} {task.id:36} {'pass' if r.passed else 'FAIL':4} "
                  f"out={r.tokens_out:5} {r.latency_ms:6}ms  {r.reason[:50]}")
    OUT.mkdir(exist_ok=True)
    with open(OUT / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Run.__dataclass_fields__))
        w.writeheader()
        w.writerows(asdict(r) for r in runs)
    (OUT / "scores.md").write_text(summarize(runs))
    print(f"\n{summarize(runs)}")


if __name__ == "__main__":
    main()
