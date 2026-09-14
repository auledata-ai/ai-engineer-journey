# Progresso

Projeto ativo: **L2 - Structured outputs** (teoria primeiro, código depois)

## Nível 0
- [x] L1 API + tokens + custo (rodado com Qwen3 8B local; lições em knowledge/L1-api-tokens-custo.md)
- [ ] L2 Structured outputs
- [ ] L3 Embeddings + chunking
- [ ] L4 Prompting + primeiro eval
- [ ] L5 Async + batching + cache

## Benchmark
- [x] DE-Bench v1: 11 tarefas, 3 modelos locais (de_bench/, knowledge/DE-bench-v1.md)

- [x] DE-Bench v2: 6 modelos, Haiku 100% (knowledge/DE-bench-v1.md)
- [x] Gerador+revisor: 4 pares, revisor sempre piora (knowledge/gen-review-v1.md)
- [ ] Claude Code com modelo local: bloqueado por latência (60k tokens/turno sem cache)

## Diário (1 linha por sessão: data, o que fiz, próximo passo)
- 2026-09-09: scaffold do repo labs + script L1 pronto. Próximo: colocar ANTHROPIC_API_KEY no .env e rodar.
- 2026-09-09: L1 concluído em modo teoria (sem chaves de API). Próximo: L2 structured outputs.
- 2026-09-10: Ollama instalado, qwen3:8b rodando. L1 executado. Lição: thinking oculto custa tokens; endpoint nativo vs compatível. Próximo: rodar llama3.1 quando baixar, depois L2.
- 2026-09-10: DE-Bench v1 rodado. qwen3 82%, qwen3+think 91%, llama 82%. Bug no eval encontrado e corrigido. Disco cheio (backups iPhone), Xcode limpo. Próximo: PR do de-bench, depois L2.
- 2026-09-11: gen-review concluído: nenhum revisor melhorou o acerto. Claude Code + Qwen3-Coder inviável em tempo. Próximo: L2 structured outputs.
