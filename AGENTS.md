# AGENTS.md

# Guia Didático para Sistemas de Linguagem, RAG, Agentes e Ferramentas

## 0. Propósito

Este arquivo estabelece uma orientação conceitual e operacional para trabalhar com modelos de linguagem modernos.

Não trate um modelo de linguagem como apenas um sistema que recebe texto e produz texto.

Um sistema moderno baseado em LLM pode ser visto como:

```text
                    ┌─────────────────────┐
                    │   Modelo de linguagem│
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
          Memória            Tools             Contexto
             │                 │                  │
             ▼                 ▼                  ▼
           RAG              Shell             Arquivos
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ▼
                         Iteração / Loop
                               │
                               ▼
                           Verificação
                               │
                               ▼
                            Resultado
```

O objetivo deste documento é ensinar o agente a raciocinar sobre esse sistema.

A pergunta principal não deve ser:

> "Qual resposta devo produzir?"

mas:

> "Qual processo produz uma resposta confiável para este problema?"

---

# 1. Modelo mental fundamental

Uma LLM é um componente probabilístico de inferência dentro de um sistema maior.

O comportamento final pode ser aproximadamente entendido como:

```text
modelo
+
contexto
+
memória
+
ferramentas
+
ambiente
+
feedback
+
iterações
=
sistema inteligente
```

Portanto, não atribua automaticamente ao modelo uma capacidade que pertence ao sistema.

Por exemplo:

* RAG não é "memória do modelo".
* Search não é "conhecimento do modelo".
* Shell não é "raciocínio do modelo".
* Um teste não é "conhecimento do modelo".
* Um arquivo não é "contexto permanente".
* Uma ferramenta não é "uma resposta".
* Uma sequência de iterações não é equivalente a uma única inferência.

O agente deve distinguir sempre entre:

```text
o que eu sei
o que está no contexto
o que posso consultar
o que posso calcular
o que posso executar
o que posso verificar
```

---

# 2. Inferência não é apenas geração

Uma geração simples é:

```text
input → model → output
```

Um sistema agentic normalmente se parece mais com:

```text
        ┌──────────────┐
        │    objetivo  │
        └──────┬───────┘
               ▼
          interpretar
               │
               ▼
           planejar
               │
               ▼
          agir / buscar
               │
               ▼
          observar
               │
               ▼
          avaliar
          /       \
       correto?   não
         │          │
        sim         ▼
         │       corrigir
         │          │
         └──────────┘
               │
               ▼
            finalizar
```

O poder adicional vem do **loop**.

Uma resposta errada pode ser corrigida.

Uma hipótese pode ser testada.

Um código pode ser executado.

Um documento pode ser pesquisado.

Um arquivo pode ser editado.

Uma afirmação pode ser confrontada com evidências.

Assim, quando um problema permite interação com o ambiente, não se deve tentar resolver tudo em uma única geração.

---

# 3. RAG

## 3.1 O que é RAG

RAG significa Retrieval-Augmented Generation.

A ideia básica é:

```text
pergunta
   ↓
retrieval
   ↓
evidências
   ↓
contexto
   ↓
LLM
   ↓
resposta
```

Mas isso é uma simplificação.

Um RAG robusto possui pelo menos quatro problemas distintos:

```text
1. recuperar
2. selecionar
3. interpretar
4. inferir
```

Recuperar informação relevante não significa necessariamente saber utilizá-la.

---

## 3.2 RAG não é apenas vector search

Não assuma:

```text
embedding → top-k → prompt → resposta
```

como definição de RAG.

Dependendo do problema, retrieval pode envolver:

* busca semântica;
* busca lexical;
* filtros estruturados;
* metadados;
* busca híbrida;
* reranking;
* expansão da consulta;
* decomposição da pergunta;
* navegação por referências;
* recuperação iterativa.

A pergunta correta é:

> "Qual mecanismo de recuperação maximiza a evidência útil para esta tarefa?"

e não:

> "Qual banco vetorial devo usar?"

---

# 4. Retrieval e raciocínio são problemas diferentes

Considere:

```text
Documento A:
Pedro comprou X em janeiro.

Documento B:
Compras acima de R$ 1.000 recebem desconto.

Documento C:
Pedro pagou R$ 1.200 por X.
```

A pergunta:

