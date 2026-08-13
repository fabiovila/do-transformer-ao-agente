# Capítulo 6 — RAG clássico: Lewis et al. (2020) e as primeiras arquiteturas

Até o capítulo anterior, a comunidade havia resolvido uma parte crucial do problema: como encontrar a informação certa em um mar de dados. Mas recuperar a evidência é apenas a metade do caminho. A pergunta seguinte, e talvez a mais importante para a viabilidade dos modelos de linguagem em ambientes reais, era como fazer o modelo usar de fato o que foi recuperado. Em 2020, o artigo de Lewis e colaboradores propôs uma mudança de perspectiva: em vez de tratar a recuperação como um acessório que apenas “cola” passagens no prompt, o sistema inteiro — *retriever* e gerador — deveria ser treinado de ponta a ponta. A ambição era criar um modelo que aprendesse a trabalhar com a evidência externa, melhorando a busca não por uma métrica isolada de relevância, mas pelo que o gerador realmente precisava para formular uma resposta. Esse marco estabeleceu o RAG (*Retrieval-Augmented Generation*) clássico e trouxe à tona uma distinção intelectual que definirá a década: recuperar informação não é o mesmo que raciocinar sobre ela.

## A arquitetura básica e o treinamento de ponta a ponta

A arquitetura proposta por Lewis et al. combinava duas linhagens que vínhamos acompanhando: um *retriever* denso, baseado no DPR, e um gerador sequencial, no caso o BART (um modelo *encoder-decoder*). O fluxo básico seguia uma lógica direta: a pergunta aciona o *retriever*, que seleciona as passagens mais prováveis; essas passagens são concatenadas à pergunta e entregues ao gerador, que produz a resposta final.

```text
pergunta
   │
   ▼
retriever (baseado em DPR)
   │  top-k passagens
   ▼
concatena [pergunta + passagens]
   │
   ▼
generator (BART)  ──► resposta
```

O artigo introduziu duas variantes para lidar com a incerteza sobre qual dos documentos recuperados continha a resposta correta. No RAG-Sequence, o gerador consome as $k$ passagens e produz a sequência de tokens mais provável considerando o conjunto. No RAG-Token, o modelo tem a flexibilidade de reponderar a importância de cada passagem a cada novo token gerado.

A matemática do RAG expressa essa marginalização sobre as passagens recuperadas $z$. As duas variantes diferem essencialmente em que ponto do processo a soma das probabilidades ocorre:

```text
RAG-Sequence:  p(y | x) = Σ_{z ∈ top-k}  p(z | x) · p(y | x, z)
RAG-Token:     p(y | x) = Π_t Σ_{z ∈ top-k}  p(z | x) · p(y_t | x, z, y_{<t})
```

Na prática, somar sobre todos os documentos de um índice é inviável, então a operação se restringe ao top-$k$ recuperado (no artigo original, $k = 5$). É nesse espaço restrito que o *retriever* denso atua. No RAG-Token, o modelo pode alternar suas “fontes” de informação a cada palavra; no RAG-Sequence, ele implicitamente escolhe um documento e gera a resposta inteira condicionada a ele.

Em código, o pipeline mínimo que captura a essência dessa arquitetura é direto:

```python
def rag(pergunta, retriever, gerador, k=5):
    docs = retriever(pergunta, k)                    # 1. recuperar evidências
    ctx = "\n".join(f"[{i}] {d}" for i, d in enumerate(docs))
    prompt = f"Com base apenas no contexto:\n{ctx}\n\nPergunta: {pergunta}"
    resposta = gerador(prompt)                       # 2. gerar condicionado à evidência
    return resposta, docs                            # 3. devolver proveniência
```

O sistema foi avaliado em *benchmarks* de perguntas e respostas de domínio aberto, como Natural Questions, TriviaQA e WebQuestions. No Natural Questions, o RAG-Sequence alcançou uma métrica de *Exact Match* (EM) de aproximadamente 44,5, superando modelos dedicados à tarefa com muito mais parâmetros, como o T5-SSM. Treinar *retriever* e gerador juntos permitiu que a busca se adaptasse às necessidades reais da geração, plantando a semente do alinhamento entre recuperação e tarefa final.

