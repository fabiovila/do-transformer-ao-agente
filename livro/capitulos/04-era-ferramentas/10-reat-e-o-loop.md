# Capítulo 10 — ReAct e o loop razão–ação (2022)

O capítulo anterior terminou com o modelo ganhando mãos. Mas havia uma diferença entre ter uma mão e saber usá-la. Em todos os marcos de 2021 a 2023, chamar uma ferramenta era um ato único: o modelo pede, o sistema executa, a observação volta, o modelo responde, fim. Se o primeiro passo estivesse errado — a busca com o termo errado, o cálculo com a fórmula errada — não havia como o modelo perceber e corrigir o próprio caminho. Em outubro de 2022, o ReAct, de Yao et al., atacou exatamente essa lacuna. Ele não acrescentou uma ferramenta nova. Acrescentou a *forma*: pense, aja, observe, pense de novo, até que o objetivo esteja satisfeito.

O problema que ele resolve é o mesmo de qualquer pessoa que erra o caminho: sem observar o resultado da própria ação, não há correção de rota. Uma pessoa que se perde olha em volta e se reorienta; um modelo que gera uma resposta errada, sem acesso ao mundo, não tem para onde olhar. O ReAct deu ao modelo esse “olhar em volta”: o resultado de cada ação volta como observação, e a observação alimenta a próxima decisão. Com isso, um modelo pode agir, errar, perceber que errou e tentar de novo — exatamente o tipo de iteração que o prefácio deste livro define como a diferença entre um sistema confiável e uma geração sortuda.

A ambição era um loop com condição de parada. E a descoberta prática foi que quase todo framework de agente — AutoGPT, LangChain, LangGraph, o que vier no capítulo 13 — é, no fundo, “ReAct + infraestrutura”. Por isso o capítulo trata o ReAct menos como um algoritmo específico e mais como o esqueleto cognitivo da era dos agentes. Ele também faz um aviso que reaparecerá no livro: reflexão do próprio modelo é útil, mas não substitui validadores externos. E mostra o preço do loop: trajetórias lineares acumulam erros, e tokens custam dinheiro.

## O problema que a ação única não resolvia

Antes do ReAct, o uso de ferramentas tinha a forma de uma substituição única. O modelo recebia uma pergunta, decidia uma ação, a ferramenta retornava um resultado, e o modelo finalizava. Esse padrão resolve tarefas simples, mas falha de uma maneira característica quando a tarefa exige mais de um passo: um erro no primeiro passo não é corrigível. Se a busca inicial retorna a página errada, o modelo não tem como saber disso. Se o primeiro cálculo usa a unidade errada, o segundo herda o erro. O sistema caminha, mas não sabe que está no caminho errado.

É o que este livro chama de “generate → hope”: gerar uma resposta na esperança de que ela esteja certa, sem nenhum mecanismo para descobrir se esteve. Uma única geração pode falhar; uma sequência com feedback pode convergir. O ReAct é a passagem do primeiro para o segundo: o modelo passa a ter acesso às consequências das próprias ações, e essa informação nova permite corrigir o rumo antes de finalizar.

## O padrão

O ReAct intercala raciocínio e ação em uma sequência alternada de três tipos de passo — *Thought*, *Action* e *Observation* — e repete o ciclo até que uma resposta final seja produzida. Um exemplo típico do paper:

```text
Thought:  "preciso saber quando o Transformer foi publicado"
Action:   search("Attention Is All You Need date")
Observe:  "12 de junho de 2017"
Thought:  "tenho a resposta"
Answer:   "12 de junho de 2017"
```

A estrutura é deliberadamente simples. O *Thought* dá ao modelo espaço para raciocinar sobre o estado atual e decidir o que precisa saber. O *Action* especifica, em linguagem estruturada, qual ferramenta chamar e com quais argumentos. O *Observe* injeta o resultado real da ferramenta de volta na sequência. E o ciclo se repete até que o modelo julgue ter informação suficiente e emita a resposta final. O detalhe decisivo é que a observação vem do ambiente, não do modelo — é aí que o loop ganha poder.

É importante notar o que o ReAct não é. O modelo não foi treinado para esse comportamento; a forma é evocada com apenas um ou dois exemplos no prompt. O paper mostra, portanto, que a estrutura razão–ação–observação não precisava ser ensinada nos pesos: ela podia ser induzida por poucas demonstrações. Isso explica por que o padrão se espalhou tão rápido — não exigia treinamento, apenas um prompt bem formado e um conjunto de ferramentas.

## Raciocínio e ação se alimentam

