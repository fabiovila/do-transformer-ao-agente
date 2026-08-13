# NOTAS — Manutenção do livro

Instruções operacionais para futuras sessões que trabalhem neste livro. Leia antes de editar.

## Como este livro é gerido

- O livro vive em `livro/`, em Markdown, organizado por eras cronológicas.
- `README.md` é a porta de entrada e contém o **estado do livro** (checkbox). Atualize-o ao concluir capítulos.
- `SUMARIO.md` é a fonte da verdade da estrutura. Capítulos novos começam aqui.
- `cronologia.md` é a linha do tempo dos marcos; toda data relevante deve estar registrada lá.
- `fontes.md` é a bibliografia; todo capítulo cita códigos aqui (ex.: `[Vaswani et al. 2017]`).
- `NOTAS.md` (este arquivo) descreve o workflow.

## Formato dos capítulos

Cada capítulo em `capitulos/` segue a mesma estrutura:

```markdown
# N — Título

Abertura em prosa: situa o capítulo na história — o problema que a era enfrentava, o porquê e o
que se ambicionava. (Não há subseções "Objetivo/Contexto/Ideia"; a abertura faz esse papel.)

## <seções temáticas>
O corpo. Cada seção desenvolve uma estrutura ou ideia; jargão técnico é definido na primeira
ocorrência; diagramas ASCII quando ajudam.

## A lição estrutural
Seção final do corpo (imediatamente antes do engbox) que sintetiza a herança conceitual da era; obrigatória em todos os capítulos, sempre com este nome.

## Para o engenheiro
Quadro final (engbox) com takeaways práticos: decisões, armadilhas, o que implementar.

---

**Fontes:** [Autor, ano] — descrição curta; [Autor, ano] — ...
```

### Regras de escrita

1. **Didático**: explique do zero; não assuma conhecimento prévio de redes neurais além de conceitos básicos.
2. **Verificável**: afirmações factuais citam `[Fonte, ano]`. Não invente datas ou números.
3. **Estrutural**: ensine a estrutura que se repete, não apenas o caso concreto.
4. **Em português**: o livro é em português; termos técnicos podem manter o original (ex.: *few-shot*, *grounding*).
5. **Sem jargão não definido**: a primeira ocorrência de um termo técnico recebe definição.
6. **Diagramas**: prefira diagramas ASCII simples (o estilo usado em AGENTS.md).

## Workflow de escrita

1. Ao iniciar uma sessão, leia `README.md` (estado) e `SUMARIO.md` (estrutura).
2. Escolha um capítulo pendente (mais antigo primeiro).
3. Antes de escrever, consulte `cronologia.md` e `fontes.md` para o período.
4. Escreva o capítulo respeitando o formato acima.
5. Atualize `README.md` (estado) e marque o capítulo como feito.
6. Se descobrir fontes novas, registre-as em `fontes.md` e a data em `cronologia.md`.

## Verificação de fatos

- Datas de papers: usar primeira publicação (arXiv). Conferir se a URL está acessível.
- Datas de produtos: anúncio oficial; cruzar com ao menos uma segunda fonte.
- Não afirmar números de parâmetros/tokens sem fonte.
- Se uma data divergir entre fontes, registrar a divergência e escolher a mais confiável.

## Contexto e ferramentas

- Use web search para atualizar o período recente (2025–2026) — o campo muda rápido.
- Sempre que um número ou data for crítico para a narrativa, verifique-o antes de publicar no capítulo.
- Capítulos ainda não escritos podem conter apenas o cabeçalho e a seção "Fontes" como esqueleto.

## Próximos passos sugeridos

1. Revisão cruzada de datas e fontes: conferir `cronologia.md` contra `fontes.md` e as citações dos capítulos.
2. Consolidação e formatação final do livro (a revisão estilística geral já foi feita).
