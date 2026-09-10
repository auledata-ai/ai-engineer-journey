# L1 - API, tokens e custo

## Em 5 linhas
1. LLM cobra por token, não por pergunta. Token ≈ 3/4 de uma palavra em inglês, menos em português.
2. Saída custa 5x mais que entrada. Resposta longa é o que pesa na conta.
3. Modelo maior = mais caro e mais lento. Haiku resolve classificação e extração simples tão bem quanto Opus.
4. Toda resposta traz `usage` (tokens in/out) e `stop_reason`. Logue sempre. Sem isso não há controle de custo.
5. Em produção, custo se controla com: modelo certo por tarefa, `max_tokens` justo, prompt curto e cache de prefixo.

## Preços de referência (USD por 1M tokens, set/2026)
| Modelo | Input | Output | Uso típico |
|---|---|---|---|
| Haiku 4.5 | 1 | 5 | classificação, extração, roteamento |
| Sonnet 5 | 2 | 10 | resumo, RAG, agentes de volume |
| Opus 5 | 5 | 25 | raciocínio difícil, código complexo, juiz |

## Conta de padeiro (decore o método, não os números)
Custo = tokens_in/1M × preço_in + tokens_out/1M × preço_out

Exemplo: classificar um email (≈120 tokens in, 3 out), 1 milhão de vezes por mês:
- Haiku: 120M/1M×1 + 3M/1M×5 = **$135/mês**
- Opus: 120M/1M×5 + 3M/1M×25 = **$675/mês**
Mesma qualidade na tarefa, 5x o preço. Esse é o argumento do projeto "roteador de custo" (P9).

## O que a resposta da API te dá
- `usage.input_tokens`, `usage.output_tokens`: base do custo. Guarde por request.
- `usage.cache_read_input_tokens`: quanto veio do cache de prompt (10% do preço). Zero = você não está cacheando.
- `stop_reason`: `end_turn` (ok), `max_tokens` (cortou, aumente o limite), `tool_use` (quer chamar ferramenta), `refusal` (recusou, trate).
- Latência: meça você mesmo com `time.perf_counter()`. Cresce com tokens de saída e com o tamanho do modelo.

## Frase para entrevista
"Antes de otimizar, eu meço tokens por request e custo por tarefa concluída. Depois escolho o modelo mais barato que passa no eval, e cacheio o prefixo estável. Custo por request não é a métrica; custo por tarefa resolvida é."

## Onde isso volta na trilha
P1 (eval em CI mede custo por caso), P3 (cache semântico), P9 (gateway com budgets), P15 (break-even de modelo próprio).

## Código de referência
l1_api_tokens_cost/run.py (branch feat/l1-api-tokens-cost). Roda com qualquer chave depois.

## O que aconteceu na prática (Ollama, M4 Pro 48 GB, 2026-09-10)

### Lição 1: raciocínio oculto custa tokens e latência
Qwen3 8B pelo endpoint compatível com OpenAI, sem conseguir desligar o `think`:
- "Lisboa": **119 tokens, 7 s**. Pelo endpoint nativo com `think: false`: **4 tokens, 245 ms**.
- Prompt de raciocínio: bateu em 512 tokens sem texto visível. Todo o orçamento foi para o pensamento.

Moral: modelos com modo de raciocínio (Qwen3, Claude com thinking, o1/o3) cobram os tokens de pensamento.
Para classificação e extração, desligue. Para problemas difíceis, ligue e aumente `max_tokens`.
Quando `stop_reason == max_tokens` e a resposta vem vazia, o culpado costuma ser esse.

### Lição 2: "compatível com OpenAI" não é igual a OpenAI
O endpoint `/v1` do Ollama ignorou `think` e devolveu o raciocínio como texto, com quebras de linha que
quebraram até o parse do JSON. O endpoint nativo `/api/chat` respeitou tudo.
Adaptador por provider (uma função por API, mesma assinatura) é o padrão que resolve isso. Foi o que fiz no run.py.

### Lição 3: modelo local de 8B resolve tarefas simples
| prompt | in | out | ms | acertou? |
|---|---|---|---|---|
| curto | 29 | 4 | 245 | sim |
| classificacao | 57 | 2 | 201 | sim |
| extracao | 79 | 46 | 1341 | sim, mas envolveu em ```json (precisa parse tolerante, tema do L2) |
| resumo | 79 | 53 | 1490 | sim |
| raciocinio | 70 | 119 | 3168 | sim, 9,6 milhões |

Custo marginal zero, 200 ms a 3 s de latência. Para essas 5 tarefas, um 8B local bastaria.
O argumento a favor de modelo pago aparece em: contexto longo, raciocínio multi-etapa, tarefas ambíguas, e SLA de latência sob carga.
