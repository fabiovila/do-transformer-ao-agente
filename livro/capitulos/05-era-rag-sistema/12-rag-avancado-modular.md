# Capítulo 12 — De RAG ingênuo a RAG modular e agêntico (2023–2025)

O capítulo 6 provou a direção: recuperar evidência e condicionar a geração a ela reduz alucinação e dá proveniência à resposta. Mas o RAG clássico, no mínimo que a Lewis et al. apresentaram, era um pipeline fixo — recuperar sempre, um número fixo de passagens, colar e gerar. A pergunta que define esta era é cruel e de engenharia: por que “recuperar e colar” ainda erra tanto em produção? A resposta é que o RAG mínimo colapsa para dentro de si mesmo um conjunto de problemas que a demonstração de laboratório esconde: chunking ruim corta a evidência ao meio, o top-k traz ruído que confunde o modelo, uma única busca não resolve perguntas que exigem juntar evidências de dois documentos, e sem metadados o modelo não consegue priorizar data ou fonte.

Entre 2023 e 2025, o RAG deixou de ser um pipeline e virou um sistema. Primeiro, o pré-processamento: parsing correto, chunking deliberado, metadados, hierarquia de resumos. Depois, o retrieval parou de errar: busca híbrida, reescrita de consulta, reranking com cross-encoder. Nesse ponto, o pipeline virou uma orquestração de módulos substituíveis — o que o survey de Gao et al. (2023) batizou de **Modular RAG**. E então a mesa virou de vez: *e se o quando, o o quê e o quantas vezes recuperar fossem decisões do próprio modelo?* O Self-RAG treina o modelo a decidir se recupera; o FLARE recupera no meio da geração quando a confiança cai; o RAFT treina o modelo a ignorar distratores; o IRCoT intercala raciocínio e busca. A recuperação deixou de ser um passo fixo e virou uma decisão de política — e, em seguida, uma ferramenta dentro de um loop de agente.

A ambição desta era pode ser resumida assim: fazer da recuperação uma capacidade adaptativa, medida por estágio, orquestrada por fluxo e, finalmente, decidida pelo próprio modelo. É o elo entre a Parte II (RAG clássico) e a Parte IV (ferramentas e loops). E o capítulo responde, no caminho, a pergunta prática que todo mundo faz em 2025: quando o contexto longo cabe inteiro, para que RAG?

## Por que “recuperar e colar” erra: o RAG ingênuo

O ponto de partida é o pipeline mínimo que o capítulo 6 formalizou, agora com um nome pejorativo que a literatura adotou: **Naive RAG**.

```text
pergunta
   ↓
retrieve top-k
   ↓
concatena [pergunta + passagens]
   ↓
generate
   ↓
resposta
```

Ele funciona em demonstrações e falha em produção. As razões são estruturais, e vale classificá-las, porque cada classe de falha vai ter uma resposta neste capítulo. A primeira é o **chunking ruim**: o documento é fatiado em pedaços fixos, e a evidência que importa fica cortada ao meio, ou o pedaço recuperado não contém a informação inteira. A segunda é o **ruído no contexto**: o top-k traz passagens irrelevantes, o modelo é confundido por elas e produz aquilo que se chama, com razão, “alucinação com apoio” — uma resposta errada, mas ancorada em algo que foi colado no prompt. A terceira é a **recuperação single-shot**: busca-se uma vez e pronto; perguntas que exigem juntar evidências de dois documentos (multi-hop) falham porque uma única consulta não captura os dois lados. A quarta é o **top-k fixo**: o mesmo número de passagens para perguntas fáceis e difíceis, de modo que ou falta evidência, ou sobra ruído. A quinta é a **ausência de metadados**: não há data, fonte, tipo ou seção, e o modelo não consegue priorizar informação mais recente ou mais confiável.

O chunking merece um exemplo concreto, porque é a falha mais barata e mais subestimada. Um documento afirma:

```text
"...A receita da vacina foi autorizada em 2021. A agência reguladora exigiu testes adicionais
antes da aprovação final. O fabricante..."

chunk 1: "...A receita da vacina foi autorizada em 2021. A agência reguladora exigiu testes
chunk 2: "adicionais antes da aprovação final. O fabricante..."
```

