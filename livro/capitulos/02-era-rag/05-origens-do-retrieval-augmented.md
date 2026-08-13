# Capítulo 5 — As origens do Retrieval-Augmented (2020): a memória fora dos pesos

A escala dos modelos de linguagem em 2020 trouxe capacidades inéditas, mas também deixou claras certas barreiras estruturais. O modelo sabia apenas o que havia visto durante o treinamento e, quando a informação lhe faltava, tendia a fabricar respostas com alta confiança. Além disso, seu conhecimento era estático: atualizar um fato ou corrigir um erro exigia retreinar a rede inteira, um processo inviável para bases que mudam diariamente. A questão que se impôs naquele ano foi direta: e se parássemos de tentar comprimir todo o conhecimento do mundo nos parâmetros da rede e, em vez disso, buscássemos a informação no momento exato em que ela fosse necessária?

A recuperação de informação (*Information Retrieval*) era uma disciplina consolidada desde a década de 1970. A novidade estava em integrá-la a modelos generativos modernos por meio de representações neurais. Esse foi o ponto de inflexão que deu origem a sistemas como DPR, REALM, kNN-LM e, por fim, ao próprio RAG. A premissa central era simples, porém transformadora: nem todo conhecimento precisa caber nos parâmetros da rede. Recuperar a evidência certa, na hora certa, funciona como uma forma de memória externa — atualizável, verificável e computacionalmente barata.

## Memória paramétrica e não-paramétrica

Para entender essa mudança de arquitetura, é preciso separar dois tipos de memória que frequentemente são confundidos. A memória paramétrica é o conhecimento consolidado nos pesos do modelo após o treinamento. A memória não-paramétrica, por sua vez, reside fora do modelo, em índices, bancos de dados ou arquivos. O modelo de linguagem mantém sua memória paramétrica para lidar com gramática, raciocínio e conhecimento geral, enquanto a memória externa fornece o contexto específico, recente ou verificável.

| Memória Paramétrica | Memória Não-Paramétrica (Externa) |
| --- | --- |
| Conhecida nos pesos da rede | Armazenada fora (índice, banco, arquivos) |
| Fixa após o treinamento | Atualizável a qualquer momento |
| Comprimida durante o treino | Recuperada sob demanda |
| Difícil de rastrear a origem | Rastreável (permite citar a fonte) |

A arquitetura de *Retrieval-Augmented Generation* (RAG) atua exatamente como a ponte entre esses dois mundos: recuperar a evidência, inseri-la no contexto e, então, gerar a resposta.

## A base lexical: o padrão BM25

Antes das representações neurais, o padrão da indústria para recuperação era lexical. O algoritmo BM25, desenvolvido na década de 1990, pontua documentos com base na sobreposição de termos com a consulta, ponderando a raridade da palavra e o tamanho do texto. A fórmula para uma consulta com termos $t$ e um documento $d$ é:

```text
score(q, d) = Σ_{t ∈ q}  IDF(t) · [ f(t,d)·(k₁+1) / (f(t,d) + k₁·(1 − b + b·|d|/avgdl)) ]
```

A lógica é prática: termos mais raros no corpus geral (IDF) valem mais; quanto mais vezes o termo aparece no documento ($f(t,d)$), maior a pontuação, mas com retornos decrescentes (controlados por $k_1$) para evitar que textos excessivamente longos dominem os resultados apenas por seu tamanho. O fator $b$ penaliza documentos muito longos em relação à média do corpus ($avgdl$).

O BM25 funciona muito bem para correspondências literais, mas esbarra em limitações semânticas. Se um usuário pergunta “quanto custa o gato” e o documento diz “preço do felino”, a busca lexical falha. Essa lacuna motivou a transição para o *retrieval* denso, onde consultas e documentos passam a ser representados como vetores, permitindo a busca por proximidade de significado.

## DPR: o retriever denso

Em 2020, Karpukhin e colaboradores apresentaram o *Dense Passage Retrieval* (DPR), um marco na consolidação da busca semântica. O modelo treina dois *encoders* distintos: um para a consulta e outro para o documento. Ambos projetam o texto em um espaço vetorial compartilhado, e a recuperação ocorre ao buscar os documentos cujos vetores estão mais próximos do vetor da consulta.

```text
consulta  ──► encoder_q ──► [0.3, 0.8, ...]      ┐
                                                 │ similaridade (cosseno/produto escalar)
docs (índice) ─► encoder_d ──► [0.2, 0.7, ...]  ┘ → top-k passagens
```

A métrica padrão para essa proximidade é a similaridade de cosseno, que mede o ângulo entre dois vetores, independentemente de suas magnitudes:

```text
cos(u, v) = (u · v) / (‖u‖ · ‖v‖)
```

Na prática, o código para selecionar os melhores candidatos é direto:

```python
import numpy as np

def top_k(consulta, docs, k=3):
    q = consulta / np.linalg.norm(consulta)
    sims = [np.dot(q, d / np.linalg.norm(d)) for d in docs]
    return np.argsort(sims)[::-1][:k]  # índices dos k mais similares
```

