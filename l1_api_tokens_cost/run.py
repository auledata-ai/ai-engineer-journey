"""L1 - Chamada de API, tokens, custo e latencia.

Envia os mesmos prompts para varios modelos (locais via Ollama e, se houver chave,
Claude via Anthropic) e registra tokens, custo e latencia.
Saida: out/results.csv e out/results.md.

Conceito central: dois providers, uma interface. Trocar de modelo nao pode exigir
reescrever a aplicacao.
"""

import csv
import os
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

OUT_DIR = Path(__file__).parent / "out"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    provider: str  # "ollama" | "anthropic"
    price_in: float  # USD por 1M tokens (0 para local)
    price_out: float


MODELS = [
    ModelSpec("qwen3:8b", "ollama", 0.0, 0.0),
    ModelSpec("llama3.1:8b", "ollama", 0.0, 0.0),
    # Descomente quando houver ANTHROPIC_API_KEY. Precos: docs Anthropic, set/2026.
    # ModelSpec("claude-haiku-4-5", "anthropic", 1.00, 5.00),
    # ModelSpec("claude-sonnet-5", "anthropic", 2.00, 10.00),
    # ModelSpec("claude-opus-5", "anthropic", 5.00, 25.00),
]

PROMPTS = {
    "curto": "Responda em uma palavra: qual a capital de Portugal?",
    "classificacao": (
        "Classifique o email abaixo em uma destas categorias: billing, technical, account, general. "
        "Responda so a categoria.\n\nEmail: Fui cobrado duas vezes este mes, podem verificar?"
    ),
    "extracao": (
        "Extraia nome, data e valor do texto e devolva JSON com as chaves nome, data, valor.\n\n"
        "Texto: A fatura de Maria Silva, emitida em 03/09/2026, tem o valor de 1.250,00 EUR."
    ),
    "resumo": (
        "Resuma em 2 frases: Delta Lake e um formato de armazenamento open source que traz "
        "transacoes ACID ao Apache Spark. Ele guarda um log de transacoes, permite time travel, "
        "impoe schema e suporta operacoes MERGE, UPDATE e DELETE sobre arquivos Parquet."
    ),
    "raciocinio": (
        "Um pipeline processa 1,2 milhao de linhas por hora. Se o volume dobra a cada 6 meses, "
        "quantas linhas por hora ele processa em 18 meses? Mostre o calculo em 3 linhas."
    ),
}


@dataclass
class Result:
    prompt: str
    model: str
    provider: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    stop_reason: str
    output: str


def call_ollama(spec: ModelSpec, prompt: str) -> tuple[str, int, int, str]:
    from openai import OpenAI

    client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
    response = client.chat.completions.create(
        model=spec.name,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"think": False},  # qwen3 tem modo de raciocinio; desligado para comparar justo
    )
    choice = response.choices[0]
    usage = response.usage
    return choice.message.content or "", usage.prompt_tokens, usage.completion_tokens, choice.finish_reason


def call_anthropic(spec: ModelSpec, prompt: str) -> tuple[str, int, int, str]:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=spec.name,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        text = "<refusal>"
    else:
        text = "".join(b.text for b in response.content if b.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens, response.stop_reason


CALLERS = {"ollama": call_ollama, "anthropic": call_anthropic}


def run_one(spec: ModelSpec, prompt_name: str, prompt: str) -> Result:
    start = time.perf_counter()
    text, tokens_in, tokens_out, stop = CALLERS[spec.provider](spec, prompt)
    latency_ms = round((time.perf_counter() - start) * 1000)
    cost = tokens_in / 1e6 * spec.price_in + tokens_out / 1e6 * spec.price_out
    return Result(
        prompt=prompt_name,
        model=spec.name,
        provider=spec.provider,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=round(cost, 6),
        latency_ms=latency_ms,
        stop_reason=stop,
        output=text.strip().replace("\n", " ")[:160],
    )


def write_outputs(rows: list[Result]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    fields = list(Result.__dataclass_fields__)
    with open(OUT_DIR / "results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(r.__dict__ for r in rows)

    lines = ["| prompt | modelo | in | out | custo USD | ms | saida |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r.prompt} | {r.model} | {r.tokens_in} | {r.tokens_out} | "
            f"{r.cost_usd:.5f} | {r.latency_ms} | {r.output[:80]} |"
        )
    (OUT_DIR / "results.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    active = [m for m in MODELS if m.provider == "ollama" or os.getenv("ANTHROPIC_API_KEY")]
    rows: list[Result] = []
    for prompt_name, prompt in PROMPTS.items():
        for spec in active:
            r = run_one(spec, prompt_name, prompt)
            rows.append(r)
            print(f"{r.prompt:14} {r.model:18} in={r.tokens_in:4} out={r.tokens_out:4} "
                  f"${r.cost_usd:.5f} {r.latency_ms:6}ms  {r.output[:60]}")
    write_outputs(rows)
    print(f"\nTabela em {OUT_DIR / 'results.md'}")


if __name__ == "__main__":
    main()