> Pedro recebeu desconto?

não exige apenas encontrar documentos.

É necessário:

```text
A → identifica a compra
C → identifica o valor
B → fornece a regra
```

Depois:

```text
R$ 1.200 > R$ 1.000
```

e então:

```text
conclusão → Pedro deveria receber desconto
```

Portanto:

```text
retrieval ≠ inference
```

Um sistema de RAG sofisticado deve considerar os dois.

---

# 5. RAG como construção de evidência

Uma visão mais útil é:

```text
query
  ↓
evidence acquisition
  ↓
evidence organization
  ↓
evidence reasoning
  ↓
answer
```

A resposta deve ser consequência de evidências suficientes.

Quando possível, o agente deve perguntar internamente:

```text
Qual afirmação estou tentando sustentar?

Qual evidência suporta essa afirmação?

Há evidência contraditória?

Estou extrapolando além da evidência?

A conclusão é dedutiva, indutiva ou apenas plausível?
```

---

# 6. Search

Search é uma ferramenta de aquisição de informação.

Não deve ser confundida com conhecimento.

A operação:

```text
search("X")
```

não significa:

```text
X é verdadeiro
```

Significa:

```text
encontrei fontes que podem conter evidências sobre X
```

Portanto, search deve normalmente ser seguido por:

```text
buscar
→ inspecionar
→ comparar
→ validar
→ utilizar
```

Não faça:

```text
buscar
→ primeira resposta
→ acreditar
```

---

# 7. Search iterativo

Consultas frequentemente precisam evoluir.

Um processo útil é:

```text
query inicial
    ↓
resultados
    ↓
identificar lacunas
    ↓
query mais específica
    ↓
novos resultados
    ↓
comparar
    ↓
concluir
```

A segunda busca deve ser informada pelo resultado da primeira.

Isso transforma search de uma operação estática em uma forma rudimentar de raciocínio exploratório.

---

# 8. Agents

"Agent" não deve ser tratado como uma entidade misteriosa.

Um agente é, essencialmente, um sistema no qual o modelo participa de um ciclo de decisão e ação.

Uma abstração simples:

```text
while not done:

    observe()
    reason()
    choose_action()
    execute()
    evaluate()
```

A ação pode ser:

```text
search
read
write
edit
shell
calculate
call API
ask user
```

O agente ganha capacidade porque pode modificar o estado do mundo e observar o resultado.

---

# 9. Agentic ≠ apenas mais prompts

Adicionar:

```text
"Você é um agente autônomo..."
```

não cria necessariamente um agente.

Agentic behavior emerge quando existe:

```text
objetivo
+
estado
+
ações
+
observações
+
feedback
+
critério de término
```

Um sistema sem capacidade de observar os efeitos das próprias ações possui autonomia muito limitada.

---

# 10. Iteration

Iteration é um dos mecanismos mais importantes de sistemas agentic.

Uma única tentativa:

```text
input → output
```

pode falhar.

Uma sequência:

```text
tentativa
→ avaliação
→ correção
→ nova tentativa
→ avaliação
→ ...
```

pode convergir.

Por isso, quando houver um mecanismo objetivo de verificação, prefira:

```text
generate → test → repair
```

a:

```text
generate → hope
```

---

# 11. Iteração precisa de feedback

Iterar sem informação nova pode simplesmente repetir o erro.

Portanto:

```text
iteration ≠ repetir
```

Iteração útil significa:

```text
ação
→ observação
→ informação nova
→ atualização
→ ação
```

O feedback pode vir de:

* testes;
* compiladores;
* execução;
* search;
* documentos;
* validação;
* comparação;
* usuário;
* métricas;
* regras formais.

---

# 12. Shell

Shell transforma o modelo em um sistema capaz de interagir com um ambiente computacional.

Em vez de:

```text
"acho que o código funciona"
```

o agente pode:

```text
executar
→ observar
→ corrigir
→ executar novamente
```

Isso é epistemicamente importante.

A execução fornece evidência externa ao próprio modelo.

---

# 13. Shell como instrumento de verificação

Quando uma propriedade pode ser testada por execução, prefira testar.

Exemplo:

```text
modelo:
"Esse programa deve produzir X."

shell:
executar programa

resultado:
Y
```

Agora existe uma discrepância observável.

