# Capítulo 4 — Escala e emergência: GPT-3 e as leis de escala (2020–2022)

Se a previsão da próxima palavra ensina a máquina a estruturar a linguagem, o que ocorre quando expandimos massivamente essa capacidade? Em 2020, a comunidade de inteligência artificial decidiu testar essa hipótese em larga escala. O GPT-3 não introduziu uma nova arquitetura; ele aplicou a estrutura do Transformer a um volume de dados e parâmetros em uma escala até então inexplorada. O resultado confirmou uma suspeita crescente: a tarefa podia ser comunicada ao modelo por meio do próprio contexto, dispensando novas fases de treinamento. Paralelamente, a formulação das leis de escala transformou o aumento de modelos de uma aposta empírica em uma ciência previsível. Contudo, o fenômeno mais notável desse período foi o aparecimento de capacidades que não haviam sido explicitamente programadas — como aritmética e raciocínio lógico —, um processo que a literatura passou a chamar de emergência. Este capítulo examina como a escala redefiniu o treinamento de modelos e quais limitações estruturais permaneceram, criando a necessidade das técnicas que dominariam os anos seguintes.

## A matemática da escala

Até 2020, aumentar o tamanho de um modelo era uma decisão baseada em intuição e disponibilidade de hardware. O trabalho de Kaplan e colaboradores mudou esse panorama ao demonstrar que o desempenho de modelos de linguagem segue leis de potência. O erro de previsão diminui de forma previsível à medida que se aumentam três variáveis: o número de parâmetros, o volume de dados e a capacidade computacional.

Matematicamente, a perda (erro) em relação ao número de parâmetros $N$ pode ser aproximada por:

```text
L(N) ≈ (N_c / N)^α_N        com  α_N ≈ 0,076
```

Em um gráfico em escala logarítmica, essa relação se manifesta como uma linha reta. Cada multiplicação por dez no tamanho do modelo reduz o erro por um fator constante. A mesma regularidade se aplica ao tamanho do conjunto de dados ($D$) e à computação total ($C$). Essa descoberta teve um impacto imediato na indústria: se o retorno do investimento em computação é previsível, o treinamento de modelos gigantes deixa de ser um experimento e passa a ser uma estratégia de engenharia.

Dois anos depois, o projeto Chinchilla (Hoffmann et al., 2022) refinou essa compreensão. A pesquisa mostrou que os modelos anteriores, incluindo o GPT-3, eram grandes demais para a quantidade de dados em que haviam sido treinados. Para um orçamento computacional fixo, existe uma proporção ótima entre parâmetros e tokens. A regra prática que emergiu desse estudo — escalar modelo e dados na mesma proporção — ditou o desenho das gerações seguintes, priorizando a curadoria de dados de alta qualidade em vez de apenas empilhar mais parâmetros.

## GPT-3 e a tarefa como contexto

O GPT-3 (Brown et al., 2020) manteve a arquitetura *decoder-only* do GPT-2, mas expandiu suas dimensões para 175 bilhões de parâmetros, distribuídos em 96 camadas, com uma janela de contexto de 2048 tokens. A mudança fundamental, no entanto, não foi estrutural, mas operacional. O modelo demonstrou que a adaptação a novas tarefas não exigia mais o ajuste fino (*fine-tuning*) dos pesos da rede.

```text
Antes (fine-tuning):   dados da tarefa → treinar mais → modelo especializado
GPT-3 (in-context):    prompt com instrução + exemplos → resposta
```

Esse paradigma, chamado de aprendizado em contexto (*in-context learning*), significa que o modelo congela seus pesos após o pré-treino. A “programação” da tarefa ocorre inteiramente na janela de contexto. Um *prompt* com alguns exemplos (*few-shot*) é suficiente para alinhar o comportamento do modelo:

```text
"Traduza do inglês para o português.
dog → cachorro
cat → gato
house → ..."        → o modelo responde "casa"
```

Para sustentar um modelo dessa magnitude, foi necessário compor o maior *corpus* textual da época, totalizando cerca de 499 bilhões de tokens. A composição dessa base de dados revela uma decisão de engenharia crucial: a filtragem.

| Fonte | Participação | Tokens (~) |
| --- | --- | --- |
| CommonCrawl (filtrado) | 60% | 410B |
| WebText2 | 22% | 19B |
| Books1 | 8% | 12B |
| Books2 | 8% | 55B |
| Wikipedia | 3% | 3B |

A tabela ilustra que o conhecimento do modelo é um reflexo direto de sua dieta textual. O CommonCrawl bruto contém dezenas de terabytes de ruído; o investimento em filtros de qualidade foi o que permitiu extrair sinal desse volume. O conhecimento, uma vez consolidado nos pesos, torna-se estático — uma limitação que exigiria soluções externas, como a busca semântica (RAG), nos capítulos seguintes.

## Capacidades emergentes

