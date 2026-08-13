# Do Transformer ao Agente

### Um livro temático e cronológico para engenheiros sobre modelos de linguagem, RAG, agentes e ferramentas

---

## Sobre o livro

Este livro conta, em ordem cronológica e temática, a história dos sistemas modernos baseados em modelos de linguagem:

- os fundamentos da modelagem de linguagem que precederam o Transformer;
- a arquitetura Transformer e a ascensão dos modelos pré-treinados (BERT, GPT);
- a escala, a emergência e a descoberta dos poucos exemplos (few-shot);
- o nascimento e a evolução da geração aumentada por recuperação (RAG);
- o alinhamento por instrução humana e o surgimento do ChatGPT;
- a aprendizagem de uso de ferramentas (tool use) e o *function calling*;
- a era dos agentes, dos frameworks e dos sistemas multi-agente;
- os protocolos de interoperabilidade (MCP, A2A);
- e a síntese do "loop cognitivo" que liga tudo isso.

Não é uma história apenas para especialistas. Cada capítulo introduz os conceitos necessários antes de avançar, sempre partindo do princípio didático:

> Não basta saber a resposta. É preciso saber **qual processo produz uma resposta confiável**.

O leitor acompanhará não só *o que* foi criado, mas *por que* cada inovação foi uma resposta a uma limitação concreta da abordagem anterior — e *como* essas peças se combinam hoje em sistemas de produção.

---

## Estrutura do livro

| Parte | Era | Período | Capítulos |
| --- | --- | --- | --- |
| 00 | Prefácio | — | como ler este livro |
| 01 | Era fundacional | ~1950–2020 | 1–4 |
| 02 | Era do RAG clássico | 2020–2021 | 5–6 |
| 03 | Era do alinhamento | 2021–2023 | 7–8 |
| 04 | Era das ferramentas | 2021–2023 | 9–11 |
| 05 | Era do RAG como sistema | 2023–2025 | 12 |
| 06 | Era dos agentes | 2022–2025 | 13–15 |
| 07 | Era dos protocolos | 2024–2026 | 16–17 |
| 08 | Síntese | — | 18–19 |

As partes seguem a cronologia em que cada estrutura *amadureceu*: o modelo (2020) → o RAG
clássico (2020–2021) → o alinhamento (2021–2023) → as ferramentas (2021–2023) → o RAG como
sistema (2023–2025) → os agentes (2022–2025) → os protocolos (2024–2026). Os períodos se
sobrepõem porque as estruturas coexistiram e evoluíram juntas — por isso algumas faixas se
cruzam. Uma técnica também pode preceder sua era (o RLHF é de 2017, antes do RAG de 2020).

Cada capítulo segue um formato didático fixo:

1. **Abertura em prosa** — situa o capítulo na história: o problema que a era enfrentava, o
   *porquê* e o que se ambicionava. Se você só puder ler uma seção, leia esta.
2. **Seções temáticas** — o corpo; cada seção desenvolve uma estrutura ou ideia, define o jargão
   na primeira ocorrência e usa diagramas em ASCII.
3. **A lição estrutural** — seção final do corpo que sintetiza a herança conceitual da era;
   presente em todos os capítulos, sempre com o mesmo nome.
4. **Para o engenheiro** — quadro final colorido com os takeaways práticos: decisões, armadilhas
   e o que levar para o projeto real.
5. **Fontes** — a linha **Fontes:** com as referências que sustentam o capítulo, no formato
   `[Autor, ano] — descrição curta`; a bibliografia completa está em `fontes.md`.

---

## Estado do livro

- [x] Pesquisa inicial e linha do tempo (fontes verificadas em `fontes.md`)
- [x] Estrutura de capítulos e arquivos de gestão
- [x] Prefácio (cap. 0)
- [x] Capítulos 1–6 (Era fundacional + RAG clássico)
- [x] Capítulos 7–8 (Era do alinhamento)
- [x] Capítulos 9–11 (Era das ferramentas)
- [x] Capítulo 12 (RAG avançado/modular)
- [x] Capítulos 13–15 (Era dos agentes)
- [x] Capítulos 16–17 (Era dos protocolos)
- [x] Capítulos 18–19 (Síntese)
- [x] Glossário — ampliado com "Por que importa" e conceitos novos (MCP, A2A, LoRA, tool use, avaliação)
- [x] Revisão estilística geral — fechamento único ("Para o engenheiro"), formato único de fontes, aspas curvas
- [ ] Revisão cruzada de datas e fontes
- [ ] Consolidação e formatação final

---

## Arquivos do projeto

| Arquivo | Propósito |
| --- | --- |
| `README.md` | este arquivo (visão geral e estado) |
| `SUMARIO.md` | sumário detalhado do livro |
| `cronologia.md` | linha do tempo dos marcos com datas e fontes |
| `fontes.md` | bibliografia consolidada com links |
| `NOTAS.md` | instruções de manutenção para futuras sessões |
| `capitulos/…` | conteúdo do livro por era |

---

## Princípios editoriais

1. **Cronológico**: a ordem é a da história, e cada capítulo aponta o que veio antes e depois.
2. **Didático**: conceitos são introduzidos do zero; jargão técnico é definido na primeira ocorrência.
3. **Verificável**: toda afirmação factual aponta para uma fonte em `fontes.md`.
4. **Estrutural**: não se trata de listar modelos, mas de ensinar as **estruturas** que se repetem (escala, recuperação, loop de agente, verificação).
5. **Sistemático**: o livro assume que inteligência efetiva emerge de modelo + contexto + retrieval + ferramentas + ambiente + memória + iteração + verificação.
