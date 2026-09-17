"""Corpus do lab: os proprios arquivos de conhecimento deste repositorio.

Escolha deliberada. Voce conhece o conteudo, entao consegue julgar se a recuperacao
acertou sem depender da minha palavra.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [f for f in sorted(ROOT.glob("knowledge/*.md")) + [ROOT / "ROADMAP.md", ROOT / "CLAUDE.md"] if f.exists()]


def load() -> str:
    """Concatena os documentos separados por marcador de arquivo."""
    parts = []
    for f in FILES:
        parts.append(f"\n\n<!-- arquivo: {f.name} -->\n\n{f.read_text()}")
    return "".join(parts).strip()
