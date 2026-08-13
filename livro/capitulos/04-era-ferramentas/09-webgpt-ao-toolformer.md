# Capítulo 9 — Do WebGPT ao Toolformer: como o modelo ganhou mãos

Até aqui, este livro tratou de um modelo que fala. O pré-treinamento lhe deu uma língua, o alinhamento lhe ensinou a obedecer e o produto o colocou diante de milhões de pessoas. Mas restava uma limitação que nenhuma dessas etapas resolvia: o modelo não podia fazer nada além de gerar texto. Não buscava a notícia de hoje, não resolvia 17×23 sem errar, não executava código, não consultava um banco de dados. Seu conhecimento estava congelado no momento em que o treinamento terminou. Para responder a uma pergunta sobre o presente, ele adivinhava a partir do passado. Para calcular, aproximava. Para executar, inventava um resultado em vez de produzir um efeito.

É essa a parte mais literal da tese deste livro. Se a inteligência efetiva do sistema emerge da combinação entre modelo, contexto, ferramentas e iteração, então era preciso ensinar o modelo a ter mãos. E havia dois caminhos possíveis. O primeiro era dizer ao modelo como usar uma ferramenta: descrever a API no prompt e esperar que a geração produzisse a chamada certa. O segundo era treinar o modelo a decidir quando uma ferramenta valia a pena, transformando o uso de ferramentas em comportamento aprendido, e não em truque de engenharia de prompt. Os quatro marcos desta era mostram os dois caminhos em ação. O WebGPT provou que um modelo podia agir em um ambiente. O MRKL ousou rotear partes da pergunta para calculadoras, conversores e bancos de dados. O PAL decidiu que o modelo nem deveria tentar calcular — melhor escrever Python e deixar a máquina executar. E o Toolformer aprendeu sozinho quais chamadas de API valiam a pena, sem que ninguém lhe dissesse. No fim do capítulo, o HuggingGPT transforma o próprio modelo em um controlador que escolhe outros modelos como ferramentas.

A ambição de toda a era cabe em uma frase: transformar **ferramentas em extensões cognitivas** do modelo. Quando isso acontece, o sistema resultante passa a ser mais capaz do que o modelo sozinho — não porque o modelo mudou, mas porque o processo do qual ele participa passou a incluir o mundo.

## WebGPT: o primeiro modelo que agiu em um ambiente

O WebGPT, de Nakano et al. (2021), foi o primeiro marco a mostrar que um modelo de linguagem podia não apenas gerar texto, mas agir dentro de um ambiente e colher o resultado dessa ação. A formulação era simples e a execução, difícil: dar ao GPT-3 um navegador de texto e treiná-lo a usá-lo para responder perguntas. O navegador não era metáfora. O modelo realizava ações discretas — buscar, abrir um resultado, rolar a página, citar um trecho — e observava o estado resultante antes de decidir o próximo passo.

```text
estado do navegador
    ↓
ação do modelo (buscar, abrir, rolar, citar)
    ↓
novo estado do navegador
    ↓
observação → próxima ação
    ↓
resposta final, apoiada em referências
```

Essa mudança é estrutural. A resposta deixava de ser produzida de uma única vez, a partir da memória interna do modelo; passava a ser construída passo a passo, à medida que as evidências eram coletadas. E havia uma regra decisiva: para responder, o modelo precisava apoiar a resposta em referências. Em vez de apenas afirmar, ele precisava demonstrar de onde vinha a informação. Exigir citação não é um detalhe de produto; é um mecanismo de verificação que desloca parte da responsabilidade do modelo para o ambiente.

O treinamento acontecia em dois estágios. No primeiro, o modelo aprendia por imitação, reproduzindo trajetórias de humanos usando o navegador. No segundo, um modelo de recompensa treinado a partir de preferências humanas selecionava, por rejeição amostral, as melhores trajetórias entre várias amostradas. Essa sequência — aprender com humanos e depois refinar com feedback — é exatamente a lógica que o capítulo 7 apresentou para o alinhamento, agora aplicada não à resposta final, mas à sequência de ações que produz a resposta. A avaliação em ELI5, um conjunto de perguntas abertas, indicou que os avaliadores preferiam as respostas do WebGPT às referências originais do Reddit na maioria das comparações, e que as respostas eram consideravelmente mais factuais e informativas.

