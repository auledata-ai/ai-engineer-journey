"""L1 - Chamada de API, tokens e custo.

Envia os mesmos prompts para 3 modelos Claude e registra tokens, custo e latencia.
Saida: out/results.csv e out/results.md (tabela pronta para o PROGRESS.md).
"""

import csv
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Preco USD por 1M tokens (input, output). Fonte: docs Anthropic, jun/2026.
MODELS = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
}

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

OUT_DIR = Path(__file__).parent / "out"


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    price_in, price_out = MODELS[model]
    return tokens_in / 1_000_000 * price_in + tokens_out / 1_000_000 * price_out


def call(client: anthropic.Anthropic, model: str, prompt: str) -> dict:
    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    latency_ms = (time.perf_counter() - start) * 1000

    if response.stop_reason == "refusal":
        text = "<refusal>"
    else:
        text = "".join(b.text for b in response.content if b.type == "text").strip()

    usage = response.usage
    return {
        "model": model,
        "tokens_in": usage.input_tokens,
        "tokens_out": usage.output_tokens,
        "cost_usd": round(cost_usd(model, usage.input_tokens, usage.output_tokens), 6),
        "latency_ms": round(latency_ms),
        "stop_reason": response.stop_reason,
        "output": text.replace("\n", " ")[:120],
    }


def main() -> None:
    client = anthropic.Anthropic()
    rows = []
    for prompt_name, prompt in PROMPTS.items():
        for model in MODELS:
            row = call(client, model, prompt)
            row["prompt"] = prompt_name
            rows.append(row)
            print(f"{prompt_name:14} {model:18} in={row['tokens_in']:4} out={row['tokens_out']:4} "
                  f"${row['cost_usd']:.5f} {row['latency_ms']:5}ms")

    OUT_DIR.mkdir(exist_ok=True)
    fields = ["prompt", "model", "tokens_in", "tokens_out", "cost_usd", "latency_ms", "stop_reason", "output"]
    with open(OUT_DIR / "results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["| prompt | model | in | out | custo USD | ms |", "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['prompt']} | {r['model']} | {r['tokens_in']} | {r['tokens_out']} | "
                     f"{r['cost_usd']:.5f} | {r['latency_ms']} |")
    total = sum(r["cost_usd"] for r in rows)
    lines.append(f"\nCusto total da rodada: ${total:.4f}")
    (OUT_DIR / "results.md").write_text("\n".join(lines))
    print(f"\nCusto total: ${total:.4f}. Tabela em {OUT_DIR / 'results.md'}")


if __name__ == "__main__":
    main()
