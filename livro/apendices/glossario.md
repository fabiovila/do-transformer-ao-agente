# Glossário

Termos definidos no livro, com uma nota prática para quem implementa. Mantido em crescimento;
cada capítulo adiciona entradas.

## Fundamentos de modelos de linguagem

| Termo | Definição | Por que importa |
| --- | --- | --- |
| **Modelo de linguagem (LM)** | Sistema que atribui probabilidade a sequências de palavras; na forma autoregressiva, prevê a próxima palavra dado o contexto. | É a unidade básica: quase todo sistema moderno começa "prevê o próximo token" e adiciona contexto e ferramentas por fora. |
| **Modelo de linguagem de grande escala (LLM)** | LM baseado em Transformer, treinado em corpus massivo, com bilhões de parâmetros ou mais. | É o que você chama via API hoje; a escala é o que faz capacidades emergirem. |
| **Pré-treinamento** | Treinamento genérico autossupervisionado em texto; objetivo de prever tokens mascarados (BERT) ou a próxima palavra (GPT). | Rótulo grátis (o texto é o rótulo): é por isso que dá para treinar com a internet inteira. |
| **Fine-tuning** | Continuação do treinamento em dados específicos de uma tarefa. | É a alavanca quando zero-shot não basta; com LoRA custa uma fração do treino original. |
| **LoRA** | Adapta o modelo treinando só pequenas matrizes de low-rank (~1–2% dos parâmetros), deixando o resto congelado. | O padrão de ouro para customizar: um adaptador por cliente/tarefa, trocável sem re-treinar o base. |
| **Zero-shot / few-shot** | Executar tarefa sem exemplos / com poucos exemplos dados no prompt, sem atualizar pesos. | Teste isso antes de qualquer fine-tuning: é barato, reversível e cobre cada vez mais casos. |
| **In-context learning** | Capacidade de executar uma tarefa a partir apenas do conteúdo do prompt. | O prompt é código de produção: versionar, testar e monitorar como qualquer código. |
| **Embedding** | Vetor numérico que representa palavra/texto; captura similaridade semântica. | Base de todo RAG/busca semântica; a qualidade do embedding decide o teto do retrieval. |
| **Atenção** | Mecanismo que pondera a relevância entre posições; base do Transformer. | A ideia de "onde olhar" reusada em cross-attention, retrieval e agentes. |
| **Transformer** | Arquitetura baseada apenas em atenção, sem recorrência; proposta em 2017. | Todo modelo moderno que você consome é um Transformer. |
| **Encoder-only / Decoder-only / Encoder–decoder** | Famílias derivadas do Transformer: entendimento (BERT), geração causal (GPT), transformação (T5). | Escolha pela tarefa: classificar → encoder; chat/geração → decoder; tradução → encoder–decoder. |
| **Autoregressivo / causal** | Geração token a token, cada previsão olha só para trás. | Geradores não podem "ver o futuro": respeite isso ao montar prompts e fluxos. |
| **Embeddings posicionais** | Vetores que codificam a ordem das posições no input. | Reordenar input muda o significado; preserve ordem ao serializar documentos. |
| **Alucinação** | Geração de conteúdo factualmente incorreto com confiança. | O motivo central de RAG e ferramentas: ancorar a resposta em evidência externa. |
| **Leis de escala (Kaplan / Chinchilla)** | Relações que predizem perda/qualidade em função de parâmetros, tokens e FLOPs. | Use para dimensionar o modelo pelo orçamento, não pelo hype. |
| **Emergência** | Capacidade que "aparece" acima de certo tamanho de modelo. | Desconfie: muitas vezes é a métrica saturando, não uma habilidade nova real. |

## RAG e recuperação

