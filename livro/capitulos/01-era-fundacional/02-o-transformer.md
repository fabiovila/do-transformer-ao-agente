# Capítulo 2 — Attention Is All You Need: o nascimento do Transformer (2017)

Em 2017, havia uma convicção quase silenciosa na comunidade de processamento de linguagem natural: se a linguagem era uma sequência, então qualquer modelo sério precisaria de algum mecanismo de memória sequencial. As RNNs e LSTMs pareciam inevitáveis, e a atenção era vista como um acessório útil — algo que ajudava o decoder a olhar para trás, mas não como o coração da arquitetura. Foi nesse cenário que um grupo pequeno fez uma aposta radical: e se a recorrência não fosse necessária? E se cada palavra pudesse conversar diretamente com todas as outras, ao mesmo tempo, sem passar por nenhum intermediário? Essa pergunta, que à primeira vista parecia apenas uma provocação técnica, acabou se tornando uma das mudanças mais profundas da história recente da inteligência artificial.

O artigo *Attention Is All You Need*, publicado por Vaswani e colaboradores em 12 de junho de 2017, não propôs apenas mais uma melhoria incremental. Ele sugeriu descartar por completo as redes recorrentes e construir tudo — leitura, relacionamento entre palavras, geração — a partir de mecanismos de atenção. A hipótese era ousada demais para passar despercebida. Um dos autores, Jakob Uszkoreit, suspeitava que atenção sozinha poderia bastar para tradução automática, contrariando a sabedoria dominante da época, inclusive a de seu pai, o linguista computacional Hans Uszkoreit. O resultado, no entanto, foi mais forte do que a aposta inicial: um modelo mais rápido de treinar, mais paralelizável e com desempenho superior em tradução. O Transformer original tinha dimensões modestas para os padrões atuais, mas sua estrutura provou-se extraordinariamente escalável. Quase tudo o que viria depois — GPT, BERT, T5, agentes, RAG, tool use — descende direta ou indiretamente dessa arquitetura.

A ideia central pode ser resumida em uma frase: a relevância entre duas palavras pode ser calculada diretamente, sem estados ocultos recorrentes, e esse cálculo pode ser feito em paralelo para todas as posições da sequência. Parece simples, mas essa mudança altera tudo. Em vez de uma memória comprimida que precisa sobreviver a muitos passos intermediários, o Transformer oferece acesso direto: qualquer token pode olhar para qualquer outro token imediatamente, com um peso de relevância calculado na hora.

## Por que descartar a recorrência?

Para entender a força da aposta, é preciso lembrar o que significava treinar uma arquitetura recorrente. Uma RNN processa tokens um após o outro. Isso quer dizer que a palavra na posição mil só é processada depois das novecentas e noventa e nove anteriores. No treinamento, essa dependência sequencial cobra um preço alto: GPUs são excelentes em fazer muitas contas ao mesmo tempo, mas não conseguem acelerar bem uma cadeia longa de passos estritamente dependentes. Além disso, a informação de posições distantes precisa atravessar muitas transformações de estado antes de chegar ao ponto atual. A cada transformação, algo se perde. O sinal enfraquece, a memória degrada, e o modelo começa a tratar o início do texto como uma lembrança vaga.

O Transformer rompe com essa lógica. Em vez de comprimir o passado em um estado que se transforma passo a passo, ele permite que cada posição consulte diretamente todas as outras. A distância deixa de ser um caminho longo e cheio de intermediários; torna-se apenas mais um par de posições cuja relevância pode ser calculada. Com isso, duas limitações históricas começam a cair ao mesmo tempo: o paralelismo deixa de ser bloqueado pela ordem de processamento, e dependências distantes passam a ser alcançáveis sem que a informação precise sobreviver a uma longa cadeia de estados.

## A atenção como operação central

A operação que torna isso possível é a chamada *scaled dot-product attention*. Nela, cada posição da sequência gera três vetores a partir de sua representação:

```text
Query (Q)  → "o que eu estou procurando?"
Key   (K)  → "o que eu ofereço?"
Value (V)  → "o conteúdo que entrego se for escolhido"
```

A intuição é elegante. O Query representa a pergunta que uma posição faz ao restante da sequência. As Keys representam aquilo que cada outra posição oferece como resposta possível. Quando Query e Key são compatíveis, a posição correspondente ganha peso. O Value, por sua vez, é o conteúdo efetivamente transmitido quando aquela posição é escolhida. Em outras palavras, Query e Key decidem a relevância; Value carrega a informação.

