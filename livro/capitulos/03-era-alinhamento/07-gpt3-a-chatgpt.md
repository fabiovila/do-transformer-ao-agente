# Capítulo 7 — De GPT-3 a ChatGPT: instrução, RLHF e o momento em que o público chegou

Em 2022, os modelos de linguagem já eram capazes de fazer coisas que, poucos anos antes, pareciam pertencer ao domínio da ficção científica. O GPT-3 escrevia textos, respondia perguntas, produzia código e conseguia realizar tarefas a partir de poucos exemplos fornecidos no prompt. Mas havia uma diferença fundamental entre possuir essa capacidade e saber utilizá-la de maneira confiável: o modelo havia sido treinado para prever o próximo token, não para obedecer a uma intenção humana.

Essa diferença define o problema central desta era. Um modelo pode ser extremamente capaz e, ainda assim, não fazer aquilo que o usuário pediu. Pode produzir uma continuação estatisticamente plausível quando o usuário esperava uma tradução, ignorar parte de uma instrução ou responder com segurança a uma pergunta para a qual não possui informação suficiente. A questão deixou então de ser apenas como aumentar a capacidade do modelo. Era preciso descobrir como transformar essa capacidade em comportamento útil.

A resposta passou pelo feedback humano e pelo *reinforcement learning from human feedback*, o RLHF. A ideia não surgiu com os modelos de linguagem. Em 2017, Christiano et al. já haviam mostrado como utilizar preferências humanas para aprender uma função de recompensa e orientar um agente de reinforcement learning. Alguns anos depois, a mesma estrutura seria aplicada à linguagem em escala, com o InstructGPT. Em novembro de 2022, essa combinação chegaria ao público na forma do ChatGPT.

O resultado foi uma mudança de natureza. O modelo deixou de ser apenas uma tecnologia que especialistas precisavam saber manipular e passou a ser uma interface conversacional acessível a milhões de pessoas. Mas essa popularização teve um efeito adicional: ao colocar os modelos diante de um público muito maior, tornou visíveis suas limitações. Alucinações, conhecimento datado, dificuldades de computação e ausência de fontes deixaram de ser apenas problemas discutidos em papers e passaram a definir a agenda da engenharia de sistemas de IA.

O GPT-3, apresentado em 2020, havia demonstrado que a escala do pré-treinamento podia produzir capacidades surpreendentes. Com 175 bilhões de parâmetros, o modelo conseguia realizar tarefas em diferentes domínios a partir de exemplos fornecidos no prompt. O *few-shot learning* mostrava que não era necessário treinar novamente o modelo para cada tarefa: muitas vezes, bastava apresentar exemplos suficientemente claros.

Mas essa flexibilidade tinha um preço. O objetivo do treinamento continuava sendo a previsão do próximo token. O modelo havia aprendido a completar sequências de texto, e não a seguir instruções da maneira como um assistente humano seguiria. O usuário precisava, portanto, transformar o prompt em uma espécie de programa informal, especificando a tarefa, o formato desejado e, muitas vezes, fornecendo exemplos para induzir o comportamento correto.

Essa situação produzia um contraste importante. O modelo podia saber como resolver um problema e, mesmo assim, não responder à pergunta que havia sido feita. Podia possuir a capacidade linguística necessária para traduzir uma frase, mas interpretar o prompt como uma continuação de texto. A partir daí, tornou-se necessário separar duas propriedades que até então apareciam misturadas:

```text
CAPACIDADE ≠ OBEDIÊNCIA

pré-treinamento
      ↓
capacidade de gerar texto
      ↓
mas não necessariamente
seguir uma intenção humana
```

A pergunta seguinte era inevitável: como ensinar ao modelo aquilo que uma pessoa considera uma boa resposta sem precisar escrever manualmente uma função matemática para cada comportamento desejado?

## A origem do RLHF

A ideia de utilizar preferências humanas para orientar um sistema de reinforcement learning surgiu antes dos modelos de linguagem. Em 2017, Christiano et al. apresentaram uma abordagem em que o ser humano não precisava definir diretamente uma recompensa numérica. Em vez disso, comparava comportamentos produzidos pelo agente e indicava qual deles estava mais próximo do objetivo.

