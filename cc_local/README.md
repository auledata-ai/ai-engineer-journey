# Claude Code com modelos locais: o que quebra e por quê

Mesmo harness (Claude Code), mesmas tarefas, modelos diferentes. A pergunta: quanto do valor
de um agente de código vem do modelo e quanto vem do harness?

Resultado mais recente em [out/scores.md](out/scores.md).

## Setup
O Claude Code fala o protocolo da Anthropic. O Ollama expõe esse protocolo em `/v1/messages`.
Trocar o modelo é trocar três variáveis de ambiente:

```bash
ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_MODEL=qwen3-coder:30b claude
```

Pré-requisito que quase ninguém menciona: o prompt de sistema do Claude Code tem ~60k tokens.
O Ollama por padrão trunca o contexto bem antes disso, e o modelo nem vê a tarefa.
`OLLAMA_CONTEXT_LENGTH=131072` no serviço resolve.

## Modelos
| modelo | onde roda | por quê |
|---|---|---|
| claude-sonnet-5 | Anthropic, via assinatura do Claude Code | baseline |
| qwen3-coder:30b | local, MoE 30B com 3B ativos, 19 GB | melhor modelo de código aberto que cabe em 48 GB |
| glm-4.7-flash | local, MoE 30B, 19 GB | concorrente direto, família chinesa diferente |

## Tarefas
Cinco tarefas de Python com testes pytest. A tarefa passa se `pytest` passa. Nada de julgamento.

| tarefa | tipo | o que exige |
|---|---|---|
| t1_parse_size | implementar do zero | parsing, validação, edge cases |
| t2_fix_dates | corrigir bug | ler o teste, entender datas DD/MM, tratar vazio |
| t3_watermark | adicionar feature | ler código existente, ordenar, paginar |
| t4_refactor_retry | refatorar | extrair decorator sem quebrar comportamento |
| t5_dq_cli | multi-arquivo | dois módulos novos, CLI, JSON |

## O que é medido
Passou ou não, número de turnos, tempo de parede, tokens, custo. Um agente que acerta em 40 turnos
e 10 minutos não é o mesmo que um que acerta em 6 turnos e 1 minuto.

## Como rodar
```bash
uv run python cc_local/run.py                    # todos os modelos
uv run python cc_local/run.py claude-sonnet-5    # só um
```