A pergunta “quando a vacina foi aprovada?” precisa da frase que começa no chunk 1 e termina no chunk 2. Se o retrieval só retorna chunks individuais, a resposta fica incompleta — ou o modelo inventa a data que falta. O problema não é o modelo nem o índice; é **como o texto foi fatiado**. O insight central desta seção é que, no RAG, *garbage in, garbage out* tem nome próprio: a resposta só pode ser tão boa quanto a **janela de evidência** que chegou ao prompt. Todos os módulos que veremos a seguir existem para alargar e limpar essa janela.

## Advanced RAG I: pré-processamento e chunking

A primeira linha de defesa é tratar o documento como dado estruturado antes de indexá-lo. O **parsing** não é “abrir o arquivo”: PDFs têm colunas, cabeçalhos, rodapés e páginas cujo layout quebra a ordem de leitura; tabelas precisam virar texto linear; imagens podem precisar de OCR ou de um modelo multimodal. Um parsing correto preserva a ordem lógica — o erro clássico é o texto “montado” fora de ordem, que transforma cada pergunta em um problema impossível para o retrieval.

O **chunking** é a decisão mais barata e mais subestimada do pipeline. Há três dimensões de estratégia, com usos diferentes:

| Estratégia | Como funciona | Quando usar |
| --- | --- | --- |
| Por tamanho fixo | N tokens (ex.: 512), com sobreposição (ex.: 50) | corpora homogêneos, textos corridos |
| Por seção/semântica | quebra em cabeçalhos, parágrafos, listas | documentos com estrutura (manuais, legislação) |
| Por frase/tópico | agrupa frases coerentes; às vezes com LLM | perguntas que exigem a passagem inteira |

A sobreposição (*overlap*) existe exatamente para mitigar o corte do exemplo anterior: pedaços consecutivos compartilham uma margem, então a frase cortada tem chance de aparecer inteira em algum chunk. O custo é mais chunks indexados e mais candidatos por consulta. Por fim, **metadados e hierarquia** anexam a cada chunk o documento, a seção, a data e o tipo, o que habilita dois ganhos: **filtros** (buscar só na legislação de 2025) e **citação precisa** (voltar do chunk para o trecho original, preservando proveniência). Técnicas como a **sumarização recursiva** (map-reduce de chunks em resumos pai) criam uma hierarquia: busca-se no nível do resumo, lê-se no nível do chunk.

## Advanced RAG II: indexação e recuperação

Com os chunks limpos, a segunda linha é fazer o retrieval parar de errar. Há quatro alavancas, em ordem crescente de custo. A primeira é a **busca híbrida** (léxica + densa). O BM25 do capítulo 5 é imbatível para nomes próprios, códigos e termos exatos; o retriever denso captura paráfrase. Produção usa os dois, combinando os rankings — e o jeito mais simples é a **fusão por ranque (RRF)**:

```text
score_final(d) = Σ_{sistemas}  1 / (k + rank_s(d))        com k ≈ 60
```

Em vez de comparar escalas incompatíveis (frequências do BM25 versus cossenos de embeddings), o RRF soma o *inverso do posto* em cada ranking: se o documento aparece em primeiro no léxico e em quarto no denso, contribui `1/61 + 1/64`. É estável, não exige calibrar pesos e melhora o recall sem exigir um modelo novo.

A segunda alavanca é a **query rewriting**. A pergunta do usuário raramente é a melhor consulta; um LLM a reescreve antes de buscar. A reescrita pode decompor perguntas compostas em subconsultas (cada uma buscando de forma independente), adicionar sinônimos ou transformar pergunta em afirmação. O **HyDE**, de Gao et al. (2022), leva a ideia ao extremo: em vez de buscar pelo embedding da pergunta, o sistema gera uma *resposta hipotética* e busca pelo embedding dela. Quando a pergunta e o documento não compartilham vocabulário, a resposta inventada “traduz” a intenção para a língua do corpus — e os experimentos mostraram que, mesmo com os detalhes falsos da resposta gerada, o encoder denso funciona como um compressor com perdas que filtra o ruído e ancora o vetor no espaço dos documentos reais.