| Termo | Definição | Por que importa |
| --- | --- | --- |
| **RAG (Retrieval-Augmented Generation)** | Paradigma que recupera evidência de uma fonte externa e a injeta no contexto antes de gerar. | O jeito padrão de dar conhecimento atualizado e auditável ao modelo. |
| **Retriever** | Componente que seleciona passagens/documentos de uma fonte externa. | Primeira linha do pipeline; é medido separadamente (recall@k, NDCG). |
| **Generator** | LLM que produz a resposta a partir de pergunta + evidências. | É medido por fidelidade: a resposta segue as evidências recuperadas? |
| **Memória paramétrica** | Conhecimento armazenado nos pesos do modelo (fixo após o treino). | Barata de usar, cara de atualizar; fonte das alucinações sobre dados recentes. |
| **Memória não-paramétrica (externa)** | Conhecimento armazenado fora do modelo, recuperado sob demanda (atualizável). | É o seu banco/índice: atualizar o conhecimento não exige re-treinar. |
| **Grounding** | Ancorar a resposta em evidência externa para reduzir alucinação. | Critério de qualidade de qualquer RAG em produção. |
| **Proveniência** | Capacidade de rastrear a fonte de uma afirmação. | Diferencia RAG de "adivinhação": sempre devolva a fonte junto da resposta. |
| **Top-k** | Número de passagens recuperadas/consideradas pelo retriever. | Hiperparâmetro clássico: k pequeno corta recall, k grande polui o contexto. |
| **BM25** | Ranking lexical por correspondência de termos (TF–IDF probabilístico). | Rápido e preciso para termos exatos; falha com paráfrases. |
| **Retrieval denso (ex.: DPR)** | Ranking por similaridade de embeddings de query e documento. | Captura paráfrase; precisa que encoders de query e documento sejam consistentes. |
| **Busca híbrida** | Combina scores lexicais e densos. | É o padrão de produção: você quer os dois, com peso combinado. |
| **Reranker (cross-encoder)** | Modelo que reordena o top-k olhando query+documento juntos. | Correção barata de ruído; quase sempre compensa a latência extra. |
| **Query rewriting / expansão** | Reescrever ou expandir a pergunta para melhorar a recuperação. | RAG avançado: o mesmo usuário mal-formula, o sistema reformula antes de buscar. |
| **HyDE** | Gera uma resposta hipotética e usa o embedding dela para buscar. | Truque de recall quando a pergunta e o documento não compartilham vocabulário. |
| **Chunking** | Divisão dos documentos em trechos indexáveis. | Decisão de qualidade barata: tamanho, sobreposição e quebra por seção importam mais que o índice. |
| **kNN-LM** | Aplica memória externa no nível do token, buscando vizinhos do contexto atual. | Mostrou que dá para recuperar no *nível do token*, não só no nível de documento. |
| **FiD** | Funde evidências no decoder, codificando cada passagem separadamente. | A saída quando o prompt não comporta concatenar muitas passagens. |
| **RETRO / REALM** | Recuperação aprendida *durante* o pré-treinamento. | Evidência de que retrieval pode ser parte do treino, não só da inferência. |
| **Self-RAG** | O modelo decide se recupera e critica suas próprias respostas via tokens de reflexão. | Torna a recuperação adaptativa: só busca quando necessário e auto-avalia a resposta. |
| **FLARE** | Recuperação ativa *durante* a geração quando a confiança do modelo cai. | Antecipa a busca no momento exato em que o modelo "não sabe", sem prompt manual. |
| **RAFT** | Modelo treinado a ignorar distratores e citar apenas fontes relevantes. | Ensina o modelo a filtrar ruído do retrieval — crucial para RAG robusto. |
| **Prompt caching** | Reutiliza a computação de atenção do prefixo do prompt em chamadas repetidas. | Corta latência e custo em chat multi-turno e agentes com prefixos fixos (system prompt). |

## Alinhamento e ferramentas

