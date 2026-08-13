# Capítulo 17 — A2A e a interoperabilidade entre agentes

O capítulo 16 apresentou o MCP como a camada que conecta o modelo ao mundo — ferramentas, dados, serviços. Este capítulo pergunta o passo seguinte: e quando o “mundo” que um agente precisa acessar é *outro agente*? Em 2025, a resposta estava clara para quem construía agentes em escala: agentes feitos por times e vendors diferentes simplesmente não conversavam. Cada par exigia integração dedicada — o problema N×M do capítulo 16, agora multiplicado por agentes que se desdobram, se autenticam e coordenam tarefas.

Em 9 de abril de 2025, a **Google** lançou o **Agent2Agent (A2A)** para resolver exatamente isso: um protocolo aberto para agentes descobrirem capacidades uns dos outros, trocarem informação e coordenarem ações — com descoberta via *Agent Card*, autenticação e troca de tarefas em JSON-RPC. Diferente do MCP, que padroniza a conexão *modelo↔ferramenta*, o A2A padroniza a conexão *agente↔agente*: um agente pode ser construído por qualquer framework, em qualquer linguagem, e ainda assim conversar com qualquer outro agente que fale o mesmo protocolo.

Em junho de 2025, o A2A foi doado à **Linux Foundation**, com AWS, Cisco e Microsoft como participantes fundadores do projeto — o mesmo gesto de governança neutra que o MCP repetiria em dezembro. E a versão 0.3, em agosto de 2025, trouxe o que faltava para o enterprise: transporte gRPC e *security cards* assinados. Este capítulo monta a visão complementar das duas camadas — vertical e horizontal — e termina com a tese da Parte VII: quando os próprios agentes viram sistema, **protocolos são a camada de ferramentas** — o padrão REST/JSON que organizou as APIs da última década se repete, agora entre agentes.

## Quando o mundo é outro agente

O MCP resolveu a conexão modelo↔mundo, mas o mundo não é feito só de ferramentas — é feito de outros agentes. Um agente de vendas precisa consultar o agente de estoque; um agente de suporte precisa delegar a um agente de faturamento. Na arquitetura ponto a ponto, cada par exigia uma integração escrita à mão: conhecer a API do outro, o formato de autenticação dele, o ciclo de vida das tarefas dele. Com poucos agentes, funciona; com dezenas — cada um em seu sistema, seu vendor, sua linguagem —, o custo de integração explode exatamente como explodiu o N×M das ferramentas antes do MCP.

O A2A trata esse problema como o MCP tratou o dele: definindo um protocolo comum, não integrações dedicadas. Três conceitos formam o núcleo. O **Agent Card** é um documento JSON que todo agente publica (em um endpoint padrão, como `/.well-known/agent-card.json`) e que descreve sua identidade, suas capacidades, suas *skills*, seu endpoint e os esquemas de autenticação que exige. A **tarefa (task)** é a unidade de trabalho: um agente envia uma tarefa ao outro via JSON-RPC, acompanha o estado (em execução, concluída, cancelada, com falha) e recebe o resultado. O **artefato** é o conteúdo produzido — texto, arquivo, dados estruturados —, o que permite transferir não só mensagens, mas entregas verificáveis.

```text
cliente (agente orquestrador)                 servidor (agente de domínio)
        │  1. GET /.well-known/agent-card.json
        │  ← Agent Card: skills, endpoint, auth │
        │  2. message/send → task (tarefa)
        │  ← task em execução                    │
        │  3. subscribe/stream → progresso
        │  ← task concluída + artefato          │
        ▼
```

A descoberta resolve o problema que nenhum framework resolveu: um agente não precisa saber *de antemão* o que o outro faz — ele lê o Agent Card, encontra a skill que precisa e autentica. O *acoplamento* deixa de ser por implementação e passa a ser por contrato declarado. É o mesmo gesto do capítulo 13 (“framework não é mágica”): o que torna a cooperação possível não é a biblioteca, é o contrato.

