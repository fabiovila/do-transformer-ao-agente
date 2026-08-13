# Capítulo 3 — Pré-treinamento: ELMo, BERT e GPT (2018–2019)

Resolvido o problema da arquitetura com o Transformer, restava outro obstáculo, menos vistoso porém mais caro: para cada tarefa — classificar, responder, traduzir, resumir — ainda era preciso construir um modelo e um conjunto de dados praticamente do zero. A ideia que emergiu entre 2018 e 2019 foi, ao mesmo tempo, preguiçosa e genial: treinar uma única vez sobre um corpus gigante e genérico, depois adaptar esse modelo a tarefas específicas. A pergunta era quase filosófica: uma rede treinada apenas para prever a próxima palavra seria capaz, de brinde, de responder perguntas, traduzir e resumir? ELMo, BERT e GPT responderam em sequência, cada um à sua maneira. O mais insolente deles, o GPT-2, revelou que prever texto pode ensinar multitarefa sem nenhuma supervisão explícita. A ambição mudou de escala: não se tratava mais de construir máquinas para tarefas isoladas, mas de criar uma base comum que contivesse todas elas. É aqui que o contexto começa a virar código — a semente do que, mais tarde, este livro chamará de engenharia de contexto.

O Transformer já havia provado que atenção pura funciona. A próxima pergunta era: como aproveitar esse poder para além da tradução? A resposta veio da combinação de duas ideias antigas com a nova arquitetura. A primeira era a noção de embeddings contextuais: uma palavra não tem um significado fixo; “a margem do rio” e “a margem de lucro” usam a mesma palavra com sentidos diferentes, e qualquer representação séria precisa capturar essa variação. A segunda era o pré-treinamento: em vez de aprender cada tarefa isoladamente, aprender primeiro com uma quantidade massiva de texto genérico, para só depois especializar-se. Entre 2018 e 2019, três modelos definiram o mapa dessa nova era: ELMo, que trouxe contextualização ainda com LSTM; BERT, que apostou no entendimento bidirecional; e GPT, que apostou na geração causal. Este capítulo segue principalmente o ramo GPT, porque é dele que descendem os LLMs modernos — mas BERT é indispensável para entender o RAG, que aparecerá mais adiante.

A ideia central pode ser enunciada de forma simples: treine primeiro em texto genérico em escala, depois adapte. E quanto mais genérica e grande for a base, mais tarefas ela desbloqueia sem treino específico. Essa mudança de perspectiva transformou o campo. O modelo deixou de ser um especialista estreito, moldado para uma única função, e passou a ser um generalista treinado na linguagem do mundo, capaz de receber instruções e se ajustar a novas demandas com muito pouco esforço adicional.

## Pré-treinar para depois adaptar

Antes dessa virada, cada tarefa exigia modelo e dados próprios. Classificação tinha seu pipeline; perguntas-respostas tinha outro; tradução, outro ainda. O novo paradigma quebrou essa lógica ao propor um fluxo único:

```text
corpus genérico (bilhões de palavras)
        │
        ▼
   PRÉ-TREINO   ←  objetivo autossupervisionado (sem anotação humana)
        │
        ▼
   MODELO BASE (representações da linguagem)
        │
        ├── adaptação 1 (fine-tuning numa tarefa pequena)
        ├── adaptação 2 (outra tarefa)
        └── adaptação 3 (...)
```

O ponto crucial é que o pré-treino é autossupervisionado: o “rótulo” é derivado do próprio texto. Isso significa que não é preciso pagar o custo humano de anotar milhões de exemplos. O texto já contém, em si mesmo, sinais suficientes para ensinar algo sobre linguagem. Essa mudança permitiu usar quantidades massivas de dados sem depender de curadoria manual, e foi isso que tornou economicamente viável treinar modelos cada vez maiores.

## ELMo: a palavra ganha dependência do contexto

ELMo, publicado por Peters e colaboradores em 2018, não era um Transformer; era uma bi-LSTM pré-treinada. Ainda assim, introduziu a ideia-chave que mudaria tudo: representações contextuais. Diferentemente do word2vec, que atribuía um único vetor fixo a cada palavra, o ELMo produzia um vetor que mudava conforme a frase. A palavra “banco” não era representada sempre da mesma forma; sua representação dependia do contexto em que aparecia. O modelo alimentava tarefas específicas com esses vetores contextualizados. Arquiteturalmente, ficou datado. Conceitualmente, marcou a transição decisiva: a palavra deixou de ser um ponto fixo no espaço e passou a ser uma função do contexto.

