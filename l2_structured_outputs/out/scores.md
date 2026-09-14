| modelo | estrategia | valido 1a tentativa | valido final | tentativas medias | latencia media |
|---|---|---|---|---|---|
| qwen3:8b | A_prompt | 9/10 | 9/10 | 1.0 | 3253ms |
| qwen3:8b | B_prompt_retry | 9/10 | 9/10 | 1.2 | 3268ms |
| qwen3:8b | C_schema | 10/10 | 10/10 | 1.0 | 2832ms |
| llama3.1:8b | A_prompt | 10/10 | 10/10 | 1.0 | 2396ms |
| llama3.1:8b | B_prompt_retry | 10/10 | 10/10 | 1.0 | 1372ms |
| llama3.1:8b | C_schema | 7/10 | 7/10 | 1.0 | 2313ms |
| claude-haiku-4-5 | A_prompt | 10/10 | 10/10 | 1.0 | 1844ms |
| claude-haiku-4-5 | B_prompt_retry | 10/10 | 10/10 | 1.0 | 1672ms |
| claude-haiku-4-5 | C_schema | 10/10 | 10/10 | 1.0 | 2707ms |