A terceira alavanca é o **reranking com cross-encoder**, e é, de longe, o módulo com melhor retorno/custo do pipeline. O retriever denso é rápido porque pontua embeddings pré-computados — mas ele nunca vê pergunta e documento *juntos*. Um reranker cross-encoder recebe o par (pergunta, documento) e pontua a relevância conjunta. É caro, porque é uma inferência por par; por isso se usa no top-100→top-5: recupera largo, reordena fino. Ele corrige o ruído que o retrieval denso deixou passar. A quarta alavanca, **multiquery**, gera várias formulações da mesma pergunta, busca com cada uma e junta os candidatos — aumenta o recall ao custo de mais chamadas.

As métricas que medem essas alavancas são as clássicas de IR, agora por estágio:

| Métrica | O que mede | Onde |
| --- | --- | --- |
| recall@k | a evidência certa está no top-k? | retriever |
| precision@k / MRR | o ranking está bem ordenado? | retriever + reranker |
| NDCG | a ordem importa com relevância graduada | reranker |
| fidelidade | a resposta segue as evidências dadas? | generator |
| utilidade | a resposta atende ao usuário? | generator (LLM-as-judge) |

A regra de ouro dessa seção: **cada módulo tem a sua métrica**. Se a resposta final piora, o problema pode estar no chunking, no retriever, no reranker ou no generator — e um número agregado não diz onde.

## Modular RAG: o pipeline vira sistema

Quando se acumulam os módulos das duas seções anteriores, o pipeline deixa de ser uma cadeia fixa e passa a ser uma **orquestração de módulos independentes** — o survey de Gao et al. (2023) batizou isso de **Modular RAG**. As peças:

```text
                        ┌─────────────────────────────┐
                        │       QUERY PROCESSING      │
                        │  rewrite · expand · decompose│
                        └──────────────┬──────────────┘
                                       │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
      ┌──────────────┐       ┌──────────────┐        ┌──────────────┐
      │ RETRIEVAL    │       │  MEMORY      │        │  ROUTING     │
      │ lexical/denso│       │  cache,      │        │  qual fonte? │
      │ híbrido      │       │  histórica   │        │  qual índice?│
      └──────┬───────┘       └──────┬───────┘        └──────┬───────┘
             └──────────────────────┼───────────────────────┘
                                    ▼
                         ┌────────────────────┐
                         │  POST-RETRIEVAL    │
                         │  rerank · filtra   │
                         │  · comprime ·      │
                         │  funde             │
                         └─────────┬──────────┘
                                   ▼
                          ┌──────────────────┐
                          │    GENERATION    │
                          └─────────┬────────┘
                                    ▼
                                resposta
```

As propriedades que distinguem *modular* de *cadeia fixa* são quatro. Primeiro, **módulos substituíveis**: troca-se o retriever (BM25 → denso → híbrido) sem tocar no generator, e testa-se cada peça isoladamente. Segundo, **fluxo não-linear**: há loops — gerar, validar, recuperar de novo — e branchings: perguntas fáceis pulam o retrieval, perguntas compostas fazem subconsultas. Terceiro, **memória de processo**: o sistema guarda o que já recuperou ou gerou, como cache de consultas repetidas e histórico da conversa, para não repetir trabalho. Quarto, **iteração explícita**: o passo “validate” re-alimenta o retrieval — se a primeira evidência não sustenta a resposta, busca-se mais uma vez. Esse último é o germe do agentic, e ele aparece até em pseudocódigo enxuto:

```python
def rag_modular(pergunta, contexto=None):
    consultas = reescrever(pergunta)                # 1. query processing
    candidatos = set()
    for q in consultas:                             # 2. recuperação (possivelmente híbrida)
        candidatos |= buscar_hibrido(q, top_k=100)
    top5 = rerank(pergunta, list(candidatos))[:5]   # 3. post-retrieval
    if contexto:                                    # 4. memória do processo
        top5 += contexto["evidencias_anteriores"]
    resposta = gerar(pergunta, top5)                # 5. generation
    if validar(resposta, top5) < limiar:            # 6. iteração
        return rag_modular(pergunta, contexto={"evidencias_anteriores": top5})
    return resposta, top5                           # resposta + proveniência
```

