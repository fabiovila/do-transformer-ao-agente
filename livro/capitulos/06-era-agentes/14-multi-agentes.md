# Capítulo 14 — Sistemas multi-agente e simulação social

O capítulo 13 fechou com a promessa de um passo seguinte: quando o agente não é um, mas muitos, o problema deixa de ser o loop e passa a ser a comunicação. Este capítulo cumpre a promessa — e começa com uma pergunta ingênua que 2023 transformou em campo de pesquisa: *se um agente é bom, dois são melhores?* A resposta, como quase sempre nesta história, é “depende” — e o mais valioso deste capítulo é entender exatamente de quê.

Em 2023, o campo experimentou com intensidade. O **CAMEL** pôs dois agentes para conversar sobre um problema e mostrou que *role-playing* produz tarefas e diálogos que um agente sozinho não gera. O **Generative Agents** construiu uma vila inteira — vinte e cinco agentes com memórias, reflexões e rotinas diárias — e convenceu observadores de que estava diante de uma sociedade mínima. O **ChatDev** organizou uma “empresa de software” em que papéis como CEO, programador e tester produziam código de ponta a ponta. O **AgentVerse** formalizou o ciclo de recrutamento, decisão, execução e avaliação. A ambição era grande: dividir o trabalho, multiplicar perspectivas e simular comportamento humano.

O problema que apareceu no caminho tem nome — *chatter* — e é a tese deste capítulo: agentes conversando produzem texto, não artefatos, e texto custa tokens sem entregar necessariamente progresso. As lições que sobreviveram — papéis claros, comunicação por artefatos estruturados em vez de mensagens soltas, hierarquia e líderes, filtragem de mensagens — valem mais do que qualquer framework. E o capítulo termina com um gancho que a Parte VII vai desatar: agentes de vendors diferentes não conversam — daí o A2A, lá na frente.

## A conversa como método: CAMEL

O **CAMEL** (Communicative Agents for “Mind” Exploration), de Li et al. (2023), perguntou o que acontece se dois modelos conversam sozinhos sobre um problema, sem humano no meio. A resposta técnica foi o *role-playing* — o *inception prompting*: cada agente recebe uma identidade (por exemplo, um *AI assistant* e um *AI user*), e o assistente interpreta a instrução do usuário, executando uma cadeia de tarefas que o próprio diálogo vai desdobrando. É o loop do capítulo 10 (thought → action → observation), mas agora a “observação” é a resposta do outro agente — o ambiente de um agente é o outro agente.

```text
AI user     →  "Desenvolva um bot de trading para ações."
AI assistant→  "Entendido. Primeiro, defino a estratégia. Você concorda?"
AI user     →  "Sim. Prossiga com a coleta de dados."
AI assistant→  "Feito. Agora vou escolher as bibliotecas de análise."
...
```

O resultado notável foi duplo. Primeiro, o *role-playing* suprimiu parte da alucinação: um modelo que divaga quando responde sozinho tende a se manter na tarefa quando interpreta um papel diante de outro agente — a estrutura social funciona como um trilho. Segundo, o esquema gerou *dados*: pares de instrução-resposta sintéticos, produzidos por agentes, para domínios arbitrários — um laboratório de geração automática de treino. O paper registrou com honestidade os limites: sem supervisão, o diálogo pode divergir, esquecer o objetivo e repetir-se. Em outras palavras, o CAMEL já anunciava o problema central da era — conversa não é progresso — antes mesmo que ele tivesse nome.

## A vila que acordou: Generative Agents

Se o CAMEL provou que dois agentes conversam, o **Generative Agents**, de Park et al. (2023), provou que vinte e cinco agentes podem parecer uma sociedade. Na vila fictícia de Smallville, cada agente tem uma identidade (profissão, família, rotina), uma **memory stream** — um registro temporal de todas as observações em linguagem natural — e três mecanismos: **retrieval** (recupera memórias pela combinação de recência, importância e relevância), **reflection** (em momentos de calma, sintetiza memórias em percepções de nível mais alto) e **planning** (decompõe o dia em planos e ações, re-planejando quando as circunstâncias mudam).

