# Capítulo 16 — MCP: o USB-C dos dados e ferramentas

Chegou a hora em que a infraestrutura virou o produto. O capítulo 11 industrializou o function calling: as APIs passaram a declarar funções, os modelos passaram a chamá-las e cada aplicação passou a integrar-se com cada fonte de dados. Foi aí que o problema virou matemático. Se existem N aplicações e M ferramentas, a arquitetura ponto a ponto exige N×M integrações dedicadas — um inferno de manutenção que só cresce: cada nova aplicação multiplica o problema por M, cada nova ferramenta o multiplica por N.

Em 25 de novembro de 2024, a **Anthropic** anunciou e open-sourceou o **Model Context Protocol (MCP)**: uma camada única entre modelos e dados/ferramentas, no lugar das integrações ponto a ponto — N + M, em vez de N×M. A analogia com o **USB-C da IA**, que acompanhou o lançamento, captura a ambição com precisão: um padrão de conector, milhares de dispositivos, qualquer cabo funciona em qualquer porta. Em pouco mais de um ano, o MCP foi adotado por OpenAI, Google, Microsoft e AWS, ultrapassou 10.000 servidores públicos e 97 milhões de downloads de SDK por mês, e entrou para a governança da Linux Foundation.

Este capítulo mostra as primitivas do protocolo — tools, resources e prompts —, a arquitetura cliente–servidor que as organiza, a conta do sucesso e os limites que ninguém deveria ignorar: o MCP é *stateless*, não traz memória duradoura nem observabilidade por padrão, e a governança — inicialmente concentrada na Anthropic — tornou-se o ponto de tensão que a própria história do protocolo teve de resolver.

## O problema das N×M integrações

Antes do MCP, cada aplicação conectava-se a cada ferramenta de forma artesanal. Um cliente conversacional que quisesse consultar um banco, ler o Slack, buscar no GitHub e olhar um calendário escrevia quatro integrações dedicadas — e o código de cada uma morria junto com o fornecedor. O capítulo 11 terminou com uma observação que agora se cobra: a camada de ferramentas tornou-se *commodity em evolução*, e a interface padronizada passou a ser pré-requisito, não diferencial.

O MCP formaliza essa interface. No lugar de integrações ponto a ponto, há uma camada única com dois papéis: o **cliente** (o host — a aplicação que hospeda o modelo) e o **servidor** (o adaptador que expõe uma ferramenta, um banco de dados ou um serviço). A comunicação usa **JSON-RPC** — o mesmo formato que já organiza os protocolos da web —, e o transporte funciona tanto para processos locais (stdio, entre o host e o servidor rodando na mesma máquina) quanto para servidores remotos (HTTP, a partir das revisões de 2025).

```text
sem MCP:  N aplicações × M ferramentas  →  N×M integrações dedicadas

          app₁  app₂  app₃            app₁  app₂  app₃
           │    │    │                 │     │     │
      ┌────┴────┴────┴────┐          ┌─┴─────┴─────┴─┐
      │  tool₁  tool₂ tool₃│          │  PROTOCOLO MCP │
      └───────────────────┘          └─┬─────┬─────┬───┘
                                      tool₁ tool₂ tool₃

com MCP:  cada app implementa o protocolo uma vez; cada ferramenta, também → N + M
```

A conta é a tese econômica do protocolo. N aplicações × M fontes vira N adaptadores de cliente + M servidores de ferramenta — e, decisivamente, qualquer cliente passa a consumir qualquer servidor sem integração nova. O padrão ganha quando reduz manutenção real; e é por isso que a adoção do MCP foi a mais rápida da história recente de protocolos de desenvolvedor.

## As primitivas: tools, resources e prompts

O MCP organiza o mundo em três primitivas — e quase toda a discussão sobre “o que dá para fazer com MCP” é uma discussão sobre qual primitiva usar:

| Primitiva | O que é | Papel no sistema |
| --- | --- | --- |
| **Tools** | ações executáveis, com schema de entrada | o modelo pode invocá-las para modificar o mundo |
| **Resources** | dados legíveis, identificados por URI | o modelo (ou o cliente) consulta informação |
| **Prompts** | templates de instrução reutilizáveis | o modelo recebe receitas prontas de uso |

A divisão é a do capítulo 11 levada ao protocolo: **tools** são as funções do function calling (chamar uma API, executar uma ação); **resources** são as fontes de contexto que o RAG do capítulo 12 buscaria (um arquivo, uma tabela, um documento); **prompts** são os exemplos e instruções que moldam a chamada. O **cliente** orquestra — o host decide quais servidores carregar, quais tools expor ao modelo e como enquadrar o contexto —; o **servidor** expõe. É o mesmo desenho de periférico e porta que a analogia do USB-C sugere: o host não conhece os detalhes de cada dispositivo, apenas o protocolo.

Os primeiros servidores de referência da Anthropic — Slack, GitHub, Postgres, Google Drive — mostraram o escopo: ferramentas de colaboração, repositórios de código, bancos de dados e armazenamento de arquivos, todos atrás da mesma interface. Em seguida, a adoção explodiu: o MCP passou a ser suportado nativamente por ChatGPT, Claude, Cursor, Gemini, Microsoft Copilot e VS Code, entre outros, e por infraestruturas enterprise da AWS, Google Cloud e Azure.

## Adoção relâmpago e governança

O ritmo de adoção do MCP não tem precedentes comparável na história de protocolos de infraestrutura. Em um ano:

```text
nov/2024  lançamento e open-source pela Anthropic
mar/2025  OpenAI adota (ChatGPT + API)
2025      Google (Gemini), Microsoft (Copilot) e AWS anunciam suporte nativo
2025      revisões da spec em 2025-03-26, 2025-06-18 e 2025-11-25
dez/2025  ~97M downloads de SDK/mês; 10.000+ servidores públicos ativos
dez/2025  Anthropic doa o MCP à Linux Foundation (Agentic AI Foundation)
```

As revisões da especificação de 2025 (que a cronologia deste livro registra em 2025-03-26, 2025-06-18 e 2025-11-25) refinaram o núcleo: operações assíncronas, statelessness explícito, identidade de servidor e extensões oficiais — as peças que faltavam para uso enterprise. O marco de dezembro de 2025 resolveu a tensão que o ecossistema vinha apontando: a **governança** do protocolo, inicialmente concentrada na Anthropic, passou para a **Linux Foundation**, sob a recém-criada **Agentic AI Foundation**, com a Anthropic, a Block e a OpenAI como co-fundadoras e AWS, Google, Microsoft, Bloomberg e Cloudflare entre os membros fundadores. O mesmo movimento que o capítulo 17 descreve para o A2A — doação a governança neutra — repetiu-se para o MCP, com a promessa de que o padrão não pertencerá a nenhum fornecedor.

## MCP e agentes: a camada vertical do mundo

Uma aplicação que a adoção revelou é que o MCP não conecta apenas *modelos* a ferramentas — conecta **agentes** a ferramentas e, indiretamente, agentes a agentes. Um agente (capítulo 13) precisa de tools para agir; o MCP entrega a interface padronizada para essas tools, independentemente de qual modelo ou framework as orquestra. A AWS demonstrou, já em maio de 2025, comunicação entre agentes construída sobre MCP — dois agentes trocando informações através da mesma camada cliente–servidor.

É útil fixar o mapa mental que o capítulo 17 vai completar: **o MCP é a camada vertical** — conecta o modelo ao mundo (ferramentas, dados, serviços). O que ele não faz é conectar dois agentes entre si com descoberta de capacidades, autenticação e troca de tarefas — esse é o espaço horizontal que o A2A ocupa. Um agente pode, perfeitamente, usar MCP para buscar dados e A2A para conversar com outro agente. São camadas complementares, não concorrentes.

