## Par gerador + revisor

| gerador | revisor | antes | depois | revisor acertou | consertou | quebrou | custo | tempo medio |
|---|---|---|---|---|---|---|---|---|
| qwen3:8b | llama3.1:8b | 9/11 | 5/11 | 3/11 | 1 | 5 | $0.000 | 15s |
| qwen3:8b | claude-sonnet-5 | 9/11 | 8/11 | 5/11 | 0 | 1 | $0.100 | 17s |
| claude-haiku-4-5 | llama3.1:8b | 11/11 | 9/11 | 1/11 | 0 | 2 | $0.008 | 7s |
| claude-haiku-4-5 | claude-sonnet-5 | 11/11 | 10/11 | 8/11 | 0 | 1 | $0.087 | 8s |