Essa mudança parece pequena, mas resolve um problema importante. Em muitos ambientes, sabemos reconhecer um comportamento adequado sem saber descrevê-lo de maneira precisa como uma função matemática. É relativamente fácil olhar para duas trajetórias e dizer qual delas parece melhor; é muito mais difícil escrever uma função de recompensa que capture todos os aspectos relevantes dessa avaliação.

Os experimentos foram realizados em ambientes de jogos Atari e em tarefas de controle robótico simulado. O agente produzia comportamentos que eram apresentados aos avaliadores humanos, que comparavam as alternativas e indicavam qual delas consideravam melhor. Essas preferências eram então utilizadas para treinar um modelo de recompensa, que passava a fornecer uma aproximação matemática da avaliação humana. O agente podia utilizar essa recompensa aprendida para orientar seu próprio aprendizado por reinforcement learning.

```text
comportamento A ──┐
                  ├──→ preferência humana
comportamento B ──┘
                         ↓
                  modelo de recompensa
                         ↓
                 reinforcement learning
```

A importância dessa abordagem estava justamente na economia do feedback humano. Em vez de um ser humano precisar atribuir uma recompensa a cada ação do agente, bastava fornecer comparações entre comportamentos. O sistema aprendia uma aproximação das preferências humanas e podia utilizá-la em uma quantidade muito maior de interações.

Mas havia um problema inevitável: o modelo de recompensa era apenas uma aproximação do objetivo humano. Se o agente encontrasse uma maneira de obter uma recompensa elevada sem realmente fazer aquilo que o avaliador pretendia, poderia explorar a falha da própria função de recompensa. O problema, conhecido como *reward hacking*, já aparecia nesses primeiros experimentos e continuaria sendo relevante quando a mesma ideia fosse aplicada a modelos de linguagem.

Essa observação é importante porque antecipa uma característica fundamental do RLHF. O objetivo não é simplesmente maximizar uma função matemática. É maximizar uma função que tenta representar preferências humanas e, portanto, pode conter erros, lacunas e ambiguidades.

## Da preferência humana ao InstructGPT

A passagem dessa ideia para os modelos de linguagem foi feita de maneira particularmente clara pelo trabalho sobre InstructGPT, publicado em 2022. O objetivo era adaptar um GPT-3 pré-treinado para que ele seguisse instruções de maneira mais adequada.

O processo foi dividido em três etapas. Primeiro, humanos produziram demonstrações de boas respostas para um conjunto de prompts, e o modelo foi ajustado para aprender esse comportamento. Essa etapa, conhecida como *supervised fine-tuning*, ou SFT, fornecia ao modelo exemplos concretos daquilo que se esperava dele.

No segundo estágio, entrava o modelo de recompensa. Para um mesmo prompt, eram produzidas várias respostas, que eram então ordenadas por avaliadores humanos. Em vez de dizer simplesmente que uma resposta era “boa” ou “ruim”, os avaliadores indicavam uma preferência entre alternativas. Essas comparações permitiam treinar um modelo capaz de atribuir uma pontuação às respostas.

No terceiro estágio, o modelo era otimizado por reinforcement learning em direção às respostas que o *reward model* considerava melhores. Havia, porém, uma restrição importante: o novo modelo não deveria se afastar excessivamente do modelo obtido no SFT. Para isso, utilizava-se uma penalidade baseada na divergência KL.

```text
GPT-3 pré-treinado
        ↓
demonstrações humanas
        ↓
SFT
        ↓
várias respostas para cada prompt
        ↓
preferências humanas
        ↓
Reward Model
        ↓
reinforcement learning
        ↓
InstructGPT
```

A estrutura completa é importante porque cada etapa resolve um problema diferente. O pré-treinamento fornece a capacidade linguística; o SFT ensina o modelo a imitar demonstrações; o *reward model* aprende com as preferências humanas; e o reinforcement learning ajusta o comportamento para maximizar essa recompensa, mantendo o modelo próximo da política que recebeu a avaliação humana.

