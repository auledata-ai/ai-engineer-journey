"""L3 - roda o experimento de chunking e recuperacao.

Para cada configuracao (estrategia x tamanho x sobreposicao):
  1. corta o corpus em chunks
  2. transforma cada chunk em vetor (embedding) com nomic-embed-text via Ollama
  3. transforma cada pergunta em vetor
  4. ordena os chunks pela similaridade do cosseno com a pergunta
  5. conta acerto: o chunk recuperado CONTEM o trecho do gabarito?

Metricas:
  hit@1  - o trecho certo veio na primeira posicao
  hit@5  - veio entre as cinco primeiras
  MRR    - 1/posicao do primeiro acerto, media. Premia acertar cedo.
  impossivel - nenhum chunk contem o trecho (o corte partiu a resposta no meio)

Saida: out/scores.md (tabela) e out/viz.json (dados do artefato visual).
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from l3_embeddings_chunking.chunking import STRATEGIES, Chunk
from l3_embeddings_chunking.corpus import load
from l3_embeddings_chunking.questions import QUESTIONS
from l3_embeddings_chunking.vectors import cosine_similarity

OUT = Path(__file__).parent / "out"
OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"

# grade de configuracoes. Mexer aqui e o jeito de testar as suas hipoteses.
CONFIGS = [
    ("fixed_size", 200, 0), ("fixed_size", 200, 50),
    ("fixed_size", 600, 0), ("fixed_size", 600, 150),
    ("fixed_size", 1500, 0), ("fixed_size", 1500, 300),
    ("by_heading", 2000, 0), ("by_heading", 600, 150),
    ("by_paragraph", 1000, 0),
]


def embed(texts: list[str]) -> list[list[float]]:
    """Uma chamada, varios textos. Embedding e barato e paralelizavel."""
    r = httpx.post(f"{OLLAMA}/api/embed", json={"model": EMBED_MODEL, "input": texts}, timeout=600)
    r.raise_for_status()
    return r.json()["embeddings"]


@dataclass
class Score:
    strategy: str
    size: int
    overlap: int
    n_chunks: int
    avg_chars: int
    hit1: int
    hit5: int
    mrr: float
    impossible: int


def rank(chunks: list[Chunk], chunk_vecs: list[list[float]], q_vec: list[float]) -> list[tuple[int, float]]:
    """Ordena os indices dos chunks do mais parecido para o menos parecido."""
    sims = [(i, cosine_similarity(q_vec, v)) for i, v in enumerate(chunk_vecs)]
    return sorted(sims, key=lambda t: t[1], reverse=True)


def evaluate(name: str, size: int, overlap: int, doc: str, q_vecs: list[list[float]]) -> tuple[Score, dict]:
    chunks = STRATEGIES[name](doc, size, overlap)
    vecs = embed([c.text for c in chunks])

    hit1 = hit5 = impossible = 0
    rr_total = 0.0
    per_question = []
    for q, qv in zip(QUESTIONS, q_vecs):
        gold = [i for i, c in enumerate(chunks) if q.answer_quote in c.text]
        ranked = rank(chunks, vecs, qv)
        if not gold:
            impossible += 1
            per_question.append({"q": q.text, "kind": q.kind, "gold": [], "ranked": ranked[:8],
                                 "hit_at": None, "impossible": True})
            continue
        position = next((p for p, (i, _) in enumerate(ranked, start=1) if i in gold), None)
        hit1 += position == 1
        hit5 += bool(position and position <= 5)
        rr_total += 1 / position if position else 0.0
        per_question.append({"q": q.text, "kind": q.kind, "gold": gold, "ranked": ranked[:8],
                             "hit_at": position, "impossible": False})

    score = Score(name, size, overlap, len(chunks),
                  round(sum(len(c.text) for c in chunks) / len(chunks)),
                  hit1, hit5, round(rr_total / len(QUESTIONS), 3), impossible)
    detail = {"config": f"{name}/{size}/{overlap}", "score": score.__dict__,
              "chunks": [{"start": c.start, "end": c.end, "label": c.label, "len": len(c.text)} for c in chunks],
              "questions": per_question}
    return score, detail


def main() -> None:
    doc = load()
    print(f"corpus: {len(doc)} caracteres, {len(QUESTIONS)} perguntas\n")
    print("gerando embeddings das perguntas...", flush=True)
    q_vecs = embed([q.text for q in QUESTIONS])

    scores: list[Score] = []
    details = []
    for name, size, overlap in CONFIGS:
        t0 = time.perf_counter()
        s, d = evaluate(name, size, overlap, doc, q_vecs)
        scores.append(s)
        details.append(d)
        print(f"{name:13} size={size:5} overlap={overlap:4} chunks={s.n_chunks:4} "
              f"hit@1={s.hit1:2}/15 hit@5={s.hit5:2}/15 MRR={s.mrr:.3f} "
              f"impossivel={s.impossible} ({time.perf_counter()-t0:.0f}s)", flush=True)

    OUT.mkdir(exist_ok=True)
    lines = ["| estrategia | tamanho | sobreposicao | chunks | chars/chunk | hit@1 | hit@5 | MRR | impossivel |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in scores:
        lines.append(f"| {s.strategy} | {s.size} | {s.overlap} | {s.n_chunks} | {s.avg_chars} | "
                     f"{s.hit1}/15 | {s.hit5}/15 | {s.mrr:.3f} | {s.impossible} |")
    table = "\n".join(lines) + "\n"
    (OUT / "scores.md").write_text(table)
    (OUT / "viz.json").write_text(json.dumps(
        {"doc": doc, "questions": [q.__dict__ for q in QUESTIONS], "configs": details}, ensure_ascii=False))
    print("\n" + table)
    print(f"tabela em {OUT/'scores.md'}, dados do artefato em {OUT/'viz.json'}")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError as e:
        print(f"erro ao falar com o Ollama: {e}\nrodou `ollama pull {EMBED_MODEL}`?", file=sys.stderr)
        sys.exit(1)
    except NotImplementedError as e:
        print(f"falta implementar: {e}\nveja vectors.py e chunking.py, depois rode os testes.", file=sys.stderr)
        sys.exit(1)
