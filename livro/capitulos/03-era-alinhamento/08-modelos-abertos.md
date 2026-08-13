# Capítulo 8 — Modelos abertos e a corrida (2023)

O capítulo anterior terminou com uma mudança importante: depois de pré-treinado e alinhado, o modelo havia se tornado produto. O ChatGPT colocou essa capacidade nas mãos de milhões de pessoas e, ao mesmo tempo, tornou visíveis limitações que apenas o alinhamento não resolvia. Havia, porém, outra questão em aberto: quem teria acesso ao modelo em si? Até 2023, o estado da arte estava concentrado em poucos laboratórios. Era possível usar seus modelos por produtos e APIs, mas não era possível, a partir de fora, trabalhar sobre os pesos com o mesmo grau de liberdade. A corrida ganhou então uma segunda dimensão: além de produzir modelos cada vez mais capazes, tornou-se estratégico decidir quem poderia modificar, executar e construir sobre esses modelos.

É nesse contexto que aparecem LLaMA, LLaMA 2, BLOOM e Mistral. Em paralelo, técnicas como LoRA tornaram a adaptação de grandes modelos muito mais barata. A questão dessa era não é apenas técnica; é também econômica e política: o que acontece quando os pesos de um modelo chegam às mãos da comunidade? A resposta foi uma multiplicação de experimentação. Pesquisadores passaram a fazer fine-tuning, testar alinhamento, construir derivações e combinar modelos com RAG e ferramentas. O custo de adaptar um modelo grande caiu, e a dependência de um único fornecedor diminuiu. Ao mesmo tempo, o GPT-4, lançado em março de 2023, mostrou que a fronteira de capacidade continuava concentrada no lado fechado. O resultado foi uma bifurcação: modelos abertos favoreceram experimentação, adaptação e controle; modelos fechados concentraram capacidade de ponta, produto e robustez. Essa bifurcação moldou a arquitetura dos sistemas que viriam depois.

Há ainda um terceiro efeito, menos visível no debate público, mas decisivo para engenharia: os modelos abertos também introduziram ou popularizaram escolhas arquiteturais que mudaram desempenho e inferência. Não se tratou apenas de “liberar pesos”. Tratou de tornar viável executar, adaptar e servir modelos fora dos laboratórios que os criaram. Janelas de contexto maiores, atenção mais eficiente, normalizações mais estáveis, ativações mais eficazes e arquiteturas esparsas alteraram o custo real de rodar esses sistemas. Em outras palavras, a abertura dos pesos veio acompanhada de uma mudança nas condições materiais de uso: inferência mais barata, adaptação mais simples e integração mais direta com RAG, ferramentas e agentes.

## Um ecossistema que deixou de ter um único centro

Em 2023, o campo começou a deixar de ser dominado exclusivamente por alguns poucos laboratórios. O LLaMA, lançado em fevereiro, abriu espaço para pesquisa com pesos disponíveis; o LLaMA 2, em julho, ampliou a possibilidade de adoção; Mistral e BLOOM ofereceram alternativas; e LoRA reduziu drasticamente o custo de adaptação. Em paralelo, o GPT-4 estabeleceu uma referência para os modelos fechados. A mudança, portanto, não foi apenas quantitativa — mais modelos, mais parâmetros ou mais capacidade. Ela alterou a estrutura do ecossistema.

Antes, a fronteira do modelo estava essencialmente dentro do laboratório que o treinava. Com pesos disponíveis, pesquisadores e engenheiros podiam partir de um modelo já treinado e modificar seu comportamento para uma finalidade específica. Isso criou uma nova dinâmica:

```text
modelo pré-treinado
        ↓
pesos disponíveis
        ↓
fine-tuning / alinhamento / adaptação
        ↓
modelos derivados e sistemas especializados
        ↓
RAG / ferramentas / agentes
```