A lição didática é que **a complexidade não está em nenhum módulo, está no fluxo entre eles**. É por isso que o capítulo 13 (frameworks de agentes) reaparecerá exatamente aqui: a orquestração de módulos com loops é a mesma forma que os frameworks de agente codificam.

## Aprendendo a recuperar: Self-RAG, FLARE, RAFT, IRCoT

Até aqui, o *quando* e o *quantas vezes* recuperar eram decididos por heurística — sempre, uma vez, top-k fixo. A virada de 2023 foi fazer o **próprio modelo** aprender a decidir. Quatro abordagens mostram o espectro, do treinamento à inferência.

O **Self-RAG**, de Asai et al. (2023), treina o modelo com *tokens de reflexão* que controlam o fluxo. Um token decide *se* deve recuperar para aquele passo, e outros criticam a resposta: a evidência é suficiente? a resposta é apoiada pelas passagens? Na inferência, o modelo recupera só quando o token indica necessidade, pode fazer várias rodadas e critica a própria saída. É retrieval como *política aprendida*, não como passo fixo. Nos experimentos, os modelos de 7B e 13B superaram o ChatGPT e o Llama2-chat com retrieval em QA de domínio aberto, raciocínio e verificação de fatos — e melhoraram a acurácia factual e de citação em gerações longas. O gesto é duplamente importante: a recuperação vira decisão, e a decisão é monitorada por autoavaliação.

O **FLARE**, de Jiang et al. (2023), faz recuperação *ativa durante a geração*. O modelo gera uma sentença provisória; se a confiança nas próximas tokens cai abaixo de um limiar, ele usa essa sentença como consulta, recupera e regera a parte incerta. A ideia é “olhar para frente”: em vez de buscar pelo passado já escrito, antecipa-se o conteúdo futuro. Funciona sem treinamento adicional — apenas um LLM de inferência e um retriever — e superou linhas de base de recuperação única e de múltiplas recuperações em tarefas de geração longa, com o maior ganho em QA multi-hop (2WikiMultihopQA), onde cada passo de raciocínio exige informação nova.

O **RAFT**, de Zhang et al. (2024), ataca o problema por outro lado: em vez de apenas recuperar melhor, o modelo é *treinado* para lidar com retrieval imperfeito. Os dados de treino incluem o documento “oracle” (aquele que contém a resposta) junto de documentos distratores — e, em uma fração dos exemplos, o oracle é omitido por completo. O modelo aprende a citar verbatim o trecho relevante e a ignorar os distratores, produzindo respostas em estilo chain-of-thought. É a metáfora do livro aberto: quem estuda para a prova de consulta aberta aprende a reconhecer o que é relevante, e não apenas a ler tudo. O RAFT melhorou o desempenho de fine-tuning supervisionado com e sem RAG em PubMed, HotpotQA e no benchmark Gorilla.

O **IRCoT**, de Trivedi et al. (2023), intercala *chain-of-thought* e *retrieval*: cada passo de raciocínio gera uma consulta, o resultado volta ao raciocínio, que gera a próxima consulta — até a cadeia terminar. É a forma de decompor problemas multi-hop sem uma arquitetura nova: o mesmo modelo raciocina e decide o que buscar. O exemplo canônico do paper é a pergunta sobre o país onde uma montanha-russa foi fabricada: a primeira busca (pela própria pergunta) não responde; é preciso inferir o fabricante e então buscar o país. Os ganhos chegaram a 21 pontos de recall e 15 pontos de F1 sobre a recuperação de passo único, em HotpotQA, 2WikiMultihopQA, MuSiQue e IIRC, com redução dos erros factuais no raciocínio intermediário.

O fio comum das quatro abordagens pode ser visto na tabela:

| Método | Ideia central | Onde foi avaliado |
| --- | --- | --- |
| Self-RAG | o modelo decide se recupera e critica a própria resposta | PopQA, TriviaQA, PubHealth, ARC-Challenge, ASQA |
| FLARE | recupera *durante* a geração quando a confiança cai | 2WikiMultihopQA, StrategyQA, ASQA, WikiAsp |
| RAFT | treinado a ignorar distratores e citar as fontes | PubMed, HotpotQA, Gorilla |
| IRCoT | intercala raciocínio e recuperação (retrieve-then-read iterativo) | HotpotQA, 2WikiMultihopQA, MuSiQue, IIRC |

*(Multi-hop significa que a resposta exige reunir evidências de mais de um documento — exatamente o caso onde recuperar uma vez não basta.)* Em todas, **recuperação deixou de ser um componente fixo e virou uma decisão** — e a decisão foi gradualmente transferida das regras para o modelo.

## Estruturando a memória: RAPTOR e GraphRAG

Há um problema que os módulos anteriores não resolvem: *perguntas globais*. “Quais são os temas recorrentes neste relatório?” ou “como essas duas seções se relacionam?” não são respondidas por top-k de chunks — a resposta está *espalhada* pelo corpus. Duas linhas tratam disso.

O **RAPTOR**, de Sarthi et al. (2024), constrói uma **árvore de resumos**: agrupa chunks por similaridade, resume cada grupo, agrupa os resumos de novo — até uma raiz. A consulta é roteada para o nível certo: pergunta específica vai às folhas (chunks), pergunta ampla vai aos nós altos (resumos). É *multigranularidade*: a memória tem zoom.

```text
                     ┌──────────────┐
                     │  resumo raiz │   ← nível alto (perguntas globais)
                     └──────┬───────┘
              ┌─────────────┼─────────────┐
          ┌────┴───┐    ┌────┴───┐    ┌────┴───┐
          │ resumo │    │ resumo │    │ resumo │   ← resumos de grupos
          └───┬────┘    └───┬────┘    └───┬────┘
         ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
         │ c  │ c  │   │ c  │ c  │   │ c  │ c  │   ← chunks (nível específico)
         └────┴────┘   └────┴────┘   └────┴────┘
```

O ponto central é que a árvore inteira participa do retrieval, não só as folhas: os experimentos mostraram que a busca em todos os níveis supera a busca apenas em camadas específicas. Com o GPT-4, o RAPTOR melhorou o melhor resultado no benchmark QuALITY em 20 pontos absolutos, e estabeleceu estado da arte em NarrativeQA e QASPER. O custo é a indexação recursiva com LLM, que roda uma vez sobre o corpus.

O **GraphRAG**, da Microsoft (Edge et al., 2024), representa o corpus como **grafo de entidades e relações**. Um LLM extrai as entidades (pessoas, empresas, conceitos) e as relações entre elas; o grafo é particionado em comunidades de entidades próximas; e cada comunidade é resumida em um relatório. Perguntas globais são respondidas em modo map-reduce: cada resumo de comunidade gera uma resposta parcial, e as parciais são combinadas na resposta final. A capacidade nova é responder perguntas que *nenhum chunk* contém — “quais são os temas dominantes deste corpus inteiro?” — com melhorias substanciais de abrangência e diversidade sobre o RAG vetorial em corpora de milhões de tokens. O custo é alto, porque a extração roda um LLM sobre o corpus inteiro uma vez; as variantes de 2025 (LightRAG, PGraphRAG) reduziram o custo e melhoraram a atualização incremental do grafo.

A escolha entre as duas, e entre elas e o RAG de chunks, é um trade-off de granularidade:

```text
pergunta específica  →  RAG de chunks (top-k)  →  barato, direto
pergunta multi-hop   →  IRCoT / iterativo      →  médio
pergunta de resumo   →  RAPTOR (níveis altos)  →  médio
pergunta global      →  GraphRAG (comunidades) →  caro, mas é o único que responde
```

## RAG versus contexto longo: o trade-off que não some

De 2023 a 2025, as janelas de contexto explodiram — de 128k tokens para 1M+ em modelos como Gemini-1.5 e Claude Sonnet. A pergunta se tornou inevitável: *se cabe tudo no prompt, para que RAG?* A resposta honesta tem três partes, e elas mudam o desenho do sistema.