O DPR foi treinado e avaliado em conjuntos de perguntas e respostas de domínio aberto, como *Natural Questions* (perguntas reais de usuários do Google sobre páginas da Wikipedia) e *TriviaQA*. O índice utilizado na época era a Wikipedia inteira, com cerca de 21 milhões de passagens — uma escala que ainda serve como base para muitos sistemas RAG em produção hoje.

## REALM e kNN-LM: integrações alternativas

Paralelamente ao DPR, outras abordagens exploraram como a recuperação poderia se integrar ao ciclo de vida do modelo. O REALM (Guu et al., 2020) propôs incluir a recuperação durante a fase de pré-treinamento. Em vez de adicionar a busca apenas na inferência, o modelo aprendia a consultar uma base externa para preencher tokens mascarados. A lição central foi que, quando o modelo aprende a recuperar desde a base, as capacidades de linguagem e de busca amadurecem juntas — uma ideia que seria retomada anos depois por arquiteturas como RETRO e RAFT.

Já o kNN-LM (Khandelwal et al., 2020) apresentou uma alternativa interessante ao atuar no nível do token. O sistema mantém um índice massivo de fragmentos de texto transformados em vetores. No momento de prever a próxima palavra, o modelo não confia apenas em seus próprios pesos; ele consulta os vizinhos mais próximos no índice e interpola as probabilidades. Funciona como um RAG aplicado a cada palavra gerada:

```text
P_final(w | contexto) = (1 − λ) · P_modelo(w | contexto) + λ · P_kNN(w | contexto)
```

No experimento original, o *datastore* continha mais de 100 milhões de chaves, e cada previsão consultava os $k=10$ vizinhos mais próximos, interpolados com peso $\lambda \approx 0,25$ à distribuição do modelo. O ponto conceitual aqui é que o tamanho da memória externa importa tanto quanto o tamanho do modelo: aumentar o índice reduzia a perplexidade sem a necessidade de retreinamento, antecipando o mesmo *trade-off* que rege o RAG atual.

## Além da busca vetorial simples

Com a popularização dessas técnicas, tornou-se comum resumir o RAG a um fluxo simplista: gerar *embeddings*, buscar os *top-k* resultados, injetar no *prompt* e obter a resposta. No entanto, sistemas em produção raramente se limitam a isso. A recuperação eficaz costuma envolver busca híbrida (combinando a precisão do BM25 com a semântica dos vetores), filtros de metadados, reordenação (*reranking*) dos resultados e até a decomposição de perguntas complexas em consultas menores. A questão de engenharia não é apenas qual banco vetorial utilizar, mas qual mecanismo de recuperação maximiza a evidência útil para a tarefa em questão.

Do ponto de vista da arquitetura de sistemas, o *retrieval* assume um papel fundamental: ele é a primeira forma de ferramenta que o modelo utiliza. A dinâmica de “consultar um índice, observar o resultado e decidir o próximo passo” estabelece o padrão de interação que será expandido no uso de ferramentas externas e na formação de agentes autônomos. O RAG atua, portanto, como a transição entre a era do modelo isolado e a era do agente conectado a fontes de dados externas.

## A lição estrutural

A lição desta era é a inversão do capítulo anterior: **nem todo conhecimento precisa caber nos pesos**. Separar memória paramétrica de memória não-paramétrica transformou o conhecimento de algo fixo em algo consultável — atualizável, rastreável e barato —, e o kNN-LM mostrou que a memória externa funciona até como eixo de escala próprio, competindo com os parâmetros. O capítulo deixa também a distinção que o livro inteiro vai repetir: **recuperar evidência não é raciocinar sobre ela** — o retriever é a primeira linha do sistema, não a última, e a resposta só é confiável quando a evidência certa chega e é interpretada. E há o germe do que virá: o padrão consultar-observar-decidir que o retrieval estabeleceu é exatamente o molde que as ferramentas dos capítulos 9 a 11 e os agentes da Parte VI vão generalizar.

## Para o engenheiro

Para quem projeta esses sistemas, algumas diretrizes práticas se destacam. A decisão arquitetural mais importante é definir onde o conhecimento deve residir: nos pesos, para estabilidade e rapidez, ou em um índice externo, para atualização constante e rastreabilidade.

Em produção, a busca híbrida costuma ser a escolha mais robusta, unindo a precisão lexical para termos técnicos ou nomes próprios à capacidade de paráfrase do *retrieval* denso. Além disso, ao implementar modelos de dois *encoders* como o DPR, é crucial garantir que o *encoder* usado para indexar os documentos seja exatamente o mesmo utilizado para processar as consultas em tempo de execução; caso contrário, os vetores não compartilharão o mesmo espaço geométrico.

Por fim, é preciso manter em mente uma distinção que acompanhará o resto do livro: recuperar evidência não é o mesmo que raciocinar sobre ela. O *retriever* é apenas a primeira linha de um pipeline que exigirá, nas etapas seguintes, a capacidade do modelo de sintetizar, filtrar e interpretar o que foi encontrado.

---

**Fontes:** [Karpukhin et al., 2020] — DPR; [Guu et al., 2020] — REALM; [Khandelwal et al., 2020] — kNN-LM; [Lewis et al., 2020] — RAG; [Gao et al., 2023] — survey RAG.