O modelo deixou de ser apenas o produto final. Passou a ser também uma base sobre a qual outros sistemas poderiam ser construídos. Essa mudança é importante porque desloca parte da inovação do pré-treino para o pós-treino, para a adaptação e para a orquestração. Em termos práticos, o valor deixou de residir apenas no modelo isolado e passou a residir também no que se consegue montar ao redor dele.

## LLaMA: quando os pesos chegam à comunidade — e a arquitetura favorece o uso

O LLaMA, de Touvron et al. (2023), foi um ponto de inflexão porque combinou duas coisas ao mesmo tempo: qualidade elevada para o tamanho do modelo e disponibilidade de pesos para pesquisa. O efeito foi multiplicador. Com os pesos disponíveis, a comunidade pôde experimentar diretamente sobre o modelo: fazer fine-tuning, investigar alinhamento, testar aplicações e combiná-lo com outros componentes. O ponto importante não é apenas que pesquisadores passaram a ter acesso a um modelo. É que passaram a ter acesso à matéria-prima de novos modelos e sistemas. Isso altera a velocidade da experimentação. Em um modelo fechado, o usuário pode testar diferentes prompts ou utilizar as interfaces disponibilizadas pelo fornecedor. Com os pesos, o espaço de experimentação aumenta: o pesquisador pode modificar o próprio comportamento do modelo. Essa diferença explica parte da multiplicação de modelos derivados que marcou o período.

Do ponto de vista arquitetural, o LLaMA também ajudou a consolidar um conjunto de escolhas que favoreciam treinamento estável e inferência mais prática. A família original era composta por modelos decoder-only de 7B, 13B, 33B e 65B parâmetros, treinados com grandes volumes de dados — chegando a cerca de 1,4 trilhão de tokens nas versões maiores. A arquitetura usava normalização RMSNorm antes das camadas, ativação SwiGLU e embeddings posicionais rotacionais (RoPE), além de operar sem bias em várias camadas. Essas escolhas não são apenas detalhes de implementação: elas melhoram a estabilidade do treinamento e contribuem para que modelos menores alcancem qualidade competitiva.

Para inferência, isso teve consequência direta. Um modelo de 13B é muito mais fácil de servir do que um modelo de centenas de bilhões de parâmetros. Ele consome menos memória, admite quantização mais agressiva e pode rodar em infraestruturas menores. A abertura dos pesos acelerou esse processo: a comunidade desenvolveu runtimes, formatos compactos e ferramentas de serviço que tornaram viável executar versões do LLaMA fora de grandes clusters. Assim, o LLaMA não apenas democratizou o acesso aos pesos; também tornou mais realista a ideia de modelos abertos como componentes de sistemas locais ou privados.

## LLaMA 2/3: da pesquisa à adoção

O movimento avançou com LLaMA 2 e, posteriormente, LLaMA 3. O material deste capítulo destaca duas mudanças centrais: uma licença mais favorável à adoção e a existência de versões instruction-tuned. Isso favoreceu a passagem do modelo como objeto de pesquisa para o modelo como componente de produtos. A distinção é importante. Um modelo que serve apenas como objeto de pesquisa tem um papel diferente de um modelo que pode ser incorporado a sistemas reais. O instruction tuning também reforça a continuidade com o capítulo anterior: o modelo aberto não precisava permanecer apenas como um modelo pré-treinado. Ele podia receber a mesma camada de adaptação comportamental que havia transformado os modelos fechados em sistemas mais utilizáveis. A abertura dos pesos, portanto, não significava voltar ao modelo bruto; significava permitir que a comunidade construísse suas próprias versões e adaptações.