Para cada posição, calcula-se a compatibilidade entre seu Query e os Keys de todas as outras posições:

```text
pesos = softmax( Q · Kᵀ / √d_k )
saída = pesos · V
```

A divisão por `√d_k` existe para estabilizar os valores durante o cálculo — e é daí que vem o termo *scaled*. Depois do softmax, os pesos se tornam uma distribuição de relevância. A saída de cada posição é, então, uma soma ponderada dos Values, em que cada Value contribui de acordo com a importância que recebeu.

Para tornar isso concreto, imagine um exemplo pequeno, com dimensão 2 apenas para caber no papel. Suponha os tokens `“a”`, `“casa”` e `“é”`. A posição `“a”` possui query `Q = [1, 0]`, e as chaves são `K_a = [1, 0]`, `K_casa = [0, 1]` e `K_é = [1, 1]`. Os produtos escalares, que medem a compatibilidade inicial, são `[1, 0, 1]`. Dividindo por `√2 ≈ 1,41` e aplicando softmax, temos algo como:

```text
escores escalados ≈ [0,71, 0, 0,71]
softmax([0,71, 0, 0,71]) ≈ [0,40, 0,20, 0,40]
```

Nesse exemplo, `“a”` presta atenção igualmente a `“a”` e a `“é”`, e pouca atenção a `“casa”`. Os pesos sobre as posições são exatamente essa distribuição. Em implementações reais, as dimensões não são 2, mas centenas — no artigo original, `d_model = 512` — e os vetores são aprendidos durante o treinamento. Ainda assim, a lógica essencial permanece a mesma.

Em código, a atenção é surpreendentemente compacta:

```python
import torch
import torch.nn.functional as F

def atencao(Q, K, V):
    d_k = Q.shape[-1]
    escores = Q @ K.transpose(-2, -1) / d_k ** 0.5
    pesos = F.softmax(escores, dim=-1)
    return pesos @ V
```

Há também um exemplo intuitivo que ajuda a perceber por que essa operação é tão poderosa. Considere a frase:

> “O animal não atravessou a rua porque estava cansado.”

Para interpretar corretamente a frase, o modelo precisa relacionar o estado de cansaço ao animal, não à rua. Em uma arquitetura recorrente, essa relação precisa sobreviver a vários passos intermediários. Na atenção, cada posição pode perguntar diretamente às demais: “quem é relevante para mim agora?” E a resposta pode vir imediatamente, sob a forma de pesos altos sobre a posição correta.

## Muitas cabeças, muitas perguntas

Uma única atenção já é capaz de capturar relações relevantes, mas a linguagem não é feita de um único tipo de relação. Há dependências sintáticas, semânticas, referenciais, discursivas. Às vezes, a palavra importante é o sujeito; às vezes, é o objeto; às vezes, é um pronome lá atrás; às vezes, é um modificador próximo. Se houvesse apenas um mecanismo de atenção, ele precisaria dar conta de todos esses padrões ao mesmo tempo.

O Transformer resolve isso executando várias atenções em paralelo, cada uma com projeções diferentes de Query, Key e Value. Esse mecanismo é chamado de *multi-head attention*:

```text
          ┌─ cabeça 1 ─→ atenção ─┐
entrada ──┼─ cabeça 2 ─→ atenção ─┼─ concatena ─→ projeção → saída
          └─ cabeça 3 ─→ atenção ─┘
```

A ideia é que diferentes cabeças possam se especializar em diferentes tipos de dependência. Uma cabeça pode aprender a ligar adjetivos a substantivos; outra pode rastrear coreferências; outra pode capturar relações de longo alcance. Análises posteriores confirmaram empiricamente que cabeças distintas tendem a desenvolver comportamentos distintos. Assim, o modelo não apenas presta atenção — ele presta atenção de várias maneiras simultaneamente.

## A ordem precisa voltar

Havia, porém, uma armadilha. A atenção, por si só, é insensível à ordem dos tokens. Ela opera como se estivesse lidando com um conjunto, não com uma sequência. Sem informação posicional, frases como “o gato mordeu o cão” e “o cão mordeu o gato” produziriam representações idênticas, porque contêm exatamente as mesmas palavras. Isso seria inaceitável para qualquer modelo de linguagem minimamente sério.

A solução foi injetar informação posicional diretamente nas representações. O artigo original fez isso por meio de embeddings posicionais senoidais, que adicionam a cada posição um sinal único e previsível. Modelos posteriores desenvolveram alternativas aprendidas e variantes mais sofisticadas, como RoPE e ALiBi. O ponto essencial é que a atenção fornece o acesso direto entre posições, mas a informação posicional devolve a ordem ao modelo. Sem ela, o Transformer enxergaria as palavras, mas não a frase.