A importância histórica do WebGPT não está nos números exatos. Está em demonstrar três coisas ao mesmo tempo: que um LLM podia interagir com um ambiente e usar a observação; que o uso de ferramentas podia ser aprendido por treinamento com feedback; e que exigir referências muda o comportamento do modelo. Agir, aprender com feedback e fundamentar são precisamente os pilares que o ReAct e o function calling transformariam em padrão nos anos seguintes.

## MRKL: roteamento neuro-simbólico

O MRKL, de Karpas et al. (2022), atacou o problema por outro ângulo. Em vez de fazer o modelo agir em um ambiente, dividiu o próprio conhecimento entre módulos especialistas e deixou o LLM decidir qual módulo deveria responder a cada parte da pergunta. A arquitetura — *Modular Reasoning, Knowledge and Language* — combinava componentes neurais e simbólicos.

```text
pergunta
    ↓
roteador (LLM)
    ↓
┌──────────────────────────────┐
│  experts                     │
│  neurais          simbólicos │
│  LLM geral        calculadora│
│  LLM de domínio   conversor  │
│                   de moeda   │
│                   API de     │
│                   dados      │
└──────────────────────────────┘
    ↓
resposta (ou fallback seguro)
```

A tese do MRKL é que nem todo raciocínio deve usar a mesma máquina. Tarefas que exigem compreensão de linguagem podem ser resolvidas por módulos neurais, como um LLM geral ou especializado por domínio. Tarefas que exigem computação exata ou dados estruturados — calcular, converter, consultar — devem ser resolvidas por módulos simbólicos, que não alucinam. O LLM, no papel de roteador, decide para qual especialista cada fragmento da consulta deve ir.

Dois detalhes de engenharia tornam a ideia robusta. O primeiro é o fallback seguro: quando o roteador não tem confiança suficiente, o sistema recorre ao LLM geral em vez de arriscar um especialista. O segundo é que os experts podem ser, eles próprios, LLMs — o roteamento não precisa escolher apenas entre símbolo e linguagem; pode escolher entre modelos de capacidades diferentes. A implementação mais conhecida da arquitetura foi o Jurassic-X, da AI21, o que mostrou que o padrão podia deixar o paper e virar produto. O MRKL não resolveu todos os problemas do tool use, mas nomeou a estrutura que praticamente todos os sistemas seguintes herdariam: um modelo que decide e módulos que executam.

## PAL: raciocínio via código

Se o MRKL roteava o cálculo para uma calculadora, o PAL, de Gao et al. (2022), foi mais radical. Em vez de o modelo calcular, o modelo deveria escrever um programa Python e deixar um interpretador resolver. O nome condensa a tese — *Program-Aided Language Models*.

```text
pergunta
   ↓
LLM escreve programa Python
   ↓
interpretador executa
   ↓
resposta exata
```

A justificativa é epistêmica: um LLM não computa, ele imita a computação. Pode reproduzir o estilo de um cálculo e errar no resultado; um interpretador, não. Ao deslocar o passo de solução para um programa, o modelo entrega aquilo que faz bem — decompor o problema, escolher as operações e organizar a lógica em linguagem natural e código — e delega à máquina aquilo que ela faz com exatidão: executar. Essa separação é o que este livro chama de distinguir o que o modelo sabe do que ele pode calcular.

Os resultados sustentaram a aposta. Na GSM8K, um benchmark de problemas de matemática, a abordagem alcançou estado da arte e superou um modelo de 540 bilhões de parâmetros usando *chain-of-thought* por 15 pontos percentuais absolutos de acurácia top-1. O padrão generalizou para 13 tarefas do BIG-Bench Hard, e os autores relataram resolver significativamente mais problemas de matemática com menos erros. O ponto não é apenas que o código acerta a aritmética; é que o LLM, ao escrever o programa, revela seu raciocínio em uma forma que pode ser executada, testada e depurada — uma propriedade que nenhuma verificação sobre o texto solto possui.

## Toolformer: o modelo que aprende sozinho quando chamar