No plano arquitetural, essa transição também veio acompanhada de ganhos concretos. O LLaMA 2 ampliou a janela de contexto para 4096 tokens e foi treinado em um volume maior de dados. Nas versões maiores, adotou grouped-query attention (GQA), uma variante de atenção que reduz o tamanho do cache de chaves e valores durante a geração. Isso tem efeito direto em inferência: menos memória por sequência, maior throughput e melhor escalabilidade quando muitas requisições são atendidas simultaneamente. Para sistemas de produção, esse tipo de escolha importa tanto quanto a qualidade bruta do modelo, porque define o custo operacional de servir respostas longas ou concorrentes.

O LLaMA 3, lançado em seguida, aprofundou essa trajetória. As primeiras versões de 8B e 70B trouxeram janela de contexto maior, vocabulário ampliado, treinamento em volume de dados ainda mais alto e melhor qualidade em tarefas instruídas. A família consolidou o uso de RMSNorm, SwiGLU e RoPE, além de variantes de atenção mais eficientes em várias configurações. O efeito combinado foi aproximar modelos abertos de requisitos reais de produto: mais contexto para RAG, mais estabilidade para chat, menor custo de inferência por qualidade entregue e maior facilidade de adaptação. Em termos práticos, o modelo aberto deixou de ser apenas uma alternativa de pesquisa e passou a ser uma base plausível para sistemas em produção.

## Mistral e BLOOM: alternativas ao caminho dominante

LLaMA não foi a única alternativa. Mistral e BLOOM ampliaram o espaço de modelos abertos e contribuíram para a diversidade do ecossistema. Essa diversidade importa porque reduz a dependência de uma única família de modelos. Diferentes arquiteturas e diferentes escolhas de projeto podem ser comparadas, adaptadas e incorporadas a sistemas distintos. O ponto estrutural é simples: a abertura cria um espaço de experimentação entre diferentes modelos, e não apenas uma alternativa binária entre “usar o modelo dominante” e “treinar um modelo do zero”.

O Mistral 7B é um exemplo especialmente relevante dessa fase. Ele combinou escolhas arquiteturais voltadas a eficiência e contexto: atenção com janela deslizante, cache rolante, grouped-query attention, RMSNorm, SwiGLU e embeddings rotacionais. A janela deslizante permite controlar o custo de atenção em sequências longas, evitando que o crescimento do contexto produza aumento excessivo de memória e computação. Para inferência, isso significa que o modelo pode lidar com mais texto sem que o custo cresça da mesma forma que cresceriam abordagens mais simples. Na prática, essa escolha favorece sistemas que precisam de contextos longos, como RAG, análise de documentos e agentes que acumulam histórico.

A contribuição da Mistral, porém, não se limitou a modelos densos compactos. A família Mixtral popularizou o uso de mixture-of-experts (MoE) em modelos abertos. Em vez de ativar todos os parâmetros para cada token, o modelo possui vários especialistas e roteia apenas um subconjunto deles para cada passo de geração. Isso cria uma assimetria útil: o modelo pode ter muitos parâmetros totais, mas usa menos parâmetros ativos por token. O resultado é uma relação melhor entre qualidade e custo computacional. Em inferência, isso pode aumentar o throughput e reduzir o custo por resposta, embora introduza novos desafios de memória e complexidade de serving. Para engenharia, o MoE representa uma troca relevante: menos FLOPs ativos, mais memória total, maior exigência de infraestrutura e maior flexibilidade para escalar qualidade sem escalar proporcionalmente o custo de geração.

O BLOOM, embora lançado em 2022, integrou esse mesmo movimento de abertura em grande escala. Ele se destacou menos por inovações de eficiência de inferência e mais por demonstrar que um modelo de grande porte poderia ser desenvolvido de forma aberta, multilíngue e com governança distribuída. Do ponto de vista arquitetural, o BLOOM é um decoder-only de grande escala, com embeddings ALiBi, que favorecem generalização de comprimento sem depender exclusivamente de posições absolutas aprendidas. Sua importância histórica está mais na prova de que modelos grandes podem ser abertos, auditáveis e multilíngues do que em economia de inferência. Ainda assim, ele ajudou a ampliar o espaço de comparação arquitetural e a mostrar que não havia um único caminho para modelos abertos.

