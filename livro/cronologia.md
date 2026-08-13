# Cronologia

Linha do tempo dos marcos que estruturam o livro. Cada entrada liga a uma fonte em `fontes.md`.
Datas de artigos seguem a primeira publicação (preprint/arXiv); datas de produtos seguem o anúncio oficial.

## Sementes (1950–2016)

| Data | Marco | Por que importa |
| --- | --- | --- |
| 1950 | Turing, "Computing Machinery and Intelligence" | Define o objetivo de conversar como critério de inteligência. |
| 1954 | Experimento de tradução de Georgetown | Primeira demonstração pública de tradução por máquina. |
| 1986 | Backpropagation (Rumelhart et al.) | Torna viável treinar redes profundas. |
| 1997 | LSTM (Hochreiter & Schmidhuber) | Mitiga o problema do gradiente que some; base das RNNs modernas. |
| 2003 | Modelo neural de linguagem (Bengio et al.) | Linguagem aprendida por rede neural + embeddings aprendidos. |
| 2013 | word2vec (Mikolov et al.) | Embeddings distribucionais: "rei – homem + mulher ≈ rainha". |
| 2014 | Seq2seq (Sutskever et al.; Cho et al.) | Encode–decode de sequências; base das arquiteturas modernas. |
| 2015 | Atenção (Bahdanau et al.) | Alinhamento dinâmico entre entrada e saída. |
| 2016 | Google Neural Machine Translation | Seq2seq + atenção em produção; derrota a tradução estatística. |

## O Transformer e o pré-treinamento (2017–2019)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2017-06-12 | **Attention Is All You Need** — o Transformer | Vaswani et al. 2017 |
| 2018-02 | ELMo — representações contextuais (bi-LSTM) | Peters et al. 2018 |
| 2018-06-11 | **GPT-1** — pré-treinamento generativo | Radford et al. 2018 |
| 2018-10-11 | **BERT** — encoder bidirecional pré-treinado | Devlin et al. 2018 |
| 2019-02-14 | **GPT-2** — modelos são aprendizes multitarefa não supervisionados | Radford et al. 2019 |
| 2019-10-23 | T5 — tudo é texto-para-texto | Raffel et al. 2019 |

## Escala, emergência e as leis de escala (2020–2022)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2020-05-28 | **GPT-3** (175B) — in-context learning | Brown et al. 2020 |
| 2020 | Leis de escala de modelos de linguagem | Kaplan et al. 2020 |
| 2022-03-29 | Chinchilla — computação ótima | Hoffmann et al. 2022 |
| 2022-04-04 | PaLM 540B | Chowdhery et al. 2022 |
| 2022-06-16 | Emergent abilities of LLMs | Wei et al. 2022 |

## Nascimento do RAG (2020–2022)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2020-05-22 | **RAG** — Retrieval-Augmented Generation | Lewis et al. 2020 |
| 2020 | REALM | Guu et al. 2020 |
| 2020 | kNN-LM | Khandelwal et al. 2020 |
| 2020 | DPR — dense passage retrieval | Karpukhin et al. 2020 |
| 2021 | FiD — fusion-in-decoder | Izacard & Grave 2021 |
| 2021-12-17 | WebGPT — modelo que navega em um browser | Nakano et al. 2021 |
| 2022 | RETRO — retrieval no pré-treinamento | Borgeaud et al. 2022 |

## Alinhamento e o momento ChatGPT (2021–2022)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2017 | **Origem do RLHF** — reward model + RL com preferências humanas (Atari/controle) | Christiano et al. 2017 |
| 2021 | LaMDA — diálogo com grounding | Thoppilan et al. 2022 |
| 2022-01-28 | **Chain-of-Thought** prompting | Wei et al. 2022 |
| 2022 | **InstructGPT / RLHF** | Ouyang et al. 2022 |
| 2022-11-30 | **ChatGPT** (produto) | OpenAI 2022 |

## Tool use: a pesquisa (2021–2023)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2022-05-01 | MRKL — sistemas neuro-simbólicos | Karpas et al. 2022 |
| 2022-10-06 | **ReAct** — raciocínio + ação | Yao et al. 2022 |
| 2022-11 | PAL — programa-aided language models | Gao et al. 2022 |
| 2023-02-09 | **Toolformer** — o modelo que se ensina a usar APIs | Schick et al. 2023 |
| 2023-03-30 | HuggingGPT — LLM como controlador de modelos | Shen et al. 2023 |
| 2023-05-24 | Gorilla — fine-tuning consciente de APIs | Patil et al. 2023 |