A primeira parte é **custo e latência**. O custo de atenção cresce com o quadrado do contexto: “cabe” não é “é barato”. Colocar um milhão de tokens em toda pergunta custa ordens de magnitude mais caro que recuperar os cinco chunks relevantes — e responde mais devagar. Para produção, o RAG continua sendo o caminho econômico padrão. A segunda parte é a **precisão no meio**. O fenômeno chamado *lost in the middle*, documentado por Liu et al. (2023), mostrou que os modelos usam bem a informação no início e no fim do contexto, e muito pior a que está no meio — uma curva em U que vale para tarefas de QA multi-documento e para recuperação de pares chave-valor. Um prompt gigante pode literalmente “esconder” a evidência relevante no meio do ruído; o RAG, ao encurtar o contexto para só o que importa, evita esse problema por construção.

A terceira parte é o **quando o contexto longo vence**. Perguntas que exigem o documento *inteiro* — uma jurisprudência de 800 páginas, um contrato completo — não cabem em top-k, porque a evidência está distribuída demais. Nesses casos, o contexto longo direto é superior. A comparação sistemática de Li et al. (2024) quantificou o equilíbrio: quando há recursos suficientes, o contexto longo supera o RAG em desempenho médio, mas a custo muito maior — e, decisivamente, em mais de 60% das consultas as predições das duas abordagens são idênticas. Isso abre espaço para o **Self-Route**, a contribuição prática do mesmo trabalho: um modelo roteia cada consulta, respondendo primeiro pelo caminho barato (RAG) e só enviando ao contexto longo as perguntas que o RAG declara incapaz de responder — com reduções de custo de 65% no Gemini-1.5-Pro e 39% no GPT-4o, mantendo desempenho comparável ao contexto longo. A regra prática:

```text
a resposta está em poucos trechos      →  RAG (barato, rápido, proveniente)
a resposta exige o documento inteiro   →  contexto longo
não sei qual é o caso                  →  roteamento (Self-Route) ou heurística
```

O trade-off não desaparece porque as janelas crescem; ele apenas muda de lugar. Agora a decisão é por consulta, não por arquitetura.

## Agentic RAG: recuperação como ferramenta no loop

A convergência do “modelo decide” (Self-RAG, FLARE, RAFT, IRCoT) com o “fluxo com loops” (Modular RAG) é o **Agentic RAG**: a recuperação vira uma *ferramenta* que o modelo invoca dentro de um ciclo observar → raciocinar → agir. Já não existe pipeline; existe um agente que decide com que consulta buscar, quantas vezes, se precisa de outra fonte e quando parar.

```text
pergunta
   ↓
┌──────────────────────────────────────────────┐
│  AGENTE (LLM)                                │
│   raciocina → decide ação                    │
│   ┌──────────────────────────────────────┐   │
│   │ buscar("X")   → top-k → observa      │   │
│   │ raciocina → buscar("Y") → observa    │   │
│   │ raciocina → calcula/outra ferramenta │   │
│   │ raciocina → resposta final           │   │
│   └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
   │
   ▼
resposta (+ proveniência das buscas)
```

O que muda em relação a tudo que vimos até aqui é a abolição das três fixações do pipeline clássico. Não existe mais **top-k fixo**: o agente decide quantas passagens precisa e quando já tem evidência suficiente. Não existem mais **consultas fixas**: a pergunta evolui durante o processo — a raiz do IRCoT, generalizada. E não existe mais o privilégio da recuperação de ser o único “mundo externo”: além do índice, o agente pode chamar calculadora, API, busca na web. A recuperação perde o monopólio da evidência externa e passa a ser uma ferramenta entre outras, no sentido exato dos capítulos 9 a 11.

Este é o ponto onde a Parte V termina e o resto do livro começa. O loop do Agentic RAG é o loop do ReAct (capítulo 10); a orquestração de módulos e ferramentas é o tema dos frameworks (capítulo 13); a avaliação por estágio e por consistência é o tema do capítulo 15. O RAG deixou de ser um produto e virou uma peça de um sistema — o que significa, para o engenheiro, que as perguntas certas deixaram de ser “qual banco vetorial” e passaram a ser “quem decide recuperar, com que critério e quando parar”.

## A lição estrutural