## A fronteira entre recuperação e raciocínio

Apesar do sucesso empírico, o RAG clássico esbarrava em uma limitação conceitual profunda. Recuperar os documentos corretos não equivale a formular uma resposta. Para ilustrar isso, considere o seguinte cenário:

```text
Documento A: Pedro comprou X em janeiro.
Documento B: Compras acima de R$ 1.000 recebem desconto.
Documento C: Pedro pagou R$ 1.200 por X.

Pergunta: Pedro recebeu desconto?
```

Responder a essa pergunta exige recuperar A (para identificar a compra), C (para saber o valor) e B (para conhecer a regra). Mas a resposta em si não está em nenhum dos textos; ela emerge da inferência lógica de que R$ 1.200 é maior que R$ 1.000. Um sistema RAG completo precisa, portanto, lidar com dois problemas distintos: a aquisição da evidência e o raciocínio sobre ela.

Essa distinção ajuda a organizar o fluxo de um sistema baseado em evidências:

```text
query
  ↓
evidence acquisition  → recuperar candidatos
  ↓
evidence organization → selecionar/ordenar o que entra no contexto
  ↓
evidence reasoning    → concluir a partir das evidências
  ↓
answer
```

Ao projetar ou depurar um pipeline, as perguntas fundamentais deixam de ser apenas sobre a precisão do banco vetorial e passam a questionar a inferência: qual afirmação estou tentando sustentar? A evidência recuperada a suporta de forma dedutiva, indutiva ou apenas plausível? Existe informação contraditória no contexto? Estou extrapolando além do que os documentos permitem?

## Variações estruturais: FiD e RETRO

### FiD: a fusão que acontece no decoder

O gargalo que o RAG clássico deixava exposto estava no ponto de entrada da evidência: concatenar muitas passagens em uma única sequência sobrecarregava o encoder, que precisava construir uma representação conjunta de tudo ao mesmo tempo, e o custo da self-attention crescia com o quadrado do comprimento total. O FiD — *Fusion-in-Decoder*, proposto por Gautier Izacard e Edouard Grave, do Facebook AI Research, e publicado no EACL 2021 [Izacard & Grave, 2021] — inverteu esse desenho. A ideia é simples de enunciar e profunda nas consequências: cada passagem é codificada **separadamente**, junto com a pergunta, e a fusão só acontece no decoder, que aplica atenção cruzada sobre a concatenação de todas as representações codificadas.

```text
pergunta + passagem 1 ──► encoder ──► E1 ─┐
pergunta + passagem 2 ──► encoder ──► E2 ──┼──► decoder ──► resposta
        ⋮                                │   (cross-attention
pergunta + passagem k ──► encoder ──► Ek ─    sobre E1..Ek)
```

Por que esse detalhe arquitetural importa? Porque, ao codificar as passagens de forma independente, o custo do encoder passa a crescer **linearmente** com o número de passagens, em vez de quadraticamente, como ocorreria se tudo fosse concatenado em uma única sequência. A separação no encoder é o que compra escala; a fusão no decoder é o que compra raciocínio conjunto — o decoder continua enxergando todas as passagens de uma vez e pode cruzá-las entre si ao gerar a resposta.

Os resultados quantificam o ganho. Usando T5 como gerador e DPR como retriever, o FiD-large com 100 passagens recuperadas atinge cerca de 51,4 de *Exact Match* no Natural Questions e 67,6 no TriviaQA, superando o RAG-Sequence em condições comparáveis [Izacard & Grave, 2021]. As ablações do artigo mostram dois comportamentos que viraram referência para a área: o desempenho cresce de forma consistente à medida que o número de passagens aumenta (de 10 para 100), e os modelos maiores extraem mais valor de cada passagem adicional — ou seja, a capacidade de aproveitar evidência também escala com o tamanho do modelo. Outro ponto prático: o FiD funciona até com recuperação lexical (BM25), embora o retrieval denso produza resultados melhores, o que torna a arquitetura tolerante à qualidade do retriever.

