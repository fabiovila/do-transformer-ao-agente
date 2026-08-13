# Capítulo 19 — Avaliação, limites e o horizonte

Todo bom livro de engenharia termina com a parte desconfortável: o que sabemos e o que não sabemos. Este capítulo de fechamento recusa o final feliz. A narrativa chegou a 2026 com agentes, RAG, ferramentas e protocolos — mas o elo mais fraco de toda a corrente é o mesmo que o capítulo 15 anunciou: **medir sistemas agentic de forma confiável continua sendo um problema em aberto**. A consistência entre tentativas é o gargalo, o LLM-as-judge não é validação independente, e avaliar processo custa muito mais do que avaliar resposta.

Os capítulos 0–18 montaram uma tese completa: um LLM é o núcleo de um sistema maior composto de contexto, recuperação, ferramentas, ambiente, memória, iteração e verificação. Este capítulo cobra a conta da tese. Para cada componente, quais são os limites conhecidos — segurança e reversibilidade das ações, custo dos loops, critérios de parada? O que o campo sabe medir, e o que ainda não sabe? E, no horizonte de 2026+, quais estruturas prometem fechar essas lacunas — orquestração multi-ferramenta, modelos de raciocínio, agentes verificáveis, a coexistência do RAG com o contexto longo?

A pergunta final é a mesma do capítulo 0, agora com as mãos sujas: *que combinação de modelo, contexto, ferramentas, ambiente, memória, feedback e verificação torna isso confiável — e como sabemos que é confiável?* A diferença é que, depois de dezoito capítulos, a pergunta deixou de ser retórica e virou especificação de engenharia.

## O elo fraco: a consistência entre tentativas

O capítulo 15 apresentou o dado que organiza todo este capítulo: o tau-bench mostrou que modelos fortes falham em mais da metade das tarefas de agente e, decisivamente, que a **consistência entre execuções é pior do que a precisão**. A consequência é implícita e brutal: um sistema que funciona em uma demo pode falhar na mesma tarefa minutos depois, com o mesmo prompt e o mesmo modelo.

Por que a consistência é o elo fraco? Porque uma tarefa de agente é uma *cadeia* de decisões — escolher a ferramenta, formular a consulta, interpretar a observação, decidir se já chegou —, e a probabilidade de a cadeia inteira dar certo é o produto das probabilidades de cada elo. Se cada passo acerta com 90% de probabilidade, dez passos sucessivos dão ~35% de sucesso — e o modelo “forte” deixa de ser forte no sistema. A robustez não se herda do modelo: constrói-se no processo — mais verificação, mais estados de recuperação, mais testes. É por isso que o capítulo 18 insistiu que o verificador é parte do loop: em sistemas agentic, a verificação é o que transforma 35% em 90%.

Para o engenheiro, o diagnóstico muda a política de produto. Uma resposta certa por acaso não é um sistema robusto — e isso vale do protótipo à produção. A primeira pergunta de qualquer sistema de agente não deve ser “qual modelo?”, mas “qual a consistência deste processo — e como a medimos?”.

## Segurança e reversibilidade: a escala das ações

O segundo limite é a classificação das ações que um agente pode tomar. Um agente que apenas lê arquivos tem um risco; um agente que escreve, envia, paga ou apaga tem outro. A classificação que o AGENTS.md (§35) deste projeto estabeleceu é o mapa de risco:

```text
ação informativa             →  ler, buscar, calcular        →  risco baixo
ação reversível              →  escrever rascunho, criar    →  risco médio
ação potencialmente destrutiva →  enviar, modificar, excluir  →  risco alto
ação irreversível            →  pagar, enviar email, apagar  →  risco máximo
```

A regra de ouro é proporcionalidade: **quanto maior o impacto, maior a verificação** — e isso se materializa em guardrails (o termo da indústria para as camadas de controle). Frameworks da era, como os que o survey Agentic AI Frameworks (2025) documentou, passaram a embutir políticas: confirmação humana para ações destrutivas (*human-in-the-loop*), permissões por escopo, logs obrigatórios, orçamentos de tokens e tempo. O capítulo 13 viu esse movimento nascendo com o LangGraph; aqui ele é princípio. Ferramentas poderosas exigem mais disciplina, não menos — e a disciplina é o que separa uma capacidade de um acidente.