Os três marcos anteriores tinham uma característica em comum: era o projetista quem decidia onde e quando a ferramenta entraria. O Toolformer, de Schick et al. (2023), inverteu essa responsabilidade. Em vez de receber instruções, o modelo aprendeu, por auto-supervisão, a decidir quando uma chamada de API valia a pena.

A receita é elegante. O modelo percorre seu próprio corpus de treinamento e, em cada trecho, gera chamadas de API candidatas — pedaços de texto como *search*, *calculator*, *QA*, *translation* ou *calendar*, posicionados no ponto em que a informação externa pareceria útil. As APIs são executadas de verdade. Então o modelo pergunta, com um critério puramente estatístico: a chamada reduziu o erro de previsão dos tokens seguintes? Apenas as chamadas que sobreviveram a esse crivo são mantidas; o resto é descartado. Por fim, o modelo é fine-tunado sobre o corpus anotado.

```text
corpus
   ↓
chamadas candidatas (busca, calculadora, QA, tradutor, calendário)
   ↓
execução das APIs
   ↓
mantém apenas chamadas que reduzem o erro de previsão
   ↓
fine-tuning sobre o corpus anotado
```

| Ferramenta | Tipo de informação que acrescenta |
| --- | --- |
| Calculadora | computação exata que o modelo aproxima |
| QA | fatos que o modelo não reteve |
| Busca | informação atualizada ou fora do treino |
| Tradutor | texto em idiomas que o modelo domina pouco |
| Calendário | datas e programação |

O resultado é um comportamento que não foi instruído por nenhum humano: o modelo descobre, por dados, que alguns problemas são melhor resolvidos chamando uma ferramenta, e passa a fazê-lo espontaneamente. As melhorias apareceram em tarefas zero-shot, e modelos menores com o Toolformer se tornaram competitivos com modelos muito maiores sem a capacidade. A lição transcende o experimento: treinar para decidir *quando* usar uma ferramenta é qualitativamente diferente de instruir *como* usá-la.

## Dois caminhos: dizer como ou aprender quando

Vistos em sequência, os quatro marcos desenham uma clivagem que atravessa toda a era das ferramentas. De um lado, o caminho do prompting: descrever a ferramenta no texto e confiar que o modelo a invoque corretamente. Do outro, o caminho do treinamento: ensinar ao modelo, por feedback ou auto-supervisão, a escolher e usar ferramentas como parte do comportamento. O MRKL e o PAL ainda dependem, em boa parte, do primeiro; o WebGPT e o Toolformer são exemplos puros do segundo.

```text
CAMINHO DO PROMPTING        CAMINHO DO TREINAMENTO
como usar a ferramenta      quando usar a ferramenta
descrita no prompt          aprendido por feedback/dados
frágil, depende do formato  robusto, vira comportamento
custo zero de treino        exige dados ou recompensa
```

Cada caminho tem seu lugar. O prompting é barato, imediato e suficiente quando o uso é raro ou simples. O treinamento é caro, mas converte o tool use em algo que não depende de o modelo “se lembrar” de chamar a ferramenta a cada vez. A história que este capítulo conta — e que o capítulo 11 completará — é a de um deslocamento progressivo do primeiro para o segundo: primeiro produzimos o tool use por prompt, depois o tornamos primitiva de API e, finalmente, garantia formal de formato. A tabela abaixo resume os quatro padrões:

| Sistema | Mecanismo | Pergunta que responde |
| --- | --- | --- |
| WebGPT | agente em um ambiente + feedback | como agir e colher observação? |
| MRKL | roteador + experts neurais/simbólicos | qual parte vai para qual ferramenta? |
| PAL | LLM escreve código, interpretador executa | como obter computação exata? |
| Toolformer | auto-supervisão sobre chamadas | quando a chamada vale a pena? |

## HuggingGPT: o LLM como controlador

O último marco da era amplia o significado de “ferramenta”. No HuggingGPT, de Shen et al. (2023), o LLM não chama APIs de cálculo ou busca: ele escolhe outros modelos como ferramentas. O ChatGPT atua como controlador de um ecossistema inteiro — o Hugging Face — e orquestra a execução em quatro etapas.