## BERT: entender olhando para os dois lados

BERT, publicado por Devlin e colaboradores em 2018, é encoder-only: ele vê a sequência inteira de uma vez. Essa escolha arquitetural tem consequências profundas. Como o modelo pode olhar simultaneamente para o que vem antes e para o que vem depois de uma palavra, ele constrói representações especialmente ricas para tarefas de entendimento. Seus dois objetivos de pré-treino eram o Masked Language Modeling e o Next Sentence Prediction. O primeiro escondia palavras e pedia ao modelo para preenchê-las usando o contexto dos dois lados. O segundo tentava ensinar se duas frases eram consecutivas.

Um exemplo clássico de MLM ajuda a perceber a força do mecanismo:

```text
Entrada:  O elefante não atravessou a [MASK] porque estava cansado.
Saída:    rua   (candidatos com score: rua 0,89 · estrada 0,78 · linha 0,31)
```

O detalhe importante é o que o modelo usa para decidir: o lado direito da frase — “porque estava cansado” — ajuda a escolher “rua”. É isso que torna o BERT bidirecional. Ele não está apenas prevendo o próximo token olhando para trás, como os geradores causais do ramo GPT; ele está interpretando a frase como um todo, com acesso ao contexto completo. Na época, o BERT superou o estado da arte em praticamente todas as tarefas de entendimento de linguagem natural. Seu impacto duradouro apareceu também fora da pesquisa: em outubro de 2019, o Google passou a usar BERT no processamento de consultas de busca, um sinal claro de que a técnica havia saído dos artigos e entrado em produção massiva.

## GPT: gerar como objetivo universal

GPT, publicado por Radford e colaboradores em 2018, seguiu o caminho oposto. Ele é decoder-only: gera token a token, de forma causal, olhando apenas para trás. Seu pré-treino usa a modelagem autoregressiva clássica: prever a próxima palavra. Para adaptar o modelo a uma tarefa, faz-se fine-tuning supervisionado sobre a base pré-treinada. A aposta do GPT era a simplicidade. Em vez de objetivos e arquiteturas customizados para cada tarefa, um único objetivo — prever texto — e uma arquitetura uniforme. Essa escolha parecia mais modesta do que a do BERT, mas acabaria se revelando extraordinariamente poderosa.

## GPT-2: quando prever texto virou multitarefa

GPT-2, publicado por Radford e colaboradores em 2019, escalou o decoder-only para 1,5 bilhão de parâmetros e fez uma descoberta que mudou a direção da pesquisa: sem nenhum treino específico para a tarefa, o modelo conseguia responder perguntas, traduzir, resumir e gerar texto coerente — bastava continuar o prompt. Os autores chamaram isso de “modelos de linguagem são aprendizes multitarefa não supervisionados”. A implicação era profunda: talvez não fosse necessário ensinar cada tarefa separadamente; talvez bastasse apresentar a tarefa no contexto certo.

O corpus usado foi o WebText: cerca de 40 GB de texto, vindos de 8 milhões de documentos coletados a partir de links do Reddit com mais de 3 upvotes. Esse filtro simples servia como um sinal de qualidade. O WebText virou o protótipo da receita que o GPT-3 expandiria depois: texto da internet filtrado por algum sinal humano indireto. Para dimensionar a escala da época, vale observar os quatro modelos centrais deste capítulo:

| Modelo | Arquitetura | Camadas | d_model | Params | Corpus de pré-treino |
| --- | --- | ---: | ---: | ---: | --- |
| BERT-base (2018) | encoder-only | 12 | 768 | 110M | BooksCorpus + Wikipedia (~3,3B palavras) |
| BERT-large (2018) | encoder-only | 24 | 1024 | 340M | idem |
| GPT-1 (2018) | decoder-only | 12 | 768 | 117M | BooksCorpus (~800M palavras) |
| GPT-2 (2019) | decoder-only | 48 | 1600 | 1,5B | WebText (~40 GB / 8M docs) |