## Síntese das mudanças arquiteturais e de inferência

Para visualizar o que essas famílias acrescentaram ao ecossistema, vale reunir as principais escolhas arquiteturais e seus efeitos práticos:

| Família / técnica | Escolhas arquiteturais relevantes | Efeito em desempenho e inferência |
| --- | --- | --- |
| LLaMA | RMSNorm, SwiGLU, RoPE, modelos de 7B a 65B | Treinamento mais estável, modelos menores competitivos, inferência local mais viável |
| LLaMA 2 / LLaMA 3 | Mais dados, contexto maior, GQA, instruction tuning | Menor custo de KV cache, maior throughput, melhor adequação a produto |
| Mistral 7B | Sliding window attention, cache rolante, GQA | Contexto longo com custo controlado, inferência mais eficiente |
| Mixtral / MoE | Especialistas esparsos, roteamento top-k | Menos parâmetros ativos por token, maior throughput, maior exigência de memória |
| BLOOM | Modelo aberto multilíngue, ALiBi | Generalização de comprimento, abertura em grande escala, menor foco em eficiência de inferência |
| LoRA | Adaptadores de baixo posto sobre modelo-base | Adaptação barata, múltiplas especializações, serving multi-inquilino |

Essa tabela resume uma mudança importante: a corrida de 2023 não foi apenas sobre quem tinha o modelo mais capaz. Foi também sobre qual arquitetura tornava o modelo utilizável, adaptável e servível em condições reais. Desempenho deixou de ser apenas uma métrica de benchmark e passou a incluir latência, throughput, memória, custo de contexto e facilidade de adaptação.

## LoRA: adaptar sem recomeçar

A abertura dos pesos resolve um problema: permite modificar o modelo. Mas surge imediatamente outro: quanto custa modificar um modelo gigantesco? LoRA, de Hu et al. (2021), oferece uma resposta importante. Em vez de atualizar todos os parâmetros de um modelo durante o fine-tuning, a técnica adapta o modelo ajustando uma matriz de baixo posto. O resultado é uma redução drástica do custo de adaptação. A ideia pode ser representada assim:

```text
modelo-base
     │
     ├── adaptador A → tarefa / cliente A
     ├── adaptador B → tarefa / cliente B
     └── adaptador C → tarefa / cliente C
```

O modelo-base permanece o mesmo. O que muda é o adaptador. Isso permite pensar em um único modelo grande como uma base para múltiplas especializações. Segundo o material, um adaptador pode representar aproximadamente 1–2% dos parâmetros. O impacto econômico dessa diferença é significativo: em vez de retreinar o modelo inteiro para cada aplicação, pode-se manter o modelo-base e treinar adaptações menores. LoRA se torna, assim, uma peça importante da multiplicação de modelos derivados.

Para inferência, LoRA também introduz uma vantagem arquitetural relevante. Como o modelo-base permanece congelado, é possível servir múltiplos adaptadores sobre a mesma infraestrutura, trocando adaptadores por cliente, tarefa ou domínio sem duplicar o modelo completo. Em alguns cenários, o adaptador pode ser mesclado aos pesos do modelo para reduzir overhead; em outros, pode permanecer separado para permitir troca dinâmica. Isso favorece sistemas multi-inquilino, experimentação rápida e especialização por domínio sem custo proibitivo. Em termos práticos, LoRA transforma adaptação de modelo de um processo de retreinamento pesado em um processo modular de engenharia.

## O contraponto: GPT-4

Enquanto o ecossistema aberto se expandia, o lado fechado também avançava. O GPT-4, lançado em março de 2023, representou a fronteira dos modelos fechados em escala, alinhamento e multimodalidade. Isso é importante porque impede uma interpretação simplista da corrida de 2023. A abertura dos pesos não significava automaticamente superioridade de capacidade. Havia duas vantagens diferentes sendo perseguidas:

```text
MODELOS ABERTOS
experimentação
adaptação
auditoria
orquestração local

MODELOS FECHADOS
capacidade de ponta
alinhamento
multimodalidade
produto e robustez
```

A corrida passou a acontecer nos dois espaços simultaneamente. De um lado, a comunidade experimentava com modelos que podia modificar. Do outro, laboratórios fechados continuavam concentrando recursos para ampliar a capacidade dos modelos e transformá-la em produtos. Essa divisão seria decisiva para a arquitetura dos sistemas seguintes. Para o engenheiro, isso significa que a escolha entre aberto e fechado não deve ser tratada como preferência ideológica, mas como decisão de requisitos: controle, custo, privacidade, capacidade, latência e governança.

## A segunda metade da história: quando o modelo se torna plataforma

O capítulo anterior terminou com uma tese: o valor do sistema está no que vem depois do modelo. Em 2023, essa tese ganhou uma segunda dimensão. Não bastava mais perguntar o que havia sido colocado dentro do modelo. Era preciso perguntar o que outras pessoas poderiam construir em cima dele. O modelo aberto introduziu uma nova camada:

```text
pré-treino
    ↓
modelo-base
    ↓
pesos disponíveis
    ↓
adaptação
    ↓
sistema especializado
```

Essa estrutura muda a economia do desenvolvimento. O laboratório que treinou o modelo continua sendo importante, porque produziu a capacidade inicial. Mas a inovação não precisa terminar ali. Outros pesquisadores podem adaptar o modelo. Outros engenheiros podem incorporá-lo a produtos. Outros projetos podem combiná-lo com recuperação de informação, ferramentas e agentes. O modelo passa a funcionar como uma infraestrutura sobre a qual uma comunidade pode construir. É essa multiplicação que dá aos pesos abertos seu significado histórico.

Do ponto de vista de inferência, essa mudança também é relevante. Quando o modelo se torna plataforma, o sistema precisa ser pensado como um todo: contexto, adaptadores, cache, batching, quantização, latência e custo por requisição. A arquitetura do modelo deixa de ser um assunto interno do laboratório e vira variável de projeto do próprio produto. Escolhas como GQA, MoE, contexto maior e adaptadores leves passam a influenciar diretamente o desenho de sistemas RAG, agentes e aplicações empresariais.

## A relação com RAG, ferramentas e agentes

A bifurcação entre modelos abertos e fechados também ajuda a explicar o ambiente em que RAG, ferramentas e agentes se desenvolveram. Um modelo sozinho possui limitações que o capítulo anterior já estabeleceu: conhecimento datado, ausência de fontes e incapacidade de realizar determinadas formas de computação. O caminho natural foi acrescentar componentes ao redor dele. RAG acrescenta recuperação de informação. Ferramentas acrescentam capacidades externas. Agentes acrescentam a possibilidade de organizar chamadas ao modelo e ações em uma sequência.

Os pesos abertos tornaram esse tipo de experimentação especialmente acessível porque o engenheiro podia controlar mais diretamente o modelo que estava no centro do sistema. Isso não significa que RAG, ferramentas ou agentes dependam de modelos abertos. Não dependem. Significa que o ecossistema aberto criou um ambiente particularmente favorável para experimentar como combinar um modelo com outros componentes. Essa é a continuidade direta com a tese do livro:

```text
modelo
  ↓
alinhamento
  ↓
produto
  ↓
limitações
  ↓
ferramentas / RAG / agentes
```

Os modelos abertos acrescentam uma nova possibilidade:

```text
modelo
  ↓
pesos disponíveis
  ↓
adaptação
  ↓
sistema especializado
```