## Tool use: a indústria (2023–2024)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2023-03-23 | ChatGPT plugins (browser, code interpreter, retrieval) | OpenAI 2023 |
| 2023-06-13 | **Function calling na API** (GPT-3.5/4) | OpenAI 2023 |
| 2023-11-06 | DevDay: parallel function calling, JSON mode, Assistants | OpenAI 2023 |
| 2023-11-21 | Claude 2.1: tool use beta + 200K de contexto | Anthropic 2023 |
| 2023-12-13 | Gemini Pro API: function declarations | Google 2023 |
| 2024-02 | Berkeley Function-Calling Leaderboard | Gorilla Group 2024 |
| 2024-05-30 | Tool use GA na Anthropic; Bedrock Converse API | Anthropic/AWS 2024 |
| 2024-08-06 | **Structured Outputs** (strict: true) | OpenAI 2024 |
| 2024-10-22 | **Computer use** (Claude 3.5) | Anthropic 2024 |

## RAG avançado (2023–2025)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2023 | Self-RAG (reflexão) | Asai et al. 2023 |
| 2023 | FLARE (recuperação ativa) | Jiang et al. 2023 |
| 2023-12 | Survey RAG: Naive/Advanced/Modular | Gao et al. 2023 |
| 2024 | RAFT (treinado para usar/ignorar contexto) | Zhang et al. 2024 |
| 2024 | RAPTOR (retrieval hierárquico) | Sarthi et al. 2024 |
| 2024 | RAG vs. contexto longo (Self-Route) | Li et al. 2024 |
| 2024-10 | Survey abrangente de RAG | Gupta et al. 2024 |
| 2025 | LightRAG, PGraphRAG, agentic RAG | diversos |

## Agentes (2023–2025)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2023-03/04 | AutoGPT, BabyAGI, AgentGPT, CAMEL | Richards 2023; Nakajima 2023; Li 2023 |
| 2023-04 | Generative Agents (simulação social) | Park et al. 2023 |
| 2023-07 | ChatDev; ToolBench | Qian 2023; Qin 2023 |
| 2023-08 | **AgentBench**; MetaGPT; AutoGen; AgentVerse | Liu 2023; Hong 2023; Wu 2023; Chen 2023 |
| 2023-08 | Survey de agentes autônomos (perfil/memória/planejamento/ação) | Wang et al. 2023/2024 |
| 2023-09 | "The Rise and Potential of LLM Agents" | Xi et al. 2023 |
| 2024-06-17 | **tau-bench** — consistência de agentes | Yao et al. 2024 |
| 2025 | WebArena/OSWorld; surveys de multi-tool orchestration | diversos |

## Protocolos (2024–2026)

| Data | Marco | Fonte |
| --- | --- | --- |
| 2024-11-05 | Especificação inicial do MCP | MCP spec 2024-11-05 |
| 2024-11-25 | **MCP** anunciado e open-source (Anthropic) | Anthropic 2024 |
| 2025-03-26 | Revisão da spec MCP | MCP spec 2025-03-26 |
| 2025-04-09 | **A2A** anunciado (Google) | Google 2025 |
| 2025-06-23 | A2A doado à Linux Foundation (com AWS, Cisco, Microsoft) | Google Cloud 2025; InfoQ 2025 |
| 2025-06-18 | Revisão da spec MCP | MCP spec 2025-06-18 |
| 2025-07-31 | A2A 0.3: gRPC e security cards assinados | Google Cloud Blog 2025; InfoWorld 2025 |
| 2025-08 | A2A: 150+ organizações apoiando | Google Cloud Blog 2025 |
| 2025-11-25 | Revisão da spec MCP (async, statelessness, identidade de servidor) | MCP spec 2025-11-25 |
| 2025-12-09 | **MCP doado à Linux Foundation** (Agentic AI Foundation) | Anthropic 2025 |
| 2025-12 | MCP: ~97M downloads de SDK/mês, 10.000+ servidores | Taskade 2026; Anthropic 2025 |
| 2026-03 | Survey "Evolution of Tool Use in LLM Agents" | arXiv 2603.22862 |

## Observação de método

Datas de *preprints* podem divergir entre repositórios (arXiv vs. conferência). Sempre que houver conflito,
o livro segue a primeira data de publicação pública e registra a divergência. As datas de produtos seguem
anúncios oficiais das empresas, citados em `fontes.md`.
