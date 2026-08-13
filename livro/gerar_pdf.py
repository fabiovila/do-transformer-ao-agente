#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte o livro (Markdown) em um PDF via XeLaTeX."""

import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_TEX = os.path.join(BASE, "livro.tex")
OUT_PDF = os.path.join(BASE, "livro.pdf")

COUNTER = {"bmk": 0, "part": 0}


# ----------------------------------------------------------------------------
# Inline markdown -> LaTeX
# ----------------------------------------------------------------------------

def escape(text):
    out = []
    for c in text:
        if c == "\\":
            out.append(r"\textbackslash{}")
        elif c == "{":
            out.append(r"\{")
        elif c == "}":
            out.append(r"\}")
        elif c == "$":
            out.append(r"\$")
        elif c == "&":
            out.append(r"\&")
        elif c == "#":
            out.append(r"\#")
        elif c == "_":
            out.append(r"\_")
        elif c == "%":
            out.append(r"\%")
        elif c == "^":
            out.append(r"\textasciicircum{}")
        elif c == "~":
            out.append(r"\textasciitilde{}")
        else:
            out.append(c)
    return "".join(out)


def inline(text):
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "`":
            j = text.find("`", i + 1)
            if j != -1:
                out.append(r"\texttt{" + escape(text[i + 1:j]) + "}")
                i = j + 1
                continue
        if c == "*" and text[i:i + 2] == "**":
            j = text.find("**", i + 2)
            if j != -1:
                out.append(r"\textbf{" + inline(text[i + 2:j]) + "}")
                i = j + 2
                continue
        if c == "*":
            j = text.find("*", i + 1)
            if j != -1:
                inner = text[i + 1:j]
                if inner and not inner[0].isspace() and not inner[-1].isspace():
                    out.append(r"\textit{" + inline(inner) + "}")
                    i = j + 1
                    continue
        if c == "[":
            m = re.match(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)", text[i:])
            if m:
                out.append(r"\href{" + m.group(2) + "}{" + inline(m.group(1)) + "}")
                i += m.end()
                continue
        if c in "hw":
            m = re.match(r"(https?://|www\.)[^\s]+", text[i:])
            if m:
                url = m.group(0).rstrip(".,;:)]}")
                out.append(r"\url{" + url + "}")
                i += m.end()
                continue
        out.append(escape(c))
        i += 1
    return "".join(out)


# ----------------------------------------------------------------------------
# Markdown blocks -> LaTeX
# ----------------------------------------------------------------------------

HEADER_RE = re.compile(r"^(#{1,4})\s+(.*)$")
CODE_RE = re.compile(r"^```")
HR_RE = re.compile(r"^-{3,}\s*$")
TABLE_RE = re.compile(r"^\s*\|")
QUOTE_RE = re.compile(r"^>")
UNORD_RE = re.compile(r"^([ \t]*)([-*])\s+(.*)$")
ORD_RE = re.compile(r"^([ \t]*)(\d+)\.\s+(.*)$")


def is_list_line(line):
    return bool(UNORD_RE.match(line) or ORD_RE.match(line))


def heading(level, title):
    if level == 1:
        COUNTER["bmk"] += 1
        k = COUNTER["bmk"]
        return ("\n\\chapter*{%s}\n\\phantomsection\n"
                "\\addcontentsline{toc}{chapter}{%s}\n"
                "\\pdfbookmark[1]{%s}{cap:%d}\n" % (title, title, title, k))
    if level == 2:
        COUNTER["bmk"] += 1
        k = COUNTER["bmk"]
        return ("\n\\section*{%s}\n\\phantomsection\n"
                "\\addcontentsline{toc}{section}{%s}\n"
                "\\pdfbookmark[2]{%s}{sec:%d}\n" % (title, title, title, k))
    if level == 3:
        return ("\n\\subsection*{%s}\n\\phantomsection\n"
                "\\addcontentsline{toc}{subsection}{%s}\n" % (title, title))
    return "\n\\subsubsection*{%s}\n" % title


