"""Adaptadores de provider com uma unica assinatura.

Trocar de modelo nao pode exigir reescrever a aplicacao. Cada provider recebe
(spec, system, prompt, max_tokens) e devolve (texto, tokens_in, tokens_out, stop_reason).
"""

import os
from dataclasses import dataclass

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


@dataclass(frozen=True)
class ModelSpec:
    label: str
    name: str
    provider: str  # "ollama" | "anthropic"
    price_in: float = 0.0  # USD por 1M tokens
    price_out: float = 0.0
    think: bool = False

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        return tokens_in / 1e6 * self.price_in + tokens_out / 1e6 * self.price_out


def call_ollama(spec: ModelSpec, system: str, prompt: str, max_tokens: int) -> tuple[str, int, int, str]:
    import httpx

    messages = [{"role": "user", "content": prompt}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    response = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": spec.name,
            "messages": messages,
            "think": spec.think,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0},
        },
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"], data["prompt_eval_count"], data["eval_count"], data["done_reason"]


def call_anthropic(spec: ModelSpec, system: str, prompt: str, max_tokens: int) -> tuple[str, int, int, str]:
    import anthropic

    client = anthropic.Anthropic()
    kwargs = {"system": system} if system else {}
    response = client.messages.create(
        model=spec.name,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    if response.stop_reason == "refusal":
        text = ""
    else:
        text = "".join(b.text for b in response.content if b.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens, response.stop_reason


CALLERS = {"ollama": call_ollama, "anthropic": call_anthropic}


def complete(spec: ModelSpec, prompt: str, system: str = "", max_tokens: int = 1024) -> tuple[str, int, int, str]:
    return CALLERS[spec.provider](spec, system, prompt, max_tokens)
