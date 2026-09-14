# Prompt caching

## Em 3 linhas
1. O provedor guarda o estado de um prefixo repetido do prompt e cobra ~10% do preço nas leituras seguintes.
2. Só funciona se o prefixo for byte a byte idêntico. Data, id ou espaço a mais invalida tudo dali para frente.
3. Ordem do prompt: estável primeiro (sistema, tools, documentos), variável por último (pergunta, timestamp).

## Números vistos
Claude Code, turno trivial: 45k tokens lidos do cache + 15k criados. Sem cache seriam 60k cheios por turno.
Ollama não tem cache de prefixo entre requests: modelo local reprocessa os 60k tokens em cada turno do agente.

## Como verificar
`usage.cache_read_input_tokens` na resposta. Zero em chamadas repetidas = algo muda o prefixo.

## Onde volta na trilha
P3 cache semântico (é outro tipo: cache de resposta por similaridade, não de prefixo), P9 gateway (custo por tenant).
