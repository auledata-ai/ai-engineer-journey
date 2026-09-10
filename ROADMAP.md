# Roadmap: Data Engineer -> AI Engineer

Objetivo: aprender os fundamentos de verdade, construir portfólio com números, e usar isso para trocar de role.
Fonte: guias BASWE (6 + 15 projetos), deduplicados, reordenados por dificuldade e com melhorias.

Premissas: ~10h/semana. Um projeto ativo por vez. Sessão = 45 a 60 min com um "done" definido antes de começar.

---

## Regras de jogo (TDAH-friendly)

1. Só existe UM projeto ativo. Os outros ficam trancados.
2. Cada sessão começa com uma tarefa de 1 linha e termina com um commit.
3. Todo projeto entrega 4 coisas: README com número no topo, vídeo de 90s, post no LinkedIn, seção "o que não funcionou".
4. Progresso vai em PROGRESS.md (checkbox por fase). Nada fica só na cabeça.
5. Se travar 2 sessões seguidas na mesma coisa, reduz o escopo, não aumenta o esforço.

---

## Trilha (do mais fácil ao mais complexo)

### Nível 0: Fundamentos (2 semanas) — mini-labs, sem portfólio ainda
Cada lab = 1 notebook + 1 parágrafo no PROGRESS.md explicando o conceito com suas palavras.

| Lab | Conceito | Prova de aprendizado |
|---|---|---|
| L1 | Chamada de API (Anthropic + OpenAI), tokens, custo, temperatura | tabela custo x latência de 5 prompts em 3 modelos |
| L2 | Structured outputs (Pydantic + tool use), retries, validação | extrator de entidades que nunca devolve JSON inválido |
| L3 | Embeddings, similaridade cosseno, chunking | gráfico: recall@k de 3 estratégias de chunking |
| L4 | Prompting (few-shot, CoT, system prompt), avaliação mínima | golden set de 20 casos + score automático |
| L5 | Async + batching + cache em Python | 100 chamadas com controle de concorrência e custo |

### Nível 1: Evals e economia (o que quase ninguém faz)

| # | Projeto | Origem | Skill principal | Número do README |
|---|---|---|---|---|
| P1 | Model Regression Detection (CI para prompts) | 15#1 | Evals, golden dataset, CI/CD | "X regressões detectadas, bloqueio de merge" |
| P2 | Prompt Versioning + A/B testing | 15#9 | Experimentação, estatística | "variante B venceu com p<0.05" |
| P3 | Semantic Cache | 15#7 | Embeddings, thresholds, latência | "hit rate X%, custo -Y%" |

Melhoria sugerida: P1 e P2 viram um único repositório "prompt-ops" (versionamento + eval + A/B). Um projeto mais forte que dois rasos.

### Nível 2: Retrieval e dados (onde seu background pesa)

| # | Projeto | Origem | Skill principal | Número do README |
|---|---|---|---|---|
| P4 | RAG híbrido (dense + BM25) com citações | 15#6 | Retrieval, reranking, grounding | "recall@5 X% vs Y% só vetor" |
| P5 | Text-to-SQL com guardrails | 15#8 | Tool use, segurança, validação | "acurácia X% em N queries, 0 operações destrutivas" |
| P6 | LLM-as-Judge calibrado com humanos | 6#4 | Evals avançadas, kappa, vieses | "kappa X, 3 vieses medidos" |
| P7 | Processador de documentos (OCR + extração + validação) | 15#14 | Multimodal, pipelines, schema | "precisão de campo X% em N docs" |
| P8 | Gerador de eval dataset a partir de logs | 15#13 | Data-centric AI, mineração de falhas | "N casos gerados, M edge cases" |

Melhorias sugeridas:
- P5 rodar contra Unity Catalog/Databricks SQL (você conhece o domínio; vira diferencial real).
- P6 usar as respostas do P4 como corpus de avaliação (portfólio coeso).
- P7 combinar com ai_parse_document do Databricks numa versão 2.

### Nível 3: Infra e operação (LLMOps)

| # | Projeto | Origem | Skill principal | Número do README |
|---|---|---|---|---|
| P9 | LLM Gateway: roteamento por custo + circuit breaker + observabilidade | 15#2 + 15#11 + 6#3 | Resiliência, custo, métricas | "X% disponibilidade em outage simulado, custo -Y%" |
| P10 | Failure Forensics (tracing de pipelines multi-step) | 15#3 | Observabilidade, root cause | "MTTR de horas para segundos" |
| P11 | AI Feature Flags com rollout gradual | 15#12 | Release engineering para IA | "rollback automático em X s" |
| P12 | Self-healing docs (GitHub Action) | 15#4 | Embeddings + geração em CI | "precisão X% em docs obsoletas" |

Melhoria sugerida: P9 funde três projetos dos guias. Um gateway com routing, breaker, budgets e Grafana é o projeto de infra mais forte do portfólio.

### Nível 4: Agentes, fine-tuning e segurança

| # | Projeto | Origem | Skill principal | Número do README |
|---|---|---|---|---|
| P13 | Knowledge Graph RAG (Neo4j + pgvector) | 6#1 | Multi-hop retrieval, ontologia | "acurácia multi-hop X% vs Y%" |
| P14 | Multi-agente com supervisor, estado durável e trace | 6#2 + 15#5 + 15#15 | LangGraph, budgets, HITL, memória | "resume após crash, custo capado" |
| P15 | Destilação: frontier -> 8B com LoRA + vLLM | 6#5 + 15#10 | Fine-tuning, unit economics | "X% da qualidade a 1/20 do custo, break-even Y req/dia" |
| P16 | Red-team harness contra os próprios projetos | 6#6 | Safety, OWASP LLM Top 10 | "N categorias, 0 regressões" |

### Extras (não estão nos guias, alto ganho para o seu perfil)

| # | Projeto | Por quê |
|---|---|---|
| E1 | Servidor MCP expondo tools de dados (catálogo, lineage, queries) | MCP é o protocolo padrão de tools; quase ninguém tem no portfólio |
| E2 | Agente de engenharia de dados (gera, valida e testa pipelines Spark) | Une seu domínio atual com agentes; história forte de entrevista |
| E3 | GenAI nativo em Databricks (Vector Search + Model Serving + MLflow eval) | Mostra a mesma competência no ecossistema que você já domina |
| E4 | Capstone: produto end-to-end que usa P4 + P6 + P9 + P16 juntos | Portfólio que se referencia, como o guia dos seis recomenda |

---

## Portfólio e LinkedIn

- Um repositório por projeto, nomeado pelo problema, não pela stack.
- README: 1 linha com resultado -> tabela/print -> diagrama único -> decisões -> o que não funcionou -> setup.
- Post por marco (3 por projeto): "comecei e por quê", "o número que saiu", "o que quebrou e como resolvi".
- Headline do LinkedIn muda no P4: "Data Engineer -> AI Engineer | RAG, evals, LLMOps".
- A partir do P9, começar a aplicar para vagas. O portfólio já cobre retrieval + evals + infra.

## Ordem de ataque
L1 -> L2 -> L3 -> L4 -> L5 -> P1+P2 -> P3 -> P4 -> P5 -> P6 -> P7 -> P8 -> P9 -> P10 -> P11 -> P12 -> P13 -> P14 -> P15 -> P16 -> E1 -> E2 -> E3 -> E4