O que convenceu não foi a arquitetura, foi o comportamento emergente que ela permitiu. Isabella, a agente que quer sediar uma festa para convidar Sam, divulga a data para amigas; elas contam para mais gente; e, em uma tarde, a informação sobre a festa se espalhou pela vila inteira — sem nenhum script global, apenas agentes trocando observações e atualizando memórias. Dois agentes que não se conheciam se “encontraram” no café porque o plano de um os levou até lá, e conversaram sobre tópicos que a memória de cada um tornava relevantes.

```text
observação  →  memory stream (timestamp)
retrieval   →  recência + importância + relevância
reflection  →  percepções de alto nível a partir das memórias
planning    →  planos diários que geram ações observáveis
```

A avaliação foi um marco metodológico: os pesquisadores entrevistaram os agentes e pediram a avaliadores humanos que julgassem o quanto o comportamento correspondia a uma pessoa fictícia. Os agentes foram julgados mais críveis do que a linha de base sem o sistema de memória. A lição estrutural não era “construímos gente” — era que **memória + reflexão + plano** bastam para sustentar comportamento consistente ao longo do tempo, e que sociedades mínimas produzem fenômenos (difusão de informação, coordenação) que um agente isolado não exibe. Essa é a base de tudo que hoje se chama “cidade de agentes”.

## A empresa que produz software: ChatDev

O **ChatDev**, de Qian et al. (2023), trocou a vila pela fábrica: uma “empresa de software” virtual em que agentes com papéis de uma companhia real — CEO, CTO, programador, revisor, tester — desenvolvem um programa de ponta a ponta por meio de uma **chat chain**, uma cadeia de conversas organizada nas fases de um modelo em cascata: design, codificação, testes e documentação.

Duas ideias técnicas merecem destaque porque respondem diretamente ao problema do *chatter*. A primeira é o *instruct-then-chat*: cada conversa começa com uma instrução rígida e só então vira diálogo — a fase define o limite, impedindo que a conversa divague para fora da etapa. A segunda é a **communicative dehallucination**: dois papéis se verificam mutuamente — o programador afirma o que implementou, o revisor testa a afirmação — e o par resolve discrepâncias antes de seguir. É a separação generator/verifier do capítulo 10, agora distribuída entre dois agentes: um agente confirma o que o outro afirma, em vez de o modelo se auto-avaliar. O ChatDev produziu software completo — incluindo o jogo do “snake” — com papéis coordenados e correções internas, mostrando que a *divisão do trabalho* é a primeira justificativa legítima para múltiplos agentes.

## Recrutar, decidir, executar e avaliar: AgentVerse

O **AgentVerse**, de Chen et al. (2023), organizou o ciclo que os trabalhos anteriores executavam de forma ad hoc. Um problema é resolvido em quatro fases:

```text
1. recrutamento de especialistas   →  escolher os agentes certos para a tarefa
2. decisão colaborativa            →  os agentes discutem, propõem e votam
3. execução da ação                →  o plano vira ação, com um agente líder
4. avaliação                       →  os resultados são avaliados; se falhar, volta à fase 2
```

O valor do esquema é tornar *explícito* o que era implícito: a seleção de quem participa (fase 1), a necessidade de um mecanismo de convergência — o voto, o consenso — em vez de simples acúmulo de mensagens (fase 2), e o critério de término (fase 4), o componente que o capítulo 13 mostrou ser o mais negligenciado. O AgentVerse também apontou a segunda justificativa para múltiplos agentes, além da divisão de trabalho: **perspectivas distintas** — um consenso de agentes com visões diferentes pode superar a resposta de um agente único, exatamente porque discordam. E observou comportamentos emergentes nas dinâmicas: especialização de papéis, transferência de informação entre participantes e *mentoring* — agentes experientes guiando novatos.

