# Capítulo 0 — Como ler este livro

## Objetivo

Todo livro de IA tem data de validade — este tenta escapar dessa regra. Em vez de catalogar o
GPT-n da vez, ele narra as **estruturas que se repetem** ao longo da história (escala, recuperação,
loop de agente, verificação) e como cada era as combinou de um jeito novo. Antes de mergulhar, o
leitor precisa de duas coisas: a tese central — *um modelo de linguagem é o núcleo de um sistema
maior, não um oráculo* — e um mapa: as eras cronológicas e as seções que organizam cada capítulo.
Este capítulo entrega as duas, e avisa que o resto do livro vai cobrar uma postura desconfortável:
**verificar** o que se aprende, em vez de apenas acreditar.

## Contexto histórico

Livros técnicos sobre “inteligência artificial” costumam envelhecer rápido. Este livro tenta
envelhecer devagar: em vez de catalogar modelos (GPT-n, LLaMA-n), ele narra **as estruturas que se
repetem** ao longo da história — escala, recuperação, loop de agente, verificação — e mostra como
cada era as combinou de forma nova.

## Ideia central

Um modelo de linguagem não é apenas um sistema que recebe texto e produz texto. Ele é o **núcleo de
inferência** de um sistema maior, e a inteligência efetiva desse sistema emerge da combinação de
modelo, contexto, recuperação, ferramentas, ambiente, memória, iteração e verificação.

## Conteúdo didático

### A tese em uma figura

```text
                    ┌─────────────────────┐
                    │   Modelo de linguagem│
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
          Memória            Tools             Contexto
             │                 │                  │
             ▼                 ▼                  ▼
           RAG              Shell             Arquivos
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ▼
                         Iteração / Loop
                               │
                               ▼
                           Verificação
                               │
                               ▼
                            Resultado
```

Ao longo do livro, cada parte desta figura é **inventada ou amadurecida em um período histórico**:

- o **modelo de linguagem** ganha forma com o Transformer (2017) e a escala (2020);
- o **contexto** vira engenharia deliberada com o pré-treinamento e o *in-context learning*;
- a **memória externa** vira RAG (2020);
- as **ferramentas** viram função de primeira classe com o *function calling* (2023);
- o **loop** vira agente com ReAct (2022) e os frameworks de agentes (2023);
- a **verificação** vira disciplina com a avaliação de agentes (2023–2025).

**As eras se sobrepõem.** As partes seguem a cronologia em que cada estrutura *amadureceu* —
modelo (2020), RAG clássico (2020–2021), alinhamento (2021–2023), ferramentas (2021–2023),
RAG como sistema (2023–2025), agentes (2022–2025), protocolos (2024–2026). Os períodos se
sobrepõem porque as estruturas coexistiram e evoluíram juntas: o alinhamento e as ferramentas
são contemporâneos (2021–2023), e a era dos agentes (2022–2025) cruza a do RAG como sistema
(2023–2025). Não se leia essas faixas como fronteiras — a ordem do livro é a ordem em que cada
estrutura amadurece, não a única linha do tempo possível. As estruturas não morrem quando a
próxima era começa: elas se combinam, e o capítulo 18 junta todas. E o inverso também vale: uma
técnica pode ser bem mais antiga do que a era em que aparece. O RLHF (2017) precedeu o próprio
RAG (2020) e só amadureceu para linguagem em 2022; a recuperação de informação existe desde os
anos 1970 e virou RAG em 2020. A era não marca o nascimento da técnica, mas o momento em que ela
amadureceu aplicada a modelos de linguagem.

### A pergunta que orienta tudo

Em cada era, há uma pergunta de fundo. Não pergunte apenas:

> “O modelo consegue fazer isso?”

Pergunte:

> “Que combinação de modelo, contexto, ferramentas, ambiente, memória, feedback e verificação
> torna isso possível de maneira confiável?”

### Como usar cada seção dos capítulos

1. **Abertura em prosa** — situa o capítulo na história: o problema que a era enfrentava, o
   *porquê* e o que se ambicionava. Se você só puder ler uma seção, leia esta.
2. **Seções temáticas** — o corpo do capítulo; cada seção desenvolve uma estrutura ou uma ideia,
   define o jargão técnico na primeira ocorrência e usa diagramas em ASCII quando ajudam.
3. **A lição estrutural** — a seção final do corpo sintetiza o que a era deixa de herança
   conceitual; presente em todos os capítulos, sempre com o mesmo nome.
4. **Para o engenheiro** — quadro final colorido com os takeaways práticos: decisões, armadilhas
   e o que levar para o projeto real.
5. **Fontes** — a linha **Fontes:** com os artigos que sustentam o capítulo, no formato
   `[Autor et al., ano] — descrição curta`; as referências completas estão em `fontes.md`.

### Convenções

- **Notação**: `[Autor et al., ano]` remete à bibliografia em `fontes.md`.
- **Diagramas**: ASCII simples; desenhe mentalmente antes de avançar.
- **Recuos didáticos**: cada capítulo presume apenas os capítulos anteriores.

## Para o engenheiro

- Antes de escolher um modelo, desenhe o **sistema**: no seu problema, o que é memória (banco,
  índice), o que é ferramenta (API, calculadora, shell) e o que é contexto (prompt, documentos).
- Separe sempre “o que o modelo sabe” (pesos) de “o que o sistema pode consultar ou executar”.
  É essa distinção que decide onde RAG e ferramentas entram.
- Use as eras como mapa mental de decisão: knowledge dinâmico → recuperação; cálculo/ação →
  ferramentas; tarefa multi-passo → loop de agente.
- Se só puder ler uma seção de um capítulo, leia a **abertura**; se for implementar, leia o
  **Para o engenheiro**.

**Fontes:** Este capítulo sintetiza a orientação do arquivo `AGENTS.md` deste repositório, que define a perspectiva operacional do livro. Referências históricas para as peças citadas (Transformer, RAG, function calling, ReAct, avaliação de agentes) estão em `fontes.md` e serão detalhadas nos capítulos correspondentes.