À medida que os modelos cruzavam a casa das centenas de bilhões de parâmetros, pesquisadores começaram a documentar um padrão recorrente: certas tarefas apresentavam desempenho medíocre em modelos pequenos, mas sofriam saltos abruptos de precisão a partir de um limiar crítico de escala. Wei e colaboradores (2022) catalogaram esse fenômeno sob o termo “capacidades emergentes”.

Exemplos notáveis incluíam operações aritméticas de múltiplos dígitos, raciocínio lógico encadeado e tradução entre idiomas com poucos recursos. Uma leitura técnica desse fenômeno revela que a emergência é, em grande parte, uma propriedade das métricas de avaliação. Quando uma métrica exige uma sequência exata de passos (como a resposta final de uma equação), o modelo parece “aprender de repente” a resolver o problema, embora a probabilidade interna de acerto venha crescendo de forma contínua com a escala.

Independentemente da interpretação, a implicação prática era clara: a escala por si só não garantia confiabilidade. Mesmo com 175 bilhões de parâmetros, o GPT-3 continuava a fabricar fatos (alucinações), falhar em cálculos básicos e operar com conhecimento congelado na data de seu treinamento. A escala resolvia a fluência e a capacidade de seguir instruções complexas, mas deixava abertas as lacunas de precisão factual e execução lógica.

## A infraestrutura que sustentou a escala

Treinar e operar modelos dessa magnitude exigiu avanços paralelos em sistemas distribuídos. A memória de uma única GPU não era suficiente para armazenar os pesos de um modelo de 175 bilhões de parâmetros, muito menos processar suas matrizes de atenção.

A pesquisa em infraestrutura respondeu com técnicas de paralelismo de modelo (como o Megatron-LM, que divide as camadas e a atenção entre diferentes dispositivos), otimizadores de memória e, posteriormente, algoritmos de atenção eficiente (como o FlashAttention), que reduziram drasticamente o custo de leitura e escrita na memória da GPU. Modelos esparsos (*Mixture of Experts* - MoE) e conjuntos de dados abertos e curados (como o *The Pile*) também se tornaram padrões da indústria. A história dos modelos de linguagem é indissociável da história do hardware e dos sistemas que os tornam viáveis.

## O que a escala deixou de herança

O período entre 2020 e 2022 consolidou três pilares que sustentam a engenharia de LLMs atual. Primeiro, a noção de que o contexto funciona como uma linguagem de programação: a tarefa é descrita, não treinada. Segundo, a escala como um vetor de melhoria contínua e previsível, desde que acompanhada de dados de qualidade. Terceiro, o mapeamento claro das limitações estruturais dos modelos puramente generativos.

## A lição estrutural

A era da escala deixou duas heranças que o livro inteiro carrega. A primeira: **escala é previsível quando se conhece a curva** — Kaplan e Chinchilla transformaram “aumentar o modelo” de aposta em engenharia, com custo estimável e retorno calculável. A segunda é a contraparte: **capacidade não é confiabilidade** — o GPT-3 falava com fluência e errava com confiança, e nenhum ponto da curva corrigia isso. As lacunas que a escala deixou em aberto — conhecimento desatualizado, alucinação, cálculo inexato — não foram resolvidas por mais parâmetros; foram resolvidas por *camadas*: recuperação, ferramentas, verificação. O resto do livro é a história dessas camadas. E a pergunta que a escala ensinou a fazer — “qual é o próximo eixo de melhoria além dos parâmetros?” — é a mesma que RAG e tool use responderam: o eixo deixou de ser o modelo e passou a ser o sistema.

## Para o engenheiro

Se você está projetando sistemas sobre essas fundações, algumas diretrizes práticas se destacam. As leis de escala devem orientar o orçamento: os dados de Kaplan e Chinchilla permitem estimar o custo computacional necessário para atingir um determinado nível de erro, substituindo o palpite por planejamento. O *prompt* deve ser tratado como código de produção — versionado, testado e documentado, pois é ele que define o comportamento do modelo em tempo de execução.

Por fim, é preciso manter o ceticismo em relação a *benchmarks*. Nem toda capacidade “emergente” se traduz em utilidade prática, e métricas saturadas costumam esconder falhas sistêmicas. As lacunas identificadas no GPT-3 — conhecimento desatualizado, alucinação e incapacidade de cálculo exato — não foram resolvidas por mais escala. Elas exigiram a criação de novas camadas arquiteturais. O modelo base aprendeu a falar e a raciocinar; caberia às técnicas de recuperação (RAG) e uso de ferramentas (*tool use*) ensiná-lo a consultar o mundo real e a executar ações.

---

**Fontes:** [Kaplan et al., 2020] — leis de escala; [Brown et al., 2020] — GPT-3; [Hoffmann et al., 2022] — Chinchilla (escala ótima); [Wei et al., 2022] — capacidades emergentes; [Zhao et al., 2023] — survey de LLMs.