As duas linhas passam a convergir. E as mudanças arquiteturais dessa fase ajudam a explicar por quê. Janelas de contexto maiores permitem injetar mais evidência em RAG. Atenção mais eficiente reduz o custo de manter histórico longo em agentes. MoE melhora a relação entre qualidade e custo em sistemas com muitas chamadas. LoRA permite especializar o modelo para tool use, domínio corporativo ou estilo de resposta sem retreinamento completo. Assim, a arquitetura dos modelos abertos não apenas acompanhou o crescimento de RAG e agentes; ela ajudou a torná-los viáveis em escala prática.

## O que significa “aberto”?

É importante não transformar “modelo aberto” em sinônimo de “modelo sem restrições”. O ponto central deste capítulo é mais específico: a disponibilidade dos pesos muda o que pode ser feito com o modelo. Com os pesos disponíveis, torna-se possível executar o modelo em infraestrutura própria, adaptá-lo e integrá-lo diretamente a outros componentes. Isso cria vantagens de controle e auditabilidade. Mas o próprio material também mostra que o ecossistema de 2023 era bifurcado. Modelos fechados continuavam oferecendo capacidades importantes que não estavam necessariamente disponíveis da mesma maneira nos modelos abertos. Portanto, a decisão não deveria ser tratada como uma questão ideológica. É uma questão de requisitos.

Há ainda uma distinção importante entre abrir pesos e abrir todo o stack de treinamento. Código de treino, dados, receitas de alinhamento e infraestrutura podem permanecer fechados mesmo quando os pesos são liberados. Para o engenheiro, o que importa de imediato é o que a abertura dos pesos permite: inspecionar comportamento, adaptar, servir localmente, quantizar, otimizar inferência e integrar com outros componentes. Essa é a diferença prática central.

## O que a abertura muda para o engenheiro

Para o engenheiro, a primeira consequência é que modelo não é mais uma escolha isolada. É preciso avaliar o modelo dentro do sistema em que ele será utilizado. Dados sensíveis, custo de inferência, necessidade de execução local e requisitos de compliance podem favorecer pesos abertos. Capacidade bruta e multimodalidade podem favorecer modelos fechados. O custo de adaptação também entra nessa decisão. LoRA permite adaptar grandes modelos sem retreinar todos os parâmetros, tornando possível manter um modelo-base e criar adaptadores específicos por cliente ou tarefa.

Os pesos abertos também permitem maior controle sobre a infraestrutura. O modelo pode ser servido em hardware próprio e combinado com RAG e ferramentas sem depender integralmente de um provedor externo. Isso traz vantagens, mas também transfere responsabilidades: segurança, escalabilidade, observabilidade, versionamento e otimização de inferência passam a ser parte do problema de engenharia da equipe. Em outras palavras, abertura dá controle, mas também exige maturidade operacional.

Além disso, a arquitetura do modelo passa a influenciar diretamente o custo do sistema. Contexto maior favorece RAG e agentes, mas aumenta consumo de memória. GQA reduz KV cache e melhora throughput, especialmente em cenários de longa duração ou alta concorrência. MoE pode reduzir custo computacional por token, mas exige mais memória e serving mais sofisticado. Quantização pode tornar modelos abertos viáveis em hardware menor, mas pode introduzir perdas de qualidade. Tudo isso significa que escolher um modelo aberto não é apenas escolher um conjunto de pesos; é escolher um perfil de inferência.

A decisão, entretanto, não é definitiva. Em 2023, a diferença entre os dois mundos parecia relativamente clara: aberto significava principalmente experimentação e pesquisa; fechado significava o topo da capacidade e do produto. Essa distância muda. Por isso, uma decisão tomada hoje pode estar errada amanhã. A arquitetura precisa ser reavaliada periodicamente, especialmente porque custo, capacidade e disponibilidade evoluem rapidamente.

## A lição estrutural

O movimento dos modelos abertos representa uma mudança diferente daquela produzida pelo RLHF. O RLHF mostrou que capacidade não era suficiente: era preciso transformar capacidade em comportamento utilizável. Os modelos abertos mostraram outra coisa: mesmo um modelo já treinado pode se tornar matéria-prima para novos sistemas. A sequência fica mais clara:

```text
pré-treino
   ↓
capacidade

RLHF / alinhamento
   ↓
obediência

produto
   ↓
acesso

modelos abertos
   ↓
distribuição da capacidade

adaptação + ferramentas + RAG
   ↓
sistemas especializados
```

O capítulo anterior mostrou o momento em que o público chegou ao modelo. Este capítulo mostra o momento em que a capacidade começa a circular fora do laboratório. Essa é a importância de 2023. Não foi o fim dos modelos fechados. O GPT-4 mostrou justamente o contrário: a fronteira de capacidade continuava sendo empurrada por laboratórios com enormes recursos. Mas, ao mesmo tempo, os pesos de alguns modelos passaram a circular, LoRA tornou a adaptação barata e uma comunidade inteira passou a experimentar com aquilo que antes estava confinado. A corrida deixou de ser apenas: quem consegue treinar o melhor modelo? E passou a incluir uma segunda pergunta: o que milhares de pesquisadores e engenheiros conseguem construir quando recebem um modelo já treinado? É essa segunda pergunta que prepara o terreno para a próxima etapa do livro.

## Para o engenheiro

Escolha aberto versus fechado por requisito, não por preferência. Dados sensíveis, custo de inferência, execução local e compliance podem favorecer pesos abertos; capacidade bruta e multimodalidade podem favorecer modelos fechados. A decisão correta depende do sistema, não apenas do modelo.

Separe modelo-base de adaptação. LoRA permite manter um modelo grande como base e criar adaptadores específicos para clientes ou tarefas, sem retreinar o modelo inteiro. Isso reduz custo, acelera experimentação e facilita servir múltiplas variantes sobre a mesma infraestrutura.

Pesos abertos significam controle, mas também responsabilidade. É possível executar o modelo em hardware próprio, adaptá-lo e combiná-lo com RAG e ferramentas sem depender integralmente de um provedor. Em troca, a equipe assume parte do trabalho de segurança, escalabilidade e otimização.

Não confunda pesos abertos com capacidade superior. Em 2023, o ecossistema era claramente bifurcado: os modelos abertos favoreciam experimentação; os fechados concentravam parte importante da capacidade de ponta e da robustez de produto. Essa diferença pode diminuir com o tempo, mas não deve ser ignorada no projeto.

Considere arquitetura como variável de inferência. Contexto maior favorece RAG e agentes. GQA reduz custo de memória e melhora throughput. MoE pode melhorar eficiência computacional, mas aumenta complexidade de serving. Quantização pode reduzir custo, mas exige avaliação de qualidade. Essas escolhas afetam diretamente latência, custo e viabilidade operacional.

O modelo é apenas um componente. A arquitetura precisa considerar o que acontece depois dele: adaptação, recuperação de informação, ferramentas e agentes. Em sistemas reais, o desempenho final depende menos do modelo isolado e mais da qualidade da integração entre modelo, contexto e infraestrutura.

Reavalie a escolha. A relação entre capacidade, custo e disponibilidade muda rapidamente. Uma arquitetura adequada hoje pode deixar de ser a melhor escolha depois. Em um ecossistema que evolui nessa velocidade, revisar periodicamente a decisão faz parte do trabalho de engenharia.

---

**Fontes:** [Touvron et al., 2023] — LLaMA; [Touvron et al., 2023] — LLaMA 2; [Hu et al., 2021] — LoRA; [OpenAI, 2023] — GPT-4 Technical Report; [Zhao et al., 2023] — survey de LLMs; [Jiang et al., 2023] — Mistral 7B; [Jiang et al., 2024] — Mixtral; [Le Scao et al., 2022] — BLOOM; [Ainslie et al., 2023] — Grouped-Query Attention.