O resultado mostrou que tamanho não era a única variável importante. Um modelo InstructGPT muito menor podia ser preferido por avaliadores humanos em comparação com o GPT-3 original muito maior. Isso fornecia uma evidência concreta de que o treinamento realizado depois do pré-treinamento podia alterar profundamente a qualidade percebida do sistema.

A lição era maior do que o resultado específico:

> **escala fornece capacidade, mas não determina sozinha o comportamento.**

Uma parte importante do valor de um LLM seria construída depois que o pré-treinamento terminasse.

## A matemática do alinhamento

O *reward model* transforma preferências humanas em uma função contínua. Dado um prompt e duas respostas, uma preferida e outra rejeitada, o treinamento procura fazer com que a primeira receba uma pontuação maior.

A perda pode ser expressa como:

```text
L(θ) =
− E [ log σ( rθ(x, yw) − rθ(x, yl) ) ]
```

em que (y_w) representa a resposta preferida, (y_l) a resposta menos preferida, (r_\theta) o *reward model* e (\sigma) a função sigmoide. Quanto maior a diferença entre a pontuação da resposta preferida e a da resposta rejeitada, menor a perda.

O terceiro estágio introduz a otimização da política. O objetivo pode ser representado de maneira simplificada por:

```text
objetivo RLHF =
E[rθ(x, y)]
− β · KL(πθ || πSFT)
```

A primeira parcela recompensa o comportamento que o *reward model* considera bom. A segunda impede que a política se afaste excessivamente do modelo SFT.

Essa segunda parcela é importante porque o *reward model* não é o objetivo humano; ele é apenas uma aproximação das preferências humanas. Se a política for otimizada agressivamente, pode aprender a explorar as imperfeições do modelo de recompensa. A penalidade KL funciona, nesse contexto, como uma âncora que limita esse desvio.

O problema é estrutural. Sempre que uma função aproximada passa a ser o alvo direto de otimização, existe o risco de o sistema descobrir maneiras de maximizar a função sem realizar exatamente aquilo que pretendíamos. O RLHF não elimina esse problema. Ele introduz mecanismos para controlá-lo.

## O que o alinhamento muda — e o que não muda

É importante não atribuir ao alinhamento aquilo que pertence ao pré-treinamento. O RLHF melhora a forma como o modelo se comporta diante das instruções, mas não transforma automaticamente o modelo em uma fonte de conhecimento atualizada ou em um mecanismo de computação confiável.

O conhecimento continua limitado ao que foi incorporado durante o treinamento. O modelo não passa a conhecer acontecimentos posteriores simplesmente porque foi alinhado. Da mesma forma, o alinhamento não elimina as alucinações. Um modelo pode se tornar muito melhor em seguir instruções e continuar produzindo uma afirmação falsa com grande fluência.

Podemos resumir a distinção assim:

```text
ALINHAMENTO

melhora
→ seguir instruções
→ comportamento desejado
→ adequação da resposta

não resolve sozinho
→ conhecimento desatualizado
→ computação exata
→ verificação das fontes
→ acesso a informações externas
```

Essa distinção seria decisiva depois do lançamento do ChatGPT. O alinhamento resolvia um problema específico: fazer o modelo se comportar mais de acordo com as intenções humanas. Outros problemas exigiriam outras camadas.

Se o modelo não possui informação atual, será necessário algum mecanismo de recuperação. Se precisa realizar uma operação que exige computação exata, poderá precisar de uma ferramenta. Se uma resposta precisa ser verificável, será necessário algum mecanismo de evidência ou de acesso às fontes.

O alinhamento, portanto, não encerra a evolução dos sistemas de IA. Ele torna mais evidente a necessidade das camadas que virão depois.

## Chain-of-Thought: quando o prompt também muda o comportamento

Enquanto o RLHF alterava o comportamento do modelo por meio de treinamento, outra linha de pesquisa mostrava que mudanças importantes podiam ser obtidas diretamente na forma de interação com o modelo.

O trabalho de Wei et al. sobre *chain-of-thought prompting* mostrou que, em determinadas tarefas, pedir ao modelo que produzisse uma sequência de passos intermediários podia melhorar significativamente o desempenho. Em vez de solicitar apenas a resposta final, o prompt induzia o modelo a decompor o problema.