O BooksCorpus é um dataset com cerca de 11.000 livros não publicados; a Wikipedia inglesa completa de 2018 entra no pré-treino do BERT. Esses dois pilares foram a base textual dessa era. Vistos de hoje, os números parecem pequenos, mas foi ali que se formou o germe do zero-shot: executar uma tarefa apenas descrevendo-a no contexto de entrada, sem exemplos e sem ajuste. O próprio GPT-2 era grande demais para a época. A primeira versão nem foi publicada integralmente, por receio de uso indevido — um dos momentos mais marcantes da história pública da OpenAI.

## A lição estrutural

Parte do legado dessa fase está no vocabulário que ainda hoje organiza o campo. Alguns termos nasceram ali ou ganharam ali sua forma moderna:

| Termo | Significado |
| --- | --- |
| zero-shot | resolver tarefa sem exemplos, só com instrução/descrição no prompt |
| few-shot | resolver tarefa com alguns exemplos dados no prompt (amadurecido no GPT-3, cap. 4) |
| fine-tuning | continuar o treinamento em dados específicos da tarefa |
| pré-treino | treinamento genérico autossupervisionado em grande corpus |

Note o vínculo com a tese deste livro: o contexto passa a ser um canal de programação. A tarefa é “descrita”, não “treinada”. Isso parece uma mudança de vocabulário, mas é uma mudança de paradigma. Em vez de modificar os pesos do modelo para cada nova necessidade, começa-se a modificar aquilo que se coloca diante dele. É o início da engenharia de contexto que os capítulos seguintes explorarão com RAG, ferramentas e agentes.

## Por que isso importa para RAG e agentes

Este capítulo não é apenas uma etapa histórica; é uma divisão de trabalho que permanece atual. O BERT fornece o retriever de muitos sistemas RAG. O DPR, por exemplo, usa uma linhagem encoder para representar consultas e documentos. Entender o que é uma representação contextual ajuda a entender por que busca semântica funciona — e por que às vezes falha. O GPT, por sua vez, fornece o generator: o cerne de todos os LLMs e agentes que aparecem neste livro.

A lição mais profunda, contudo, vem do GPT-2: prever texto ensina muito. É isso que torna RAG e agentes viáveis. Um bom modelo base já “sabe” usar informação quando ela lhe é apresentada no contexto. Ele não precisa ser treinado do zero para cada documento novo; ele precisa receber o documento certo, no lugar certo, no formato certo. Essa percepção é uma das chaves que conectam pré-treinamento, recuperação e agentes.

## Para o engenheiro

Para quem projeta sistemas, a primeira lição é escolher a família pela tarefa. Encoders são adequados para classificação e entendimento; decoders, para chat e geração; encoder-decoders, para tradução e transformações texto-para-texto. Na prática atual, você raramente treina esses modelos do zero; você os escolhe. Essa decisão arquitetural inicial ainda importa, mesmo quando o modelo final já vem pronto como serviço.

A segunda lição é que pré-treino autossupervisionado significa dados sem anotação. Se falta dado rotulado, o caminho natural é partir de um modelo pré-treinado e fazer fine-tuning. Treinar do zero sem um motivo muito forte costuma ser caro, lento e desnecessário. A base já carrega linguagem, mundo e estilo; o fine-tuning apenas ajusta a direção.

A terceira lição é que, antes de fine-tunar, vale testar zero-shot ou few-shot no prompt. Essa abordagem é barata, reversível e hoje cobre muito do que, em 2018, exigia treinamento. Em produção, o zero-shot sobrevive até como fallback: antes de orquestrar retrieval ou ferramentas, muitas vezes vale tentar resolver o problema apenas com uma boa instrução.

Por fim, lembre que zero-shot foi onde tudo começou. Ele não é apenas um truque de prompt; é a primeira evidência empírica de que o contexto pode programar o modelo. Quando um sistema de RAG injeta documentos no prompt, ou quando um agente injeta resultados de ferramentas, está estendendo exatamente essa intuição: se o modelo aprende com o texto à sua frente, então controlar esse texto é controlar parte do comportamento do modelo.

---

**Fontes:** [Peters et al., 2018] — ELMo; [Devlin et al., 2018] — BERT; [Radford et al., 2018] — GPT-1; [Radford et al., 2019] — GPT-2; [Wikipedia, Transformer] — visão geral da arquitetura; [Zhao et al., 2023] — survey de LLMs.
