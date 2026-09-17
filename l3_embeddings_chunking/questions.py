"""Perguntas com gabarito ancorado em TRECHO, nao em indice de chunk.

Por que trecho: as fronteiras dos chunks mudam a cada estrategia e tamanho.
Um chunk conta como acerto se ele CONTEM o trecho da resposta. Efeito colateral
valioso: se o trecho cai em cima de uma fronteira, NENHUM chunk o contem e todos
falham. E exatamente assim que se enxerga para que serve a sobreposicao.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    text: str
    answer_quote: str  # substring exata do corpus
    kind: str  # factual | tabela | conceitual | multi_hop


QUESTIONS: list[Question] = [
    Question("Qual modelo teve o melhor custo-benefício no benchmark de engenharia de dados?",
             "Haiku é o vencedor por custo-benefício", "factual"),
    Question("Quanto custou rodar as 11 tarefas do DE-Bench no Haiku?",
             "menos de 1 centavo pelas 11 tarefas", "factual"),
    Question("O Opus acertou tudo no benchmark?",
             "Opus errou uma tarefa que Haiku acertou", "factual"),
    Question("Qual foi a taxa de acerto do qwen3 com raciocínio ligado?",
             "10/11 (91%)", "tabela"),
    Question("Quanto tempo a mais o modo de raciocínio custa?",
             "mas leva 10x mais tempo", "factual"),
    Question("O revisor melhorou o resultado do código gerado?",
             "Nenhum revisor melhorou o resultado", "conceitual"),
    Question("O que acontece quando um revisor fraco avalia código correto?",
             "Revisor fraco rejeita tudo", "conceitual"),
    Question("Por que colar o JSON Schema no prompt quebra modelo pequeno?",
             "Schema cru no prompt derruba modelo pequeno", "conceitual"),
    Question("A restrição de schema no provedor garante que os valores estejam no intervalo certo?",
             "Restrição de schema garante tipo, não intervalo", "conceitual"),
    Question("Quanto custa em dólares por milhão de tokens a saída do Opus 5?",
             "| Opus 5 | 5 | 25 |", "tabela"),
    Question("O que significa o stop_reason igual a max_tokens?",
             "`max_tokens` (cortou, aumente o limite)", "factual"),
    Question("Como eu verifico se o cache de prompt está funcionando?",
             "`usage.cache_read_input_tokens` na resposta", "factual"),
    Question("Qual regra eu sigo quando todos os modelos erram a mesma tarefa?",
             "falha unânime é sinal de bug no eval", "conceitual"),
    Question("Por que o Claude Code com modelo local ficou inviável?",
             "prompt de sistema tem ~60k tokens", "conceitual"),
    Question("Qual projeto de portfólio eu faço primeiro depois dos labs?",
             "prompt-ops", "multi_hop"),
]


def validate(corpus: str) -> list[str]:
    """Devolve as perguntas cujo trecho de gabarito NAO existe no corpus."""
    return [q.text for q in QUESTIONS if q.answer_quote not in corpus]