def render_table(rows):
    parsed = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        parsed.append(cells)

    sep_idx = None
    for idx, cells in enumerate(parsed):
        if cells and all(re.match(r"^:?-+:?$", c) for c in cells):
            sep_idx = idx
            break

    if sep_idx is not None:
        header = parsed[sep_idx - 1] if sep_idx > 0 else []
        data = parsed[sep_idx + 1:]
    else:
        header, data = parsed[0], parsed[1:]

    allrows = ([header] if header else []) + data
    ncols = max((len(r) for r in allrows), default=0)
    if ncols == 0:
        return ""

    col_max = [1] * ncols
    for ridx, cells in enumerate(allrows):
        is_hdr = ridx == 0 and bool(header)
        for k in range(ncols):
            cell = cells[k] if k < len(cells) else ""
            w = len(cell)
            if is_hdr:
                w = int(w * 1.75) + 1  # cabeçalho em negrito é mais largo que a estimativa
            col_max[k] = max(col_max[k], w)
    total = float(sum(col_max))
    # tabcolsep (4pt = ~0.017 de linewidth por coluna) e regras verticais
    # consomem largura fora das colunas p{}: deixe espaço reservado.
    overhead = ncols * 0.017 + (ncols + 1) * 0.0009
    scale = max(0.05, 1.0 - overhead)
    shares = [max(0.06, col_max[k] / total) for k in range(ncols)]
    if ncols >= 3:
        shares[0] = max(shares[0], 0.20)  # coluna de termos/curta recebe mínimo
    s = float(sum(shares))
    spec = [">{\\raggedright\\arraybackslash}p{%f\\linewidth}" % (x / s * scale)
            for x in shares]
    spec = "|" + "|".join(spec) + "|"

    out = ["\\small\\begin{longtable}{%s}" % spec, "\\hline"]
    if header:
        hdr = " & ".join("\\textbf{" + inline(c) + "}" for c in header)
        out.append("\\rowcolor{engbluebg}\n" + hdr + " \\\\ \\hline \\endfirsthead")
        out.append("\\rowcolor{engbluebg}\n" + hdr + " \\\\ \\hline \\endhead")
    for cells in data:
        cells = cells + [""] * (ncols - len(cells))
        out.append(" & ".join(inline(c) for c in cells) + " \\\\ \\hline")
    out.append("\\end{longtable}")
    return "\n".join(out)


def parse_list(raw_lines):
    items, stack = [], []
    for ln in raw_lines:
        mu, mo = UNORD_RE.match(ln), ORD_RE.match(ln)
        if mu:
            indent = len(mu.group(1))
            item = {"kind": "ul", "indent": indent, "num": None,
                    "lines": [mu.group(3)], "children": []}
        elif mo:
            indent = len(mo.group(1))
            item = {"kind": "ol", "indent": indent, "num": int(mo.group(2)),
                    "lines": [mo.group(3)], "children": []}
        else:
            if stack:
                stack[-1]["lines"].append(ln.strip())
            continue
        while stack and stack[-1]["indent"] >= indent:
            stack.pop()
        if stack:
            stack[-1]["children"].append(item)
        else:
            items.append(item)
        stack.append(item)
    return items


REF_RE = re.compile(r"^\[([^\]]+)\]\s*[—-]\s*")


def is_ref_list(items):
    return any(REF_RE.match(" ".join(it["lines"]).strip()) for it in items)


def render_ref_list(items):
    out = []
    for it in items:
        content = " ".join(it["lines"]).strip()
        m = REF_RE.match(content)
        if m:
            rest = content[m.end():].strip()
            body = r"\textbf{[" + inline(m.group(1)) + "]} — " + inline(rest)
        else:
            body = inline(content)
        out.append("\n\\par\\noindent\\hangindent=3.4em\\hangafter=1 " + body + "\n")
    return "\n".join(out)


def render_list(items, depth=0):
    if is_ref_list(items):
        return render_ref_list(items)
    counters = ["enumi", "enumii", "enumiii", "enumiv"]
    out = []
    i = 0
    while i < len(items):
        first = items[i]
        grp = [first]
        j = i + 1
        while j < len(items) and items[j]["kind"] == first["kind"] and items[j]["indent"] == first["indent"]:
            grp.append(items[j])
            j += 1
        if first["kind"] == "ol":
            out.append("\\begin{enumerate}")
            if first["num"] and first["num"] != 1:
                out.append("\\setcounter{%s}{%d}" % (counters[min(depth, 3)], first["num"] - 1))
        else:
            out.append("\\begin{itemize}")
        for it in grp:
            content = " ".join(it["lines"])
            rendered = inline(content)
            rendered = re.sub(r"^\[[xX]\]\s*", r"\\chkOn{} ", rendered)
            rendered = re.sub(r"^\[ \]\s*", r"\\chkOff{} ", rendered)
            out.append("\\item " + rendered)
            if it["children"]:
                out.append(render_list(it["children"], depth + 1))
        out.append("\\end{itemize}" if first["kind"] == "ul" else "\\end{enumerate}")
        i = j
    return "\n".join(out)


