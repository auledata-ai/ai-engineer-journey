# DE-Bench v1: modelos locais em tarefas de engenharia de dados (2026-09-10)

## Resultado
| modelo | pass | tokens out (média) | latência média | custo |
|---|---|---|---|---|
| qwen3:8b | 9/11 (82%) | 75 | 3,0 s | 0 |
| qwen3:8b + think | 10/11 (91%) | 938 | 25 s | 0 |
| llama3.1:8b | 9/11 (82%) | 83 | 2,8 s | 0 |

11 tarefas: 7 SQL (DuckDB), 3 Python (pandas), 1 qualidade de dados (JSON). Verificação por execução.

## Lições

### 1. Raciocínio compra 9 pontos por 12x tokens e 9x latência
O modo think do Qwen3 resolveu o anti-join e o acumulado mensal que o modo rápido errou.
Preço: 938 tokens por resposta em vez de 75, e 25 s em vez de 3 s. Em API paga, 12x o custo de saída.
Decisão de arquitetura: modo rápido por padrão, escalar para think só quando a validação falha.
É exatamente o padrão "router + escalonamento" do projeto P9.

### 2. Audite o eval antes de acreditar no score
Na primeira rodada, os 3 modelos falharam a mesma tarefa. Suspeitei do benchmark, não dos modelos.
Achei dois bugs meus: prompt ambíguo ("total de pedidos" = contagem ou soma?) e comparador por string
(DATE vs TIMESTAMP, 200 vs 200.00). Corrigido, a tarefa passou a discriminar modelos.
Regra: falha unânime é sinal de bug no eval. Gabarito de referência tem que passar no verificador (test_tasks.py).

### 3. 8B local resolve 80% do trabalho de SQL e pandas
Joins, window functions, top-N, dedup, flatten de JSON, geração de regras de DQ: tudo certo, a custo zero e 1 a 3 s.
Onde erram: lógica de negação (anti-join com WHERE em vez de NOT EXISTS) e detalhes de sintaxe do dialeto.

### 4. Bug clássico de produção apareceu sozinho
Llama usou `dateutil.parser.parse("10/09/2025")` e leu 9 de outubro (mês primeiro, padrão americano).
Passa em teste ingênuo, quebra em produção com datas brasileiras. Bom exemplo para entrevista.

### 5. Verificação por execução > comparação de texto
Duas queries diferentes com o mesmo resultado são ambas corretas. Comparar SQL como string
reprovaria respostas válidas. Rodar e comparar o resultado é o que se faz em eval de código.

## Frase para entrevista
"Montei um benchmark de tarefas de engenharia de dados com verificação por execução.
Um 8B local acerta 82%; com raciocínio ligado vai a 91%, mas custa 12x mais tokens.
Isso define a política de roteamento: barato por padrão, escalar quando a validação falha."

## Próximos passos do benchmark
- Adicionar coluna de modelos pagos quando houver chave (código pronto).
- Mais tarefas: PySpark (precisa Java), Delta MERGE, text-to-SQL com schema grande, explicação de erro.
- Rodar 3x por tarefa e reportar variância. Uma rodada é anedota.

## Rodada 2: modelos pagos entram (2026-09-11)

| modelo | pass | tokens out | latência | custo (11 tarefas) |
|---|---|---|---|---|
| qwen3:8b | 82% | 75 | 2,9 s | 0 |
| qwen3:8b + think | 91% | 938 | 25,6 s | 0 |
| llama3.1:8b | 82% | 83 | 2,9 s | 0 |
| claude-haiku-4-5 | **100%** | 108 | **2,0 s** | $0,008 |
| claude-sonnet-5 | **100%** | 136 | 2,3 s | $0,022 |
| claude-opus-5 | 91% | 155 | 3,0 s | $0,059 |

### Lições
1. **Haiku é o vencedor por custo-benefício.** 100% de acerto, o mais rápido de todos, menos de 1 centavo pelas 11 tarefas.
   Para SQL e pandas de complexidade normal, não há motivo para pagar Sonnet ou Opus.
2. **Opus errou uma tarefa que Haiku acertou.** Modelo maior não é monotonicamente melhor em tarefa simples.
   O erro foi de sintaxe do dialeto DuckDB (BinderException), o mesmo tipo que derrubou o Qwen. Uma rodada só: pode ser ruído. Rodar 3x antes de concluir.
3. **Local vs pago no mesmo eixo.** 8B local: 82% a custo zero e 3 s. Haiku: 100% a 0,07 centavo por tarefa e 2 s.
   A diferença de 18 pontos custa menos de 1 centavo. O argumento a favor do local passa a ser privacidade ou volume gigante, não dinheiro.
4. **Qwen com raciocínio empata com Opus em acerto**, mas leva 10x mais tempo. Raciocínio local é um substituto lento, não barato.

### Frase para entrevista
"No meu benchmark de engenharia de dados, Haiku acertou 100% a menos de 1 centavo por 11 tarefas e foi o mais rápido.
Um 8B local ficou em 82%. A regra que tirei: comece pelo menor modelo pago, meça, e só suba quando o eval mostrar falha."