O agente deve atualizar seu estado:

```text
hipótese inicial ≠ observação
```

e investigar a causa.

Não trate a saída do modelo como autoridade quando existe uma maneira barata de verificar a afirmação.

---

# 14. Read antes de Edit

Antes de modificar um artefato:

```text
read
→ understand
→ edit
```

não:

```text
guess
→ overwrite
```

Arquivos possuem contexto, convenções e dependências que podem não estar presentes no prompt.

O agente deve preservar:

* comportamento existente;
* interfaces;
* convenções;
* dependências;
* comentários relevantes;
* testes;
* compatibilidade.

Uma edição boa é uma transformação mínima que produz a mudança desejada.

---

# 15. Edit como transformação

Considere um arquivo como um estado:

```text
S₀
```

e a alteração desejada como uma função:

```text
f(S₀) = S₁
```

O objetivo não é simplesmente produzir um novo texto.

É produzir:

```text
S₁ = S₀ + mudança necessária
```

preservando tudo aquilo que não deveria mudar.

Portanto:

> Quanto menor a mudança suficiente para satisfazer o objetivo, menor o espaço de regressão.

---

# 16. Search, Read, Edit e Shell formam um ciclo

Uma grande parte do trabalho de engenharia pode ser representada por:

```text
        ┌───────────┐
        │   Search  │
        └─────┬─────┘
              ↓
        ┌───────────┐
        │    Read   │
        └─────┬─────┘
              ↓
        ┌───────────┐
        │    Edit   │
        └─────┬─────┘
              ↓
        ┌───────────┐
        │   Shell   │
        └─────┬─────┘
              ↓
        ┌───────────┐
        │ Evaluate  │
        └─────┬─────┘
              │
              └──────→ próxima iteração
```

Esse ciclo é muito mais importante que qualquer ferramenta isolada.

---

# 17. Ferramentas como extensões cognitivas

Não pense em tools apenas como "funções que o modelo pode chamar".

Uma ferramenta fornece uma capacidade que o modelo sozinho não possui ou possui de forma pouco confiável.

Exemplos:

```text
Search      → aquisição de informação
RAG         → recuperação contextual
Shell       → experimentação
Calculator  → computação exata
Code runner → execução
Filesystem  → memória externa / estado
Browser     → observação do mundo
Tests       → verificação
Compiler    → verificação formal parcial
```

A arquitetura passa a ser:

```text
modelo
   ↓
decisão
   ↓
ferramenta
   ↓
observação
   ↓
nova decisão
```

Isso é uma forma de cognição distribuída entre modelo e ambiente.

---

# 18. Context engineering

Prompt engineering é apenas uma parte do problema.

Em sistemas complexos, a pergunta mais importante é:

> "Qual informação deve estar presente no contexto neste momento?"

O contexto pode conter:

```text
instruções
documentos
resultados de search
estado do ambiente
histórico
saídas de ferramentas
restrições
exemplos
memória
```

Mais contexto não significa necessariamente melhor contexto.

O objetivo é:

```text
maximizar informação relevante
minimizar ruído
```

---

# 19. Contexto como recurso limitado

Trate o contexto como uma memória de trabalho.

Uma boa política é:

```text
informação relevante
+
estado necessário
+
evidência necessária
-
redundância
-
ruído
-
histórico inútil
```

Quando o contexto cresce demais, o agente deve considerar:

```text
summarization
compression
retrieval
reorganization
discarding
```

---

# 20. Memória

Diferencie:

```text
contexto
```

de:

```text
memória
```

Contexto é o que está disponível agora.

Memória é informação preservada para uso futuro.

Uma memória útil deve responder:

> "O que vale a pena preservar porque provavelmente será útil novamente?"

Não transforme todo histórico em memória.

Memória indiscriminada produz ruído, contradições e contexto desnecessário.

---

# 21. Planejamento

Planejamento não significa necessariamente produzir uma lista enorme de passos antes de agir.

Um planejamento útil é adaptativo:

```text
objetivo
→ próximo passo informativo
→ observação
→ atualização do plano
→ próximo passo
```

Em ambientes desconhecidos, planejar tudo antecipadamente pode ser inferior a planejar incrementalmente.

Uma boa pergunta é:

> "Qual próxima ação reduz mais a incerteza?"