Vale registrar ainda o trabalho anterior da mesma dupla, *Distilling Knowledge from Reader to Retriever* (2020), em que o “leitor” (o modelo que processa as passagens) é usado para ensinar o retriever a recuperar melhor. É a destilação reader→retriever, um germe direto da ideia de alinhar a recuperação à tarefa final — a mesma linhagem que reaparecerá em Self-RAG e RAFT nos capítulos seguintes. A lição estrutural do FiD para o engenheiro é que **onde** a evidência é fundida no modelo é uma decisão de projeto com impacto direto sobre quanta evidência o sistema comporta — e o decoder provou ser um ponto de fusão mais escalável que o prompt ou o encoder.

### RETRO: memória externa como eixo de escala

Se o FiD moveu o ponto de fusão, o RETRO — *Retrieval-Enhanced Transformer*, da DeepMind (Borgeaud et al., 2022) — moveu o ponto do ciclo de vida: a recuperação deixa de ser um módulo acrescentado na inferência e passa a fazer parte da arquitetura desde o pré-treino. O modelo consulta uma base de cerca de **2 trilhões de tokens**, construída a partir do corpus MassiveText e dividida em trechos de 64 tokens. O mecanismo funciona em três peças: um retriever BERT **congelado**, que busca no índice os trechos mais similares ao chunk atual da entrada (os dois vizinhos mais próximos, pela similaridade local com os tokens precedentes); um **encoder diferenciável**, treinado junto com o modelo, que representa os trechos recuperados; e um mecanismo de **chunked cross-attention**, intercalado com as camadas comuns de self-attention, que permite ao modelo condicionar cada previsão aos vizinhos recuperados [Borgeaud et al., 2022].

```text
entrada dividida em chunks de 64 tokens
   │  para cada chunk: retriever BERT congelado busca
   │  os 2 vizinhos mais próximos no índice (2T tokens)
   ▼
camadas Transformer padrão (self-attention)
   │  (intercaladas)
   ▼
chunked cross-attention sobre os vizinhos codificados
   ▼
previsão do próximo token
```

O resultado que definiu o artigo: com **7,5 bilhões de parâmetros**, o RETRO atinge no benchmark The Pile uma perplexidade comparável à do GPT-3 (175B) e à do Jurassic-1, usando 25 vezes menos parâmetros [Borgeaud et al., 2022]. Em avaliações por dataset, o modelo de 7,5B supera o Jurassic-1 (175B) em 10 de 16 conjuntos e o Gopher (280B) em 9 de 16 [Borgeaud et al., 2022]. Após fine-tuning, os ganhos se transferem para tarefas de conhecimento intensivo, como perguntas e respostas. E há um detalhe operacional relevante: os autores mostram que é possível fazer *RETROfit* — acrescentar recuperação a um Transformer já pré-treinado, sem treinar do zero, e ainda assim obter bom desempenho — o que sugere que a memória externa pode ser acoplada a modelos existentes.

Talvez o dado mais importante do paper seja a curva de escala da própria memória: a perplexidade melhora de forma contínua à medida que a base de recuperação cresce, pelo menos até os 2 trilhões de tokens [Borgeaud et al., 2022]. Isso transforma a memória externa em um eixo de escala próprio, paralelo ao eixo dos parâmetros e ao eixo dos dados das leis de Kaplan e Chinchilla do capítulo 4. É a confirmação empírica da tese que o REALM havia plantado em 2020: quando a recuperação é integrada à arquitetura desde o início, ela funciona como um multiplicador de capacidade — um modelo menor, apoiado em um índice grande, compete com modelos muito maiores que precisam guardar tudo nos pesos.

As limitações também são instrutivas. O retriever é congelado e busca por similaridade local, não por relevância à tarefa — o alinhamento entre recuperação e objetivo final fica para trabalhos posteriores. E o modelo pode reproduzir trechos recuperados quase literalmente, uma questão de memorização e privacidade que o próprio artigo discute. Ainda assim, o RETRO fecha o arco iniciado por REALM e kNN-LM em 2020: a memória não-paramétrica deixou de ser um acessório de inferência para se tornar parte da definição do modelo.

