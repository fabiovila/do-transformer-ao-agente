# Capítulo 11 — Function calling, structured outputs e computer use (2023–2024)

O capítulo anterior terminou com o loop como forma. Este capítulo mostra o que aconteceu quando essa forma deixou os papers e virou superfície padrão de API. Em cerca de trinta meses — do ReAct, em outubro de 2022, à Responses API, em março de 2025 — “chamar ferramenta” deixou de ser tema de pesquisa e se tornou um parâmetro de chamada de API. A pergunta desta era era de padronização: cada provedor inventava seu jeito de declarar uma função, e o modelo devolvia um JSON que quebrava a aplicação. O problema não era mais provar que tool use era possível; era torná-lo confiável o bastante para produção.

A resposta veio em camadas. Function calling tornou a ferramenta uma primitiva da API, com o nome e os argumentos devolvidos em uma estrutura que a aplicação pode executar sem parsing frágil. JSON mode forçou o formato da saída. As chamadas paralelas cortaram a latência de loops que dependiam de várias ferramentas. E os Structured Outputs, com `strict: true`, garantiram que o que saísse do modelo satisfizesse o schema declarado — o fim da era “o modelo devolveu JSON inválido”. Então a fronteira se expandiu de novo, na direção que poucos esperavam: o computer use, em outubro de 2024, transformou a tela inteira em ferramenta.

A ambição deste capítulo é silenciosa e central. Quando a interface para ferramentas é padronizada — função descrita em JSON, argumentos validados, saída garantida por schema — o *tool use* vira engenharia de produção, não experimento. E, quando a camada de ferramentas é padronizada, ela se prepara para virar commodity: o diferencial deixa de ser “conseguir chamar uma função” e passa a ser o que se faz com a orquestração, os dados e a verificação. Esse é o caminho que os capítulos 16 e 17 completarão, com MCP e A2A.

## ChatGPT plugins: o primeiro ecossistema em escala de produto

Em 23 de março de 2023, a OpenAI anunciou os plugins do ChatGPT. O marco não foi a tecnologia — o capítulo 9 já havia mostrado modelos usando ferramentas — mas a escala e a abertura. Pela primeira vez, um produto usado por milhões de pessoas permitia que desenvolvedores externos declarassem capacidades que o assistente podia invocar no meio do diálogo: navegação na web, execução de código, busca em serviços de terceiros. O modelo, que o capítulo 7 tinha transformado em produto, transformava-se agora em plataforma.

O desenho já carregava a divisão de responsabilidades que o function calling formalizaria meses depois: o desenvolvedor descreve a interface da ferramenta; o modelo decide quando chamá-la; a aplicação executa; e o resultado volta para o modelo. Os plugins foram aposentados em 2024 em favor dos GPTs, mas a ideia estrutural permaneceu. Eles provaram que havia demanda real por um assistente que não apenas respondesse, mas *fizesse* — e que esse fazer dependia de uma camada de integração padronizada entre o modelo e o mundo.

## Function calling: a ferramenta vira primitiva de API

Em 13 de junho de 2023, a OpenAI lançou o function calling como parte da API. A mudança parece pequena e é enorme: até então, o tool use dependia de o modelo escrever texto e a aplicação interpretá-lo; a partir daí, a decisão e o formato passaram a ser parte da própria API. O desenvolvedor descreve as funções disponíveis — com nome, descrição e JSON Schema para os argumentos — e o modelo devolve uma chamada estruturada que a aplicação pode executar diretamente.

```text
1. o desenvolvedor declara as funções (JSON Schema)
2. o modelo decide se deve chamar alguma
3. o modelo devolve {"nome da função", "argumentos"}
4. a aplicação executa e devolve o resultado
5. o modelo continua de onde parou
```

Esse é o ponto exato em que o ReAct vira produto. O loop do capítulo anterior — pensar, agir, observar — continua existindo, mas agora o “agir” é entregue por uma primitiva de API: em vez de o modelo escrever `search(“...”)` como texto e esperar que a aplicação parseie, ele devolve uma chamada estruturada que o sistema reconhece de forma determinística. A fragilidade do parsing de texto desaparece da camada de transporte, e o engenheiro pode se concentrar no que realmente importa: decidir quais ferramentas existem e o que fazer com os resultados.

A padronização também mudou a natureza do problema para os provedores. Declarar funções em JSON Schema transformou a chamada de ferramenta em um problema de *schema*: o modelo precisava aprender a respeitar tipos, campos obrigatórios e enumerações. Isso aproximou o tool use do problema de output estruturado — e preparou o terreno para os Structured Outputs do ano seguinte. A era da divergência, porém, começaria antes.

## Expansão e divergência: três provedores, três formatos

