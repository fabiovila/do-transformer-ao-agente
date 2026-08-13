# Capítulo 18 — O loop cognitivo: RAG + agentes + ferramentas como um só sistema

Este é o capítulo em que o livro fecha o círculo — e pede que você desconfie das divisões que ele próprio usou. RAG, ferramentas, agentes e protocolos parecem quatro tecnologias, contadas em quatro partes separadas. A tese deste capítulo é que são **uma única arquitetura vista de ângulos diferentes**. O RAG é memória externa; as ferramentas são ação; os agentes são o loop que liga memória a ação; os protocolos são a camada que permite a tudo isso cooperar entre sistemas. Nenhuma das quatro existe isolada em um sistema real — e o livro que as separou em capítulos agora tem a obrigação de juntá-las.

O problema que este capítulo resolve é conceitual: como encaixar tudo o que veio antes em um só padrão? A resposta é o **loop** — objetivo, observar, raciocinar, agir, observar, verificar, atualizar —, a mesma estrutura que o capítulo 10 (ReAct) introduziu, que o capítulo 13 elevou a sistema e que os capítulos 14 a 17 expandiram para muitos agentes e protocolos. A tabela de equivalências em que cada ferramenta é uma extensão cognitiva organiza a síntese: search é aquisição, RAG é recuperação, shell é experimentação, testes são verificação, arquivos são memória.

E a ambição didática é a maior do livro: um **projeto completo** — pergunta → recuperar → planejar → chamar ferramenta → executar → verificar → corrigir → responder — que mostra cada peça dos capítulos anteriores em ação. Não como código de framework, mas como a forma mínima de um sistema que percebe, busca, raciocina, age, verifica e corrige. Quando você reconhecer esse loop dentro de todo sistema que construir, os capítulos deste livro deixam de ser uma história e viram uma caixa de ferramentas.

## Um só padrão, quatro ângulos

Os capítulos 5–17 contaram a história de quatro peças. A Parte II e a Parte V contaram o **RAG**: conhecimento externo recuperado e condicionando a geração — memória não-paramétrica. A Parte IV contou as **ferramentas**: o modelo que chama funções, executa código, navega em tela — ação. A Parte VI contou os **agentes**: loops com estado, objetivo e critério de término — o sistema que orquestra memória e ação. A Parte VII contou os **protocolos**: camadas padronizadas entre modelos, ferramentas e agentes — a interoperabilidade. Quatro histórias, um só ciclo:

```text
objetivo
   ↓
observar  (contexto, estado, memória)
   ↓
raciocinar (modelo)
   ↓
agir       (search | RAG | shell | edit | API | ...)
   ↓
observar   (resultado da ação)
   ↓
verificar  (testes, execução, comparação)
   ↓
atualizar  → loop ou finalizar
```

RAG e search alimentam o “observar”; o modelo faz o “raciocinar”; ferramentas e shell fazem o “agir”; testes e execução fazem o “verificar”; arquivos e banco são o “estado” que persiste entre iterações. Cada parte do livro construiu um pedaço do loop, e nenhum sistema real sobrevive com um pedaço só. A pergunta de desenho deixa de ser “qual tecnologia usar?” e vira “qual peça do loop o meu problema exige?”.

## A tabela de equivalências: ferramentas como extensões cognitivas

O passo seguinte é mapear cada ferramenta para a capacidade cognitiva que ela estende. A metáfora não é decorativa: diz por que cada ferramenta existe e o que ela acrescenta que o modelo sozinho não tem:

| Ferramenta | Extensão cognitiva | O que o modelo ganha |
| --- | --- | --- |
| Search | aquisição de informação | acesso a fontes externas ao conhecimento paramétrico |
| RAG | recuperação contextual | evidência específica condicionando a geração |
| Shell | experimentação | executar hipóteses e observar os resultados |
| Calculator / código | computação exata | precisão onde a inferência probabilística falha |
| Arquivos / banco | memória externa | estado que persiste entre sessões e iterações |
| Testes | verificação | evidência objetiva de que a mudança funciona |
| Compilador | verificação formal parcial | erros de tipo e sintaxe detectados antes de executar |