A reversibilidade também define a estratégia de teste. Ações informativas podem ser executadas livremente em produção; ações destrutivas devem ser testadas em ambientes de replicação antes de tocar o mundo real. Um agente que envia e-mails deveria ter, por padrão, um modo de ensaio — a mesma lógica de *staging* que o shell deste projeto usa para experimentação controlada. O custo de errar cresce com a irreversibilidade; a inspeção deve crescer na mesma proporção.

## Custo e o critério de parada

O terceiro limite é o mais prosaico e o mais negligenciado: **custo**. Cada iteração do loop consome tokens, e o custo de um loop longo é a diferença entre uma demo e um sistema de produção. O critério de parada do capítulo 13 — *quando parar?* — tem aqui a sua formulação econômica:

```text
continue enquanto:  ganho de informação esperado  >  custo da ação
pare quando:        ganho de informação esperado  ≤  custo da ação
```

É a mesma lógica do capítulo 18 aplicada ao orçamento: iterar sem informação nova apenas repete o erro pagando por ele. Os protocolos da Parte VII acrescentaram uma dimensão nova a essa conta — o *custo da comunicação*. MCP e A2A “gastam tokens para falar”: cada primitiva trocada entre cliente, servidor e agentes consome contexto e latência, e em sistemas com muitos servidores ou muitos agentes a soma é real. O capítulo 14 já vira esse custo no multi-agente; aqui ele aparece como propriedade dos protocolos — e exige a mesma disciplina de orçamento: medir tokens por tarefa, limitar iterações, monitorar deriva.

## O horizonte 2026+

Com os limites mapeados, o horizonte tem quatro movimentos que prometem — com a honestidade de quem viu a hype de 2023 de perto — *avançar*, não *resolver*.

**Orquestração multi-ferramenta.** O survey *From Single-Tool Call to Multi-Tool Orchestration* (2026) registra a transição das chamadas únicas para trajetórias longas com estado, em que o agente alterna ferramentas, reutiliza observações e gerencia contexto entre chamadas. É o loop do capítulo 18 em escala industrial — e o problema de desenho passa a ser segurança, custo e verificabilidade de trajetórias, não a chamada individual.

**Modelos de raciocínio.** O raciocínio explícito como etapa de inferência — o *test-time compute*, o “pensar antes de responder” — mudou a economia do loop: mais tokens gastos *dentro* da inferência podem reduzir o número de iterações *externas* de busca e correção. A pergunta de pesquisa é quanta deliberação compensa em cada tarefa — o mesmo trade-off do critério de parada, agora dentro do modelo.

**Agentes verificáveis.** A fronteira estrutural que os protocolos stateless não entregam por padrão — proveniência, linhagem e memória duradoura — virou objeto de design. Agentes verificáveis são aqueles em que cada ação tem rastro, cada resposta tem fonte e o estado persiste entre sessões; o movimento completa o que o capítulo 15 começou (medir processo) e o capítulo 18 tornou princípio (verificação como peça do loop).

**RAG e contexto longo.** O capítulo 12 terminou com o roteamento dinâmico — contexto longo quando a resposta exige o documento inteiro, RAG quando exige trechos. O horizonte aponta a *coexistência*: janelas de 1M+ de tokens tornaram o contexto longo uma opção econômica em casos específicos, e o desenho maduro roteia por consulta, em vez de apostar em uma arquitetura única. A conclusão de Li et al. (2024) — na maioria das consultas RAG e contexto longo concordam — permanece a bússola da decisão.

## As perguntas que o campo ainda não respondeu

Por fim, o inventário honesto do que permanece aberto — porque um livro de engenharia termina melhor apontando o desconhecido do que fingindo que acabou:

- **Consistência**: por que a variabilidade entre execuções é tão alta, e como projetar processos que a reduzam? O tau-bench mediu o sintoma; a cura é pesquisa em aberto.
- **Avaliação objetiva de processo**: como medir planejamento, seleção de ferramenta e recuperação de falha sem depender de LLM-as-judge — o verificador que o capítulo 18 exige para operação ainda é frágil para avaliação?
- **Governança de protocolos**: o MCP e o A2A migraram para a Linux Foundation, mas o poder de definir o padrão — e de estendê-lo — é um equilíbrio em movimento; quem decide, com que critério e em que velocidade?
- **Segurança de recuperação**: o RAG herda os riscos das suas fontes — envenenamento de documentos, distratores injetados, jailbreaks via contexto; como o loop verifica a *fonte*, não apenas a resposta?
- **O custo de tudo**: quando o loop, os protocolos e os multi-agentes somam tokens, latência e complexidade, qual a lei de custo dos sistemas agentic — e quem a está medindo com rigor?