```text
pergunta
   ↓
passo 1
   ↓
passo 2
   ↓
passo 3
   ↓
resposta
```

Essa diferença é particularmente relevante em tarefas de múltiplas etapas. Se o modelo precisa chegar diretamente a uma conclusão, qualquer erro intermediário pode comprometer o resultado. Ao produzir passos intermediários, o processo se torna mais estruturado e, em princípio, mais fácil de acompanhar.

No GSM8K, conjunto de problemas matemáticos de múltiplas etapas, o trabalho mostrou um ganho expressivo com *chain-of-thought*. O ponto central, porém, não é o benchmark específico. É a demonstração de que o comportamento de um LLM depende não apenas de seus pesos, mas também da maneira como o problema é apresentado.

Isso cria uma distinção complementar ao RLHF. O RLHF modifica o modelo por treinamento; o *chain-of-thought* modifica a forma como o modelo é induzido a trabalhar durante a inferência. Em ambos os casos, a mesma capacidade subjacente pode produzir comportamentos diferentes dependendo da camada que se coloca sobre ela.

## LaMDA e a ideia de diálogo fundamentado

Antes do ChatGPT, o Google havia apresentado o LaMDA, um trabalho que ajuda a mostrar como diferentes problemas começavam a convergir. O sistema buscava melhorar a qualidade do diálogo por meio de critérios como sensibilidade e fundamentação.

A sensibilidade estava relacionada à capacidade de produzir respostas adequadas ao contexto da conversa. A fundamentação introduzia outra preocupação: quando uma afirmação podia ser verificada, o sistema deveria buscar fontes externas.

Essa combinação é importante porque aproxima dois problemas que posteriormente seriam tratados por camadas diferentes. O alinhamento procura fazer com que o modelo responda de maneira adequada à intenção do usuário; a recuperação de informação procura fornecer ao modelo informações externas que ele não possui ou que precisam ser verificadas.

O diálogo, entretanto, seria a característica que chegaria ao público de maneira mais decisiva.

## ChatGPT: quando o modelo virou produto

Em 30 de novembro de 2022, a OpenAI lançou o ChatGPT. O sistema combinava um modelo da família GPT-3.5, treinamento com feedback humano e uma interface conversacional simples.

Nenhum desses componentes, isoladamente, explica o impacto do lançamento. O modelo já existia, as técnicas de alinhamento já haviam sido apresentadas e interfaces conversacionais não eram uma novidade. O que mudou foi a combinação desses elementos em um produto que qualquer pessoa podia experimentar diretamente.

Essa mudança de interface foi fundamental. Para utilizar GPT-3 de maneira eficaz, era necessário compreender relativamente bem como estruturar prompts e exemplos. O ChatGPT escondia grande parte dessa complexidade. O usuário simplesmente escrevia o que queria e recebia uma resposta.

O público, portanto, deixou de interagir com um modelo de linguagem como objeto técnico e passou a interagir com ele como uma ferramenta.

Em cerca de dois meses, o ChatGPT atingiu aproximadamente 100 milhões de usuários ativos. Essa escala produziu um efeito que nenhum benchmark poderia produzir sozinho: milhões de pessoas começaram a testar os mesmos limites.

E os limites apareceram rapidamente. O modelo podia produzir informações falsas com enorme confiança. Seu conhecimento não era automaticamente atualizado. Podia cometer erros em operações que exigiam computação precisa. E suas respostas não vinham, por padrão, acompanhadas das fontes que permitiriam verificar cada afirmação.

Esses problemas não eram novos para a comunidade de pesquisa. O que mudou foi sua visibilidade.

O ChatGPT transformou problemas conhecidos de LLMs em problemas concretos de produto.

## As limitações definem a próxima geração

O aspecto mais interessante do lançamento do ChatGPT talvez não esteja apenas no que ele conseguiu fazer, mas no que suas limitações revelaram sobre a arquitetura necessária para sistemas mais confiáveis.

A falta de conhecimento atualizado aponta para a recuperação de informação. A dificuldade em realizar determinados cálculos aponta para ferramentas externas. A ausência de fontes verificáveis aponta para mecanismos de evidência e proveniência. A incapacidade de executar ações de maneira autônoma aponta para agentes.

