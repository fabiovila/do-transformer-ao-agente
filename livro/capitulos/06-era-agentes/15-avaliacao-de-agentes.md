# Capítulo 15 — Avaliação de agentes: o que medir e por que é difícil

O capítulo 13 mostrou que agente é sistema, não prompt; o capítulo 14 mostrou que sistemas conversam entre si. Resta a pergunta que transforma técnica em produto: *como saber que o agente funciona?* Medir respostas foi a era anterior — “acertou a saída?” —; esta era é sobre medir **processos**: planejamento, seleção de ferramenta, recuperação, execução, custo e recuperação de falhas. E medir processo é muito mais difícil do que parece.

Em 2023–2024, a avaliação de agentes passou por três saltos. O **AgentBench** colocou dezenas de modelos em oito ambientes e revelou, com números, a distância entre os melhores modelos fechados e todo o resto. O **WebArena** e o **OSWorld** trocaram ambientes sintéticos por tarefas realistas — sites de verdade, sistemas operacionais de verdade. E o **tau-bench** introduziu o dado mais desconfortável da era: modelos fortes falham em mais da metade das tarefas, e a *consistência entre tentativas* é pior do que a precisão — um agente pode acertar na segunda tentativa o que errou na primeira, e nenhum benchmark tradicional captura isso.

A pergunta que organiza este capítulo é uma só: **uma resposta certa por acaso não é um sistema robusto**. Ela tem duas consequências práticas. A primeira: avaliar agente exige critérios de processo — e não apenas de resposta. A segunda: as ferramentas baratas de avaliação, como o LLM-as-judge, são tentadoras e viesadas — e confundi-las com validação independente é exatamente o erro que o AGENTS.md (§25) deste projeto avisa para evitar.

## O laboratório dos oito ambientes: AgentBench

O **AgentBench**, de Liu et al. (2023), foi a primeira tentativa sistemática de medir “quão bom agente é um modelo” — e não apenas “quão bom é em responder perguntas”. A definição de tarefa era ampla: o agente recebe um ambiente e um objetivo, e precisa *agir* para alcançá-lo. Foram oito ambientes: sistema operacional (comandos em um terminal), banco de dados (consultas SQL), grafo de conhecimento (consultas sobre uma base de fatos), jogos de cartas digitais, quebra-cabeças de pensamento lateral, tarefas domésticas simuladas, compras na web e navegação em páginas da web.

Os resultados expuseram a hierarquia da época de forma brutal. O GPT-4 liderava com folga, mas mesmo ele ficava longe de dominar os ambientes; os modelos abertos — a família LLaMA 2, naquele momento o melhor disponível — caíam de forma abrupta, com uma margem que as comparações de QA tradicionais não mostravam. A conclusão diagnóstica de Liu et al. foi qualitativa e durável: o gargalo dos modelos não era vocabulário nem conhecimento, mas **raciocínio de longo prazo, tomada de decisão e adesão a instruções** — exatamente as capacidades que um agente precisa em cada loop. O AgentBench estabeleceu o formato da era: ambientes múltiplos, modelos múltiplos, e uma lição de que “modelo forte” e “agente bom” são coisas distintas.

## A internet e o desktop de verdade: WebArena e OSWorld

O AgentBench abriu o caminho, mas seus ambientes eram, em larga medida, construídos. O passo seguinte foi levar o agente para ambientes *realistas*. O **WebArena** (Zhou et al., 2023) replica a experiência de navegar na web: quatro sites autocontidos — um fórum no estilo Reddit, um repositório de código no estilo GitLab, uma loja no estilo Amazon e um CMS no estilo WordPress — sobre os quais são definidas 812 tarefas que exigem planejar, navegar e executar ações reais (editar um perfil, fazer uma compra, publicar um post). O **OSWorld** (Xie et al., 2024) vai mais fundo: 369 tarefas em sistemas operacionais de verdade (Ubuntu, Windows, macOS), em que o agente interage pela tela inteira — capturas de tela e movimentos de mouse e teclado — como um usuário humano, sem API nem assistência.