## Horizontal e vertical: A2A versus MCP

A pergunta inevitável de 2025 foi: *MCP ou A2A?* A resposta madura é que são camadas diferentes, e a confusão entre elas é o erro mais comum da era. A imagem que os dois protocolos juntos formam é de duas direções ortogonais:

```text
                AGENTE A ──────────── AGENTE B
                  │                        │
        (A2A)     │                        │      (A2A)
        horizontal│                        │horizontal
                  │                        │
             [MCP] │                   [MCP] │
                  ▼                        ▼
            ferramentas                ferramentas
              / dados                    / dados
               (vertical)
```

O **MCP é a camada vertical**: conecta um modelo (ou agente) para baixo, ao mundo de ferramentas e dados — a “porta USB” de cada agente. O **A2A é a camada horizontal**: conecta agentes entre si, para os lados. Eles não competem; compõem-se. Um agente usa MCP para buscar dados e A2A para falar com outro agente — a AWS e a própria especificação do A2A descreveram essa composição. O mapa mental para o engenheiro é simples: **um agente fala com o mundo pelo MCP; fala com outros agentes pelo A2A.**

## Adoção e governança: de 50 parceiros à Linux Foundation

O A2A nasceu com um ecossistema que o MCP não tinha no dia do lançamento. No anúncio de 9 de abril de 2025, a Google listou o apoio de **mais de 50 parceiros de tecnologia** — Atlassian, Box, Cohere, Intuit, LangChain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG e Workday, entre outros — além de provedores de serviço como Accenture, BCG, Capgemini, Deloitte, Infosys e PwC. A adoção enterprise chegou rápido: o **Microsoft** passou a oferecer suporte a A2A no Azure AI Foundry, o **SAP** integrou ao Joule, o **ServiceNow** ao Agent Fabric, e plataformas como Zoom e Vertex seguiram o mesmo caminho.

O movimento de governança veio em junho de 2025: a Google doou a especificação, os SDKs e as ferramentas de desenvolvimento do A2A à **Linux Foundation**, que anunciou o projeto *Agent2Agent* com AWS, Cisco, Google, Microsoft, Salesforce, SAP e ServiceNow como fundadores. Mais de 100 empresas apoiavam o protocolo naquele momento — número que passou de 150 até agosto. A doação respondeu à preocupação central que os observadores levantaram desde o lançamento: um protocolo de interoperabilidade controlado por um único fornecedor é uma contradição. Ao entregar o padrão a governança neutra, o A2A seguiu o caminho que consagrou os grandes padrões de infraestrutura — e que o MCP repetiria em dezembro de 2025.

## A evolução 0.3: gRPC e segurança enterprise

A versão **0.3**, anunciada em julho/agosto de 2025, converteu o protocolo em candidato a infraestrutura enterprise. Duas novidades foram as principais. A primeira é o **gRPC** como transporte de alto desempenho, ao lado do JSON-RPC sobre HTTP — para cenários com grande número de agentes e requisitos de baixa latência. A segunda é a capacidade de **assinar security cards**: o documento que descreve as capacidades e políticas de segurança de um agente passa a ser assinado, criando a base para autenticação e autorização verificáveis entre agentes de domínios diferentes — um passo rumo à *trust* entre organizações, não apenas entre serviços.

A mesma rodada trouxe o suporte nativo no **Agent Development Kit (ADK)** e a abertura de um **marketplace** de agentes A2A no ecossistema Google Cloud, além de avaliação de sistemas A2A no Vertex GenAI Evaluation Service. A direção é a de qualquer protocolo maduro: menos demos, mais operação — descoberta, autenticação, monitoramento e mercado.

## O cenário 2025–2026: dois padrões, uma mesma forma