## O vocabulário que permanece

À medida que essas arquiteturas se consolidavam, um vocabulário comum passou a organizar o campo:

| Termo | Significado |
| --- | --- |
| retriever | componente que seleciona passagens de uma fonte externa |
| generator | LLM que produz a resposta a partir de pergunta + passagens |
| top-k | número de passagens recuperadas |
| grounding | ancorar a resposta em evidência externa (reduz alucinação) |
| proveniência | capacidade de citar a fonte da informação |

Contudo, o próprio artigo fundador de 2020 já deixava transparecer os limites da abordagem. A qualidade do *retriever* atua como um teto para o sistema: se a evidência não é recuperada, o gerador não tem como inventá-la de forma confiável. Além disso, selecionar o que é relevante em meio a documentos ruidosos ou contraditórios continua sendo um desafio aberto, exigindo camadas adicionais de filtragem e reordenação que evoluiriam nos anos seguintes.

## A lição estrutural

Lidos em sequência, RAG, FiD e RETRO formam uma progressão clara sobre **onde e quando** a informação externa entra no modelo — e essa progressão é um bom mapa mental para decisões de engenharia:

| | RAG (2020) | FiD (2021) | RETRO (2022) |
| --- | --- | --- | --- |
| Quando a recuperação entra | inferência (prompt) | inferência (decoder) | pré-treino + inferência |
| Onde a evidência é fundida | concatenação no contexto/encoder | cross-attention no decoder | chunked cross-attention |
| Volume de evidência | k = 5 passagens | até 100 passagens | 2 vizinhos por chunk; índice de 2T tokens |
| Retriever treinado junto? | sim (ponta a ponta) | não (DPR/BM25 congelado) | não (BERT congelado) |
| Resultado de referência | EM ≈ 44,5 (NQ) | EM ≈ 51,4 (NQ) | perplexidade comparável à do GPT-3 com 25× menos parâmetros |

A leitura da tabela sugere duas regras práticas. Primeira: quanto mais tarde a fusão acontece (decoder em vez de prompt), mais evidência o sistema comporta sem degradar a representação. Segunda: quanto mais cedo a recuperação entra no ciclo de vida (pré-treino em vez de inferência), mais a memória externa se comporta como capacidade adicional do modelo — ao custo de perder o treinamento conjunto do retriever, que só a linhagem RAG preservava. Essas duas tensões — ponto de fusão versus volume de evidência, e integração precoce versus alinhamento do retriever — organizarão a evolução do RAG avançado no capítulo 12.

## Para o engenheiro

Para a engenharia de sistemas, o RAG clássico deixa diretrizes práticas que permanecem atuais. A primeira é a defesa do pipeline mínimo: comece recuperando o top-$k$, concatenando no prompt e gerando a resposta. A maioria dos casos de uso iniciais funciona bem com essa abordagem, e a complexidade só deve ser adicionada quando as métricas de avaliação exigirem.

A segunda diretriz é a avaliação modular. É um erro medir o sistema apenas por uma métrica final agregada. O *recall@k* mede a eficácia do *retriever*; a fidelidade (se a resposta gerada respeita as evidências fornecidas) mede o gerador. Separar essas métricas é a única forma de identificar onde está o gargalo real.

Por fim, é preciso reconhecer as limitações operacionais. Manter um índice vetorial atualizado tem custo; a busca adiciona latência; e lidar com evidências contraditórias exige lógica de reordenação (*reranking*). Projetar caches e mecanismos de *reranking* desde o início não é superengenharia, mas uma necessidade para sistemas em produção. Quando o volume de evidências excede a janela de contexto do prompt, arquiteturas como o FiD, que fundem a informação no *decoder*, tornam-se a saída natural.

---

**Fontes:** [Lewis et al., 2020] — RAG clássico; [Karpukhin et al., 2020] — DPR; [Izacard & Grave, 2021] — FiD; [Borgeaud et al., 2022] — RETRO; [Gao et al., 2023] — survey RAG.