Os resultados foram humilhantes no bom sentido: mesmo os melhores agentes autônomos ficavam na casa dos 10–20% de sucesso no OSWorld, e o WebArena, com os modelos de topo da época, raramente passava da casa dos 30% em abordagens gerais. Duas leituras se impuseram. A primeira: ambientes realistas punem implacavelmente a *fragilidade* — um clique errado, uma janela modal inesperada, uma mudança de layout derrubam trajetórias que funcionavam em ambientes limpos. A segunda: esses benchmarks viraram o padrão de facto da área — quem quer dizer “meu agente funciona” hoje é medido contra eles —, e continuam sendo o ponto de partida de qualquer suíte de avaliação, nunca o ponto de chegada.

## O usuário que responde: tau-bench e a consistência

O **tau-bench**, de Yao et al. (2024), fez a pergunta que faltava: *o que acontece quando o usuário também é simulado?* Em dois domínios de atendimento — uma loja de varejo e uma companhia aérea —, um **usuário simulado** conversa com o agente, que só pode responder por meio de ferramentas (consulta de catálogo, reserva, cancelamento, política de reembolso), enquanto uma **política de domínio** define quais estados são válidos e o que conta como sucesso. O agente precisa, literalmente, completar a tarefa no mundo — como um funcionário real — e não apenas dizer a coisa certa.

O tau-bench introduziu uma métrica que se tornou central para toda a avaliação de agentes: o **pass@k**. A definição é implícita no nome — *k* tentativas independentes da mesma tarefa —, mas a leitura correta é a mais importante deste capítulo: pass@k não mede “acertou de primeira”, mede **consistência**. Um agente que acerta 1 de 3 execuções tem pass@1 = 33% e pass@3 = 100% *se* qualquer uma das tentativas contar — mas o tau-bench computa a fração das tentativas que *realmente* têm sucesso, e é essa fração que revela o problema.

Os resultados confirmaram a intuição com números: modelos fortes falhavam em mais da metade das tarefas, e — o dado decisivo — a **consistência entre execuções era pior do que a precisão**. O mesmo modelo, a mesma tarefa, o mesmo prompt: uma execução completa a tarefa, a seguinte se perde em um desvio. Para o engenheiro, a consequência não pode ser subestimada: nenhum benchmark de “acurácia média” captura a diferença entre um sistema que acerta consistentemente e um que acerta por acaso. A consistência, e não a precisão, é o que separa uma demo de um produto.

## Métricas de processo, não só de resposta

Com o campo maduro, a revisão *From Language to Action* (2025) organizou o que a avaliação de agentes realmente precisa medir. A mudança de mentalidade é de granularidade: um agente não é uma função input→output, é uma sequência de estados, ações e observações — e cada elo da cadeia tem a sua métrica:

| Componente | Pergunta que responde | Métrica típica |
| --- | --- | --- |
| Retrieval | a evidência certa chegou? | recall@k, fidelidade da fonte |
| Tool selection | a ferramenta certa foi escolhida? | acurácia da chamada, taxa de erro |
| Planning | o plano conduziu ao objetivo? | completude do plano, passos por tarefa |
| Execution | a ação modificou o mundo como esperado? | sucesso da execução, efeitos colaterais |
| Verification | o resultado foi checado antes de responder? | taxa de correção após feedback |
| Failure recovery | o sistema se recupera de um erro? | taxa de retomada, passos de correção |
| Cost / latency | quanto o processo custou? | tokens, chamadas, tempo por tarefa |

A regra de ouro é a mesma do capítulo 12, transposta para agentes: **cada estágio tem a sua métrica, e o número agregado não diz onde está a falha**. Se a resposta final está errada, pode ser um retriever ruim, uma ferramenta errada, um plano frágil ou uma verificação ausente — e um score médio não discrimina nenhum deles. Para o diagnóstico, é preciso observar a trajetória inteira: quais ações foram tomadas, quais observações voltaram, onde o agente desviou. É a diferença entre avaliar a resposta e auditar o processo.

## LLM-as-judge: barato, viesado, inevitável