def collect_list(lines, i):
    start = i
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if s == "":
            if i + 1 < len(lines) and is_list_line(lines[i + 1]):
                i += 1
                continue
            break
        if CODE_RE.match(s) or HEADER_RE.match(s) or s.startswith(">") or s.startswith("|") or HR_RE.match(s):
            break
        if is_list_line(l) or re.match(r"^[ \t]{2,}\S", l):
            i += 1
            continue
        break
    return parse_list(lines[start:i]), i


def md_to_latex(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    out = []
    open_box = None  # titulo do quadro aberto (engbox)
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s == "":
            i += 1
            continue

        m = HEADER_RE.match(line)
        if m:
            raw = m.group(2).strip()
            if len(m.group(1)) == 2 and raw in ("Objetivo", "Para o engenheiro"):
                if open_box:
                    out.append("\n\\end{engbox}\n")
                out.append("\n\\begin{engbox}{%s}" % inline(raw))
                open_box = raw
                i += 1
                continue
            if open_box:
                out.append("\n\\end{engbox}\n")
                open_box = None
            level = len(m.group(1))
            out.append(heading(level, inline(raw)))
            i += 1
            continue

        if HR_RE.match(s):
            out.append("\n\\par\\medskip{\\color{engbord}\\hrule}\\medskip\\par\n")
            i += 1
            continue

        if CODE_RE.match(s):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append("\\par\\smallskip\\noindent\\begin{minipage}{\\linewidth}\n"
                       "\\begin{Code}\n" + "\n".join(buf) + "\n\\end{Code}\n"
                       "\\end{minipage}\\par\\smallskip")
            continue

        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            out.append(render_table(rows))
            continue

        if QUOTE_RE.match(line):
            buf = []
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ""):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append("\\begin{quote}\n" + inline(" ".join(x for x in buf if x)) + "\n\\end{quote}")
            continue

        if is_list_line(line):
            items, i = collect_list(lines, i)
            out.append(render_list(items))
            continue

        # paragraph
        buf = [s]
        i += 1
        while i < len(lines):
            l = lines[i]
            ls = l.strip()
            if (ls == "" or HEADER_RE.match(ls) or CODE_RE.match(ls)
                    or ls.startswith("|") or ls.startswith(">")
                    or HR_RE.match(ls) or is_list_line(l)):
                break
            buf.append(ls)
            i += 1
        out.append("\n\\par " + inline(" ".join(buf)) + "\n")
    if open_box:
        out.append("\n\\end{engbox}\n")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# Preamble e estrutura
# ----------------------------------------------------------------------------

