"""Gerador + revisor: o revisor ajuda ou atrapalha?

Para cada tarefa do DE-Bench e cada par (gerador, revisor):
1. gerador escreve o codigo            -> testa (antes)
2. revisor recebe tarefa + codigo, devolve veredito JSON e codigo corrigido
3. aplica o codigo final               -> testa (depois)

Metricas: acerto antes/depois, precisao do revisor (veredito bate com os testes?),
dano (quebrou o que passava), tokens e custo por etapa.
"""

import csv
import itertools
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from common.llm import ModelSpec, complete  # noqa: E402
from de_bench.tasks import SYSTEM as GEN_SYSTEM, TASKS, extract_code  # noqa: E402

OUT = Path(__file__).parent / "out"

LOCAL = ModelSpec("qwen3:8b", "qwen3:8b", "ollama")
LOCAL_REVIEWER = ModelSpec("llama3.1:8b", "llama3.1:8b", "ollama")
HAIKU = ModelSpec("claude-haiku-4-5", "claude-haiku-4-5", "anthropic", 1.00, 5.00)
SONNET = ModelSpec("claude-sonnet-5", "claude-sonnet-5", "anthropic", 2.00, 10.00)

# (gerador, revisor). Revisor de familia diferente do gerador evita autopreferencia.
PAIRS = [
    (LOCAL, LOCAL_REVIEWER),
    (LOCAL, SONNET),
    (HAIKU, LOCAL_REVIEWER),
    (HAIKU, SONNET),
]

REVIEW_SYSTEM = (
    "Voce e um revisor de codigo senior e cetico. Recebe uma tarefa e uma solucao proposta. "
    "Verifique se a solucao resolve exatamente o que foi pedido, incluindo nomes de colunas, "
    "ordem, tipos e casos de borda. Responda APENAS com JSON no formato:\n"
    '{"verdict": "approve" | "reject", "issues": ["..."], "fixed_code": "codigo completo corrigido ou null"}\n'
    "Se aprovar, fixed_code deve ser null. Se reprovar, fixed_code deve conter a solucao completa, "
    "na mesma linguagem, sem markdown."
)


@dataclass
class Row:
    task: str
    generator: str
    reviewer: str
    pass_before: bool
    verdict: str
    pass_after: bool
    reviewer_correct: bool  # veredito bate com o teste "antes"
    harmed: bool  # passava antes, falhou depois
    fixed: bool  # falhava antes, passou depois
    gen_tokens: int
    rev_tokens: int
    cost_usd: float
    latency_s: float
    note: str


def parse_review(text: str) -> dict:
    raw = extract_code(text, "json") if "```" in text else text
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    try:
        d = json.loads(m.group(0) if m else raw)
    except json.JSONDecodeError:
        return {"verdict": "unparseable", "issues": [], "fixed_code": None}
    d.setdefault("verdict", "unparseable")
    d.setdefault("fixed_code", None)
    return d


def run_pair(gen: ModelSpec, rev: ModelSpec, task) -> Row:
    t0 = time.perf_counter()
    code_text, g_in, g_out, _ = complete(gen, task.prompt, system=GEN_SYSTEM, max_tokens=1024)
    code = extract_code(code_text, task.lang)
    pass_before, _ = task.check(f"```{task.lang}\n{code}\n```")

    review_prompt = f"TAREFA:\n{task.prompt}\n\nSOLUCAO PROPOSTA ({task.lang}):\n{code}"
    review_text, r_in, r_out, _ = complete(rev, review_prompt, system=REVIEW_SYSTEM, max_tokens=2048)
    review = parse_review(review_text)
    verdict = review["verdict"]

    final_code = code
    fixed = review.get("fixed_code")
    if verdict == "reject" and fixed:
        # modelos as vezes devolvem o codigo como lista/dict em vez de string
        fixed = fixed if isinstance(fixed, str) else json.dumps(fixed, ensure_ascii=False)
        final_code = extract_code(fixed, task.lang)
    pass_after, note = task.check(f"```{task.lang}\n{final_code}\n```")

    reviewer_correct = (verdict == "approve" and pass_before) or (verdict == "reject" and not pass_before)
    return Row(
        task=task.id, generator=gen.label, reviewer=rev.label,
        pass_before=pass_before, verdict=verdict, pass_after=pass_after,
        reviewer_correct=reviewer_correct, harmed=pass_before and not pass_after,
        fixed=(not pass_before) and pass_after,
        gen_tokens=g_in + g_out, rev_tokens=r_in + r_out,
        cost_usd=round(gen.cost(g_in, g_out) + rev.cost(r_in, r_out), 5),
        latency_s=round(time.perf_counter() - t0, 1), note=note[:80],
    )


def summarize(rows: list[Row]) -> str:
    lines = ["## Par gerador + revisor", "",
             "| gerador | revisor | antes | depois | revisor acertou | consertou | quebrou | custo | tempo medio |",
             "|---|---|---|---|---|---|---|---|---|"]
    for (g, r), grp in itertools.groupby(rows, key=lambda x: (x.generator, x.reviewer)):
        rs = list(grp)
        n = len(rs)
        lines.append(f"| {g} | {r} | {sum(x.pass_before for x in rs)}/{n} | {sum(x.pass_after for x in rs)}/{n} | "
                     f"{sum(x.reviewer_correct for x in rs)}/{n} | {sum(x.fixed for x in rs)} | {sum(x.harmed for x in rs)} | "
                     f"${sum(x.cost_usd for x in rs):.3f} | {sum(x.latency_s for x in rs)/n:.0f}s |")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows: list[Row] = []
    for gen, rev in PAIRS:
        for task in TASKS:
            row = run_pair(gen, rev, task)
            rows.append(row)
            print(f"{gen.label:16} -> {rev.label:16} {task.id:36} antes={'ok' if row.pass_before else 'X '} "
                  f"{row.verdict:11} depois={'ok' if row.pass_after else 'X '} {row.latency_s:5.0f}s", flush=True)
    OUT.mkdir(exist_ok=True)
    with open(OUT / "rows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Row.__dataclass_fields__))
        w.writeheader()
        w.writerows(asdict(r) for r in rows)
    (OUT / "scores.md").write_text(summarize(rows))
    print("\n" + summarize(rows))


if __name__ == "__main__":
    main()