## Uma arquitetura com duas metades

O Transformer de 2017 não era apenas uma operação de atenção isolada. Ele foi apresentado como uma arquitetura completa de encoder-decoder, herdando do seq2seq a divisão entre leitura e geração, mas substituindo a recorrência por atenção em todos os lugares.

```text
            ENCODER (N camadas)                DECODER (N camadas)
entrada ─► [embeddings + posição]
           [self-attention multi-head]
           [feed-forward]
           [camada norm / resíduo]
                 │                               ┌───────────────────────┐
                 │           saída já gerada ───►│ [embeddings + posição] │
                 │                               │ [self-attention *mascarada*]
                 │                               │ [cross-attention sobre o encoder]
                 │                               │ [feed-forward]
                 ▼                               └──────────┬────────────┘
           contexto do encoder ────────────────────────────►│
                                                           ▼
                                                     softmax → próxima palavra
```

Três detalhes dessa arquitetura são especialmente importantes. O primeiro é a *self-attention*: cada posição atende a outras posições da mesma sequência. No encoder, isso significa que a entrada pode se relacionar internamente consigo mesma. No decoder, significa que a saída já gerada pode consultar o próprio passado.

O segundo detalhe é a *masked self-attention* no decoder. Como o modelo está prevendo a próxima palavra, ele não pode trapacear olhando para o futuro. A máscara impede que posições ainda não geradas influenciem a previsão atual. É esse cuidado que torna o Transformer usável para geração autoregressiva, token a token.

O terceiro detalhe é a *cross-attention*. Além de olhar para si mesmo, o decoder também atende à saída do encoder, conectando a entrada lida à saída que está sendo produzida. Trata-se da generalização direta da atenção de Bahdanau, agora integrada a uma arquitetura inteiramente baseada em atenção.

Para dimensionar mentalmente o tamanho do Transformer original, vale observar sua configuração:

| Hiperparâmetro | Transformer base | Transformer big |
| --- | ---: | ---: |
| `d_model` (dimensão das representações) | 512 | 1024 |
| Cabeças de atenção | 8 | 16 |
| Camadas (encoder + decoder) | 6 + 6 | 6 + 6 |
| Feed-forward (camada oculta) | 2048 | 4096 |
| Parâmetros | ~65M | ~213M |

Comparados aos bilhões e trilhões de parâmetros dos modelos atuais, esses números parecem pequenos. Mas a estrutura essencial é a mesma. O que mudou depois não foi a invenção de uma arquitetura completamente nova, e sim a escala, os dados e o refinamento de treino.

## Três linhagens para o futuro

Embora o Transformer original tenha nascido como um modelo encoder-decoder, o mais importante para o restante da história não foi exatamente o modelo de 2017, e sim as três linhagens que derivaram dele:

```text
Encoder-only     BERT  →  entendimento (classificação, perguntas-respostas)
Decoder-only     GPT   →  geração autoregressiva  ←  base dos LLMs modernos
Encoder–decoder  T5    →  transformações texto→texto
```

A linhagem *encoder-only* usa apenas a metade encodadora do Transformer. Ela enxerga a sequência inteira de uma vez, de forma bidirecional, e por isso é especialmente adequada para tarefas de entendimento: classificar texto, extrair informação, responder perguntas a partir de um trecho fornecido. O BERT é o exemplo clássico dessa família.

A linhagem *decoder-only* usa apenas a metade decodadora. Ela gera token a token, sempre olhando para trás, respeitando a causalidade. É a família que domina os grandes modelos de linguagem modernos, porque se mostrou extremamente eficaz para geração, raciocínio em linguagem natural e uso interativo. O GPT é seu representante mais famoso.

A linhagem *encoder-decoder* preserva as duas metades e permanece útil para tarefas de transformação de texto em texto, como tradução, sumarização e reformulação. O T5 é um exemplo importante dessa abordagem.

O Transformer de 2017 era encoder-decoder. Nos anos seguintes, BERT e GPT exploraram caminhos diferentes: um apostou no entendimento bidirecional; outro, na geração causal. Esses dois ramos pareciam distintos, mas voltariam a se encontrar mais tarde, especialmente em sistemas de RAG, onde compreensão e geração precisam trabalhar juntas.

## O que o Transformer mudou de fato

