"""Tres estrategias de cortar um documento em pedacos.

`by_heading` ja vem pronta, para voce comparar. `fixed_size` VOCE IMPLEMENTA:
e onde mora a sutileza da sobreposicao (overlap).
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    start: int  # posicao do primeiro caractere no documento original
    end: int
    label: str  # de onde veio (cabecalho ou indice), so para exibir


def fixed_size(doc: str, size: int, overlap: int) -> list[Chunk]:
    """Corta o documento em janelas de `size` caracteres que se sobrepoem em `overlap`.

    Regras:
    - a primeira janela comeca em 0
    - cada janela seguinte comeca `size - overlap` caracteres depois da anterior
    - a ultima janela termina no fim do documento (pode ser menor que `size`)
    - nao devolva janelas vazias
    - `overlap` deve ser menor que `size` (levante ValueError se nao for)

    Exemplo com size=5, overlap=2, doc="abcdefgh":
        "abcde" (0-5), "defgh" (3-8), "gh" (6-8)

    O campo label pode ser f"chars {start}-{end}".
    """
    raise NotImplementedError("implemente em chunking.py")


def by_heading(doc: str, max_size: int = 2000, overlap: int = 0) -> list[Chunk]:
    """Corta nos cabecalhos markdown. Secao maior que max_size cai para fixed_size.

    Esta vem pronta: use como referencia de estilo e como termo de comparacao.
    """
    positions = [m.start() for m in re.finditer(r"^#{1,6} .+$", doc, flags=re.MULTILINE)]
    if not positions:
        return fixed_size(doc, max_size, overlap)
    bounds = list(zip([0] + positions, positions + [len(doc)]))
    chunks: list[Chunk] = []
    for start, end in bounds:
        text = doc[start:end]
        if not text.strip():
            continue
        heading = text.strip().splitlines()[0][:60]
        if len(text) <= max_size:
            chunks.append(Chunk(text, start, end, heading))
        else:
            # secao grande demais: reaproveita a janela deslizante dentro dela
            for sub in fixed_size(text, max_size, overlap):
                chunks.append(Chunk(sub.text, start + sub.start, start + sub.end, heading))
    return chunks


def by_paragraph(doc: str, max_size: int = 1000, overlap: int = 0) -> list[Chunk]:
    """Agrupa paragrafos ate encher max_size. Corte 'semantico' pobre, mas honesto."""
    chunks: list[Chunk] = []
    buf, buf_start = "", 0
    pos = 0
    for para in re.split(r"(\n\s*\n)", doc):
        if len(buf) + len(para) > max_size and buf.strip():
            chunks.append(Chunk(buf, buf_start, buf_start + len(buf), f"par {len(chunks)}"))
            buf, buf_start = "", pos
        if not buf:
            buf_start = pos
        buf += para
        pos += len(para)
    if buf.strip():
        chunks.append(Chunk(buf, buf_start, buf_start + len(buf), f"par {len(chunks)}"))
    return chunks


STRATEGIES = {"fixed_size": fixed_size, "by_heading": by_heading, "by_paragraph": by_paragraph}