A consequência é dupla. Primeiro, nenhuma dessas capacidades é do *modelo*: é do sistema composto. O capítulo 0 prometeu isso e os capítulos 1–17 provaram por partes. Segundo, a escolha de ferramenta vira uma questão de *custo da capacidade*: search quando falta informação, shell quando uma hipótese pode ser testada, calculadora quando o número precisa ser exato, testes quando a propriedade pode ser verificada. O modelo decide; a ferramenta confere. Essa é a separação generator/verifier que o capítulo 10 introduziu e que aqui se generaliza: **o modelo propõe, o mundo confirma**.

## RAG não é só retrieval: é construção de evidência

O capítulo 12 terminou no agentic RAG: recuperação como *decisão* dentro do loop. Este capítulo completa a frase: o RAG não é um mecanismo de busca — é um processo de **construção de evidência**. A diferença é de propósito:

```text
query
  ↓
evidência: aquisição   (qual fonte, qual consulta, quantas buscas)
  ↓
evidência: organização (rerank, filtrar, fundir, priorizar)
  ↓
evidência: raciocínio  (a resposta é consequência das evidências?)
  ↓
answer (+ proveniência)
```

Cada estágio responde a uma pergunta de qualidade. A aquisição responde “a evidência certa chegou?”; a organização, “a evidência está na ordem e no peso certos?”; o raciocínio, “a conclusão decorre da evidência?” — e a pergunta final, que o capítulo 15 transformou em método de avaliação, é “a resposta é consequência de evidências suficientes, sem extrapolar além delas?”. Quando o RAG vira peça do loop, essas perguntas deixam de ser de um pipeline e passam a ser do sistema inteiro: o agente decide quando já tem evidência suficiente (retrieval como política), quando a evidência contradiz a hipótese (comparação) e quando precisa buscar de novo (iteração). Retrieval não é o mecanismo; a construção de evidência é o objetivo.

## Geração não é validação

O loop tem uma porta de saída que os sistemas reais frequentemente esquecem: o **verificar**. E este capítulo repete, agora com o peso de todas as partes do livro, a distinção que o AGENTS.md (§24–25) deste projeto tornou princípio: **geração não é validação**. Reflexão do próprio modelo — Reflexion, Self-Refine, LATS, LLM-as-judge — melhora candidatos, mas não é evidência independente: o mesmo sistema que gera também avalia, e vieses se repetem. O capítulo 15 mostrou o custo disso em avaliação; aqui a regra é para operação.

O verificador deve ser tão independente quanto possível da geração:

```text
teste unitário      →  propriedade verificável do resultado
execução            →  o código roda? a resposta do shell confirma?
comparação          →  a afirmação bate com a fonte recuperada?
cálculo independente→  a aritmética confere?
validação estrutural→  o schema foi respeitado? o contrato foi cumprido?
```

A hierarquia é a do capítulo 15, agora aplicada dentro do loop: quando uma propriedade pode ser testada por execução ou comparação, prefira o teste à autoavaliação. O modelo explora; o verificador decide; o loop corrige. Um sistema que ignora o verificar não é um agente — é um gerador otimista.

## O projeto didático: pergunta → evidência → ação → verificação

Para fechar, o projeto prometido: um sistema completo, mínimo, em que cada peça dos capítulos anteriores aparece com nome. A pergunta do exemplo é prosaica — “quanto custou a última campanha de marketing, e o gasto passou do orçamento?” — porque o valor didático está no fluxo, não no domínio.

