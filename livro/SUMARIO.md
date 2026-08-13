# Sumário

> **Sobre as eras.** As partes deste livro seguem a cronologia em que cada estrutura *amadureceu*:
> o modelo (2020) → o RAG clássico (2020–2021) → o alinhamento (2021–2023) → as ferramentas
> (2021–2023) → o RAG como sistema (2023–2025) → os agentes (2022–2025) → os protocolos
> (2024–2026). Os períodos se sobrepõem porque as estruturas coexistiram e evoluíram juntas — por
> isso algumas faixas se cruzam (ex.: alinhamento e ferramentas, ambos 2021–2023). Uma técnica
> também pode preceder sua era: o RLHF nasceu em 2017, antes do RAG (2020), e só amadureceu para
> linguagem em 2022.

## Prefácio

- **Capítulo 0 — Como ler este livro**
  - Para quem é, o que se pressupõe, como usar os diagramas, os exercícios e as fontes.
  - A tese central: um LLM é o núcleo de um sistema maior, não um oráculo.

---

## Parte I — Era fundacional (≈1950–2020)

- **Capítulo 1 — Antes do Transformer: a longa busca por uma máquina que fale**
  - O teste de Turing e o experimento de Georgetown.
  - Modelos estatísticos de linguagem (n-gramas) e a maldição da dimensionalidade.
  - Modelos neurais de linguagem (Bengio, 2003) e *word embeddings* (word2vec, 2013).
  - RNNs, LSTM e o problema das dependências longas.
  - Seq2seq (2014), atenção (Bahdanau, 2015) e o Google Neural Machine Translation (2016).
  - *Leitura essencial*: Bengio 2003; Mikolov 2013; Hochreiter & Schmidhuber 1997; Sutskever 2014; Bahdanau 2015.

- **Capítulo 2 — Attention Is All You Need: o nascimento do Transformer (2017)**
  - A limitação que o Transformer resolve: paralelismo e dependências de longo alcance.
  - O mecanismo de atenção, atenção de múltiplas cabeças e posições.
  - Encoder-decoder e as arquiteturas descendentes (encoder-only, decoder-only).
  - Por que 2017 é o ano zero dos sistemas modernos.
  - *Leitura essencial*: Vaswani et al. 2017.

- **Capítulo 3 — Pré-treinamento: ELMo, BERT e GPT (2018–2019)**
  - A ideia de pré-treinar representações e adaptá-las a tarefas.
  - ELMo (contextualização) → BERT (bidirecional, encoder) → GPT (autoregressivo, decoder).
  - O contraste gerativo vs. discriminativo e o que cada escolha desbloqueia.
  - GPT-2 e a descoberta de que prever texto ensina multitarefa sem supervisão.
  - *Leitura essencial*: Peters 2018; Devlin 2018; Radford 2018; Radford 2019.

- **Capítulo 4 — Escala e emergência: GPT-3 e as leis de escala (2020–2022)**
  - Leis de escala, Chinchilla e o custo de treinar melhor.
  - GPT-3, *in-context learning* e o fim da era do *fine-tuning* como caminho único.
  - Emergência, capacidades que aparecem em escala.
  - O momento em que "mais dados" e "mais parâmetros" mudam qualitativamente o jogo.
  - *Leitura essencial*: Kaplan 2020; Brown 2020; Hoffmann 2022; Wei 2022 (emergent abilities).

---

## Parte II — Era do RAG clássico (2020–2021)

- **Capítulo 5 — Origens do retrieval-augmented (2017–2020)**
  - Por que conhecimento paramétrico não basta: dados estáticos, alucinação, atualização.
  - Predecessores: recuperação clássica (BM25), DPR, REALM, kNN-LM.
  - O retorno da recuperação como memória externa não-paramétrica.
  - *Leitura essencial*: Karpukhin 2020 (DPR); Guu 2020 (REALM); Khandelwal 2020 (kNN-LM).

- **Capítulo 6 — RAG clássico: Lewis et al. (2020) e as primeiras arquiteturas**
  - O paper fundador: recuperar → contextualizar → gerar.
  - Retriever + generator treinados juntos; Fusão no Decoder (FiD); RETRO.
  - RAG ≠ vector search: a pergunta certa é qual evidência maximizar.
  - *Leitura essencial*: Lewis 2020; Izacard & Grave 2021; Borgeaud 2022 (RETRO).

---

## Parte III — Era do alinhamento (2021–2023)

- **Capítulo 7 — De GPT-3 a ChatGPT: instrução, RLHF e o momento em que o público chegou**
  - Limitações de GPT-3: o modelo não "seguia instruções".
  - InstructGPT e RLHF: alinhar por preferência humana.
  - Chain-of-Thought: raciocínio explícito passo a passo.
  - ChatGPT (nov/2022) e o que mudou: o produto, o loop e a escala de adoção.
  - *Leitura essencial*: Ouyang 2022; Wei 2022 (CoT); OpenAI 2022 (ChatGPT).

- **Capítulo 8 — Modelos abertos e a corrida (2023)**
  - LLaMA e o impacto de pesos abertos na pesquisa e na indústria.
  - LLaMA 2/3, Mistral, BLOOM; LoRA e o custo da adaptação.
  - GPT-4: a convergência de escala, alinhamento e multimodalidade.
  - *Leitura essencial*: Touvron 2023; Hu 2021 (LoRA); OpenAI 2023 (GPT-4).