HEADER_TEX = r"""\documentclass[10pt,a4paper,oneside,openany]{book}
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}[Scale=0.85]
\newfontfamily\dejavusans{DejaVu Sans}
\newcommand{\chkOn}{{\dejavusans ☑}}
\newcommand{\chkOff}{{\dejavusans ☐}}

\usepackage[a4paper,margin=2.2cm,headheight=14pt]{geometry}

\usepackage[table]{xcolor}

% --- paleta "engenharia" ---
\definecolor{engblue}{HTML}{1F4E79}        % títulos e bordas principais
\definecolor{engblueaccent}{HTML}{2E75B6}  % realces e subtítulos
\definecolor{engbluebg}{HTML}{EAF1F8}      % fundo de quadros e cabeçalho de tabela
\definecolor{codebg}{HTML}{F4F6F8}         % fundo de código
\definecolor{engbord}{HTML}{AFC4DC}        % bordas suaves
\definecolor{linkblue}{HTML}{1155CC}

\usepackage{array}
\usepackage{longtable}
\usepackage{fancyvrb}
\usepackage{fancyhdr}
\usepackage[most]{tcolorbox}
\usepackage{titlesec}
\usepackage[colorlinks=true,linkcolor=engblueaccent,urlcolor=linkblue,
            citecolor=engblueaccent,pdftitle={Do Transformer ao Agente}]{hyperref}
\def\UrlBreaks{\do\/\do\-\do\_\do\.\do\?\do\&\do\#\do\%\do\~\do\=\do\:}
\urlstyle{tt}
% quadros coloridos (ex.: Objetivo, Para o engenheiro)
% sem breakable: o quadro é movido inteiro para a próxima página quando não couber
\newtcolorbox{engbox}[1]{enhanced,colback=engbluebg,colframe=engblueaccent,
  boxrule=0.6pt,arc=1.5mm,left=6pt,right=6pt,top=4pt,bottom=4pt,
  coltitle=white,fonttitle=\small\bfseries\sffamily,title={#1}}

\DefineVerbatimEnvironment{Code}{Verbatim}{
  fontsize=\scriptsize,
  frame=single,
  framesep=4pt,
  rulecolor=\color{engbord},
  fillcolor=\color{codebg},
  xleftmargin=8pt,
  xrightmargin=8pt,
}

% títulos coloridos
\titleformat{\chapter}[display]
  {\LARGE\bfseries\color{engblue}}{}{0pt}{}
  [\vspace{1ex}{\color{engblueaccent}\rule{\linewidth}{1pt}}]
\titleformat{\section}{\Large\bfseries\color{engblue}}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\color{engblueaccent}}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{engblue}}{}{0pt}{}
\titlespacing{\chapter}{0pt}{24pt}{16pt}
\titlespacing{\section}{0pt}{14pt}{6pt}
\titlespacing{\subsection}{0pt}{10pt}{4pt}
\titlespacing{\subsubsection}{0pt}{8pt}{3pt}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\itshape\color{engblueaccent} Do Transformer ao Agente}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.3pt}

\setlength{\parindent}{1em}
\setlength{\parskip}{0.35em}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\emergencystretch=3em
\setcounter{tocdepth}{2}
\makeatletter\renewcommand{\@pnumwidth}{2em}\makeatother

\begin{document}
\frontmatter

\begin{titlepage}
\centering
\vspace*{2cm}
{\color{engblue}\Huge\bfseries Do Transformer ao Agente\par}
\vspace{0.7em}
{\color{engblueaccent}\rule{0.62\linewidth}{1.2pt}\par}
\vspace{1.4em}
{\LARGE Um livro cronológico e prático para engenheiros\par}
{\LARGE sobre modelos de linguagem, RAG, agentes e ferramentas\par}
\vspace{4cm}
{\large\itshape Modelo de linguagem + contexto + recuperação + ferramentas\par}
{\large\itshape + ambiente + memória + iteração + verificação\par}
\vspace{3.5cm}
{\normalsize\itshape \today\par}
\vfill
\end{titlepage}

\thispagestyle{empty}
\vspace*{2.2cm}
{\color{engblue}\Large\bfseries Como este livro foi escrito\par}
\vspace{1em}
{\color{engblueaccent}\rule{0.3\linewidth}{0.8pt}\par}
\vspace{1.6em}
Este livro foi produzido com \textbf{vibe coding}: uma escrita colaborativa e iterativa
entre um humano e um modelo de linguagem, com curadoria e revisão humanas ao longo de todo
o processo. Cada capítulo seguiu o ciclo que o próprio livro ensina --- objetivo, estado,
informação, hipótese, ação, observação, verificação e iteração.

\par\medskip
A ideia deste livro nasceu de uma inquietação: acompanhar a evolução acelerada dos modelos
de linguagem pós-Transformer, em especial o momento atual dos sistemas \textit{agentic}.
Nada ilustrava essa trajetória de ponta a ponta --- do Transformer ao agente --- de forma
cronológica e prática, e este livro tenta preencher essa lacuna.

\par\medskip
Ele foi sugerido e conduzido por \textbf{Fábio Vila}, que pode ser encontrado no Telegram
(\url{https://t.me/viladx2}) e no GitHub (\url{https://github.com/fabiovila}).

\par\medskip
Aqui, dizer isso sem rodeios faz parte do método: o valor do livro não está na autoria
exclusiva, mas no processo que o produziu. Ser honesto sobre como ele foi feito é
coerente com o que ele defende.

\vspace{2.5cm}
{\dejavusans\large\itshape Fábio Vila\par}
{\dejavusans\small\itshape\color{engblueaccent} Telegram: \url{https://t.me/viladx2}\par}
{\dejavusans\small\itshape\color{engblueaccent} GitHub: \url{https://github.com/fabiovila}\par}
\vfill
"""

FOOTER_TEX = "\n\\end{document}\n"

