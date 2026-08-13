# Capítulo 13 — Frameworks de agentes: de AutoGPT a LangGraph

Em 2023, todo mundo queria um agente autônomo — e muita gente construiu um que ficava rodando até esgotar o cartão de crédito. O problema desta era foi o hype em cima de loops sem critério de parada: AutoGPT e BabyAGI provaram que a ideia era viável e, na mesma cena, que era frágil. A pergunta madura foi: *o que um agente realmente é?* A resposta estrutural — objetivo, estado, ações, observações, feedback e condição de término — virou o mapa do capítulo. Frameworks não criam a mágica; dão a infraestrutura para ela existir de forma controlável. A ambição evoluiu de “prompts autônomos” para grafos de estado com observabilidade (LangGraph), equipes com papéis (CrewAI), conversação (AutoGen) e agentes que produzem artefatos em vez de chat (MetaGPT).

Este capítulo é a ponte entre o loop que o capítulo 10 (ReAct) estabeleceu e os sistemas multi-agente do capítulo 14. Ele parte da explosão de 2023, passa pela anatomia estrutural de um agente e termina na lição que orienta a escolha de framework: agente não é um prompt — é um sistema com estado, ações, observações, feedback e critério de término.

## A explosão de 2023: AutoGPT e BabyAGI

O ponto de partida é o momento em que a palavra “agente” deixou os papers e virou notícia. Em março de 2023, o **AutoGPT**, de Toran Richards (Significant-Gravitas), e o **BabyAGI**, de Yohei Nakajima, invadiram o GitHub como projetos open-source que usavam GPT-4 para perseguir um objetivo de forma *autônoma*: o AutoGPT encadeava pensamento, ação, observação e memória externa para iterar sobre uma tarefa; o BabyAGI era, essencialmente, um *gerenciador de tarefas* que criava, priorizava e executava passos até um objetivo pré-definido. Nenhum deles inventou o loop — o ReAct (capítulo 10) já o tinha formalizado —, mas ambos o *democratizaram*: dezenas de milhares de desenvolvedores rodaram agentes pela primeira vez, com uma linha de comando e uma chave de API.

A mesma cena que provou a viabilidade mostrou a fragilidade. Os loops eram lineares, sem critério de término confiável: o agente repetia tentativas, se perdia da tarefa original (a *deriva*), e o custo crescia a cada chamada. A piada da época — o agente que “rodava até esgotar o cartão de crédito” — era, na verdade, a descrição precisa de um sistema sem condição de parada. A indústria aprendeu a lição em duas frentes: definir estruturalmente o que um agente é e, em seguida, construir infraestrutura para que essa estrutura fosse controlável.

## O que é um agente, afinal

A resposta estrutural que organiza a era vem da literatura de surveys: um agente é um sistema que combina **perfil** (quem é o agente — o papel, o objetivo, a identidade), **memória** (curto prazo — a sessão; longo prazo — o que persiste entre sessões), **planejamento** (decompor o objetivo, refletir sobre os passos) e **ação** (chamadas de ferramentas que modificam o mundo). O survey de Wang et al. (2024) mostrou que, sob essa lente, quase todos os sistemas da era — do AutoGPT ao LangGraph — são instâncias da mesma estrutura.

Mas a estrutura mais útil para o engenheiro é a do próprio AGENTS.md:

```text
objetivo
+ estado
+ ações
+ observações
+ feedback
+ critério de término
```

Cada um desses componentes tem um papel preciso. O **objetivo** define o que conta como sucesso — sem ele, não existe critério de avaliação. O **estado** é a memória de trabalho: o que o agente sabe sobre onde está. As **ações** são o conjunto de operações que o agente pode executar — buscar, calcular, escrever, chamar API. As **observações** são os resultados das ações voltando ao sistema — sem elas, o agente age às cegas. O **feedback** é o sinal que permite corrigir o curso. O **critério de término** é a condição que interrompe o loop — e é ele, exatamente ele, que faltou em 2023.

A consequência operacional é direta: qualquer sistema que tenha esses seis elementos *é* um agente, com ou sem a palavra “agente” no nome; qualquer sistema que não os tenha, não é — mesmo que o prompt comece com “Você é um agente autônomo”. E é por isso que a era seguinte se dedicou a construir infraestrutura para esses elementos: estado explícito, observabilidade, critérios de parada e guardrails.

## De cadeias a grafos: LangChain e LangGraph

A trajetória do ecossistema mais usado da era é uma história em dois atos. O **LangChain**, lançado em outubro de 2022, popularizou a *composição de cadeias*: encadear passos de LLM — recuperar, processar, gerar — como peças de um pipeline linear. Foi o jeito mais rápido de colocar uma aplicação de LLM em pé, e por isso virou o ponto de entrada de uma geração inteira de desenvolvedores. Mas cadeias lineares têm um limite estrutural: não expressam *ciclos*. Um agente de verdade precisa voltar ao raciocínio depois da observação — e um DAG (grafo acíclico dirigido), por definição, não tem retorno.