O sucesso do function calling abriu a porta para os concorrentes — e cada um inventou o próprio mecanismo. No DevDay de novembro de 2023, a OpenAI apresentou o *parallel function calling*, o JSON mode e a Assistants API. Em 21 de novembro de 2023, a Anthropic lançou o Claude 2.1 com tool use em beta e 200 mil tokens de contexto. Em dezembro de 2023, a Google expôs function calling no Gemini, com funções declaradas em schema compatível com OpenAPI. Três provedores, três formatos, três maneiras de declarar e devolver uma chamada.

| Provedor | Mecanismo | Lançamento |
| --- | --- | --- |
| OpenAI | function calling (`functions`) | jun/2023 |
| OpenAI | parallel function calling, JSON mode | nov/2023 |
| Anthropic | tool use (Claude 2.1) | nov/2023 |
| Google | function declarations (Gemini) | dez/2023 |

A divergência produziu um problema que a era dos protocolos resolveria: portabilidade. Um sistema que usasse o formato da OpenAI não migrava trivialmente para a Anthropic ou a Google sem reescrever a camada de ferramentas. Para o engenheiro, isso significava que o tool use, recém-industrializado, já estava fragmentado. A padronização da interface — feita por protocolos abertos como MCP — se tornaria a resposta a esse problema, e é o tema dos capítulos 16 e 17. Antes disso, porém, era preciso medir.

## Medir para industrializar

Nenhuma camada de infraestrutura se torna confiável sem medição. Em fevereiro de 2024, o Berkeley Function-Calling Leaderboard, do grupo Gorilla, começou a avaliar chamadas de função de forma quantitativa, comparando modelos pela capacidade de produzir invocações corretas em cenários de múltiplas ferramentas. O gesto é característico da maturidade da área: o que antes era demonstrado por exemplos passava a ser pontuado por números, com critérios explícitos e comparação direta entre modelos.

Em junho de 2024, o tau-bench, de Yao et al., acrescentou uma dimensão diferente: consistência. Em vez de medir apenas se o agente acerta a tarefa, o benchmark mede se ele repete o comportamento correto entre tentativas — uma propriedade que importa mais para produção do que para pesquisa. Um agente que acerta uma vez e falha nas outras não é confiável; um que se comporta de forma consistente permite prever custo, latência e qualidade. Medir consistência, e não apenas acurácia pontual, é o tipo de refinamento que separa uma técnica promissora de uma infraestrutura utilizável.

## Structured Outputs: o fim do JSON inválido

Em 6 de agosto de 2024, a OpenAI lançou os Structured Outputs. A promessa é direta: com `strict: true`, a saída do modelo é garantida para satisfazer o JSON Schema declarado. Nos testes da própria OpenAI, o novo modelo atingiu 100% de conformidade em avaliações de schemas JSON complexos, contra menos de 40% da geração anterior. O que antes era probabilidade passou a ser contrato.

A diferença é sutil e fundamental. Function calling já estruturava as chamadas de ferramenta; os Structured Outputs estenderam a garantia a qualquer saída consumida por código. Para o engenheiro, isso significa o fim de uma classe inteira de bugs: o parser da aplicação não quebra mais porque o modelo devolveu um JSON inválido, um campo a mais, um tipo errado. A validação que antes precisava ser feita por código — com retentativas, fallbacks e tratamento de erro — passa a ser responsabilidade da API.

É preciso, porém, manter a distinção que este livro repete: a garantia é de *forma*, não de *conteúdo*. O schema garante que os campos existem, têm o tipo certo e seguem a estrutura declarada; não garante que o valor preenchido esteja semanticamente correto. Um sistema de produção precisa das duas camadas: a garantia estrutural da API para o formato, e a verificação externa — execução, testes, validação de negócio — para o sentido. Structured Outputs resolveu metade do problema; a outra metade continuou sendo responsabilidade do engenheiro.

## Computer use: quando a ferramenta é a tela inteira

Em 22 de outubro de 2024, a Anthropic apresentou o computer use. A mudança de escala é conceitual: em vez de expor funções discretas, o modelo recebe uma captura da tela e produz ações de mouse e teclado. Screenshot entra, cliques e digitação saem. A “ferramenta” deixou de ser uma API específica e passou a ser a interface gráfica inteira — qualquer aplicação, qualquer site, qualquer fluxo, desde que visível.

```text
captura da tela
    ↓
modelo decide a próxima ação (mover, clicar, digitar)
    ↓
sistema executa
    ↓
nova captura de tela
    ↓
loop até o objetivo
```