```text
1. pergunta:  "Quanto custou a campanha de março e passou do orçamento?"
2. observar:  contexto = usuário + histórico (arquivos/memória)
3. raciocinar: que informação falta? valores e regra de orçamento
4. agir 1:    RAG → buscar("campanha março custo")  →  top-k de chunks
5. observar:  chunks com valores parciais; falta o valor do orçamento
6. agir 2:    RAG → buscar("orçamento anual marketing 2026")
7. agir 3:    calculadora → 48250.00 + 12350.00 + 9150.00 = 69750.00
8. verificar:  69750.00 > 60000.00?  →  sim, estourou em 9750.00
9. corrigir:  confrontar o total com a planilha recuperada (fonte)
10. responder: resposta + proveniência (chunks e cálculo)
```

Cada passo usa uma peça do livro. O passo 2 é o estado e a memória do capítulo 13; os passos 4–7 são o RAG (capítulo 12) e a ferramenta de cálculo (capítulos 9–11); o passo 8 é a verificação do capítulo 15; o passo 9 é a iteração corrigindo a resposta; o passo 10 é a proveniência que o RAG sempre prometeu. Se a verificação falhasse — o total não batesse com a planilha —, o loop voltaria ao passo 4 com uma consulta nova: é a iteração dos capítulos 10 e 12 em ação.

A versão sua desse projeto é um template, não um produto: escolha **uma** ferramenta real — search, calculadora ou shell —, um objetivo e um critério de parada, e rode o loop explicitamente. É o passo a passo mínimo de um agente, e é também o menor sistema que honra a tese deste livro: modelo + contexto + recuperação + ferramentas + ambiente + memória + iteração + verificação.

## A lição estrutural

RAG, ferramentas, agentes e protocolos são uma arquitetura só: **objetivo → observar → raciocinar → agir → observar → validar → atualizar**. As “eras” do livro foram uma organização didática de uma estrutura que sempre esteve inteira. O RAG sem agente é um pipeline sem decisão; o agente sem RAG é um raciocinador sem evidência; o agente sem verificação é um gerador otimista; e o agente sem protocolo é um sistema que não conversa.

A pergunta que o capítulo 0 fez — que combinação de modelo, contexto, ferramentas, ambiente, memória, feedback e verificação torna o sistema confiável? — encontrou aqui a sua resposta estrutural: **o loop**. É o padrão que o capítulo 10 descobriu, que o capítulo 13 sistematizou, que o capítulo 14 multiplicou, que os capítulos 16–17 conectaram ao mundo — e que o próximo e último capítulo vai avaliar, limitar e projetar para o horizonte.

## Para o engenheiro

Quando for desenhar um produto, comece pelo loop, não pela stack. Mapeie cada peça do ciclo para um componente concreto do código: retriever, tools, scheduler, logger, validador, armazenamento de estado. Se alguma peça não tem dono no seu projeto, ela está invisível — e uma peça invisível é uma falha latente. A maioria dos problemas de sistemas agentic está na orquestração (evidência, estado, validação), não no modelo.

Use a tabela de equivalências como checklist de capacidades: o seu sistema tem aquisição de informação? recuperação? experimentação? computação exata? memória persistente? verificação? Cada “não” é um risco — e cada resposta adiada é um custo futuro. Antes de trocar o modelo por um maior, feche as lacunas do loop: quase sempre rende mais.

Teste o loop antes de otimizar o modelo. Construa a versão mínima do projeto didático com uma ferramenta real e um critério de parada; meça onde ele quebra; só então escale. E nunca deixe o “verificar” ser feito só pelo próprio modelo: quando a propriedade puder ser testada por execução ou comparação, teste. O loop explora; o verificador decide; o seu sistema, se estiver bem desenhado, corrige e responde.

---

**Fontes:** Síntese conceitual baseada nos capítulos anteriores e na orientação do AGENTS.md; [Survey de tool use, 2026] — single-tool vs. multi-tool orchestration; [Gao et al., 2023] e [Li et al., 2024] — RAG como paradigma.