| Termo | Significado |
| --- | --- |
| Naive RAG | retrieve → augment → generate, sem ajustes; o baseline que falha em produção |
| Advanced RAG | pré-processamento, busca híbrida, reranking, query rewriting |
| Modular RAG | módulos independentes e orquestráveis, com loops e memória de processo |
| Chunking | divisão do documento em trechos indexáveis; a decisão de qualidade mais barata |
| RRF | fusão de rankings por inverso do posto; combina lexical + denso sem calibrar pesos |
| HyDE | buscar pelo embedding de uma resposta hipotética gerada pelo modelo |
| Reranker (cross-encoder) | reordena o top-k olhando pergunta + documento juntos |
| Self-RAG / FLARE / RAFT / IRCoT | aprender a decidir quando recuperar |
| RAPTOR / GraphRAG | estruturar a memória em árvores de resumo ou grafos de entidades |
| Lost in the middle | degradação da precisão para informação no meio do contexto |
| Self-Route | roteamento entre RAG e contexto longo por consulta |
| Agentic RAG | recuperação como ferramenta dentro de um loop de agente |

Este vocabulário é o que a Parte IV reutiliza quando fala de “observar” no loop, e o que a Parte VI reutiliza quando fala de ferramentas de um agente. Quem domina essas distinções não está apenas montando um pipeline; está desenhando o sistema de evidência que o modelo consulta.

## Para o engenheiro

Antes de trocar o vector store, meça o ROI dos módulos baratos. Query rewriting, HyDE, reranking e chunking movem mais a qualidade do que o índice em si. É tentador culpar o banco vetorial quando a resposta piora; na prática, a falha está quase sempre na janela de evidência — e a janela se corrige com pré-processamento e pós-processamento, não com um índice novo.

Trate o RAG como um pipeline de módulos substituíveis — rewrite → retrieve → rerank → refine → generate. Isso permite testar e trocar cada peça isoladamente, sem reindexar tudo, e transforma o debug de “a resposta está errada” em “qual estágio vazou”. Use um reranker cross-encoder no top-k: é barato, adiciona pouca latência e corrige o ruído do retrieval denso. Quase sempre compensa.

Separe as métricas por estágio. Recall@k e NDCG para o retriever; fidelidade e utilidade para a geração. Só suba a complexidade de um módulo quando a métrica dele piorar — e não quando a resposta final incomodar, porque o número agregado não diz onde o problema está.

Chunking é a decisão mais subestimada do sistema. Teste tamanho × sobreposição × quebra por seção antes de otimizar qualquer outra coisa; um bom chunking resolve mais que um modelo melhor. E guarde os metadados (fonte, data, seção) desde o índice: sem eles não existe filtro, nem proveniência, nem reranking contextual — e proveniência é o que diferencia RAG de adivinhação.

Escalone a complexidade na ordem certa: híbrido → rerank → iterativo → agentic. Pular etapas cobra caro em debug, porque cada nível só existe porque o anterior vazou. Para perguntas globais (“o que este corpus diz sobre X?”), um chunk não responde — avalie RAPTOR ou GraphRAG; para o resto, o top-k continua sendo o melhor custo-benefício.

Finalmente, quando o contexto longo for uma opção, não a trate como substituto do RAG, mas como alternativa a ser roteada por consulta. Use heurística ou Self-Route para decidir por pergunta, em vez de apostar em uma arquitetura única. E lembre: a decisão de quem recupera, com que critério e quando parar é o desenho central — não o índice.

---

**Fontes:** [Gao et al., 2023] — survey RAG (Naive/Advanced/Modular); [Asai et al., 2023] — Self-RAG; [Jiang et al., 2023] — FLARE; [Zhang et al., 2024] — RAFT; [Trivedi et al., 2023] — IRCoT; [Sarthi et al., 2024] — RAPTOR; [Edge et al., 2024] — GraphRAG; [Liu et al., 2023] — Lost in the Middle; [Li et al., 2024] — Self-Route; [Gao et al., 2022] — HyDE; [Gupta et al., 2024] — survey abrangente de RAG; [Revisão sistemática, 2025] — síntese de 128 estudos (2020–2025).
