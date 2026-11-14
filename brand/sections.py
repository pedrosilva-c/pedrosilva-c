"""Gera as seções do README abaixo do topo, no mesmo estilo do painel de terminal.

Saídas (assets/sections/, desktop 1280 e celular 720 de largura de referência; o README serve
a versão de celular com <picture> abaixo de 600 px, como no topo):
  stack(-mobile).svg               Tech Stack: categorias em linhas, nível por bloco
  project-<repo>(-mobile).svg      cartões de projeto com a capa do repositório embutida
  status-legend.svg                legenda de status dos projetos
  cert-<id>.svg                    cartões de certificação
  experience(-mobile).svg          experiência (o que foi feito) e formação
  footer.svg                       encerramento

As estatísticas (analytics*.svg) ficam em brand/stats.py, porque a Action semanal só roda aquele script.
Uso:  python brand/sections.py      (requer Pillow para reduzir as capas embutidas)
Conteúdo conferido com portfolio/js/data.js e os READMEs dos repositórios. Nada é inventado aqui.
"""
from __future__ import annotations

import base64
import io
from html import escape
from pathlib import Path

from components import (BG, BORDER, CYAN, DATA as CDATA, DIM, EDGE, GLYPHS, LEVELS, MONO, MONO_W, MUTED, OK,
                        PETROL, SANS, SOFT, SURFACE, TEXT, WIP, icon, mono_text, svg)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sections"
COVERS = ROOT / "assets" / "covers"