O impacto do Transformer pode ser entendido em três grandes frentes. A primeira é o paralelismo. Como a self-attention é computada sobre todas as posições de uma vez, o treinamento se tornou muito mais eficiente em GPUs. O modelo original treinou em cerca de três dias e meio usando oito GPUs e, mesmo assim, alcançou estado da arte em tradução automática. Para a época, isso era impressionante — não apenas pelo resultado, mas pelo fato de que a arquitetura permitia aproveitar muito melhor o hardware disponível.

A segunda frente é o acesso direto a dependências de longo alcance. Em uma RNN, a informação entre tokens distantes precisa atravessar muitos estados intermediários. No Transformer, qualquer posição pode atender diretamente a qualquer outra. A distância deixa de ser um funil de degradação e passa a ser apenas mais uma relação a ser ponderada.

A terceira frente é a escalabilidade. O Transformer se mostrou compatível com escalas de dados e parâmetros que as arquiteturas recorrentes não suportavam bem. Isso não era apenas uma vantagem técnica: era uma porta aberta para o futuro. Os capítulos seguintes explorarão como essa escalabilidade permitiu transformar um modelo de tradução em uma base para sistemas cada vez mais gerais.

O teste original foi feito no WMT 2014, um benchmark de tradução automática com aproximadamente 4,5 milhões de pares inglês-alemão e cerca de 36 milhões de pares inglês-francês. O Transformer big alcançou BLEU 28,4 em inglês para alemão e BLEU 41,8 em inglês para francês. BLEU é uma métrica que mede a sobreposição de n-gramas entre a tradução gerada e referências humanas, variando de 0 a 100. Na prática, o resultado mostrava que, com uma fração do custo de treinamento em comparação com modelos recorrentes de ponta, o Transformer conseguia empatar ou superar o estado da arte de então.

## A lição estrutural

O Transformer não venceu por ser mais complexo — venceu por **remover a estrutura que limitava**: o estado sequencial comprimido. Toda vez que um sistema obriga a informação a atravessar um funil de transformações intermediárias, algo se perde no caminho; o ganho do Transformer veio de substituir o funil por acesso direto — qualquer posição pode olhar qualquer posição, na hora. Essa lição tem duas faces que o livro inteiro vai reutilizar. A primeira: **arquitetura é a escolha de quais distâncias importam** — quando a distância deixa de ser um caminho e vira uma relação ponderada, o problema que parecia estrutural vira questão de escala. A segunda: **Query, Key e Value são o molde de todo retrieval** — relevância decidida por compatibilidade, conteúdo entregue pelo Value —, e esse é, palavra por palavra, o desenho da busca semântica e do RAG. O Transformer de 2017 não previu o RAG; previu a *forma* que o RAG usa.

## Para o engenheiro

Para quem projeta sistemas, o Transformer deixa algumas lições duradouras. A primeira é que Query e Key definem relevância, enquanto Value carrega o conteúdo. Sempre que você pensar em um sistema de recuperação, vale perguntar: qual é a chave que determina se algo é relevante? E qual é o valor que deve ser retornado quando essa relevância é detectada? Essa separação mental é mais útil do que parece, porque ela aparece não apenas na atenção, mas também em busca semântica, cross-attention e RAG.

A segunda lição é que geradores são causais. Um modelo decoder-only só pode olhar para trás; ele não pode ver o futuro do texto que ainda vai produzir. Isso tem implicações práticas diretas na construção de prompts, agentes e tool use. O contexto fornecido ao modelo precisa conter tudo o que ele precisa saber antes da geração. Não se pode contar com uma suposta visão futura do processo.

A terceira lição é que ordem importa. Se o seu pipeline reordena dados, serializa documentos de forma inconsistente ou altera a posição de trechos relevantes, os embeddings posicionais mudarão a interpretação do modelo. Preservar a ordem ao preparar documentos para o contexto não é um detalhe cosmético; é parte da semântica que o Transformer consome.

Por fim, é importante lembrar que todo modelo moderno que você usa é, em algum nível, um Transformer. A chamada janela de contexto é, na prática, a quantidade de informação sobre a qual o modelo pode aplicar atenção em um determinado momento. É ela que limita quantos documentos, instruções, exemplos ou passos de raciocínio cabem em um prompt. Compreender isso não é apenas compreender uma arquitetura: é compreender a base material sobre a qual praticamente todo o ecossistema atual de LLMs foi construído.

---

**Fontes:** [Vaswani et al., 2017] — Attention Is All You Need (Transformer); [Bahdanau et al., 2015] — atenção em seq2seq; [Wikipedia, Transformer] — visão geral da arquitetura; [Zhao et al., 2023] — survey de LLMs.