O gesto estende o tool use de APIs estruturadas para interfaces não estruturadas — e é exatamente essa a troca. Onde não existe API, a tela se torna a interface universal. Isso abre um espaço enorme: sistemas legados, ferramentas internas, ambientes para os quais ninguém construiu integração. Mas tem um custo alto. Cada ação envolve captura de tela, processamento visual e decisão; a latência é muito maior que uma chamada de API, o consumo de tokens por ação é elevado, e a observação visual introduz novas fontes de erro — pixels ambíguos, elementos que mudam de posição, janelas que sobrepõem. Para o engenheiro, a orientação é clara: prefira APIs e integrações estruturadas sempre que existirem; reserve o computer use para ambientes sem alternativa.

## Convergência: do parâmetro de API ao protocolo

No fim de 2024, a camada de ferramentas estava padronizada no nível de cada provedor, mas fragmentada entre provedores. Em 2025, a convergência começou. A OpenAI unificou chat, ferramentas e estado na Responses API. E, mais importante, os protocolos abertos começaram a uniformizar a camada de ferramentas independentemente do provedor: o MCP, que o capítulo 16 apresentará, padroniza como um agente descobre e chama ferramentas de qualquer servidor; o A2A, tema do capítulo 17, padroniza a comunicação entre agentes. O tool use, que nasceu como pesquisa em 2021 e virou primitiva de API em 2023, estava se tornando commodity.

```text
2021  WebGPT: ferramenta como treinamento
2022  ReAct: ferramenta como loop
2023  Function calling: ferramenta como primitiva de API
2024  Structured Outputs: garantia de schema
      Computer use: tela como ferramenta
2025  Responses API + MCP + A2A: camada de ferramentas commodity
```

Essa é a trajetória que dá sentido ao título do capítulo. A padronização não é o fim do trabalho; é o que liberta o trabalho para subir de nível. Quando a interface para ferramentas é commodity, o valor migra para a orquestração, a qualidade dos dados, a verificação e o design dos agentes — os temas das próximas partes do livro. A era das ferramentas termina, portanto, não porque as ferramentas deixaram de importar, mas porque importam tanto que viraram infraestrutura: algo que se assume, não se constrói.

## A lição estrutural

A era da padronização consolidou a lição que os capítulos de protocolos vão repetir: **contrato vence convenção**. O function calling venceu porque transformou a chamada de ferramenta em uma garantia de API — nome, argumentos e schema declarados e validados —, em vez de depender de o modelo “se lembrar” de obedecer a um formato descrito no prompt. A mesma lógica se repete em cada nível: o JSON Schema é para o tool use o que o grounding foi para o RAG no capítulo 6 — a garantia de forma que permite confiar no transporte. E é essa a segunda lição, complementar e essencial: **garantia de forma não é garantia de conteúdo** — o contrato assegura que os campos existem e têm o tipo certo, mas não que o valor esteja certo; o sentido continua sendo responsabilidade do sistema, com validação própria. Contrato resolve a camada de transporte; o sistema resolve o resto. Essa separação é o que permite à camada de ferramentas virar commodity sem que o sistema perca rigor.

## Para o engenheiro

Use o function calling nativo em vez de forçar o modelo a “emitir JSON”. Declare as ferramentas no schema da API, deixe o provedor devolver a chamada estruturada e concentre o código na execução e no tratamento do resultado. Forçar formato por prompt é o caminho do capítulo 9: funciona, mas é frágil e depende do modelo “se lembrar” de obedecer.

Sempre que a saída for consumida por código, exija Structured Outputs — JSON Schema com `strict: true`. O parser da sua aplicação nunca mais quebra por JSON inválido. Mas não confunda garantia de schema com garantia de conteúdo: a estrutura é contratual, o sentido continua sendo responsabilidade do seu sistema, com validação e testes próprios.

Agrupe chamadas independentes em parallel function calling. Um loop que chama várias ferramentas uma a uma multiplica latência por round-trip; chamar em paralelo corta o tempo total. A regra é de custo: ferramentas independentes não precisam esperar umas pelas outras.

Computer use é sedutor, mas caro e frágil. A tela como ferramenta deve ser a última opção, reservada a ambientes sem API. Quando a integração estruturada existe — ou pode ser construída — ela é mais rápida, mais barata e mais confiável. Computer use resolve o problema de não ter API; não é uma forma melhor de resolver o que já tem.

Trate a camada de ferramentas como commodity em evolução. A interface padronizada não é um diferencial duradouro; é pré-requisito. O valor do sistema está na orquestração, nos dados e na verificação — e é para lá que os próximos capítulos apontam.

---

**Fontes:** [OpenAI, 2023] — ChatGPT plugins; function calling; DevDay; [Anthropic, 2023] — Claude 2.1; [Google, 2023] — Gemini API function calling; [OpenAI, 2024] — Structured Outputs; [Anthropic, 2024] — Computer use; [Berkeley Leaderboard, 2024] — avaliação de function calling; [Yao et al., 2024] — tau-bench; [Taskade, 2026] — timeline de tool use na indústria; [Konishi, 2026] — timeline de tool use e protocolos.