A tese do ReAct é que raciocinar e agir não são habilidades que se somam; elas se reforçam. O raciocínio melhora a ação porque decide *o que* buscar e *por quê* — em vez de chamar ferramentas às cegas, o modelo raciocina sobre qual informação falta e, portanto, qual ação reduziria a incerteza. A ação melhora o raciocínio porque produz observações do mundo real, que substituem suposições por evidência. No ReAct, cada Thought é informado pela observação anterior, e cada Action é justificada por um Thought anterior.

Esse entrelaçamento ataca diretamente o problema das alucinações. Um modelo que apenas raciocina (*chain-of-thought*) pode afirmar um fato falso com total confiança, porque não tem acesso ao mundo. Um modelo que apenas age pode executar ações sem sentido, porque não tem um raciocínio orientando as decisões. O ReAct combina os dois: o raciocínio gera hipóteses testáveis, e a observação valida ou corrige essas hipóteses antes de elas virarem resposta. Nos benchmarks de question answering com evidência, como HotpotQA e Fever, o ReAct reduziu alucinação e propagação de erro em comparação com linhas de base que usavam apenas raciocínio ou apenas ação.

## Os números

Os resultados quantitativos do ReAct foram impressionantes justamente porque comparavam o padrão com métodos muito mais caros. Em ALFWorld, um ambiente doméstico em primeira pessoa onde o agente deve completar tarefas físicas, o ReAct alcançou cerca de 34 pontos percentuais a mais de sucesso absoluto sobre linhas de base de imitação e aprendizado por reforço — métodos que exigiam milhares de demonstrações e treinamento dedicado. Em WebShop, um ambiente de compras online, o ganho foi de cerca de 10 pontos percentuais sobre as mesmas linhas de base.

| Tarefa | Ganho do ReAct | Comparação |
| --- | --- | --- |
| ALFWorld | ~34 pontos absolutos | linhas de base de imitação/RL |
| WebShop | ~10 pontos absolutos | linhas de base de imitação/RL |
| HotpotQA / Fever | menos alucinação e propagação de erro | CoT e Act-only |

O ponto estrutural é o contraste entre esforço e resultado. As linhas de base de imitação e RL eram treinadas especificamente para cada ambiente, com enormes conjuntos de demonstrações. O ReAct usava apenas um ou dois exemplos no prompt e, ainda assim, superava esses métodos. Isso mudou a economia da pesquisa: se uma forma de prompting alcançava o que antes exigia treinamento especializado, a barreira para construir sistemas agentic caía de forma drástica. O padrão se tornou a opção padrão não porque fosse a mais sofisticada, mas porque era a mais barata e a mais geral.

## Uma forma, não um framework

Talvez a contribuição mais duradoura do ReAct não seja o algoritmo, mas a percepção de que ele descreve uma *forma*, e não um framework. Todo agente que intercala raciocínio e ação em um loop com observação está, conscientemente ou não, usando o padrão ReAct. Quando o capítulo 13 apresentar os frameworks de agentes, o leitor reconhecerá a mesma estrutura sob nomes diferentes: AutoGPT é ReAct com ferramentas e memória; LangGraph é ReAct com grafos e estados; a maioria dos loops de agente é ReAct com infraestrutura adicional de planejamento, memória e orquestração.

O indício mais concreto dessa universalidade é o parâmetro que quase todo framework expõe: `max_steps`. Ele não é um detalhe de implementação; é a condição de parada do loop. Um loop ReAct precisa saber quando parar — quando o objetivo foi satisfeito, por condição explícita ou por julgamento do modelo — e precisa de um limite de segurança para os casos em que o modelo não converge. `max_steps`, `max_iterations`, `max_loops`: nomes diferentes para a mesma pergunta que o ReAct tornou inevitável. Quem projeta um agente está, na prática, decidindo como parametrizar um ReAct.

## Aprender com o feedback do loop

Uma vez que o loop existe, surge naturalmente a pergunta: o que fazer com o que o loop aprendeu? Duas linhagens responderam. A Reflexion, de Shinn et al. (2023), transformou o loop em um ciclo de aprendizado verbal: quando o agente falha, ele reflete sobre a causa e guarda a lição em uma memória de texto; na tentativa seguinte, essa memória orienta as decisões. O agente não atualiza os pesos — atualiza um diário de bordo que melhora a próxima tentativa. O nome dado pelos autores, *verbal reinforcement learning*, captura a ideia: a recompensa e a correção são expressas em linguagem, não em números.

A Self-Refine, de Madaan et al. (2023), explorou a mesma intuição por outro ângulo: o mesmo modelo gera uma saída, critica a própria saída e a reescreve, repetindo o ciclo algumas vezes sem qualquer treinamento. O modelo atua como gerador e como crítico de si mesmo. Essa abordagem produziu ganhos consistentes em uma ampla variedade de tarefas, e tem a vantagem de não exigir dados nem recompensas.

