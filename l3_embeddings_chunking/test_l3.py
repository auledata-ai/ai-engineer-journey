"""Testes das duas funcoes que VOCE implementa. Rode ate ficarem verdes."""

import math

import pytest

from l3_embeddings_chunking.chunking import Chunk, by_heading, fixed_size
from l3_embeddings_chunking.corpus import load
from l3_embeddings_chunking.questions import validate
from l3_embeddings_chunking.vectors import cosine_similarity


# ---------- cosine_similarity ----------

def test_vetores_iguais_dao_1():
    assert cosine_similarity([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_mesma_direcao_escala_diferente_da_1():
    # o cosseno ignora o tamanho do vetor, so olha a direcao
    assert cosine_similarity([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)


def test_perpendiculares_dao_0():
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_opostos_dao_menos_1():
    assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)


def test_caso_conhecido():
    esperado = 11 / (math.sqrt(5) * math.sqrt(25))
    assert cosine_similarity([1, 2], [3, 4]) == pytest.approx(esperado)


# ---------- fixed_size ----------

def test_sem_sobreposicao_cobre_o_texto_uma_vez():
    chunks = fixed_size("abcdefgh", size=4, overlap=0)
    assert [c.text for c in chunks] == ["abcd", "efgh"]


def test_com_sobreposicao_repete_o_final_do_anterior():
    chunks = fixed_size("abcdefgh", size=5, overlap=2)
    assert [c.text for c in chunks] == ["abcde", "defgh", "gh"]


def test_posicoes_apontam_para_o_documento_original():
    doc = "abcdefgh"
    for c in fixed_size(doc, size=5, overlap=2):
        assert doc[c.start:c.end] == c.text


def test_ultimo_chunk_pode_ser_menor():
    assert fixed_size("abcdefg", size=3, overlap=0)[-1].text == "g"


def test_documento_menor_que_a_janela_vira_um_chunk_so():
    assert len(fixed_size("abc", size=100, overlap=10)) == 1


def test_overlap_maior_ou_igual_ao_size_e_erro():
    with pytest.raises(ValueError):
        fixed_size("abcdefgh", size=4, overlap=4)


def test_nao_devolve_chunk_vazio():
    assert all(c.text for c in fixed_size("abcdefghij", size=3, overlap=1))


# ---------- sanidade do lab ----------

def test_gabaritos_existem_no_corpus():
    faltando = validate(load())
    assert not faltando, f"trechos nao encontrados: {faltando}"


def test_by_heading_corta_nos_cabecalhos():
    doc = "# A\ntexto a\n\n## B\ntexto b\n"
    assert [c.label for c in by_heading(doc)] == ["# A", "## B"]


def test_chunk_e_imutavel():
    with pytest.raises(Exception):
        Chunk("x", 0, 1, "l").text = "y"  # type: ignore[misc]