No horizonte em que este livro fecha, o desenho ficou claro: **MCP lidera em adoção de desenvolvedores** — é a porta de entrada para tools e dados, com dezenas de milhões de downloads —, enquanto **A2A é forte em ecossistemas enterprise** — é o idioma da cooperação entre agentes de vendors diferentes, com parceiros como Salesforce, SAP e ServiceNow já usando-o em plataformas próprias. Os especialistas divergem sobre qual prevalecerá ou se os dois convergirão — e há um debate real sobre a dupla segurança/abertura: o A2A nasceu com primitivas de segurança mais estruturadas (security cards assinados, zero-trust), enquanto o MCP é mais flexível e depende de implementação cuidadosa por cada integrador.

A lição que interessa ao engenheiro não é a aposta em um dos lados — é a *forma* que os dois compartilham. O padrão REST/JSON que organizou a integração de APIs na última década está se repetindo, agora no nível de agentes: descoberta declarada (Agent Card), tarefas com ciclo de vida, autenticação padronizada, artefatos como unidade de entrega. Não é coincidência; é o mesmo problema de sempre — como fazer sistemas independentes cooperarem sem acoplar — reaparecendo uma camada acima.

## A lição estrutural

O fio que liga o MCP ao A2A é o mesmo que liga o function calling ao MCP: **a interface padronizada transforma integração em commodity**. Quando o MCP padronizou a camada modelo↔mundo, ferramentas deixaram de ser integração dedicada e viraram serviço. Quando o A2A padronizou a camada agente↔agente, a cooperação entre agentes de vendors diferentes deixou de ser projeto de engenharia por par e virou protocolo.

Para a tese deste livro, a consequência é a última peça do quebra-cabeça das Partes VI e VII. O capítulo 13 mostrou o agente como sistema com estado, ações, observações e critério de término; o capítulo 14 mostrou que múltiplos agentes só valem com divisão de trabalho, perspectivas ou heterogeneidade; os capítulos 15 e 16 mostraram como medir e como conectar ao mundo. O A2A mostra o agente *como serviço*: um sistema que declara suas capacidades, autentica-se, aceita tarefas e entrega artefatos — consumível por qualquer outro sistema que fale o mesmo contrato. É o mesmo gesto que transformou aplicações monolíticas em APIs; agora, aplicações viram agentes, e APIs viram protocolos de agente.

## Para o engenheiro

A2A resolve o problema agente↔agente: descoberta de capacidades via Agent Card, autenticação e troca de tarefas em JSON-RPC, sem integração ponto a ponto entre pares. Se você orquestra agentes de vendors diferentes — ou vai orquestrar —, planeje em torno do protocolo, não de um SDK proprietário: é a diferença entre portabilidade e lock-in.

Tenha o mapa mental fixo: **MCP é vertical** (modelo→mundo) e **A2A é horizontal** (agente→agente). Não use um no lugar do outro, e não trate os dois como concorrentes a escolher — um agente usa MCP para ferramentas e A2A para falar com outros agentes.

Ao publicar um agente, pense em contrato antes de implementação: qual Agent Card ele vai expor, quais skills declara, como autentica e qual o ciclo de vida das tarefas que aceita. Um agente sem contrato declarado é um serviço que ninguém consegue descobrir — o equivalente exato a uma API sem documentação.

E adote o protocolo cedo, mesmo com o ecossistema ainda amadurecendo. Os padrões de interoperabilidade sobrevivem aos modelos que os usam: designs neutros de vendor duram mais que qualquer framework da temporada. O valor está na forma, não na hype.

---

**Fontes:** [Google, 2025] — Announcing the Agent2Agent Protocol (A2A); [InfoQ, 2025] — A2A na Linux Foundation; [InfoWorld, 2025] — A2A 0.3, gRPC e segurança; [VentureBeat, 2025] — A2A e MCP em interoperabilidade; [MIT Tech Review, 2025] — panorama de protocolos; [Agentic AI Frameworks, 2025] — protocolos de comunicação entre agentes.