É aqui que este livro precisa fazer uma distinção importante, que o AGENTS.md estabelece: *reflexão do próprio modelo não é validação independente*. A Reflexion e a Self-Refine são úteis — elas corrigem a rota usando informações que o próprio modelo produz. Mas, quando a tarefa permite, a validação deve vir de fora: executar o código, rodar o teste, verificar o schema. O clássico exemplo é a Reflexion em tarefas de código: o modelo reflete sobre o erro, mas quem confirma se a correção funciona é o interpretador. Reflexão corrige a direção; verificação externa confirma a chegada. Um sistema robusto usa as duas, na ordem certa.

## Os limites do loop

O loop resolveu o problema da correção de rota, mas introduziu dois custos que a era dos agentes carregaria desde então. O primeiro é a linearidade: um loop ReAct percorre uma trajetória linear — cada passo depende do anterior — e, portanto, um erro no início se propaga por toda a cadeia. O modelo pode corrigir, mas corrigir exige que o erro seja detectável na observação; se o modelo interpreta mal uma observação intermediária, o engano persiste. Trajetórias lineares acumulam erros iniciais.

O segundo custo é de recursos: cada ciclo consome tokens, e tokens custam tempo e dinheiro. Um loop longo pode gastar dezenas de chamadas para responder o que um modelo faria em uma. A latência também cresce a cada ida e volta. Por isso, a era seguinte investiria em formas de escapar da linearidade: planejamento topológico que divide a tarefa em ramos independentes (DAGs), busca em árvore que explora múltiplos caminhos em vez de um só — como Tree of Thoughts e LATS — e planejadores dedicados que decidem a sequência antes de agir. O capítulo 13 tratará desses caminhos. O ReAct estabeleceu o loop; o que veio depois foi aprender a não desperdiçá-lo.

## A lição estrutural

O ReAct é, em muitos sentidos, o ponto em que o livro converge com seu próprio prefácio. O loop cognitivo descrito na abertura — observar, raciocinar, agir, observar, verificar — é exatamente o padrão que o ReAct tornou concreto em 2022. Antes dele, era possível imaginar o loop como abstração; depois dele, ele se tornou um padrão de engenharia com implementação, resultados e limites conhecidos.

A mudança de natureza que o ReAct produz pode ser resumida assim:

```text
MODELO QUE GERA  →  SISTEMA QUE ITERA

input → output         objetivo
                       ↓
                       observar
                       ↓
                       raciocinar
                       ↓
                       agir
                       ↓
                       observar
                       ↓
                       verificar
                       ↓
                       convergir
```

Essa passagem — do modelo como produtor de texto para o sistema como produtor de resultado — é a tese central do livro, e o ReAct é o mecanismo concreto que a tornou prática. Os capítulos anteriores deram ao modelo língua, obediência, produto e mãos. Este capítulo deu o último ingrediente: a possibilidade de usar as mãos repetidamente, corrigindo a rota a cada observação, até chegar a um resultado verificável. Com isso, a era das ferramentas estava completa — e a era dos agentes podia começar.

## Para o engenheiro

Desenhe agentes no molde do ReAct. Thought → Action → Observation é a forma de todo agente, mesmo por baixo dos frameworks: é esse loop que roda quando o framework esconde a complexidade. Em vez de procurar “prompts mágicos”, projete o ciclo — o que o modelo deve raciocinar, que ferramentas pode chamar, como as observações voltam e quando o loop deve parar.

Sem observação das próprias ações não há correção de rota. Portanto, logue sempre o que o agente pensou, o que chamou e o que viu. Um loop sem log é um buraco negro: quando a resposta final está errada, não há como reconstruir a trajetória que a produziu. O log é o que permite debugar, reexecutar e melhorar — a observabilidade de que trata o AGENTS.md.

Loop custa tokens e tempo. Defina teto de iterações, orçamento de tokens e critério de parada antes de subir para produção. Um agente sem `max_steps` em ambiente real é uma conta aberta: pode rodar indefinidamente, acumulando custo e latência. A condição de parada é parte do design, não um detalhe.

Reflexão do próprio modelo ajuda, mas não substitui checagem externa. Quando a tarefa permite, valide a saída com execução, teste ou schema — não com o mesmo modelo olhando para si mesmo. Use a reflexão para orientar a próxima tentativa; use validadores externos para confirmar a chegada. Essa separação entre gerador e verificador é o que separa iteração produtiva de iteração que apenas repete o erro.

---

**Fontes:** [Yao et al., 2022] — ReAct; [Shinn et al., 2023] — Reflexion; [Madaan et al., 2023] — Self-Refine; [survey de tool use, 2026] — contexto de orquestração multi-ferramenta; [Taskade, 2026] — histórico e números do ReAct.
