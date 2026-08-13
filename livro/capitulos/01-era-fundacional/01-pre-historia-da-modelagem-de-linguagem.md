# Capítulo 1 — Antes do Transformer: a longa busca por uma máquina que fale

Antes de 2017, “fazer a máquina falar” já era uma obsessão de décadas — e uma coleção de fracassos elegantes. Este capítulo não começa no Transformer de propósito: para entender por que aquele ano foi o ano zero, é preciso caminhar pelo que veio antes, pelo que cada abordagem resolveu e, sobretudo, pelo que cada uma deixou em aberto. A pergunta que atravessa tudo é simples e cruel: por que uma máquina não entende “a casa é azul”? As respostas da época — primeiro regras, depois contagens, depois vetores — formam a pré-história dos grandes modelos de linguagem, e cada uma delas ilumina um pedaço do problema enquanto revela outro. A ambição nunca foi escrever um dicionário; era comprimir a linguagem em algo que um computador pudesse carregar, manipular e, de alguma forma, generalizar. O capítulo termina em 2016, com três portas entreabertas — portas que o Transformer vai arrombar de uma só vez.

## Uma linha do tempo de tentativas

A história dos modelos de linguagem modernos se estende muito antes de qualquer arquitetura profunda. Para sentir o peso do que o Transformer representou, vale olhar para trás e perceber quantas peças precisaram ser inventadas, uma a uma, ao longo de quase setenta anos:

```
1950  Turing propõe o teste de conversação
1954  Georgetown demonstra tradução automática (regras)
1986  Redes neurais e backpropagation
1997  LSTM
2003  Primeiro modelo neural de linguagem (Bengio)
2013  word2vec (embeddings)
2014  seq2seq (encode–decode)
2015  Atenção (Bahdanau)
2016  Google NMT (produto: seq2seq + atenção em produção)
2017  Transformer  ←  ponto de partida do resto deste livro
```

Cada linha dessa tabela não é apenas um marco cronológico: é uma resposta parcial a uma pergunta que se recusava a ser respondida por inteiro. Linguagem é sequencial, estruturada e ambígua — e cada geração de pesquisadores resolveu um desses três aspectos enquanto deixava os outros dois em aberto, até que o Transformer apareceu com a resposta que combinava todas as peças: atenção total, em paralelo, sobre tudo o que veio antes.

## O que significa, afinal, “modelar linguagem”?

Antes de mergulhar nas tentativas históricas, convém fixar o que está em jogo. Um modelo de linguagem atribui uma probabilidade a sequências de palavras. A forma mais comum é a modelagem autoregressiva: dado o que já foi escrito, prever a próxima palavra. Matematicamente, isso se escreve assim:

```
P("a casa é azul") = P(a) · P(casa | a) · P(é | a casa) · P(azul | a casa é)
```

Parece trivial, mas é poderoso. Um bom preditor de próxima palavra acaba aprendendo gramática, vocabulário, fatos sobre o mundo e até estilo — tudo como subproduto de tentar adivinhar o token seguinte. Quase toda inovação que este livro vai explorar, do GPT ao RAG aos agentes autônomos, preserva essa espinha dorsal: gerar a próxima palavra condicionada ao contexto. O que muda, de era em era, é *como* o contexto é representado e *quanto* dele a máquina consegue enxergar.

## A era das regras: quando a linguagem era gramática

Entre 1950 e 1980, a abordagem dominante tratava a linguagem como um sistema de regras. Gramáticas formais, dicionários bilíngues, regras de tradução escritas à mão por linguistas pacientes. O experimento de Georgetown, em 1954, traduziu frases do russo para o inglês diante de jornalistas e prometeu que em cinco anos a tradução automática seria um problema resolvido. Não foi. O que ficou claro, ao longo das duas décadas seguintes, é que regras não escalam para a ambiguidade real da língua. “A casa é azul” exige saber o que é uma casa, o que é azul, e que o adjetivo concorda com o substantivo — e isso para uma frase de cinco palavras. Multiplique por um parágrafo, por um livro, por uma conversa inteira, e o castelo de regras desmorona sob o próprio peso.

## A era das contagens: estatística contra a maldição

A partir dos anos 1980, a comunidade trocou regras por contagens. Em vez de dizer à máquina *como* a língua funciona, deixou-se que ela observasse *o que aparece*. Modelos de n-gramas estimam a probabilidade de uma palavra a partir das n−1 anteriores, simplesmente contando frequências num corpus:

```
P(azul | casa é) ≈ contagem("casa é azul") / contagem("casa é")
```

É uma ideia honesta e brutalmente simples. E funciona — até certo ponto. O problema tem nome: a maldição da dimensionalidade. A maioria das frases possíveis nunca apareceu no corpus de treino. Quando n cresce, as contagens ficam esparsas demais; truques de suavização remendam, mas não resolvem, porque o modelo não generaliza de verdade para combinações novas. Um bigrama em Python é literalmente um dicionário de contagens, e já revela a fratura:

```python
from collections import defaultdict, Counter

corpus = ["a casa é azul", "o céu é azul", "a casa é grande"]
contagens = defaultdict(Counter)

for frase in corpus:
    tokens = ["<inicio>"] + frase.split()
    for w1, w2 in zip(tokens, tokens[1:]):
        contagens[w1][w2] += 1

def prob(w1, w2):
    total = sum(contagens[w1].values())
    return contagens[w1][w2] / total if total else 0

print(prob("é", "azul"))    # 2/3 → "azul" seguiu "é" em 2 das 3 frases
print(prob("casa", "roxa")) # 0/3 → nunca visto: probabilidade zero
```

A última linha é o veredito da era inteira: o modelo só “acerta” o que viu. Se a combinação não está no corpus, a probabilidade é zero e ponto final. O Brown Corpus, referência da época, tinha cerca de um milhão de palavras — um instantâneo de uma década do inglês. As contagens de um bigrama cabem na memória de qualquer máquina atual; a maldição não está no volume de dados, mas no crescimento combinatorial de n. A estatística resolveu a rigidez das regras, mas criou outra prisão: a dependência absoluta do que já foi observado.

## A era neural: palavras viram vetores

A virada conceitual veio em 2003, quando Bengio e colegas propuseram algo radicalmente diferente: em vez de contar, *aprender uma função contínua* que estima a probabilidade condicional. A ideia-chave é distribuir o aprendizado por palavras similares — se o modelo nunca viu “casa é azul” mas já viu “céu é azul”, ele transfere conhecimento de uma situação para a outra. É aqui que nascem os embeddings: cada palavra vira um vetor numérico em um espaço de alta dimensão, e a proximidade geométrica entre vetores codifica proximidade de significado.

```
        mapa de palavras (espaço de embeddings)
            manhã  ~  tarde  ~  noite
            gato   ~  cachorro
            rei - homem + mulher ≈ rainha
```

O word2vec, de Mikolov e colaboradores em 2013, transformou essa intuição em ferramenta prática. Treinado sobre o corpus de notícias do Google — cerca de 100 bilhões de palavras —, o modelo produziu vetores de 300 dimensões por palavra e mostrou que relações semânticas e sintáticas emergiam espontaneamente da geometria. De repente, “máquina que fala” parecia menos delírio e mais engenharia. Mas embeddings sozinhos não bastam: eles capturam o significado de palavras isoladas, não a dinâmica de uma frase inteira se desdobrando no tempo.

## Redes recorrentes e o drama da memória

A linguagem é sequencial. Para prever a próxima palavra, o contexto relevante pode estar longe — muito longe. As Redes Neurais Recorrentes (RNNs) enfrentam esse fato processando tokens um a um, mantendo um estado oculto que, em tese, “lembra” de tudo o que passou:

```
t0:  estado h0 ← f(embedding("a"), h_ini)
t1:  estado h1 ← f(embedding("casa"), h0)
t2:  estado h2 ← f(embedding("é"), h1)
t3:  previsão   ← softmax(h2 · W)   →  próxima palavra
```

Na teoria, a memória é infinita. Na prática, durante o treinamento, o gradiente — a medida de “quanto devo ajustar cada peso” — precisa viajar para trás por muitos passos temporais, e a cada passo ele se multiplica por números menores que um. O resultado é o chamado vanishing gradient: o sinal de erro desaparece antes de alcançar os tokens distantes, e a rede simplesmente esquece o começo da frase. A LSTM, proposta por Hochreiter e Schmidhuber em 1997, introduziu “portões” que regulam o que lembrar e o que descartar — uma melhoria enorme, sem dúvida. Mas a LSTM ainda processa um token de cada vez, o que impede paralelização e mantém um limite prático de memória. Em textos longos, o começo da frase já é neblina quando o modelo chega ao final.

## Seq2seq e a semente da atenção

O paradigma seq2seq, consolidado por Sutskever e por Cho em 2014, separou o problema em duas redes distintas:

```
entrada  →  ENCODER (lê tudo)  →  vetor de contexto  →  DECODER (escreve)  →  saída
```

A arquitetura é elegante, mas esconde um gargalo severo: todo o significado da entrada precisa caber em um único vetor no final do encoder. Uma frase de cinquenta palavras, com todas as suas nuances, reduzida a um ponto no espaço. A resposta veio em 2015, com Bahdanau e colaboradores: em vez de espremer tudo em um vetor, o decoder pode *olhar de volta* para partes relevantes da entrada, ponderando cada posição por relevância.

```
decoder ao escrever "azul"  →
    consulta: "qual posição da entrada é mais relevante?"
    resposta: a palavra "céu" (alto peso), "a" (peso baixo)
```

Essa ideia — relevância como pesos sobre posições — é a semente de tudo o que vem a seguir. Em 2016, o Google NMT levou seq2seq com atenção para produção e derrotou a tradução estatística que dominava havia uma década. Parecia o auge. Mas não era.

## O que ainda faltava em 2016

Apesar do entusiasmo, as melhores arquiteturas de 2016 continuavam sendo recorrentes no coração, e três limitações estruturais permaneciam abertas como feridas. Primeiro, a *paralelização*: RNNs processam token a token, sequencialmente, e não há como acelerar toda a sequência de uma vez — o que, na era dos GPUs e dos clusters massivos, era um desperdício doloroso. Segundo, a *memória de longo alcance*: mesmo a LSTM tem um limite prático em dependências muito distantes, e textos reais são cheios de referências cruzadas que atravessam parágrafos inteiros. Terceiro, a *unificação*: cada tarefa exigia arquitetura e treinamento próprios; não havia um caminho comum de “pré-treinar uma vez e reutilizar para tudo”.

O Transformer, que ocupará o capítulo seguinte, foi a resposta a essas três limitações de uma só vez. Mas vale notar o que ele *não* inventou: a ideia de embedding veio da era neural, a estrutura de atenção veio de Bahdanau, e o objetivo de prever a próxima palavra veio da era estatística. Revoluções raramente começam do zero — elas arrombam portas que outros já haviam destrancado.

## A lição estrutural

A pré-história deixa a lição mais antiga deste livro, e ela se repetirá em cada era: **o que permanece não é a técnica, é a representação que generaliza**. As regras de Georgetown morreram por não escalar; as contagens dos n-gramas, por não generalizar para o que nunca foi visto; o word2vec, por fixar cada palavra a um único ponto; e as RNNs, por comprimirem o passado em um estado que a memória perdia. Cada resposta resolveu um pedaço do problema e entregou o resto para a próxima. O fio que liga 1950 a 2016 é o mesmo que atravessará o livro inteiro: **a capacidade não está na regra escrita, mas no processo que a aprende** — e o processo que aprende com uma situação transfere para as outras. Essa é a diferença entre memorizar e generalizar, e é ela que o capítulo seguinte transforma em máquina.

## Para o engenheiro

Se você está do lado da engenharia, há três lições que essa pré-história deixa gravadas. Não tente varrer combinações de n-gramas: a maldição da dimensionalidade garante que você vai esbarrar em dados que nunca viu; prefira representações aprendidas, que generalizam por similaridade. Embeddings são o pré-requisito de todo sistema de busca semântica — é neles que “gato” e “felino” passam a ser vizinhos — e testar a qualidade do embedding antes de otimizar o índice economiza semanas de dor. E, para sequências longas, fique atento ao caminho entre tokens distantes: arquiteturas com passo curto, como atenção ou convolução, capturam dependências de longo alcance muito melhor do que recorrência. A atenção de Bahdanau, aliás, é o molde mental de retrieval: pesos por posição dizem onde olhar. A mesma ideia reaparece em cross-attention, em RAG, em praticamente tudo que este livro vai construir daqui para frente.

---

**Fontes:** [Turing, 1950] — teste de conversação; [Bengio et al., 2003] — primeiro modelo neural de linguagem; [Mikolov et al., 2013] — word2vec/embeddings; [Hochreiter & Schmidhuber, 1997] — LSTM; [Sutskever et al., 2014] — seq2seq; [Cho et al., 2014] — seq2seq/GRU; [Bahdanau et al., 2015] — atenção; [Wu et al., 2016] — Google NMT. Visão geral histórica: [Wikipedia, Transformer]; [Springer, 2025]; [MDPI, 2023].
