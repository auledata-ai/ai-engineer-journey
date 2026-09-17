# L2 - Structured outputs: JSON válido sempre

## Em 5 linhas
1. LLM gera texto. "Devolva JSON" é um pedido, não uma garantia. Aspas, chaves no conteúdo, markdown, injeção: tudo quebra o parse.
2. O contrato é um schema (Pydantic no Python). Ele vale para o prompt, para a validação e para a documentação. Uma fonte só.
3. Três níveis de garantia: pedir no prompt (frágil), validar e re-pedir mandando o erro de volta (robusto, custa tentativas), ou restringir a geração ao schema no provedor (garantido no formato).
4. Restrição de schema garante sintaxe e tipos. Não garante que o conteúdo esteja certo. Validação de negócio continua sendo sua.
5. Todo tool use e todo agente é structured output por baixo: a chamada de ferramenta é um JSON contra um schema.

## Como cada provedor faz
- **Anthropic**: `client.messages.parse(..., output_format=Modelo)` devolve `parsed_output` já validado. Ou `output_config={"format": ...}` no create.
- **Ollama**: campo `format` recebe o JSON Schema e o sampler só emite tokens que respeitam a gramática.
- **OpenAI**: `response_format` com `json_schema` e `strict: true`.

## Padrão de código
```python
class Review(BaseModel):
    verdict: Literal["approve", "reject"]
    confidence: float = Field(ge=0, le=1)
    issues: list[Issue]

# 1. schema vira o contrato        Review.model_json_schema()
# 2. provedor restringe a geração   format=schema / output_format=Review
# 3. Pydantic valida de novo        Review.model_validate_json(text)
# 4. se falhar, retry com o erro    prompt += f"Erro: {e}. Corrija."
```

## Onde volta na trilha
Tool use (L4/P14), extração de documentos (P7), text-to-SQL (P5), qualquer juiz (P6): sempre schema primeiro.

## Resultado do lab (2026-09-14, 10 inputs hostis: aspas, chaves, unicode, vazio, injeção)

| modelo | prompt com exemplo | prompt + retry | schema no provedor |
|---|---|---|---|
| qwen3:8b | 9/10 | 9/10 | **10/10** |
| llama3.1:8b | 10/10 | 10/10 | 7/10 |
| claude-haiku-4-5 | 10/10 | 10/10 | 10/10 |

### Lições que só apareceram rodando
1. **Schema cru no prompt derruba modelo pequeno.** Llama com o JSON Schema colado no prompt: 0/10. Ele devolvia o próprio schema.
   Com um exemplo de instância: 10/10. Modelo pequeno imita o que vê. Mostre o exemplo, não a definição.
2. **Restrição de schema garante tipo, não intervalo.** Llama com `format` devolveu JSON perfeito com `confidence: 100` num campo de 0 a 1.
   A gramática do provedor não lê `minimum`/`maximum`. Pydantic pegou. Validar do seu lado é obrigatório mesmo com schema no provedor.
3. **Aspas escapadas ainda derrubam o Qwen no prompt**, e o retry não salvou (3 tentativas, mesmo erro). Só o schema no provedor resolveu. É o caso que justifica a estratégia C.
4. **Haiku acerta tudo nas três.** Modelo forte tolera prompt ruim. Modelo fraco precisa de engenharia. O custo de engenharia é o que você paga para usar local.

### Regra final
Schema no provedor + Pydantic do seu lado + retry com o erro como última rede. As três camadas, sempre.