---

## Parte IV — Era das ferramentas (2021–2023)

- **Capítulo 9 — Do WebGPT ao Toolformer: como o modelo ganhou mãos**
  - WebGPT e o modelo agindo em um ambiente.
  - MRKL: roteamento neuro-simbólico; PAL: raciocínio via código.
  - Toolformer: o modelo que aprende sozinho quando chamar uma API.
  - *Leitura essencial*: Nakano 2021; Karpas 2022 (MRKL); Gao 2022 (PAL); Schick 2023.

- **Capítulo 10 — ReAct e o loop razão–ação (2022)**
  - Thought → Action → Observation → loop.
  - Por que ReAct é a forma, não um framework.
  - Reflexion, Self-Refine e o aprendizado com feedback.
  - *Leitura essencial*: Yao 2022 (ReAct); Shinn 2023; Madaan 2023.

- **Capítulo 11 — Function calling, structured outputs e computer use (2023–2024)**
  - ChatGPT plugins; a API de *function calling* (jun/2023).
  - Parallel function calling, JSON mode, Assistants API; Claude tool use.
  - Structured Outputs (ago/2024): a garantia de schema.
  - Computer use (out/2024): a ferramenta é a tela inteira.
  - *Leitura essencial*: OpenAI 2023 (function calling); OpenAI 2024 (structured outputs); Anthropic 2024 (computer use).

---

## Parte V — Era do RAG como sistema (2023–2025)

- **Capítulo 12 — De RAG ingênuo a RAG modular e agêntico (2023–2025)**
  - Naive RAG → Advanced RAG (pré-processamento, reranking, hibridismo).
  - Modular RAG: orquestração, iteração e memória.
  - Self-RAG, FLARE, IRCoT, RAFT, RAPTOR, GraphRAG.
  - RAG contra contexto longo (Self-Route, 2024); quando usar cada um.
  - Agentic RAG: recuperação como decisão de política, não como passo fixo.
  - *Leitura essencial*: Gao 2023 (survey); Asai 2023 (Self-RAG); Jiang 2023 (FLARE); Zhang 2024 (RAFT).

---

## Parte VI — Era dos agentes (2022–2025)

- **Capítulo 13 — Frameworks de agentes: de AutoGPT a LangGraph**
  - AutoGPT, BabyAGI: a explosão de 2023 e o que deu errado.
  - A estrutura de um agente: perfil, memória, planejamento, ação.
  - LangChain/LangGraph, CrewAI, AutoGen, MetaGPT, Semantic Kernel.
  - *Leitura essencial*: Richards 2023; Wang 2024 (survey); Wu 2023 (AutoGen); Hong 2023 (MetaGPT).

- **Capítulo 14 — Sistemas multi-agente e simulação social**
  - CAMEL, ChatDev, Generative Agents, AgentVerse.
  - Comunicação, papéis e a dificuldade do chatter improdutivo.
  - *Leitura essencial*: Li 2023 (CAMEL); Park 2023; Chen 2023 (ChatDev).

- **Capítulo 15 — Avaliação de agentes: o que medir e por que é difícil**
  - AgentBench, WebArena, OSWorld, tau-bench.
  - Métricas de tarefa vs. métricas de processo; consistência, segurança, custo.
  - A diferença entre resposta certa por acaso e processo robusto.
  - *Leitura essencial*: Liu 2023 (AgentBench); Yao 2024 (tau-bench).

---

## Parte VII — Era dos protocolos (2024–2026)

- **Capítulo 16 — MCP: o USB-C dos dados e ferramentas**
  - O problema: N×M integrações → N+M.
  - A arquitetura cliente–servidor, JSON-RPC, primitivas (tools, resources, prompts).
  - Adoção: OpenAI, Google, Microsoft, AWS; revisões da spec 2024–2025.
  - Limitações: estado, observabilidade, governança.
  - *Leitura essencial*: Anthropic 2024 (MCP); spec 2024-11-05 → 2025-11-25.

- **Capítulo 17 — A2A e a interoperabilidade entre agentes**
  - O problema que A2A resolve: agentes conversando com agentes.
  - Relação complementar com MCP (integração vertical vs. horizontal).
  - Linux Foundation, gRPC, segurança; o cenário 2025–2026.
  - *Leitura essencial*: Google 2025 (A2A); InfoQ 2025; VentureBeat 2025.

---

## Parte VIII — Síntese

- **Capítulo 18 — O loop cognitivo: RAG + agentes + ferramentas como um só sistema**
  - O padrão que unifica tudo: observar → raciocinar → agir → verificar.
  - Construção de evidência, memória externa e iteração.
  - Um projeto didático completo conectando as peças das partes I–VII.

- **Capítulo 19 — Avaliação, limites e o horizonte**
  - Como avaliar sistemas (não só respostas): retrieval, planejamento, execução, verificação.
  - Segurança, reversibilidade, custo e quando parar.
  - Rumo a 2026+: multi-tool orchestration, modelos de raciocínio, agentes verificáveis.
  - As perguntas que o campo ainda não respondeu.

---

## Apêndices

- **Apêndice A — Cronologia completa** → `cronologia.md`
- **Apêndice B — Bibliografia e fontes** → `fontes.md`
- **Apêndice C — Glossário** → `apendices/glossario.md`