Quando a resposta certa não existe — uma resposta bem escrita, um resumo útil, um plano bom —, a avaliação automática precisa de um julgador. O padrão da era é o **LLM-as-judge**: um modelo lê a resposta e atribui uma nota, com ou sem rubrica. É barato, escalável e alinhado com a preferência humana em uma variedade de tarefas — e por isso virou a ferramenta padrão de avaliação de LLMs.

Mas o LLM-as-judge não é **validação independente**. O julgador é a mesma espécie de sistema que produz a resposta: tem os mesmos vieses, as mesmas preferências de posição e verbosidade, a mesma tendência de preferir respostas parecidas com as suas. Aplicado a avaliação de *processo* — julgar se o agente escolheu a ferramenta certa, planejou bem, verificou —, o viés do julgador se soma ao problema de não existir “resposta certa”. A disciplina que este capítulo recomenda é a do AGENTS.md (§25): use LLM-as-judge como *primeira triagem* — rubricas explícitas, escalas definidas, calibração periódica contra uma amostra de julgamento humano — e jamais como tribunal final dos casos críticos. A regra não muda porque a ferramenta é conveniente: **o gerador não valida a si mesmo** — e um modelo julgando outro modelo é, no limite, o mesmo gerador avaliando-se através de um espelho.

## A lição estrutural

O capítulo 13 definiu o critério de término como o componente mais negligenciado de um agente: *quando parar?* Este capítulo definiu o critério de avaliação: *como saber que funcionou?* A lição estrutural é que são **a mesma pergunta vista por dois ângulos**. Para saber quando parar, o sistema precisa saber o que conta como sucesso; para saber se funcionou, precisa do mesmo critério. Um agente sem objetivo verificável não tem como parar nem como ser avaliado — ele apenas termina quando o orçamento acaba.

Isso resolve também o mistério do tau-bench: a consistência é o elo fraco porque o critério de sucesso, em tarefas de agente, é um *estado do mundo* — a tarefa foi completada? —, e alcançar esse estado exige uma cadeia de decisões corretas, qualquer uma das quais pode falhar. A avaliação de agentes é, portanto, a engenharia do critério de término, medida em escala: definir o objetivo, decompor o processo em estágios mensuráveis e verificar, repetidamente, que o sistema alcança o estado desejado — não uma vez, mas de forma consistente.

## Para o engenheiro

Avalie o processo, não apenas a resposta. Planejamento, seleção de ferramenta, recuperação, execução e recuperação de falha são exatamente o que você vai depurar em produção — se não medir cada estágio, o debug de um agente quebrado é adivinhação. Trace cada trajetória: ações, observações, desvios. Um score médio diz que algo está errado; só a trajetória diz onde.

Consistência importa mais que acerto isolado. Um agente que acerta 1 em 3 execuções não é confiável, por mais forte que seja o modelo por baixo — meça pass@k e a variabilidade entre execuções da mesma tarefa. Se a sua suíte não roda cada caso múltiplas vezes, você está medindo a sorte, não o sistema.

Benchmarks públicos — AgentBench, WebArena, OSWorld, tau-bench — são pontos de partida, não contratos. Use-os para calibrar o que é possível e para treinar o seu vocabulário de avaliação; mas o que decide o seu produto é uma suíte própria de tarefas reais, com critérios explícitos de sucesso, ranhura de estado do mundo, e executada repetidamente.

E quando a “resposta certa” não existir, use LLM-as-judge com disciplina: rubricas explícitas, escalas definidas, amostra periódica de calibração humana — e checagem manual dos casos críticos. Barato não é sinônimo de independente. Lembre-se: a pergunta de avaliação e a pergunta de término são a mesma — defina o objetivo, decomponha o processo e meça a consistência com que o sistema chega lá.

---

**Fontes:** [Liu et al., 2023] — AgentBench; [Yao et al., 2024] — tau-bench; [Masterman et al., 2024] — métricas objetivas vs. subjetivas; [From Language to Action, 2025] — revisão de benchmarks de agentes; [Agentic AI Frameworks, 2025] — guardrails e avaliação em frameworks.