---

# 22. Informação versus ação

Antes de executar uma ação, considere:

```text
Qual informação falta?

Posso obtê-la mais barato?

A ação é reversível?

Qual é o custo de errar?

Existe uma forma de testar primeiro?
```

Especialmente para ações destrutivas, prefira:

```text
inspect
→ validate
→ act
```

em vez de:

```text
act
→ descobrir o que aconteceu
```

---

# 23. Verificação

Um sistema inteligente deve possuir mecanismos que não dependam exclusivamente da mesma inferência que produziu o resultado.

Em termos simples:

```text
generator
    ↓
candidate
    ↓
verifier
    ↓
accept / reject / repair
```

O verificador pode ser:

* teste unitário;
* execução;
* regra lógica;
* comparação com fonte;
* cálculo independente;
* outro modelo;
* validação estrutural;
* humano.

Quanto mais independente for o mecanismo de verificação, maior tende a ser seu valor.

---

# 24. Generator ≠ Verifier

Não suponha que:

```text
o modelo produziu X
```

implique:

```text
X está correto
```

O modelo deve produzir hipóteses.

O ambiente, ferramentas ou verificadores devem fornecer evidência adicional.

Um sistema robusto explora essa separação:

```text
propor
→ verificar
→ corrigir
```

---

# 25. Self-reflection deve ser usada com cuidado

"Reflita sobre sua resposta" pode ajudar, mas reflexão produzida pelo mesmo modelo não constitui necessariamente verificação independente.

Existe uma diferença entre:

```text
modelo:
"acho que minha resposta está correta."
```

e:

```text
teste:
resultado = sucesso
```

Prefira evidência objetiva quando disponível.

Self-critique é útil principalmente quando não existe um verificador externo barato.

---

# 26. Raciocínio como transformação de estado

Uma maneira poderosa de pensar sobre problemas complexos é:

```text
estado inicial
      ↓
operação
      ↓
novo estado
      ↓
operação
      ↓
novo estado
      ↓
...
      ↓
estado objetivo
```

Isso conecta:

```text
reasoning
planning
tool use
agentics
iteration
```

O agente não precisa necessariamente "saber a resposta".

Ele precisa saber:

```text
qual estado possui
qual estado deseja
qual ação pode aproximá-lo do objetivo
como saber se a ação funcionou
```

---

# 27. Generalização

Não treine ou avalie apenas instâncias específicas.

Procure estruturas reutilizáveis.

Por exemplo:

```text
problema A
problema B
problema C
```

podem ser instâncias de:

```text
estrutura X
```

O objetivo didático deve ser ensinar:

```text
estrutura X
```

e não apenas memorizar:

```text
A, B, C
```

Quando possível, varie:

* vocabulário;
* domínio;
* tamanho;
* ordem;
* representação;
* superfície textual;
* fontes;
* combinação de ferramentas.

Mantenha constante a estrutura que realmente interessa aprender.

---

# 28. Aprender regras em vez de apenas exemplos

Quando for possível gerar dados sinteticamente, considere:

```text
regra abstrata
      ↓
gerador
      ↓
muitas instâncias
      ↓
treinamento
      ↓
generalização
```

Isso é particularmente poderoso para:

* lógica;
* transformação de dados;
* planejamento;
* uso de ferramentas;
* recuperação;
* classificação;
* programação;
* verificação.

A quantidade de exemplos pode então vir da combinação de estruturas, e não da coleta manual de casos reais.

---

# 29. Composição

Uma capacidade importante de sistemas modernos é combinar capacidades simples.

Por exemplo:

```text
search
+
RAG
+
reasoning
+
shell
+
verification
```

pode produzir uma capacidade que não existe em nenhuma ferramenta isoladamente.

Isso sugere uma regra:

> Não avalie uma ferramenta apenas pela capacidade que ela possui isoladamente; avalie também quais processos ela torna possíveis quando combinada com outras.

---

# 30. Tool selection

O agente deve escolher ferramentas pelo ganho esperado.

Uma heurística:

```text
Se posso responder com segurança → responda.

Se falta informação factual → search/RAG.

Se preciso de informação específica em documentos → retrieval.

Se preciso modificar um artefato → read/edit.

Se preciso testar comportamento → shell/test.

Se preciso de precisão matemática → calculator/code.

Se há incerteza relevante → buscar evidência.

Se há risco de dano ou alteração irreversível → validar antes.
```

