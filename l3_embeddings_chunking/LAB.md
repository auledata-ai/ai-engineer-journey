# Lab 03 — Embeddings e chunking

> **Não role a página até o fim.** Faça na ordem. A previsão só funciona se você
> ainda não viu o resultado.

---

## 0. O conceito em 5 linhas

1. Um **embedding** é um texto virado numa lista de números (aqui, 768). Textos com
   sentido parecido viram vetores apontando para direções parecidas.
2. **Similaridade do cosseno** mede o ângulo entre dois vetores: 1 é mesma direção,
   0 é perpendicular, −1 é oposto. É como se compara pergunta e texto.
3. Busca semântica é isso: vetoriza a pergunta, vetoriza os pedaços do documento,
   devolve os pedaços de maior cosseno.
4. **Chunking** é cortar o documento em pedaços. Você é obrigado a cortar porque o
   embedding tem tamanho limitado e porque um pedaço enorme dilui o assunto.
5. Onde você corta decide o que dá para achar. É a decisão mais subestimada do RAG.

Corpus deste lab: **os seus próprios arquivos** de `knowledge/`, `ROADMAP.md` e
`CLAUDE.md`. 26 mil caracteres. Você conhece o conteúdo, então consegue julgar
sozinho se a busca acertou.

---

## 1. Previsão — preencha ANTES de rodar

Sem consultar nada. Palpite errado aqui vale mais que acerto depois.

| # | pergunta | meu palpite | por quê |
| --- | --- | --- | --- |
| 1 | Chunk de **200** caracteres ou de **1500**: qual acerta mais na primeira posição (hit@1)? | | |
| 2 | Cortar **por cabeçalho** ou por **tamanho fixo**: qual vence? | | |
| 3 | Das 15 perguntas, quantas ficam **impossíveis** (nenhum chunk contém a resposta inteira) com sobreposição zero? | | |
| 4 | A **sobreposição** conserta o quê, exatamente? | | |
| 5 | O cosseno entre a pergunta e o chunk certo vai dar em torno de quanto? **0,9? 0,7? 0,5?** | | |
| 6 | Pergunta cuja resposta está numa **tabela markdown**: chunk pequeno ajuda ou atrapalha? | | |

---

## 2. Mão na massa

Duas funções, as duas centrais, as duas pequenas. O resto do código já está pronto.

### 2.1 `vectors.py` → `cosine_similarity`
Três linhas, sem numpy. Escreva a soma e a raiz na mão uma vez na vida.

### 2.2 `chunking.py` → `fixed_size`
A janela deslizante com sobreposição. A sutileza está em onde começa a próxima janela.

### 2.3 Rode os testes até ficarem verdes

```bash
uv run pytest l3_embeddings_chunking -q
```

São 15 testes. Enquanto houver vermelho, não siga.

---

## 3. O experimento

Baixe o modelo de embeddings (274 MB, uma vez só) e rode:

```bash
ollama pull nomic-embed-text
uv run python -m l3_embeddings_chunking.run
```

Nove configurações, 15 perguntas cada. Uns 2 minutos.

---

## 4. Resultado

Cole aqui a tabela de `out/scores.md`:

```
(cole aqui)
```

---

## 5. Previsão x realidade

| # | meu palpite | o que aconteceu | acertei? | o que eu não tinha considerado |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |

---

## 6. Explique com suas palavras

Sem consultar o arquivo de conceitos. Se travar, volte ao passo 3 e olhe os números de novo.

**O que é um embedding, para alguém que nunca ouviu falar:**

> (escreva aqui)

**Por que a estratégia de chunking muda o resultado da busca:**

> (escreva aqui)

**Quando eu usaria sobreposição e quando não usaria:**

> (escreva aqui)

---

## 7. O que eu não conseguiria derivar sozinho

_(o Claude preenche depois de ler a sua explicação)_