O **LangGraph**, introduzido em janeiro de 2024, foi a resposta: um *grafo de estados* — uma máquina de estados em que nós são etapas (raciocinar, chamar ferramenta, validar) e arestas condicionais decidem o próximo passo, com o estado centralizado e atualizado a cada nó. As propriedades que o distinguem são exatamente as que o hype de 2023 negligenciou:

```text
estado explícito   →  cada nó lê e atualiza o estado central
durable execution  →  o agente sobrevive a falhas e retoma de onde parou
streaming          →  o usuário vê o raciocínio e as ações em tempo real
human-in-the-loop  →  humano inspeciona/edita o estado em qualquer ponto
observabilidade    →  rastreamento de cada transição para debug e métricas
```

É a mesma lição do capítulo 12 aplicada a agentes: quando o fluxo tem loops, o controle explícito vale mais que a conveniência da abstração. A ideia não era nova — o LangGraph é inspirado no Pregel (Google) e no Apache Beam, e a representação de máquinas de estados é antiga —, mas a aplicação a LLMs fez do “grafo com estado” o idioma dominante da orquestração de agentes. É por isso que o capítulo 10 tinha razão ao dizer que LangGraph é “ReAct com grafos e estados”: o loop cognitivo é o mesmo, o que muda é a infraestrutura que o torna previsível.

## Equipes, conversas e artefatos

Se LangGraph é o *runtime* de baixo nível, uma segunda onda de frameworks explorou a pergunta *quantos agentes* e *como eles se comunicam* — o tema que o capítulo 14 tratará em profundidade. Três modelos mentais se destacaram.

O **CrewAI**, de João Moura, organiza agentes como *equipes com papéis*: cada agente tem um role, um goal e um backstory, e os *crews* executam *tasks* em processos sequenciais ou hierárquicos. É o modelo mental mais próximo de uma empresa: especialistas com identidades definidas que colaboram para um objetivo comum, com delegação de tarefas entre eles. O **AutoGen**, da Microsoft (Wu et al., 2023), trata agência como *conversação*: agentes conversáveis — como o AssistantAgent e o UserProxyAgent — trocam mensagens, com um GroupChatManager escolhendo dinamicamente quem fala a cada turno. O insight é o *conversation programming*: definir o controle do fluxo em termos de quem fala com quem. O **MetaGPT**, de Hong et al. (2023), ataca o problema que o chatter entre LLMs cria: em vez de diálogo, agentes trocam *artefatos estruturados* — PRDs, documentos de design, diagramas e especificações de interface — seguindo SOPs (procedimentos operacionais padronizados) que espelham o fluxo de uma empresa de software, do product manager ao QA. A comunicação por documentos em vez de conversa eliminou o *chatter* improdutivo (“Olá! Como vai?”) e melhorou a consistência das entregas.

```text
                 perfil        comunicação        analogia
CrewAI           papéis        tarefas + papéis   uma empresa
AutoGen          conversáveis  mensagens          uma reunião
MetaGPT          especialistas artefatos + SOPs   uma linha de produção
LangGraph        nós de grafo  estado + arestas   uma máquina de estados
```

O **Semantic Kernel**, da Microsoft, completa o quadro como a opção *enterprise*: orquestração de agentes, plugins e memória voltada para integração com infraestrutura corporativa. Juntos, esses frameworks formam um espectro, não uma competição: quanto mais controle você precisa, mais baixo você desce (grafo com estado explícito); quanto mais autonomia deseja, mais alto sobe (equipes com papéis ou conversas).

## Planejamento além do linear

O ReAct estabeleceu o loop, mas o loop linear tem um custo: cada passo depende do anterior, erros acumulam e a trajetória não tem alternativa. A era dos frameworks trouxe três respostas a essa limitação, que o capítulo 10 anunciou e que aqui se materializam.

O **Tree of Thoughts** (ToT), de Yao et al. (2023), transforma raciocínio em *busca sobre uma árvore de pensamentos*: em vez de uma única cadeia, o modelo gera múltiplos pensamentos candidatos em cada passo, avalia cada um e explora deliberadamente os mais promissores — com backtracking quando um caminho falha. O **ReWOO**, de Xu et al. (2023), *desacopla o raciocínio da observação*: em vez de intercalar pensamento-ação-observação (ReAct), um módulo Planner gera o plano inteiro de antemão, um Worker executa as chamadas de ferramenta e um Solver sintetiza a resposta. A economia é enorme — os autores relataram eficiência de tokens até 5× e ganho de acurácia no HotpotQA, além de robustez a falhas de ferramenta — porque o prompt de raciocínio não é repetido a cada iteração. O **LATS** (Language Agent Tree Search), de Zhou et al. (2023/2024), unifica as duas ideias: expande o ReAct em uma *busca em árvore* (Monte Carlo Tree Search), usando o LLM como agente, avaliador de estados e gerador de reflexões, com feedback do ambiente externo e autoavaliação guiando a exploração. Com GPT-4, o LATS alcançou 92,7% pass@1 no HumanEval, dobrou o desempenho do ReAct no HotpotQA e elevou a pontuação média no WebShop.