Nenhuma dessas perguntas tem resposta fechada em 2026. A disciplina que o livro ofereceu — avaliar por estágio, verificar com independentes, medir consistência, classificar risco, definir critério de parada — é exatamente a ferramenta para trabalhar dentro dessa incerteza: não para eliminá-la, mas para torná-la observável.

## A lição estrutural

A herança deste capítulo não é um veredito, é um método — e o método é a tese do livro testada no limite: **a confiabilidade de um sistema agentic é propriedade do processo, não do modelo**. A consistência é o elo fraco porque uma tarefa de agente é uma cadeia de decisões, e a cadeia inteira só dá certo quando cada elo acerta — mas é também a prova de que a robustez se constrói: mais verificação, mais estados de recuperação e mais testes são o que transforma um sistema que acerta 35% das vezes em um que acerta 90%. As quatro disciplinas do capítulo — medir por estágio, verificar com mecanismos independentes do gerador, classificar ações por risco e definir critério de parada — não fecham as perguntas que a seção anterior deixou em aberto; elas fazem o que a engenharia sempre faz com o desconhecido: torná-lo observável. E é esse o fecho do arco: cada era do livro adicionou uma peça ao sistema — contexto, recuperação, ferramentas, agentes, protocolos —, e a última peça é a que mede se as outras funcionam.

## A pergunta final

O capítulo 0 abriu o livro com uma pergunta que parecia de filosofia e era de engenharia: *que combinação de modelo, contexto, ferramentas, ambiente, memória, feedback e verificação torna o sistema confiável?* Dezoito capítulos depois, a pergunta se desdobrou em especificações: a recuperação precisa construir evidência (capítulos 5–12); as ferramentas precisam ser extensões com contrato (capítulos 9–11); os agentes precisam de estado, objetivo e critério de término (capítulos 13–14); a avaliação precisa medir processo e consistência (capítulo 15); os protocolos precisam padronizar o mundo (capítulos 16–17); e o loop precisa verificar, corrigir e parar (capítulos 10 e 18).

A metade que falta é a que este capítulo deixou em aberto: *como sabemos que é confiável?* A resposta madura não é um benchmark novo, nem um modelo maior — é a combinação das duas disciplinas que este livro repetiu até a exaustão: **medir o processo, não apenas a resposta, e verificar com mecanismos independentes do gerador**. Quem construir sistemas assim não terá eliminado a incerteza — ninguém tem —, mas terá feito o que a engenharia sempre faz com o desconhecido: transformado-o em observável, em medível e, portanto, em gerenciável.

## Para o engenheiro

O elo fraco atual é a consistência: um sistema que falha em mais da metade das tarefas não é de produção, por mais forte que seja o modelo por baixo. Meça pass@k e a variabilidade entre execuções antes de confiar em qualquer demo — e não aceite “funcionou na minha máquina” como evidência de robustez.

Avaliar sistema custa mais que avaliar resposta. Reserve orçamento e construa uma suíte própria de testes de agente — tarefas reais, critérios explícitos, execução repetida — exatamente como você já faz com testes unitários. Sem essa suíte, qualquer melhoria é opinião, não medida.

Classifique as ações do seu agente por risco: informativa → reversível → destrutiva → irreversível. Quanto mais irreversível, mais confirmação explícita, mais logs e mais ambiente de ensaio. Guardrails não são burocracia: são o que permite dar autonomia sem acidente.

E quanto ao horizonte 2026+ — orquestração multi-ferramenta, modelos de raciocínio, agentes verificáveis, RAG e contexto longo — acompanhe, mas meça no seu caso antes de confiar. Capacidade demonstrada em demo não é robustez, e a regra que fechou este livro vale para as tecnologias que ainda não existem: o modelo propõe, o processo decide, e o sistema verifica — é nessa combinação, e não em nenhuma peça isolada, que a confiabilidade se constrói.

---

**Fontes:** [From Language to Action, 2025] — revisão de benchmarks e avaliação; [Agentic AI Frameworks, 2025] — guardrails; [Survey de tool use, 2026] — multi-tool orchestration; [Yao et al., 2024] — tau-bench, consistência; [Li et al., 2024] — RAG vs. long-context; [InfoWorld, 2025] — limites de estado/observabilidade dos protocolos; [MIT Tech Review, 2025] — custo de tokens em comunicação entre agentes; [Revisão sistemática, 2025] — lacunas de avaliação de RAG.