# ---------------------------------------------------------------- base comum
def wrap(text: str, limit: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def sans(x, y, text, size, fill, weight=400, anchor="start"):
    return (f'<text x="{x:g}" y="{y:g}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{escape(text)}</text>')


def panel(w: int, h: int, cmd: str, mobile: bool, right: str = "") -> tuple[list[str], int]:
    """Moldura igual à do painel do topo: barra de título, três pontos, barra petróleo, raio 20."""
    head = 50 if mobile else 48
    out = [f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="20"/></clipPath></defs>',
           f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/>',
           f'<rect width="{w}" height="{head}" fill="{SURFACE}"/><rect width="10" height="{h}" fill="{PETROL}"/></g>',
           f'<path d="M10 {head}.5H{w}" stroke="{EDGE}"/>',
           f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="{EDGE}"/>']
    for i, c in enumerate([BORDER, BORDER, PETROL]):
        out.append(f'<circle cx="{36 + i * 18}" cy="{head / 2}" r="5" fill="{c}"/>')
    fs = 18 if mobile else 16
    out.append(mono_text(100, head / 2 + fs * 0.32, cmd, fs, MUTED)[0])
    if right:
        out.append(mono_text(w - 30, head / 2 + fs * 0.32, right, fs - 2, DIM, "end")[0])
    return out, head


def dot(x, y, level, r=5):
    color = LEVELS[level][1]
    if level == "estudo":
        return f'<circle cx="{x:g}" cy="{y:g}" r="{r}" fill="none" stroke="{color}" stroke-width="1.8" stroke-dasharray="2.4 1.8"/>'
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r}" fill="{color}"/>'


def write(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- Tech Stack
STACK_ORDER = ["infra", "redes", "cloud", "dev", "tools"]


def tile_g(x, y, size, label, ic, level, label_size):
    """Um bloco de tecnologia dentro do painel (mesmo desenho dos blocos individuais)."""
    dash = (f' stroke="{WIP}" stroke-opacity=".75" stroke-dasharray="5 4"' if level == "estudo"
            else f' stroke="{BORDER}"')
    out = [f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{size - 1}" height="{size - 1}" rx="14" fill="{SURFACE}"{dash}/>',
           dot(x + size - 13, y + 13, level, 5 if size < 130 else 6)]
    isz = round(size * 0.42)
    iy = y + size * 0.15
    if ic.startswith("mono:"):
        txt = ic[5:]
        fs = round(size * (0.21 if len(txt) <= 3 else 0.17 if len(txt) <= 4 else 0.135))
        out.append(mono_text(x + size / 2, iy + isz * 0.72, txt, fs, CYAN, "middle", weight=700)[0])
    else:
        out.append(icon(ic, x + (size - isz) / 2, iy, isz))
    fit = len(label) * label_size * MONO_W > size - 12
    out.append(mono_text(x + size / 2, y + size * 0.86, label, label_size, SOFT, "middle", fit=fit)[0]
               .replace(f'textLength="{len(label) * label_size * MONO_W:.1f}"',
                        f'textLength="{min(len(label) * label_size * MONO_W, size - 12):.1f}"'))
    return "".join(out)


def level_summary(tiles) -> list[str]:
    seen = []
    for *_, level in tiles:
        if level not in seen:
            seen.append(level)
    return seen


def stack(mobile: bool = False) -> str:
    cats = [(k, *CDATA["stack"][k]) for k in STACK_ORDER]
    if mobile:
        w, tile, gap, per = 720, 150, 14, 4
        x0, label_size = 44, 21
    else:
        w, tile, gap, per = 1280, 108, 12, 7
        x0, label_size = 340, 15
    head = 50 if mobile else 48
    y = head + (40 if mobile else 30)
    legend_y = y
    y += 84 if mobile else 30      # no celular a legenda ocupa 2 linhas
    body, alt = [], []
    for i, (key, title, tiles) in enumerate(cats):
        lines = -(-len(tiles) // per)
        if i:
            body.append(f'<path d="M44 {y - (22 if mobile else 18)}H{w - 34}" stroke="{EDGE}"/>')
        levels = level_summary(tiles)
        if mobile:
            body.append(sans(44, y + 26, title, 26, TEXT, 700))
            lx = 44
            for lv in levels:
                name = LEVELS[lv][0]
                body.append(dot(lx + 6, y + 50, lv, 6))
                t, tw = mono_text(lx + 18, y + 57, name, 19, MUTED)
                body.append(t)
                lx += tw + 46
            ty = y + 78
        else:
            tlines = wrap(title, 22)
            for k, ln in enumerate(tlines):
                body.append(sans(50, y + 30 + k * 26, ln, 21, TEXT, 700))
            ly = y + 30 + (len(tlines) - 1) * 26
            for j, lv in enumerate(levels):
                body.append(dot(56, ly + 25 + j * 24, lv, 5))
                body.append(mono_text(70, ly + 30 + j * 24, LEVELS[lv][0], 15, MUTED)[0])
            ty = y
        for j, (tid, label, ic, level) in enumerate(tiles):
            r, c = divmod(j, per)
            body.append(tile_g(x0 + c * (tile + gap), ty + r * (tile + gap), tile, label, ic, level, label_size))
        block = lines * tile + (lines - 1) * gap
        y = ty + block + (44 if mobile else 36)
        if not mobile:
            y = max(y, ty + 60 + (len(wrap(title, 22)) - 1) * 26 + len(levels) * 24 + 36)
        alt.append(f"{title}: " + ", ".join(f"{label} ({LEVELS[lv][0]})" for _, label, _, lv in tiles))
    h = y - (4 if mobile else 6)
    out, _ = panel(w, h, "pedro@infra:~$ ls stack/", mobile)
    # legenda
    lx = 44 if mobile else 50
    fs = 19 if mobile else 15
    for k in ("prof", "proj", "fund", "estudo"):
        name = LEVELS[k][0]
        out.append(dot(lx + 6, legend_y - fs * 0.35, k, 6 if mobile else 5))
        t, tw = mono_text(lx + 18, legend_y, name, fs, MUTED)
        out.append(t)
        lx += tw + (40 if mobile else 44)
        if mobile and k == "proj":
            lx, legend_y = 44, legend_y + 32
    out += body
    label = "Tech Stack. Ponto verde: uso profissional; ciano: projetos próprios; cinza: fundamentos (curso concluído); âmbar tracejado: em estudo. " + " ".join(alt)
    return svg(w, h, label, "\n".join(out))


# ---------------------------------------------------------------- Projetos
PROJECTS = [
    # repo, nome, status (grupo, rótulo), descrição, tecnologias [(rótulo, ícone|None)], fatos
    ("kaizen-tech", "Kaizen Tech", ("ok", "Funcional"),
     "Utilitário de manutenção para técnicos de suporte: diagnóstico, ponto de restauração, limpeza com confirmação e relatório do atendimento em PDF.",
     [("Python", "python"), ("Tkinter", None), ("PowerShell", "powershell"), ("fpdf2", None)],
     "14 testes automatizados · uso em atendimentos"),
    ("lab-active-directory", "Laboratório Active Directory", ("doc", "Em documentação"),
     "Domínio Windows Server 2019 em VirtualBox, com cliente Windows 10 em rede isolada e scripts PowerShell somente leitura para coletar evidências.",
     [("Windows Server", "windows8"), ("AD DS", None), ("PowerShell", "powershell"), ("VirtualBox", "virtualbox")],
     "ambiente existe · evidências ainda não coletadas"),
    ("fleet-report-demo", "Fleet Report Demo", ("ok", "Funcional"),
     "Importação conferida de planilhas de telemetria, com motivo de cada rejeição, e relatórios diários em XLSX e PDF.",
     [("Python", "python"), ("FastAPI", "fastapi"), ("SQLite", "sqlite"), ("pytest", "pytest")],
     "20 testes automatizados · dados 100% fictícios"),
    ("inclusao-360", "Inclusão 360°", ("ok", "Concluído · v5.2"),
     "Site para experimentar recursos de acessibilidade, com leitura em voz alta, VLibras e um desafio de correção de um portal fictício.",
     [("HTML", "html5"), ("CSS", "css3"), ("JavaScript", "javascript"), ("VLibras", None)],
     "27 verificações de interface · projeto individual"),
    ("campus-ai", "Campus AI", ("wip", "Em desenvolvimento"),
     "Assistente acadêmico local que organiza materiais e prazos do Moodle no Obsidian. Protótipo, ainda não validado com contas reais.",
     [("Python", "python"), ("PySide6", "qt"), ("Playwright", "playwright"), ("SQLite", "sqlite")],
     "566 testes Python + 97 da extensão"),
    ("portfolio", "Portfólio", ("ok", "Publicado"),
     "Experiência, casos técnicos e laboratórios, com status declarado em cada item. Sem frameworks, publicado no GitHub Pages.",
     [("HTML", "html5"), ("CSS", "css3"), ("JavaScript", "javascript"), ("GitHub Pages", "github")],
     "verificado em 375 a 1440 px, claro e escuro"),
]
STATUS = {"ok": OK, "wip": WIP, "doc": WIP}
CARD_H = 289  # altura única dos cartões de desktop (o maior, com descrição de 3 linhas)
STATUS_GLYPH = {
    "ok": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "wip": '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor" stroke="none"/>',
    "doc": GLYPHS["file"],
}


def cover_uri(repo: str, width: int) -> str:
    from PIL import Image
    im = Image.open(COVERS / f"{repo}.png").convert("RGBA").convert("RGB")
    im = im.resize((width, width // 2), Image.LANCZOS)
    buf = io.BytesIO()
    im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def status_pill(x, y, group, label, fs):
    color = STATUS[group]
    t = label.upper()
    tw = len(t) * fs * MONO_W + (len(t) - 1) * 0.8
    h = fs * 2.1
    gs = fs * 1.15
    w = tw + gs + fs * 2.3
    return (f'<rect x="{x:g}" y="{y:g}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".5"/>'
            f'<svg x="{x + fs * 0.8:.1f}" y="{y + (h - gs) / 2:.1f}" width="{gs:.1f}" height="{gs:.1f}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" color="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{STATUS_GLYPH[group]}</svg>'
            f'<text x="{x + fs * 1.3 + gs:.1f}" y="{y + h / 2 + fs * 0.36:.1f}" font-family="{MONO}" font-size="{fs}" font-weight="600" '
            f'letter-spacing=".8" fill="{color}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>'), w


def chips(x, y, items, fs, gap=10):
    out = []
    h = fs * 2.2
    isz = fs * 1.35
    for label, ic in items:
        tw = len(label) * fs * MONO_W
        w = tw + fs * 1.6 + (isz + fs * 0.55 if ic else 0)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{SURFACE}" stroke="{BORDER}"/>')
        tx = x + fs * 0.8
        if ic:
            out.append(icon(ic, tx, y + (h - isz) / 2, isz))
            tx += isz + fs * 0.55
        out.append(mono_text(tx, y + h / 2 + fs * 0.36, label, fs, SOFT)[0])
        x += w + gap
    return "".join(out)


def project(p, mobile: bool = False) -> str:
    repo, name, (group, slabel), desc, tech, facts = p
    color = STATUS[group]
    if mobile:
        w, pad, cw = 720, 30, 300
        ch = cw // 2
        ix = pad + 10 + cw + 24
        parts = []
        y = pad
        parts.append(mono_text(ix, y + 18, "Pedro-Osaka /", 16, DIM)[0])
        parts.append(mono_text(ix, y + 40, repo, 17, CYAN)[0])
        name_lines = wrap(name, 15)
        for k, ln in enumerate(name_lines):
            parts.append(sans(ix, y + 82 + k * 36, ln, 31, TEXT, 700))
        pill, _ = status_pill(ix, y + 82 + len(name_lines) * 36 - 10, group, slabel, 15)
        parts.append(pill)
        y = max(pad + ch, y + 82 + len(name_lines) * 36 + 24) + 34
        for k, ln in enumerate(wrap(desc, 47)):
            parts.append(sans(pad + 10, y + k * 33, ln, 23, MUTED))
        y += len(wrap(desc, 47)) * 33 + 6
        parts.append(chips(pad + 10, y, tech, 17, 10))
        y += 37 + 34
        parts.append(mono_text(pad + 10, y, "▸ " + facts, 18, SOFT, fit=False)[0])
        h = y + 30
    else:
        # desktop compacto: selo na linha do caminho, descrição em 2 linhas, capa 440 x 220
        w, pad, cw = 1280, 26, 440
        ch = cw // 2
        ix = pad + 10 + cw + 36
        parts = [mono_text(ix, pad + 22, f"Pedro-Osaka / {repo}", 16, DIM)[0]
                 .replace(f">Pedro-Osaka / {repo}<", f'>Pedro-Osaka / <tspan fill="{CYAN}">{repo}</tspan><')]
        pill, pw = status_pill(0, pad + 2, group, slabel, 14)
        parts.append(f'<g transform="translate({w - 34 - pw:.1f} 0)">{pill}</g>')
        parts.append(sans(ix, pad + 68, name, 34, TEXT, 700))
        y = pad + 102
        lines = wrap(desc, 70)
        for k, ln in enumerate(lines):
            parts.append(sans(ix, y + k * 27, ln, 18.5, MUTED))
        y += (len(lines) - 1) * 27 + 20
        parts.append(chips(ix, y, tech, 15, 10))
        y += 33 + 30
        parts.append(mono_text(ix, y, "▸ " + facts, 15, SOFT, fit=False)[0])
        h = max(pad * 2 + ch, y + 24, CARD_H)
    uri = cover_uri(repo, 600 if mobile else 880)
    cx, cy = pad + 10, pad
    head = [f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="20"/></clipPath>'
            f'<clipPath id="cv"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12"/></clipPath></defs>',
            f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/><rect width="10" height="{h}" fill="{color}"/></g>',
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="{EDGE}"/>',
            f'<image href="{uri}" x="{cx}" y="{cy}" width="{cw}" height="{ch}" clip-path="url(#cv)" preserveAspectRatio="xMidYMid slice"/>',
            f'<rect x="{cx + .5}" y="{cy + .5}" width="{cw - 1}" height="{ch - 1}" rx="12" fill="none" stroke="{BORDER}"/>']
    label = (f"{name} — status: {slabel}. {desc} Tecnologias: {', '.join(t for t, _ in tech)}. {facts}.")
    return svg(w, h, label, "\n".join(head + parts))


def status_legend(mobile: bool = False) -> str:
    """Legenda de status. No celular, empilhada e em tamanho natural (cabe nos 293 px úteis)."""
    items = [("ok", "pronto para uso"), ("wip", "em desenvolvimento"), ("doc", "em documentação")]
    fs, out = 13, []
    x, y = 4, 6
    for g, t in items:
        color = STATUS[g]
        out.append(f'<svg x="{x}" y="{y}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" color="{color}" '
                   f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{STATUS_GLYPH[g]}</svg>')
        tt, tw = mono_text(x + 22, y + 13, t, fs, MUTED)
        out.append(tt)
        if mobile:
            y += 24
        else:
            x += 22 + tw + 26
    w, h = (190, y + 4) if mobile else (round(x - 22), 28)
    return svg(w, h, "Legenda de status: verde com visto, pronto para uso; âmbar com meio círculo, em desenvolvimento; "
                     "âmbar com documento, em documentação.", "\n".join(out))


# ---------------------------------------------------------------- Certificações
CERTS = [
    ("aws-cloud-foundations", "aws", "AWS Academy", ["AWS Academy Graduate —", "Cloud Foundations"], "Training Badge · 20 h · nov/2026",
     ("verificável no Credly", OK)),
    ("cisco-cybersecurity", "cisco", "Cisco Networking Academy", ["Introduction to", "Cybersecurity"], "abr/2026",
     ("sem link público", MUTED)),
    ("cisco-redes", "cisco", "Cisco Networking Academy", ["Fundamentos de Redes"], "nome oficial e data pendentes",
     ("dados pendentes", WIP)),
]


def cert(c) -> str:
    cid, ic, issuer, lines, meta, (stext, scolor) = c
    w, h = 268, 168
    out = [f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>',
           f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/><rect width="{w}" height="40" fill="{SURFACE}"/>'
           f'<rect width="5" height="{h}" fill="{PETROL}"/></g>',
           f'<path d="M5 40.5H{w}" stroke="{EDGE}"/>',
           f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{EDGE}"/>',
           icon(ic, 18, 8 if ic == "aws" else 6, 24 if ic == "aws" else 28),
           mono_text(56, 25, issuer, 11, MUTED)[0]]
    for i, ln in enumerate(lines):
        out.append(sans(20, 70 + i * 21, ln, 16, TEXT, 700))
    out.append(mono_text(20, 70 + len(lines) * 21 + 6, meta, 11, MUTED)[0])
    t = stext.upper()
    tw = len(t) * 10 * MONO_W + (len(t) - 1) * 0.8
    out.append(f'<rect x="20.5" y="{h - 34.5}" width="{tw + 30:.0f}" height="21" rx="10.5" fill="{scolor}" fill-opacity=".1" stroke="{scolor}" stroke-opacity=".45"/>')
    out.append(f'<circle cx="31" cy="{h - 24}" r="3" fill="{scolor}"/>')
    out.append(f'<text x="39" y="{h - 20.4}" font-family="{MONO}" font-size="10" font-weight="600" letter-spacing=".8" fill="{scolor}" '
               f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>')
    return svg(w, h, f"{' '.join(lines)} — {issuer} — {meta} — {stext}", "\n".join(out))


# ---------------------------------------------------------------- Experiência
EXPERIENCE = [
    ("abr/2026 – atual", OK, "Jovem Aprendiz · equipe de TI", "Transmargoo Turismo e Fretamento", [
        "Usuários, acessos e permissões no Active Directory; GPOs para padronizar estações e mapear unidades",
        "Retomada de um servidor Windows Server após queda de energia",
        "Conflito de IP entre roteador e gateway corrigido; Wi-Fi de visitantes isolado da rede interna",
        "Diagnóstico de placa-mãe com defeito e reaproveitamento de componentes",
    ]),
    ("fev/2025 – abr/2026", CYAN, "Estagiário de Suporte Técnico", "Faculdade Dom Bosco (AEDB) · laboratórios", [
        "Atendimento N1 presencial a alunos, professores e colaboradores",
        "Manutenção preventiva e corretiva; instalação de Windows, drivers, impressoras e periféricos",
        "Cabeamento e crimpagem; participação na implantação de um laboratório",
        "Controle de ativos e inventário em planilhas",
    ]),
]
EDUCATION = ("Sistemas de Informação", "Faculdade Dom Bosco (AEDB)", "4º período · em andamento")


def experience(mobile: bool = False) -> str:
    if mobile:
        w, cols, pad = 720, 1, 34
        f_per, f_role, f_org, f_b, lim, lh = 19, 26, 20, 21, 50, 30
    else:
        w, cols, pad = 1280, 2, 40
        f_per, f_role, f_org, f_b, lim, lh = 15, 22, 16, 16.5, 58, 24
    head = 50 if mobile else 48
    gap = 24
    cw = (w - 10 - 2 * pad - (cols - 1) * gap) / cols
    blocks, heights = [], []
    for period, color, role, org, bullets in EXPERIENCE:
        b, y = [], 0
        b.append(("dot", color, y))
        b.append(("period", period, color, y))
        y += f_per + 16
        b.append(("role", role, y + f_role))
        y += f_role + 10
        b.append(("org", org, y + f_org))
        y += f_org + 22
        for bl in bullets:
            lines = wrap(bl, lim)
            b.append(("bullet", lines, y + f_b))
            y += len(lines) * lh + 8
        blocks.append(b)
        heights.append(y + 14)
    rows = -(-len(blocks) // cols)
    row_h = [max(heights[r * cols:(r + 1) * cols]) for r in range(rows)]
    top = head + 26
    edu_y = top + sum(row_h) + (rows - 1) * gap + 22
    edu_h = 92 if mobile else 64
    h = edu_y + edu_h + 26
    out, _ = panel(w, h, "pedro@infra:~$ history", mobile)
    alt = []
    for i, b in enumerate(blocks):
        r, c = divmod(i, cols)
        x = 10 + pad + c * (cw + gap)
        y0 = top + sum(row_h[:r]) + r * gap
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{cw:.1f}" height="{row_h[r]}" rx="12" fill="{SURFACE}" fill-opacity=".55" stroke="{BORDER}"/>')
        ix = x + 22
        for item in b:
            kind = item[0]
            if kind == "dot":
                out.append(f'<circle cx="{ix + 6}" cy="{y0 + 24 + item[2]}" r="6" fill="{BG}" stroke="{item[1]}" stroke-width="2"/>'
                           f'<circle cx="{ix + 6}" cy="{y0 + 24 + item[2]}" r="2.6" fill="{item[1]}"/>')
            elif kind == "period":
                out.append(mono_text(ix + 22, y0 + 24 + f_per * 0.36 + item[3], item[1], f_per, item[2], weight=600)[0])
            elif kind == "role":
                out.append(sans(ix, y0 + 22 + item[2], item[1], f_role, TEXT, 700))
            elif kind == "org":
                out.append(sans(ix, y0 + 22 + item[2], item[1], f_org, MUTED))
            elif kind == "bullet":
                for k, ln in enumerate(item[1]):
                    yy = y0 + 22 + item[2] + k * lh
                    if k == 0:
                        out.append(mono_text(ix, yy, "▸", f_b, CYAN, fit=False)[0])
                    out.append(sans(ix + f_b * 1.2, yy, ln, f_b, SOFT))
        period, _, role, org, bullets = EXPERIENCE[i]
        alt.append(f"{period}, {role}, {org}: " + "; ".join(bullets))
    # formação
    ex = 10 + pad
    out.append(f'<rect x="{ex}" y="{edu_y}" width="{w - 10 - 2 * pad}" height="{edu_h}" rx="12" fill="none" stroke="{BORDER}" stroke-dasharray="5 4"/>')
    course, inst, when = EDUCATION
    if mobile:
        out.append(mono_text(ex + 22, edu_y + 34, "formação", 18, CYAN)[0])
        out.append(sans(ex + 130, edu_y + 35, course, 22, TEXT, 700))
        out.append(sans(ex + 22, edu_y + 70, f"{inst} · {when}", 19, MUTED))
    else:
        out.append(mono_text(ex + 22, edu_y + 38, "formação", 15, CYAN)[0])
        out.append(sans(ex + 120, edu_y + 39, course, 19, TEXT, 700))
        out.append(sans(ex + 352, edu_y + 39, f"{inst} · {when}", 16, MUTED))
    alt.append(f"Formação: {course}, {inst}, {when}")
    return svg(w, h, "Experiência e formação. " + " | ".join(alt), "\n".join(out))


# ---------------------------------------------------------------- Rodapé
def footer() -> str:
    w, h = 560, 44
    body = (f'<path d="M0 22.5H170M390 22.5H{w}" stroke="{BORDER}"/>'
            + mono_text(w / 2, 27, "pedro@infra:~$ exit", 14, DIM, "middle")[0]
            + f'<rect x="{w / 2 + 84}" y="14" width="8" height="16" fill="{PETROL}"/>')
    return svg(w, h, "Fim do perfil", body)


def main() -> None:
    write("stack.svg", stack())
    write("stack-mobile.svg", stack(mobile=True))
    for p in PROJECTS:
        write(f"project-{p[0]}.svg", project(p))
        write(f"project-{p[0]}-mobile.svg", project(p, mobile=True))
    write("status-legend.svg", status_legend())
    write("status-legend-mobile.svg", status_legend(mobile=True))
    for c in CERTS:
        write(f"cert-{c[0]}.svg", cert(c))
    write("experience.svg", experience())
    write("experience-mobile.svg", experience(mobile=True))
    write("footer.svg", footer())
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.stat().st_size // 1024:>4} KB  {f.name}")


if __name__ == "__main__":
    main()