PARTS = [
    ("Prefácio", ["capitulos/00-prefacio/00-como-ler-este-livro.md"]),
    ("Parte I — Era fundacional (≈1950–2020)", [
        "capitulos/01-era-fundacional/01-pre-historia-da-modelagem-de-linguagem.md",
        "capitulos/01-era-fundacional/02-o-transformer.md",
        "capitulos/01-era-fundacional/03-bert-e-gpt.md",
        "capitulos/01-era-fundacional/04-gpt3-escala-e-emergencia.md"]),
    ("Parte II — Era do RAG clássico (2020–2021)", [
        "capitulos/02-era-rag/05-origens-do-retrieval-augmented.md",
        "capitulos/02-era-rag/06-rag-classico-lewis-2020.md"]),
    ("Parte III — Era do alinhamento (2021–2023)", [
        "capitulos/03-era-alinhamento/07-gpt3-a-chatgpt.md",
        "capitulos/03-era-alinhamento/08-modelos-abertos.md"]),
    ("Parte IV — Era das ferramentas (2021–2023)", [
        "capitulos/04-era-ferramentas/09-webgpt-ao-toolformer.md",
        "capitulos/04-era-ferramentas/10-reat-e-o-loop.md",
        "capitulos/04-era-ferramentas/11-function-calling-e-structured-outputs.md"]),
    ("Parte V — Era do RAG como sistema (2023–2025)", [
        "capitulos/05-era-rag-sistema/12-rag-avancado-modular.md"]),
    ("Parte VI — Era dos agentes (2022–2025)", [
        "capitulos/06-era-agentes/13-frameworks-de-agentes.md",
        "capitulos/06-era-agentes/14-multi-agentes.md",
        "capitulos/06-era-agentes/15-avaliacao-de-agentes.md"]),
    ("Parte VII — Era dos protocolos (2024–2026)", [
        "capitulos/07-era-protocolos/16-mcp.md",
        "capitulos/07-era-protocolos/17-a2a-e-interoperabilidade.md"]),
    ("Parte VIII — Síntese", [
        "capitulos/08-sintese/18-o-loop-cognitivo.md",
        "capitulos/08-sintese/19-avaliacao-limites-e-horizonte.md"]),
]

APPENDICES = [
    ("cronologia.md", "Anexo A — Cronologia"),
    ("apendices/glossario.md", "Anexo B — Glossário"),
    ("fontes.md", "Anexo C — Fontes"),
    ("NOTAS.md", "Anexo D — NOTAS: manutenção do livro"),
]


def part_cmd(title):
    COUNTER["part"] += 1
    return ("\n\\part*{%s}\n\\phantomsection\n"
            "\\addcontentsline{toc}{part}{%s}\n"
            "\\pdfbookmark[0]{%s}{part:%d}\n" % (title, title, title, COUNTER["part"]))


def main():
    chunks = [HEADER_TEX]

    chunks.append(md_to_latex(os.path.join(BASE, "README.md")))
    chunks.append("\n\\tableofcontents\n")
    chunks.append("\n\\mainmatter\n")

    for part_title, files in PARTS:
        chunks.append(part_cmd(part_title))
        for f in files:
            p = os.path.join(BASE, f)
            chunks.append("\n%% ===== %s =====\n" % f)
            chunks.append(md_to_latex(p))

    chunks.append("\n\\appendix\n")
    for f, note in APPENDICES:
        chunks.append(part_cmd(note))
        chunks.append("\n%% ===== %s =====\n" % f)
        # anexos com URLs longas: permitem quebra liberal de linha
        if f in ("fontes.md", "cronologia.md"):
            chunks.append("\\sloppy\n")
        chunks.append(md_to_latex(os.path.join(BASE, f)))
        if f in ("fontes.md", "cronologia.md"):
            chunks.append("\n\\fussy\n")

    chunks.append(FOOTER_TEX)

    tex = "\n".join(chunks)
    with open(OUT_TEX, "w", encoding="utf-8") as fh:
        fh.write(tex)
    print("escrevi", OUT_TEX, len(tex), "bytes")

    for run in range(1, 4):
        print("xelatex run", run)
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
             OUT_TEX],
            cwd=BASE, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-6000:])
            print(r.stderr[-2000:])
            sys.exit("lualatex falhou no run %d" % run)
    if os.path.exists(OUT_PDF):
        print("OK:", OUT_PDF, os.path.getsize(OUT_PDF), "bytes")


if __name__ == "__main__":
    main()