```text
ReAct (cap. 10)   →  uma trajetória, decide a cada passo   →  simples, frágil
ToT               →  múltiplas trajetórias, avalia e volta  →  raciocínio deliberado
ReWOO             →  planeja antes, executa depois           →  economia de tokens
LATS              →  busca em árvore com feedback externo   →  exploração + ambiente
```

O padrão comum é a fuga da linearidade: o agente deixa de ser uma cadeia única e passa a explorar um *espaço* de possibilidades, guiado por avaliação e feedback. É o movimento que conecta os frameworks de orquestração (grafos com estado) aos métodos de planejamento (busca em árvore) — e, mais tarde, aos protocolos da Parte VII.

## A lição estrutural

No fim, a lição que o capítulo quer deixar é a mesma que organiza este livro: **agente não é um prompt**. Escrever “você é um agente autônomo” no system prompt não cria agência; cria uma expectativa. Agência emerge quando existem objetivo, estado, ações, observações, feedback e critério de término — e a diferença entre os frameworks da era é *qual desses elementos eles tornam explícitos e controláveis*:

| Framework | O que torna explícito | O que esconde |
| --- | --- | --- |
| AutoGPT / BabyAGI | o loop de execução | o critério de parada, o custo, o controle |
| LangChain | a sequência de passos | os ciclos, o estado de execução |
| LangGraph | o estado, os ciclos, a observabilidade | — (pouco abstrai) |
| CrewAI | os papéis e as tarefas | os detalhes do loop interno |
| AutoGen | a conversa entre agentes | o custo do chatter |
| MetaGPT | os artefatos e os SOPs | o estado de execução |

O contraste entre AutoGPT e LangGraph é o resumo da era: o primeiro provou que o loop é possível; o segundo tornou o loop *previsível*. E é essa previsibilidade — estado explícito, observabilidade, guardrails, critérios de término — que separa uma técnica de laboratório de uma infraestrutura utilizável. O capítulo 14 explorará o passo seguinte: quando o agente não é um, mas muitos, o problema deixa de ser o loop e passa a ser a comunicação.

## Para o engenheiro

AutoGPT e BabyAGI provaram o custo do loop sem critério de parada. Antes de qualquer “agente autônomo”, defina explicitamente objetivo, estado, ações, observações, feedback e condição de término — os seis componentes da estrutura que este capítulo apresentou. Se você não sabe dizer o que conta como sucesso, não tem como saber quando parar.

Framework não é mágica. Escolha por **observabilidade, testabilidade e controle de estado**, não pelo hype da semana. Se o fluxo for majoritariamente linear, uma cadeia simples resolve; se houver loops, ramos condicionais ou retomada após falha, um grafo de estados (como o LangGraph) justifica a complexidade. A regra prática: suba de abstração quando quiser velocidade, desça quando precisar de controle.

Em produção, `max_iterations`, orçamento de tokens, timeout e logs estruturados são obrigatórios. O mesmo agente que funciona em dev pode custar dez vezes mais em prod — a diferença não é o modelo, é o loop que nunca termina. Instrumente desde o início: rastreie cada transição de estado e cada chamada de ferramenta; sem isso, o debug de um agente é adivinhação.

Separe **memória de sessão** (o estado da conversa atual) de **conhecimento de longo prazo** (o banco, o índice, o perfil persistido). Misturar os dois é a causa clássica de agentes “que se esquecem” ou que “inventam” contexto. E quando a tarefa permitir, prefira a troca de artefatos estruturados ao diálogo aberto: a lição do MetaGPT vale fora dele — comunicação por documentos é mais barata e menos ruidosa que chatter.

Finalmente, desconfie de autonomia sem verificação. Reflexão do próprio modelo (Reflexion, LATS) melhora, mas não substitui validadores externos: testes, execução de código e avaliação objetiva. O loop explora; o verificador decide. Essa é a separação generator/verifier que o capítulo 10 introduziu e que os capítulos 14 e 15 levarão ao limite.

---

**Fontes:** [Richards, 2023] — AutoGPT; [Nakajima, 2023] — BabyAGI; [Wang et al., 2023/2024] — survey de agentes autônomos (perfil/memória/planejamento/ação); [Wu et al., 2023] — AutoGen; [Hong et al., 2023] — MetaGPT; [Yao et al., 2023] — Tree of Thoughts; [Xu et al., 2023] — ReWOO; [Zhou et al., 2023/2024] — LATS; [Masterman et al., 2024] — panorama de arquiteturas de agentes; [Agentic AI Frameworks, 2025] — comparação CrewAI/LangGraph/AutoGen/ADK/MetaGPT.