```text
tarefa do usuário
    ↓
planejamento (ChatGPT)
    ↓
seleção de modelos no Hugging Face
    ↓
execução dos modelos escolhidos
    ↓
sumarização da resposta
```

A inovação conceitual é dupla. Primeiro, o modelo deixa de ser a única inteligência do sistema e passa a ser o cérebro que contrata cérebros: para cada subtarefa, ele seleciona o especialista mais adequado — um modelo para visão, outro para áudio, outro para linguagem. Segundo, a linguagem deixa de ser apenas o meio da resposta e se torna a interface de controle: é por texto que o controlador descreve o plano, chama os especialistas e sintetiza o resultado. O que antes era um único modelo respondendo torna-se uma organização temporária de modelos coordenada por linguagem.

O HuggingGPT antecipa, na escala das ferramentas, o que os capítulos 13 e 14 tratarão nos agentes: a ideia de que o valor está menos no modelo isolado e mais no processo de orquestração. Quando ferramentas passam a incluir outros modelos, o limite do sistema deixa de ser o modelo e passa a ser a capacidade de decidir o que usar, quando e para quê.

## A lição estrutural

O fio que atravessa os cinco marcos é a resposta que o livro vem construindo desde a primeira parte: a capacidade não reside apenas no modelo, mas no processo em torno dele. O WebGPT mostrou que o modelo pode agir; o MRKL, que pode delegar; o PAL, que pode evitar computar; o Toolformer, que pode decidir quando chamar; e o HuggingGPT, que pode comandar outros modelos. Em todos os casos, o modelo não ficou mais inteligente no sentido de pré-treinamento. O sistema ao redor dele ficou mais capaz, porque passou a incluir ação, observação e computação externa.

Isso tem uma consequência direta para a engenharia: a pergunta deixou de ser apenas “o que o modelo consegue fazer?” e passou a ser “que processo — com quais ferramentas, acionadas por qual lógica — produz o resultado de forma confiável?”. Os marcos desta era dão, cada um, uma peça dessa resposta. Falta, porém, a peça que transforma o uso de ferramentas de evento isolado em comportamento contínuo: o loop. É dela que trata o próximo capítulo.

## Para o engenheiro

Se a resposta exige fato novo, cálculo ou ação, não deixe o modelo adivinhar: dê a ferramenta. A regra de ouro desta era é simples — se um humano resolveria o problema com uma calculadora, uma busca ou uma API, o sistema deve ter a mesma opção. Modelo que adivinha um fato é uma fonte de erro evitável; modelo que busca, calcula ou executa é uma fonte de evidência.

Os quatro padrões do capítulo são receitas diretamente reaproveitáveis. O WebGPT ensina a aprender por feedback quando a tarefa envolve sequências de ações. O MRKL ensina a rotear cada parte da pergunta para a ferramenta certa e a prever um fallback seguro. O PAL ensina a delegar computação ao código — e é, até hoje, a forma mais barata de obter matemática confiável. O Toolformer ensina a deixar o modelo descobrir quando chamar, o molde de referência para sistemas que precisam acionar APIs espontaneamente. Em 2026, o function calling nativo cobre boa parte desses casos, mas o raciocínio por trás de cada padrão permanece.

Ferramenta não é “mais uma função” no sistema; é uma fonte de evidência. Meça o ganho real de cada uma. Se adicionar uma ferramenta não muda a resposta certa, ela está apenas adicionando latência e superfície de erro. A disciplina de ferramentas é a mesma da memória: só o que produz evidência útil deve permanecer.

Finalmente, separe o que o modelo sabe do que ele pode calcular. Sempre que a operação for executável — aritmética, consulta, código — prefira executar a inferir. O custo é pequeno; o ganho de confiabilidade é a própria justificativa do capítulo.

---

**Fontes:** [Nakano et al., 2021] — WebGPT; [Karpas et al., 2022] — MRKL; [Gao et al., 2022] — PAL; [Schick et al., 2023] — Toolformer; [Shen et al., 2023] — HuggingGPT; [survey de tool use, 2026] — evolução do tool use em agentes; [Taskade, 2026] — histórico do tool use.