| Termo | Definição | Por que importa |
| --- | --- | --- |
| **Instruction tuning** | Fine-tuning em pares instrução→resposta para o modelo obedecer comandos. | Foi o que transformou "completar texto" em "assistente". |
| **RLHF** | Aprendizado por reforço a partir de feedback humano: SFT → reward model → RL. | O custo está nos dados de preferência, não na matemática. |
| **Reward model** | Modelo que pontua respostas; usado como sinal no RLHF. | Se for viesado, o modelo final herda o viés — avalie-o à parte. |
| **Alinhamento** | Ajuste para que o modelo siga intenções e valores humanos. | Defina o comportamento-alvo, não só a tarefa. |
| **Chain-of-Thought (CoT)** | Padrão de gerar passos intermediários de raciocínio antes da resposta. | Ferramenta de prompt barata para tarefas que exigem passos; custa tokens. |
| **Tool use** | Capacidade de um LLM invocar ferramentas externas (APIs, calculadoras, busca, código). | Quando um humano resolveria com ferramenta, o sistema deve ter a ferramenta. |
| **Function calling** | Primitiva de API em que o modelo retorna nome + argumentos de uma função. | Use o formato nativo do provedor em vez de "faça o modelo emitir JSON". |
| **Parallel function calling** | Múltiplas chamadas independentes numa só resposta do modelo. | Corta round-trips e latência do loop. |
| **JSON mode / Structured Outputs** | Garantia de que a saída obedece a um JSON Schema (ex.: `strict: true`). | Fim da era "o modelo devolveu JSON inválido": parser nunca mais quebra. |
| **Computer use** | Uso do computador inteiro (tela, teclado) como ferramenta. | Reserve para ambientes sem API; para produção, prefira integrações estruturadas. |
| **MRKL** | Roteia partes da pergunta para ferramentas específicas (calculadora, banco…). | Molde mental de *roteamento*: nem toda pergunta vai para o modelo. |
| **PAL** | O modelo escreve o código e a máquina executa a resposta. | Delegue matemática e lógica exata a código em vez de pedir ao modelo que calcule. |
| **Toolformer** | Aprende sozinho, por auto-supervisão, quando chamar cada API. | Em 2026, o function calling nativo cobre a maioria dos casos que ele demonstrou. |

## Agentes e avaliação

| Termo | Definição | Por que importa |
| --- | --- | --- |
| **ReAct** | Padrão que intercala raciocínio (Thought) e ação (Action) com observações, em loop. | A *forma* de todo agente: desenhe agentes nesse molde. |
| **Agente (LLM-based)** | Sistema em que o modelo participa de um ciclo observar → raciocinar → agir → observar → validar. | O poder vem do loop, não do modelo isolado. |
| **Loop de agente** | Ciclo de decisão-ação com observação e condição de parada. | Sem critério de parada, o custo explode — define `max_iterations` antes de rodar. |
| **Observabilidade** | Capacidade de ver o que o agente pensou, chamou e observou. | É o que permite debugar e reexecutar; logue sempre. |
| **Multi-agente** | Sistema com múltiplos agentes com papéis, comunicação e coordenação. | Vale quando há divisão real de trabalho; senão, um loop bem feito ganha. |
| **Chatter** | Agentes conversando sem produzir nada. | Evite com artefatos estruturados e papéis claros, em vez de mensagens soltas. |
| **AgentBench / WebArena / OSWorld** | Benchmarks que colocam agentes em ambientes realistas (web, terminal, desktop). | Pontos de partida para avaliação; crie a sua suite de tarefas reais. |
| **tau-bench** | Bench de tarefas realistas (viajens, atendimento) com avaliação multi-turno. | Mostrou o dado incômodo: modelos fortes falham na maioria das tarefas. |
| **Consistência** | Estabilidade do agente entre tentativas da mesma tarefa. | Acertar 1 em 3 não é produção: meça pass@k e variabilidade. |
| **LLM-as-judge** | Uso de um modelo para avaliar respostas. | Barato e viesado: rubrica explícita + amostra humana de calibração. |
| **Guardrails** | Mecanismos que validam saídas, impõem segurança e mantêm integridade de fluxos. | Camada de produção: valide schema, alcance e políticas antes de liberar a saída. |

## Protocolos e sistema

| Termo | Definição | Por que importa |
| --- | --- | --- |
| **MCP (Model Context Protocol)** | Protocolo aberto para conectar modelos a ferramentas/dados (modelo ↔ mundo). | Elimina integrações N×M: exponha uma vez, consuma de qualquer cliente. |
| **tools / resources / prompts (MCP)** | As três primitivas do MCP: ações, dados e receitas prontas. | Se o seu domínio não cabe nessas três, talvez não precise de MCP. |
| **A2A (Agent2Agent)** | Protocolo aberto para interoperabilidade entre agentes (agente ↔ agente). | Agentes de vendors diferentes conversam sem integração ponto a ponto. |
| **Estateless protocol** | Protocolo que não mantém estado entre chamadas. | Persistência é responsabilidade sua (banco, memória, cache). |
| **Loop cognitivo** | Síntese do livro: objetivo → observar → raciocinar → agir → observar → validar → atualizar. | Use como checklist de arquitetura: cada peça precisa de um dono no seu código. |
