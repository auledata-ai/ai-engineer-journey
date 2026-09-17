"""Similaridade entre vetores.

VOCE IMPLEMENTA a funcao abaixo. E o coracao de todo sistema de busca semantica
e cabe em tres linhas. Depois rode: uv run pytest l3_embeddings_chunking -q
"""


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Similaridade do cosseno entre dois vetores.

    E o cosseno do angulo entre eles: 1.0 = mesma direcao, 0.0 = perpendicular,
    -1.0 = direcao oposta. Formula:

        produto_escalar(a, b) / (norma(a) * norma(b))

    onde produto_escalar = soma de a[i]*b[i], e norma = raiz da soma dos quadrados.

    Nao use numpy. Escreva com soma e raiz para ver o que acontece.
    """
    raise NotImplementedError("implemente em vectors.py")