## Chatter: o custo invisível

Nenhum desses sistemas escondeu a dor que os acompanhava, e a literatura de surveys da era a classificou: **chatter**. A palavra descreve o modo de falha no qual os agentes produzem cada vez mais mensagens e cada vez menos resultado — conversa sem artefato, sem decisão e sem término.

As causas são estruturais, não acidentais. Cada mensagem entre agentes custa tokens — e o custo *composto* importa mais que o unitário: em um grupo de N agentes que todos falam com todos, cada turno amplifica o contexto de todos os participantes, e o custo da conversa cresce mais que o valor do que se diz. Sem um mecanismo de convergência (um voto, um líder, um artefato que “fecha” a decisão), o diálogo roda sem um ponto de chegada. E sem uma âncora externa, o objetivo original se perde na deriva — a mesma deriva do AutoGPT (capítulo 13), agora multiplicada por N. O Masterman et al. (2024), no panorama de arquiteturas, documentou a resposta empírica: estruturas com **liderança** — um agente que decide, em vez de todos votarem — e com **filtragem de mensagens** — nem tudo que um agente diz chega a todos os outros — reduzem o ruído e melhoram a robustez, ao custo de menos “democracia”. E o mesmo panorama anotou a lição mais desconfortável: para muitas tarefas, um agente único bem projetado vence dois ou mais agentes — a coordenação é cara demais para o ganho.

## De conversas a artefatos: MetaGPT

A resposta mais influente ao *chatter* veio do **MetaGPT**, de Hong et al. (2023), que o capítulo 13 apresentou: trocar mensagens por **artefatos estruturados**. A empresa de software virtual do MetaGPT não conversa para decidir — ela produz documentos: o product manager emite o PRD, o arquiteto emite o documento de design, o engenheiro escreve o código, o QA escreve os testes. O fluxo segue **SOPs** — procedimentos operacionais padronizados, modelados a partir de empresas reais de software — e a comunicação usa um padrão **publish–subscribe**: cada artefato é publicado em um lugar onde os interessados podem assinar e consumir, em vez de ser empurrado em uma conversa.

```text
PM → PRD          (requisitos)      ─┐
arquiteto → design (diagramas)      ─┤  cada papel publica um artefato
engenheiro → código                 ─┤  quem precisa, assina e consome
QA → testes        (verificação)    ─┘
```

A consequência é que a informação não trafega como texto efêmero, mas como estado durável que qualquer papel pode consultar a qualquer momento — a comunicação vira *memória de processo*, no sentido do capítulo 12. O *chatter* (“Ok, entendi! Vamos nessa!”) some porque a entrega é um documento com schema, não uma mensagem. O custo é a rigidez: nem todo problema tem um SOP óbvio, e a automação de processos só paga quando o processo realmente existe. Mas a lição — comunicação por artefatos estruturados rende mais que diálogo aberto — escapou do MetaGPT e virou um princípio de desenho para toda a era.

## A aritmética da coordenação

O survey de Guo et al. (2024) organizou a maturidade da área, e uma conta simples resume a dificuldade econômica do multi-agente. Em um grupo totalmente conectado, N agentes produzem O(N²) pares de conversas potenciais. Cada par consome tokens em duas direções, cada participante carrega o contexto dos outros, e cada agente adicional aumenta a superfície de falha — mais mensagens, mais deriva, mais custo. A conta não diz “não use múltiplos agentes”; ela diz **por que**:

```text
divisão de trabalho real  →  tarefa decompõe-se naturalmente em subtarefas com experts distintos
perspectivas distintas    →  o valor está na discordância, não na soma de respostas iguais
heterogeneidade           →  sistemas, vendors ou objetivos diferentes precisam negociar
```