Não use ferramentas apenas porque estão disponíveis.

Tool use também possui custo.

---

# 31. Custo da inferência

Cada ação possui custo:

```text
tempo
tokens
latência
complexidade
risco
```

O objetivo não é maximizar o número de ferramentas utilizadas.

É maximizar:

```text
qualidade da decisão
/
custo total
```

Um bom agente sabe quando **não** usar uma ferramenta.

---

# 32. Quando parar

Um agente precisa de um critério de término.

Possíveis critérios:

```text
objetivo satisfeito
+
evidência suficiente
+
verificação concluída
```

Não continue iterando apenas porque ainda é possível fazer alguma coisa.

O processo deve terminar quando o benefício marginal da próxima ação for pequeno.

Uma heurística:

```text
expected_information_gain
>
cost_of_action
```

Se não:

```text
stop
```

---

# 33. Erros

Classifique o erro antes de corrigi-lo.

Um erro pode ser:

```text
retrieval error
reasoning error
tool-selection error
execution error
interpretation error
context error
memory error
verification error
```

Corrigir o tipo errado de erro desperdiça iterações.

Exemplo:

```text
resposta errada
```

não significa necessariamente:

```text
raciocínio ruim
```

Pode significar:

```text
documento errado foi recuperado.
```

---

# 34. Observabilidade

Sistemas agentic devem tornar possível responder:

```text
O que o agente tentou fazer?

Por quê?

Qual informação utilizou?

Qual ferramenta chamou?

Qual foi o resultado?

O que mudou depois?

Por que terminou?
```

Isso é essencial para debugging.

Uma sequência de ações deve ser tratada como um traço observável:

```text
state₀
→ action₁
→ observation₁
→ state₁
→ action₂
→ observation₂
→ state₂
```

---

# 35. Segurança e reversibilidade

Quanto maior o impacto da ação, maior deve ser o nível de verificação.

Uma ação pode ser classificada aproximadamente como:

```text
informativa
→ reversível
→ potencialmente destrutiva
→ irreversível
```

Quanto mais irreversível:

```text
mais inspeção
mais confirmação
mais validação
```

Ferramentas poderosas exigem mais disciplina, não menos.

---

# 36. O agente como sistema experimental

Uma forma particularmente útil de pensar sobre agentics é como experimentação.

O agente possui uma hipótese:

```text
H
```

executa uma ação:

```text
A
```

observa:

```text
O
```

e atualiza sua hipótese:

```text
H → H'
```

Então:

```text
hypothesis
→ experiment
→ observation
→ update
```

Esse ciclo conecta agentes a uma ideia muito mais ampla de inteligência:

> agir sobre o mundo para obter informação e utilizar essa informação para melhorar a próxima ação.

---

# 37. O verdadeiro loop cognitivo

Uma abstração geral para sistemas de linguagem modernos é:

```text
             ┌───────────────────────┐
             │       OBJECTIVE       │
             └───────────┬───────────┘
                         ↓
                  ┌──────────────┐
                  │   OBSERVE    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │    MODEL     │
                  │    STATE     │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │    REASON    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │    ACT       │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   OBSERVE    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   VERIFY     │
                  └──────┬───────┘
                         │
                 ┌───────┴───────┐
                 │               │
               FAIL            PASS
                 │               │
                 ↓               ↓
              UPDATE          FINISH
                 │
                 └──────→ LOOP
```

RAG, search, shell, edit e tools são mecanismos diferentes dentro desse ciclo.

---

# 38. Princípio de ouro

Não pergunte apenas:

> "O modelo consegue fazer isso?"

Pergunte:

> "Que combinação de modelo, contexto, ferramentas, ambiente, memória, feedback e verificação torna isso possível de maneira confiável?"

Essa mudança de perspectiva é fundamental.

---

# 39. Como ensinar um agente

Ao explicar uma tarefa para um agente, prefira ensinar:

```text
objetivo
restrições
estado relevante
ferramentas disponíveis
critérios de sucesso
métodos de verificação
```

em vez de fornecer apenas uma sequência rígida de ações.

Uma instrução rígida:

```text
faça A
depois B
depois C
```

pode falhar quando o ambiente mudar.

Uma instrução orientada a objetivo:

```text
obtenha X
usando as fontes disponíveis
e verifique Y
antes de finalizar
```

permite adaptação.

---

# 40. Como construir exemplos para treinamento

Quando produzir dados para treinamento, procure separar:

```text
conteúdo
```

de:

```text
estrutura
```

Sempre que possível:

```text
estrutura abstrata
→ instanciação automática
→ perturbação
→ solução
→ verificação
```

Exemplos devem variar o suficiente para impedir que o modelo memorize superficialmente.

Uma boa bateria de avaliação deve conter:

```text
casos conhecidos
+
casos novos
+
combinações novas
+
casos adversariais
+
casos fora da distribuição
```

A verdadeira pergunta é:

> O sistema aprendeu a regra ou apenas reconheceu o padrão superficial?

---

# 41. Avaliação

Não avalie somente a resposta final.

Avalie também:

```text
retrieval
tool selection
planning
reasoning
execution
verification
final answer
```

Uma resposta correta obtida por acaso é diferente de um processo robusto.

Quando possível, meça:

```text
accuracy
robustness
cost
latency
tool efficiency
failure recovery
generalization
```

---

# 42. RAG + Agent + Tools

Uma arquitetura conceitual completa pode ser:

```text
                         USER
                          │
                          ▼
                    ┌───────────┐
                    │   AGENT   │
                    └─────┬─────┘
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
           SEARCH         RAG         MEMORY
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                     REASONING
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
           SHELL         EDIT        APIs
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                      OBSERVE
                          │
                          ▼
                      VERIFY
                          │
                    ┌─────┴─────┐
                    │           │
                  FAIL        SUCCESS
                    │           │
                    ▼           ▼
                  LOOP        ANSWER
```

Esse é o tipo de sistema ao qual o termo "modelo de linguagem" já não descreve adequadamente todo o fenômeno.

---

# 43. Princípios operacionais para o agente

Ao trabalhar, siga estas heurísticas:

```text
1. Entenda o objetivo antes da ação.

2. Separe conhecimento de evidência.

3. Quando faltar informação, busque-a.

4. Quando houver documentos, leia-os antes de inferir.

5. Quando uma conclusão puder ser testada, teste.

6. Quando uma alteração puder ser verificada, verifique.

7. Prefira mudanças mínimas e reversíveis.

8. Use ferramentas pelo ganho que proporcionam.

9. Não confunda geração com verificação.

10. Não confunda retrieval com reasoning.

11. Não confunda contexto com memória.

12. Não confunda reflexão com validação independente.

13. Use iteração quando houver feedback útil.

14. Pare quando o objetivo estiver suficientemente verificado.

15. Quando errar, identifique primeiro a classe do erro.

16. Ao enfrentar um problema novo, procure a estrutura abstrata por trás dele.

17. Prefira processos que generalizam a receitas que apenas funcionam para um caso.

18. Sempre que possível, transforme uma tarefa subjetiva em uma propriedade verificável.

19. Quando uma ferramenta puder produzir evidência melhor que uma inferência do modelo, use a ferramenta.

20. O objetivo não é produzir mais tokens; é produzir uma decisão melhor.
```

---

# 44. Princípio final

Um sistema baseado em LLM deve ser entendido menos como:

```text
pergunta → resposta
```

e mais como:

```text
objetivo
   ↓
estado
   ↓
informação
   ↓
hipótese
   ↓
ação
   ↓
observação
   ↓
verificação
   ↓
atualização
   ↓
nova ação
   ↓
...
   ↓
resultado
```

A LLM é o núcleo de inferência linguística desse processo.

Mas a inteligência efetiva do sistema emerge da combinação:

```text
MODEL
+
CONTEXT
+
RETRIEVAL
+
TOOLS
+
ENVIRONMENT
+
MEMORY
+
ITERATION
+
VERIFICATION
```

O desenvolvimento de sistemas de linguagem deve, portanto, migrar progressivamente da pergunta:

> "Como faço o modelo responder melhor?"

para:

> "Como construo um processo no qual o modelo possa perceber, buscar, raciocinar, agir, verificar e corrigir?"

Essa é a perspectiva operacional adotada por este projeto.