## Os limites que ninguém deveria ignorar

A mesma análise que explica o sucesso explica as fronteiras. O protocolo é **stateless**: cada conexão entre cliente e servidor não carrega memória entre sessões — não há, por padrão, histórico, estado de conversa nem memória duradoura. Quem precisa de persistência — e todo sistema em produção precisa — tem de construí-la fora do protocolo: banco, cache, camada de memória, pipeline de eventos. O MCP entrega o transporte; o estado é seu.

O segundo limite é a **observabilidade**. O protocolo não define, por padrão, linhagem completa das ações nem rastreamento uniforme das chamadas entre cliente e servidor. Em produção, isso significa camadas externas de monitoramento e auditoria — especialmente quando as chamadas de ferramentas têm efeitos no mundo (escrever, enviar, pagar). O terceiro é a **governança**: concentrada na Anthropic até dezembro de 2025, e só então aberta à Linux Foundation — um período em que a dependência de um único fornecedor foi, com razão, apontada como ponto de tensão.

E há o custo silencioso: protocolos “gastam tokens para falar” — cada primitiva trocada entre cliente e servidor consome contexto e latência, e a soma disso em sistemas com muitos servidores é real.

## A lição estrutural

A lição é a do capítulo 11, agora elevada à infraestrutura: **a interface padronizada é pré-requisito, e o valor está no que você constrói sobre ela** — o estado, a memória, a observabilidade e a verificação continuam sendo responsabilidade do sistema. O MCP transformou a integração ponto a ponto em protocolo, mas o protocolo entrega o transporte, não o sistema: stateless e sem observabilidade por padrão, ele devolve ao engenheiro exatamente as camadas que um sistema de produção não pode dispensar. É a aritmética do capítulo em outra moeda — o padrão ganha quando reduz manutenção real, e por isso a adoção do MCP foi a mais rápida da história recente de protocolos de desenvolvedor. E a mesma forma se repetirá no capítulo 17: quando o mundo que o agente acessa é outro agente, a padronização continua sendo o pré-requisito — mas o valor continua estando no que se constrói sobre ela.

## Para o engenheiro

MCP elimina o inferno das integrações N×M — use-o. Exponha suas APIs internas uma vez como servidor MCP e qualquer cliente compatível as consome; no sentido contrário, consuma as ferramentas do ecossistema sem integração dedicada. A conta é a do capítulo: N + M em vez de N×M. Se a sua integração se repete para múltiplos clientes, o servidor MCP já se pagou.

Modele o domínio nas três primitivas: tools para ações, resources para dados, prompts para receitas prontas. Se algo não cabe em nenhuma das três, provavelmente não precisa de MCP — o protocolo simplifica a integração, não a substitui. E comece pequeno: um servidor para um par de ferramentas internas vale mais que adotar o ecossistema inteiro de uma vez.

Não espere que o transporte resolva estado. O protocolo é stateless: persistência, memória, cache e observabilidade são suas — banco, pipeline de eventos, monitoramento. Trate cada chamada de tool como um efeito observável que precisa de log e, quando o efeito for no mundo, de validação antes e auditoria depois.

E acompanhe a governança de perto. A doação à Linux Foundation reduziu o risco de dependência de fornecedor, mas padrões vivos mudam — especificações, revisões e extensões. Construa sobre o protocolo, não sobre SDKs proprietários: é a diferença entre portabilidade e lock-in.

---

**Fontes:** [Anthropic, 2024] — Introducing the Model Context Protocol; [MCP Specification] — revisões 2024–2025; [AWS Open Source Blog, 2025] — interoperabilidade entre agentes sobre MCP; [InfoWorld, 2025] — MCP/A2A em produção, stateless e memória; [MIT Tech Review, 2025] — panorama de protocolos; [Taskade, 2026] — métricas de adoção; [Konishi, 2026] — timeline de MCP e tool use.