```text
conhecimento desatualizado
          ↓
   recuperação / RAG

computação limitada
          ↓
      ferramentas

resposta sem evidência
          ↓
   fontes / proveniência

necessidade de agir
          ↓
        agentes
```

A direção da evolução começa então a mudar.

Até aquele momento, grande parte da corrida havia sido concentrada em melhorar o modelo: mais dados, mais parâmetros, melhor pré-treinamento, melhor alinhamento. O ChatGPT mostrou que isso não era suficiente.

A pergunta passou a ser outra:

> **o que devemos colocar ao redor do modelo para que ele consiga fazer aquilo que não consegue fazer sozinho?**

Essa pergunta é uma das chaves para compreender o restante do livro.

## A lição estrutural

O período entre GPT-3 e ChatGPT estabeleceu uma distinção que continuaria orientando a engenharia de LLMs: **o modelo é apenas uma das camadas do sistema**.

O pré-treinamento fornece capacidade. O alinhamento transforma parte dessa capacidade em comportamento orientado por instruções. A interface transforma esse comportamento em produto. E o uso em escala expõe limitações que exigem novas camadas.

```text
pré-treinamento
      ↓
capacidade
      ↓
alinhamento
      ↓
obediência
      ↓
produto
      ↓
acesso em escala
      ↓
limitações
      ↓
RAG + ferramentas + agentes
```

A sequência é importante porque mostra que cada etapa resolve um problema que a anterior não resolvia completamente. O pré-treinamento produz uma capacidade geral, mas não garante obediência. O alinhamento melhora a obediência, mas não fornece conhecimento atualizado nem capacidade de computação externa. O produto torna o sistema acessível, mas o uso em escala revela limitações que o modelo sozinho não consegue superar.

Essa é a razão pela qual a história não termina no ChatGPT. Pelo contrário: o sucesso do produto torna mais clara a necessidade de construir sistemas em torno do modelo.

O capítulo seguinte continuará essa história por outro eixo. Se o capítulo 7 mostrou como a capacidade foi transformada em comportamento e depois em produto, o próximo mostrará o que aconteceu quando essa capacidade começou a ser distribuída para além dos laboratórios que haviam treinado os grandes modelos.

A pergunta deixaria de ser apenas **quem consegue treinar o melhor modelo?**

Passaria a ser também:

> **o que acontece quando outras pessoas podem modificar o modelo e construir sobre ele?**

Essa é a segunda metade da história.

## Para o engenheiro

A principal lição desta era é separar claramente as camadas. Um problema de comportamento pode exigir alinhamento; um problema de conhecimento pode exigir recuperação; um problema de computação pode exigir uma ferramenta. Tentar resolver todos eles aumentando simplesmente o modelo é uma forma cara de confundir problemas diferentes.

O RLHF também mostra que dados de preferência são parte da arquitetura, não apenas um detalhe do treinamento. A qualidade do comportamento aprendido depende da qualidade das avaliações humanas e da capacidade do *reward model* de representar essas preferências sem ser explorado pela política.

O *chain-of-thought* acrescenta outra lição: nem toda melhoria exige alterar os pesos. A forma como o modelo recebe uma tarefa pode mudar significativamente o comportamento durante a inferência. Isso significa que, ao projetar um sistema, treinamento e prompting devem ser considerados como mecanismos diferentes para controlar uma mesma capacidade.

Finalmente, o ChatGPT mostra que colocar um modelo diante de usuários reais muda a natureza do problema. Um comportamento que parece aceitável em uma demonstração pode se tornar crítico quando milhões de pessoas dependem dele. É nesse ponto que questões como conhecimento atualizado, verificabilidade, computação e uso de ferramentas deixam de ser detalhes e passam a determinar a arquitetura do sistema.

---

**Fontes:** [Ouyang et al., 2022] — InstructGPT (*Training Language Models to Follow Instructions with Human Feedback*); [Christiano et al., 2017] — *Deep Reinforcement Learning from Human Preferences*; [Wei et al., 2022] — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*; [Thoppilan et al., 2022] — LaMDA; [OpenAI, 2022] — *Introducing ChatGPT*.