Quando nenhuma das três condições existe, o multi-agente é um custo sem benefício: a conversa é a forma mais cara de chegar à resposta que um agente único daria. Quando pelo menos uma existe, o problema muda de “quantos agentes” para “como se comunicam” — o que conecta diretamente ao próximo estágio da história. Agentes que usam frameworks e vendors diferentes não conversam por padrão: cada par exige integração dedicada, e o problema N×M reaparece em uma escala nova. A saída não será mais um framework — será um **protocolo** entre agentes, o tema do capítulo 17.

## A lição estrutural

A era multi-agente de 2023–2024 deixou um vocabulário que sobreviveu intacto. Papéis: agente sem identidade clara é só um loop sem direção — o *role* define o que ele pode e deve fazer. Comunicação: o canal importa menos que o *conteúdo* — artefatos estruturados com schema vencem mensagens soltas, porque podem ser validados, versionados e consumidos por outros sistemas. Coordenação: sem um mecanismo de convergência — voto, líder, artefato final — o grupo conversa sem decidir. E custo: cada agente adicional é um multiplicador de contexto, tokens e falhas; a pergunta certa não é “quantos agentes” mas “qual tarefa genuinamente se beneficia de mais de um”.

A tabela que fecha o capítulo 13 pode ser estendida com o que esta era acrescentou:

| Sistema | Unidade de organização | Como comunica | O que entrega |
| --- | --- | --- | --- |
| CAMEL | dois papéis | diálogo instrutor–executor | dados e tarefas sintéticos |
| Generative Agents | memória individual | observações no espaço compartilhado | comportamento plausível |
| ChatDev | papéis de empresa | cadeia de fases (chat chain) | software completo |
| AgentVerse | ciclo de fases | discussão + voto | decisão coletiva |
| MetaGPT | SOPs | publish–subscribe de artefatos | documentos e código |

O fio comum é a resposta à pergunta inicial: dois agentes não são melhores por serem dois — são melhores quando o problema se decompõe, quando as perspectivas divergem ou quando os mundos são heterogêneos. E é exatamente essa heterogeneidade que empurra a próxima era: quando os agentes viram *sistemas* que precisam cooperar sem compartilhar código, a conversa não pode ser resolvida por framework — só por protocolo. A Parte VII começa aqui.

## Para o engenheiro

Múltiplos agentes valem a pena apenas quando existe divisão de trabalho real ou perspectivas genuinamente distintas — nunca por padrão. Antes de arquitetar um “time” de agentes, responda: esta tarefa se decompõe em subtarefas com experts diferentes? A discordância entre modelos agregaria valor? Se as duas respostas são não, um único loop bem projetado (capítulo 13) vence dois agentes que se atrapalham — e custa uma fração.

O inimigo número um é o *chatter*: agentes que conversam sem produzir artefato. Troque mensagens soltas por comunicação estruturada — arquivos, schemas, tickets, documentos de interface. Defina o que conta como “entrega” para cada papel, e faça a conversa avançar na direção da entrega. Se você não sabe qual é o artefato final, o sistema não tem critério de parada.

Papéis e hierarquia não são burocracia, são robustez. Defina quem decide, quem executa e como um resultado é passado adiante; um líder que filtra mensagens e decide reduz o ruído mais do que uma votação entre pares. Comece com dois agentes e escale apenas quando latência e custo justificarem — cada agente extra soma contexto, tokens e superfície de falha ao sistema inteiro.

E quando os agentes vierem de times, sistemas ou vendors diferentes, não tente fazê-los conversar por integração ponto a ponto. Esse é o problema que nenhum framework resolve — e é exatamente o que os protocolos da Parte VII endereçam.

---

**Fontes:** [Li et al., 2023] — CAMEL; [Park et al., 2023] — Generative Agents; [Qian et al., 2023] — ChatDev; [Chen et al., 2023] — AgentVerse; [Hong et al., 2023] — MetaGPT; [Masterman et al., 2024] — panorama de arquiteturas single/multi-agente; [Guo et al., 2024] — survey de multi-agentes (IJCAI).
