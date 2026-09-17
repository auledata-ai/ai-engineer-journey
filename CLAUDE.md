# CLAUDE.md — contexto do projeto

> Leia este arquivo inteiro antes de qualquer trabalho neste repositório.
> Ele é o estado atual do projeto. Mantê-lo atualizado é parte da tarefa, não um extra.

---

## 1. Objetivo

Arthur é **engenheiro de dados** (Databricks, TAP Data Lake) migrando para **AI Engineer**.
Este repositório é o diário de aprendizado dessa transição: labs de fundamentos, benchmarks,
e a base de conhecimento que ele relê antes de entrevista.

Três metas, nesta ordem:
1. **Aprender de verdade** os conceitos (não copiar tutorial).
2. **Construir portfólio** com resultados medidos, não demos.
3. **Trocar de role** usando esse portfólio no LinkedIn e em entrevistas.

Os projetos maiores de portfólio ganham **repositório próprio** na org `auledata-ai`.
Este repo guarda os labs, os benchmarks e o conhecimento.

---

## 2. Duas práticas obrigatórias

### 2.1 Gravar o andamento, sempre
Ao final de **todo** trabalho significativo, atualize:
- **Este arquivo** (seção 5 Estado atual e seção 6 Próximos passos).
- **PROGRESS.md**: marque o checkbox e adicione uma linha no diário com data, o que foi feito e o próximo passo.
- **knowledge/**: uma lição por tema, escrita para ser relida meses depois.

O critério: um agente novo, sem histórico de conversa, deve conseguir ler este arquivo e continuar o trabalho.

### 2.2 Labs são ativos, não passivos
Ler conclusão pronta não ensina. Todo lab segue o template `LAB_TEMPLATE.md`:

1. **Conceito em 5 linhas** — o mínimo para formar um palpite.
2. **Previsão** — o Arthur escreve o palpite ANTES de rodar qualquer coisa.
3. **Mão na massa** — 1 ou 2 funções centrais ficam como `NotImplementedError` com teste pronto. Ele implementa.
4. **O Arthur roda os comandos.** O Claude entrega código e explicação. Nada de experimento rodando em segundo plano sem ele ver.
5. **Ele explica com as próprias palavras.** O Claude só corrige e acrescenta o que ele não derivaria sozinho.
6. **Artefato visual interativo** quando o conceito for abstrato (vetores, cortes, custo). Publicado, vira peça de portfólio.

### 2.3 Reformular o prompt antes de executar
Todo pedido do Arthur deve ser **reformulado como um profissional da área escreveria**, e
**mostrado a ele para revisão antes de executar**. O formato:

```
## Prompt reformulado
<objetivo, escopo, restrições, critério de pronto, entregáveis>

Rodo assim, ou quer ajustar?
```

Só executar depois do aceite. Exceções: pedidos triviais de leitura ou status
("onde paramos?", "mostre o arquivo X"), que podem ser respondidos direto.

---

## 3. Como o Arthur trabalha

- **TDAH**: respostas curtas, uma tarefa por vez, **uma única próxima ação no final**. Planos longos vão para arquivo, não para o chat.
- **Idioma**: português no chat e nos documentos de conhecimento. Código, commits e PRs em inglês.
- **Um projeto ativo por vez.** Os outros ficam trancados.
- Não pedir chaves de API ou setup manual sem necessidade real. Preferir Ollama local.

---

## 4. Ambiente e convenções

### Stack
- Python 3.12 gerenciado por **uv**. Rodar com `uv run python -m <modulo>`.
- `pytest` para testes. `pydantic` para schemas. `duckdb` e `pandas` nos benchmarks.
- Chave da Anthropic em `.env` (fora do git). Carregar com `load_dotenv(".env")`.

### Modelos disponíveis
| modelo | onde | uso |
|---|---|---|
| `qwen3:8b` | Ollama local | geração rápida, suporta `think` |
| `llama3.1:8b` | Ollama local | segundo ponto de comparação |
| `qwen3-coder:30b` e `qwen3-coder-128k` | Ollama local | código, 19 GB, lento no Mac |
| `claude-haiku-4-5` | API | melhor custo-benefício medido |
| `claude-sonnet-5`, `claude-opus-5` | API | quando a tarefa exige |

Ollama: usar o endpoint **nativo** `/api/chat`, não o compatível com OpenAI. O compatível ignora `think`.

### Git
- **Nunca commitar em `main`.** Branch por tarefa: `feat/`, `fix/`, `docs/`, `chore/`.
- Conventional Commits, descrição em inglês, imperativo, minúscula, sem ponto final.
- PR com resumo e plano de teste. Merge pelo GitHub.
- `.env`, `out/*.csv`, `out/*.log` e `__pycache__` ficam fora do git.

---

## 5. Estado atual (atualizado em 2026-09-16)

### Concluído

| item | resultado | lição em |
|---|---|---|
| **L1** API, tokens, custo | raciocínio oculto custa 12x tokens e 9x latência | `knowledge/L1-api-tokens-custo.md` |
| **L3** embeddings e chunking | em andamento, formato ativo | `l3_embeddings_chunking/LAB.md` |
| **L2** structured outputs | exemplo vence schema no prompt; gramática não valida intervalo | `knowledge/L2-structured-outputs.md` |
| **DE-Bench** 11 tarefas, 6 modelos | Haiku 100% por $0,008; 8B local 82% | `knowledge/DE-bench-v1.md` |
| **Gerador+revisor** 4 pares | nenhum revisor melhorou; revisor fraco derrubou 9/11 para 5/11 | `knowledge/gen-review-v1.md` |
| **Prompt caching** | conceito e números | `knowledge/conceito-prompt-caching.md` |

### Bloqueado
- **Claude Code com modelo local**: inviável no Mac. O prompt de sistema tem ~60k tokens e, sem cache de prefixo,
  o Ollama leva minutos por turno e retorna 500. Registrado como resultado negativo, que já vale para o portfólio.

### Pendências operacionais
- A chave da Anthropic passou pelo chat e **deve ser rotacionada** no console.
- Xcode.app ainda ocupa 3,7 GB e precisa de `sudo rm -rf` para sair.

---

## 6. Próximos passos

1. **L3 — embeddings e chunking** *(em andamento)*: `l3_embeddings_chunking/LAB.md`. Arthur preenche a previsão,
   implementa `cosine_similarity` e `fixed_size`, roda os testes e o experimento. Depois o Claude monta o artefato
   interativo a partir de `out/viz.json`.
2. **L4 — prompting e primeiro eval**: golden set de 20 casos com score automático.
3. **L5 — async, batching e cache**: controlar concorrência e custo.
4. Primeiro projeto de portfólio em repo próprio: **prompt-ops** (versionamento + eval em CI + A/B).

A trilha completa, com os 16 projetos e os 4 extras, está em `ROADMAP.md`.

---

## 7. Mapa do repositório

```
CLAUDE.md          este arquivo, contexto para agentes
ROADMAP.md         trilha completa, do fundamento ao capstone
PROGRESS.md        checkboxes e diário de sessões
knowledge/         uma lição por tema, em português
common/llm.py      adaptador de providers, mesma assinatura para Ollama e Anthropic
de_bench/          benchmark de engenharia de dados, verificação por execução
gen_review/        experimento gerador + revisor
l1_*/ l2_*/        labs de fundamentos
```

---

## 8. Princípios técnicos aprendidos

Estes vieram de erro próprio, não de leitura. Respeitar.

1. **Verificação por execução vence opinião.** Código se testa rodando. LLM explica, teste decide.
2. **Falha unânime é bug no eval.** Se todos os modelos erram a mesma tarefa, suspeite do seu gabarito primeiro.
3. **Gabarito de referência precisa passar no próprio verificador.** Teste o teste.
4. **Comece pelo modelo mais barato e meça.** Haiku bateu Opus em tarefa de SQL.
5. **Schema no provedor, Pydantic do seu lado, retry como última rede.** As três camadas.
6. **Custo por tarefa resolvida**, não por request. Modelo barato que erra duas vezes não é barato.
