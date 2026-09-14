# Gerador + revisor: o revisor ajuda ou atrapalha? (2026-09-11)

11 tarefas do DE-Bench. Gerador escreve, revisor devolve veredito JSON e código corrigido, testes rodam antes e depois.

| gerador | revisor | antes | depois | revisor acertou | consertou | quebrou | custo |
|---|---|---|---|---|---|---|---|
| qwen3:8b | llama3.1:8b | 9/11 | **5/11** | 3/11 | 1 | 5 | 0 |
| qwen3:8b | claude-sonnet-5 | 9/11 | 8/11 | 5/11 | 0 | 1 | $0,10 |
| claude-haiku-4-5 | llama3.1:8b | 11/11 | 9/11 | 1/11 | 0 | 2 | $0,01 |
| claude-haiku-4-5 | claude-sonnet-5 | 11/11 | 10/11 | 8/11 | 0 | 1 | $0,09 |

## Lições

### 1. Nenhum revisor melhorou o resultado. Todos pioraram.
Nas 4 combinações o acerto caiu depois da revisão. O melhor caso (Sonnet revisando Haiku) perdeu 1 tarefa.
O pior (Llama revisando Qwen) destruiu 4 de 9 acertos. Revisão por LLM sem verificação executável é ruído caro.

### 2. Revisor fraco rejeita tudo.
Llama reprovou 21 de 22 códigos, incluindo os 11 do Haiku que estavam 100% corretos. Um revisor que sempre
reprova tem precisão zero e ainda substitui código bom por código pior. Isso é o "viés de severidade" que o
projeto de juiz calibrado (P6) mede antes de confiar.

### 3. Revisor forte é conservador, mas não é oráculo.
Sonnet aprovou 8 dos 11 do Haiku (certo) e ainda assim reprovou e quebrou 1 correto. Precisão de 73%, e as
2 tarefas que o Qwen errou ele não consertou (respostas unparseable). Revisor bom reduz dano, não cria valor.

### 4. O que cria valor é execução, não opinião.
A única fonte de verdade que funcionou em todo o experimento foi rodar o código. Regra de arquitetura:
LLM revisa para explicar, testes decidem. Nunca aplicar a "correção" do revisor sem re-executar.

### 5. Saída estruturada frágil.
3 vereditos vieram unparseable (JSON quebrado, código como lista). Motivo direto para o L2 (structured outputs).

## Frase para entrevista
"Testei LLM revisando LLM em 44 pares. Nenhuma combinação melhorou o acerto; um revisor fraco derrubou de 82% para 45%.
A lição: revisor sem verificação executável é ruído. Eu uso o modelo para explicar e os testes para decidir."

## Limitações
Uma rodada, 11 tarefas, revisor sem acesso a execução. Próximo: dar ferramenta de execução ao revisor e medir de novo.
