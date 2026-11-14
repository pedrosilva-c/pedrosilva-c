"""Gera os componentes visuais do README de perfil (SVG, sem serviço externo).

Saídas:
  assets/ui/whoami.svg            cartão de apresentação em estilo terminal
  assets/ui/btn-*.svg             botões de contato
  assets/ui/legend.svg            legenda dos níveis do Tech Stack
  assets/ui/div-*.svg             divisores das categorias do Tech Stack
  assets/ui/timeline.svg          experiência e formação
  assets/stack/*.svg              um bloco por tecnologia (logotipo oficial ou monograma)
  assets/certs/*.svg              cartões de certificação

Uso:  python brand/components.py
Todo o conteúdo vem de DATA abaixo e foi conferido com o portfólio (js/data.js) e os READMEs.
Ícones: brand/_source/icons (ver LICENSES.md).
"""
from __future__ import annotations

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "brand" / "_source" / "icons"
ASSETS = ROOT / "assets"

BG, SURFACE, BORDER, EDGE = "#0F1419", "#151C23", "#2A3540", "#222C36"
TEXT, SOFT, MUTED, DIM = "#E8ECF0", "#C6D0DA", "#9AA7B4", "#5E6B78"
CYAN, PETROL, PETROL_DARK, OK, WIP = "#5FB6C8", "#2B8A9E", "#1F6F80", "#6CC79A", "#E0A030"
SANS = "Inter, 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', Consolas, Menlo, 'DejaVu Sans Mono', monospace"
MONO_W = 0.6  # largura média de um caractere monoespaçado, em em

LEVELS = {
    "prof": ("uso profissional", OK),
    "proj": ("projetos próprios", CYAN),
    "fund": ("fundamentos · curso", MUTED),
    "estudo": ("em estudo", WIP),
}

# Ícones de linha no grid 24x24 (redesenhados a partir do Feather, MIT).
GLYPHS = {
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
           '<path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
    "wifi": '<path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/>',
    "headset": '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="M22 6l-10 7L2 6"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
}

# Cores quase pretas dos logotipos trocadas para leitura em fundo escuro.
RECOLOR = {
    "github": {"#181616": TEXT},
    "aws": {"#252f3e": TEXT},
    "virtualbox": {None: "#7FA6D9"},
    "cisco": {None: "#1BA0D7"},
}

DATA = {
    "whoami": [
        ("whoami", "Pedro Henrique da Silva Pereira"),
        ("cargo", "Jovem Aprendiz · equipe de TI · desde abr/2026"),
        ("formacao", "Sistemas de Informação · 4º período · AEDB"),
        ("foco", "Windows Server · AD · GPO · DNS · DHCP · redes"),
        ("automacao", "Python e PowerShell para problemas que se repetem"),
        ("status", None),
    ],
    "buttons": [
        ("linkedin", "LinkedIn", "linkedin"),
        ("portfolio", "Portfólio", "globe"),
        ("email", "E-mail", "mail"),
        ("curriculo", "Currículo PDF", "file"),
    ],
    # (id, rótulo, ícone: arquivo | glyph:nome | mono:texto, nível)
    "stack": {
        "infra": ("Suporte e infraestrutura Windows", [
            ("windows", "Windows", "windows11", "prof"),
            ("windows-server", "Win Server", "windows8", "prof"),
            ("active-directory", "Active Dir.", "mono:AD", "prof"),
            ("gpo", "GPO", "mono:GPO", "prof"),
            ("hardware", "Hardware", "glyph:cpu", "prof"),
            ("suporte", "Suporte N1", "glyph:headset", "prof"),
        ]),
        "redes": ("Redes", [
            ("tcpip", "TCP/IP", "mono:TCP/IP", "prof"),
            ("dns", "DNS", "mono:DNS", "prof"),
            ("dhcp", "DHCP", "mono:DHCP", "prof"),
            ("wifi", "Wi-Fi", "glyph:wifi", "prof"),
            ("cabeamento", "Cabeamento", "mono:RJ45", "prof"),
        ]),
        "cloud": ("Cloud e segurança", [
            ("aws", "AWS", "aws", "fund"),
            ("ciberseguranca", "Segurança", "glyph:shield", "fund"),
            ("azure", "Azure", "azure", "estudo"),
        ]),
        "dev": ("Automação e sistemas", [
            ("python", "Python", "python", "proj"),
            ("powershell", "PowerShell", "powershell", "estudo"),
            ("fastapi", "FastAPI", "fastapi", "proj"),
            ("sqlite", "SQLite", "sqlite", "proj"),
            ("javascript", "JavaScript", "javascript", "proj"),
            ("typescript", "TypeScript", "typescript", "proj"),
            ("html5", "HTML", "html5", "proj"),
            ("css3", "CSS", "css3", "proj"),
            ("pyside6", "PySide6", "qt", "proj"),
            ("playwright", "Playwright", "playwright", "proj"),
            ("pytest", "pytest", "pytest", "proj"),
        ]),
        "tools": ("Ferramentas", [
            ("git", "Git", "git", "proj"),
            ("github", "GitHub", "github", "proj"),
            ("virtualbox", "VirtualBox", "virtualbox", "proj"),
        ]),
    },
    "certs": [
        ("aws-cloud-foundations", "aws", ["AWS Academy Graduate", "Cloud Foundations"], "AWS Academy · nov/2026",
         ("verificável · Credly", OK)),
        ("cisco-cybersecurity", "cisco", ["Introduction to", "Cybersecurity"], "Cisco NetAcad · abr/2026",
         ("sem link público", MUTED)),
        ("cisco-redes", "cisco", ["Fundamentos de Redes", ""], "Cisco NetAcad · data pendente",
         ("dados pendentes", WIP)),
    ],
    "timeline": [
        ("abr/2026 – atual", OK, "Jovem Aprendiz · equipe de TI", "Transmargoo Turismo e Fretamento",
         ["Active Directory", "GPO", "Windows Server", "redes", "suporte"]),
        ("fev/2025 – abr/2026", CYAN, "Estagiário de Suporte Técnico", "Faculdade Dom Bosco (AEDB) · laboratórios",
         ["N1 presencial", "manutenção", "Windows", "cabeamento"]),
        ("em andamento", CYAN, "Sistemas de Informação · 4º período", "Faculdade Dom Bosco (AEDB) · graduação",
         ["formação"]),
    ],
}


# ---------------------------------------------------------------- utilidades
def svg(w: float, h: float, label: str, body: str, extra: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="0 0 {w:g} {h:g}" '
            f'role="img" aria-label="{escape(label)}">\n<title>{escape(label)}</title>\n{extra}{body}\n</svg>\n')


def mono_text(x, y, text, size, fill, anchor="start", weight=400, spacing=0.0, fit=True):
    """Texto monoespaçado com largura fixada (textLength), igual em qualquer fonte de fallback."""
    n = len(text)
    width = n * size * MONO_W + max(0, n - 1) * spacing
    tl = f' textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs"' if fit and n > 2 else ""
    return (f'<text x="{x:g}" y="{y:g}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{tl}>{escape(text)}</text>'), width


def frame(w, h, bar=True):
    out = [f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>',
           f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/>']
    if bar:
        out.append(f'<rect width="6" height="{h}" fill="{PETROL}"/>')
    out.append("</g>")
    out.append(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{EDGE}"/>')
    return "".join(out)


def icon(name: str, x, y, size) -> str:
    if name.startswith("glyph:"):
        return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{CYAN}" '
                f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[name[6:]]}</svg>')
    raw = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", raw, flags=re.S)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    for old, new in RECOLOR.get(name, {}).items():
        if old is None:
            inner = re.sub(r"<path ", f'<path fill="{new}" ', inner)
        else:
            inner = re.sub(re.escape(old), new, inner, flags=re.I)
    # ids únicos por arquivo, para gradientes não colidirem se o SVG for combinado
    inner = re.sub(r'id="([^"]+)"', rf'id="{name}-\1"', inner)
    inner = re.sub(r'url\(#([^)]+)\)', rf'url(#{name}-\1)', inner)
    inner = re.sub(r'href="#([^"]+)"', rf'href="#{name}-\1"', inner)
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}">{inner}</svg>'


def write(rel: str, content: str) -> None:
    p = ASSETS / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- componentes
def whoami() -> str:
    w, lh, top = 840, 34, 74
    rows = DATA["whoami"]
    h = top + lh * len(rows) + 22
    out = [frame(w, h),
           f'<rect x="6" y="0" width="{w - 6}" height="42" fill="{SURFACE}" clip-path="url(#c)"/>',
           f'<path d="M6 42.5H{w}" stroke="{EDGE}"/>']
    for i, c in enumerate([BORDER, BORDER, PETROL]):
        out.append(f'<circle cx="{30 + i * 18}" cy="21" r="5" fill="{c}"/>')
    out.append(mono_text(w / 2, 26, "pedro@infra: ~", 13, MUTED, "middle")[0])
    alt = []
    for i, (cmd, val) in enumerate(rows):
        y = top + i * lh + 12
        out.append(mono_text(34, y, "$", 16, PETROL, fit=False)[0])
        out.append(mono_text(56, y, cmd, 16, CYAN)[0])
        if val is None:
            out.append(f'<circle cx="214" cy="{y - 5}" r="5" fill="{OK}"/>')
            t, tw = mono_text(228, y, "aberto a oportunidades", 16, OK, weight=600)
            out.append(t)
            out.append(f'<rect class="cur" x="{236 + tw:.0f}" y="{y - 15}" width="9" height="19" fill="{CYAN}"/>')
            alt.append("status: aberto a oportunidades")
        else:
            out.append(mono_text(200, y, val, 16, TEXT)[0])
            alt.append(f"{cmd}: {val}")
    style = ('<style>@keyframes b{50%{opacity:0}}.cur{animation:b 1.1s steps(1) infinite}'
             '@media (prefers-reduced-motion:reduce){.cur{animation:none}}</style>\n')
    return svg(w, h, "; ".join(alt), "\n".join(out), style)


def button(key: str, label: str, glyph: str) -> str:
    text = label.upper()
    h, size, sp = 40, 13, 1.2
    tw = len(text) * size * MONO_W + (len(text) - 1) * sp
    w = round(16 + 18 + 10 + tw + 18)
    if key == "linkedin":
        fill, stroke, fg = "#0A66C2", "#0A66C2", "#FFFFFF"
        ic = (f'<rect x="16" y="11" width="18" height="18" rx="3" fill="#FFFFFF"/>'
              f'<text x="25" y="25.5" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="#0A66C2">in</text>')
    elif key == "portfolio":
        fill, stroke, fg = PETROL_DARK, PETROL_DARK, "#FFFFFF"
        ic = icon("glyph:" + glyph, 16, 11, 18).replace(f'stroke="{CYAN}"', 'stroke="#FFFFFF"')
    else:
        fill, stroke, fg = SURFACE, BORDER, TEXT
        ic = icon("glyph:" + glyph, 16, 11, 18)
    t = (f'<text x="44" y="25" font-family="{MONO}" font-size="{size}" font-weight="600" letter-spacing="{sp}" fill="{fg}" '
         f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    body = f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{fill}" stroke="{stroke}"/>{ic}{t}'
    return svg(w, h, label, body)


def tile(label: str, ic: str, level: str) -> str:
    w, h = 78, 90
    lname, lcolor = LEVELS[level]
    dash = f' stroke-dasharray="4 3" stroke="{WIP}" stroke-opacity=".7"' if level == "estudo" else f' stroke="{BORDER}"'
    out = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{SURFACE}"{dash}/>',
           f'<circle cx="{w - 11}" cy="11" r="4" fill="{lcolor}"/>']
    if ic.startswith("mono:"):
        txt = ic[5:]
        size = 20 if len(txt) <= 3 else 16 if len(txt) <= 4 else 13
        out.append(mono_text(w / 2, 46, txt, size, CYAN, "middle", weight=700)[0])
    else:
        out.append(icon(ic, w / 2 - 18, 15, 36))
    out.append(mono_text(w / 2, 76, label, 10.5, SOFT, "middle", fit=len(label) * 10.5 * MONO_W > 66)[0])
    return svg(w, h, f"{label} — {lname}", "\n".join(out))


def legend() -> str:
    items = [LEVELS[k] for k in ("prof", "proj", "fund", "estudo")]
    # 2 x 2: legível também quando a imagem é reduzida no celular
    size, col = 12, 210
    w, h = 2 * col, 50
    out = []
    for i, (name, color) in enumerate(items):
        x, cy = 14 + (i % 2) * col, 14 + (i // 2) * 24
        if color == WIP:
            out.append(f'<circle cx="{x + 5}" cy="{cy}" r="4.5" fill="none" stroke="{WIP}" stroke-width="1.6" stroke-dasharray="2.2 1.6"/>')
        else:
            out.append(f'<circle cx="{x + 5}" cy="{cy}" r="4.5" fill="{color}"/>')
        out.append(mono_text(x + 16, cy + 4, name, size, MUTED)[0])
    return svg(w, h, "Legenda: ponto verde, uso profissional; ciano, projetos próprios; cinza, fundamentos (curso concluído); "
                      "âmbar tracejado, em estudo", "\n".join(out))


def divider(title: str) -> str:
    w, h, size, sp = 520, 30, 12, 1.6
    text = title.upper()
    tw = len(text) * size * MONO_W + (len(text) - 1) * sp
    x0, x1 = (w - tw) / 2 - 16, (w + tw) / 2 + 16
    body = (f'<path d="M0 15.5H{x0:.0f}M{x1:.0f} 15.5H{w}" stroke="{BORDER}"/>'
            f'<text x="{w / 2}" y="19.5" text-anchor="middle" font-family="{MONO}" font-size="{size}" font-weight="600" '
            f'letter-spacing="{sp}" fill="{CYAN}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    return svg(w, h, title, body)


def cert(icon_name: str, lines: list[str], meta: str, status: tuple[str, str]) -> str:
    w, h = 268, 132
    stext, scolor = status
    out = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
           f'<rect x="16" y="18" width="40" height="40" rx="9" fill="{SURFACE}" stroke="{BORDER}"/>',
           icon(icon_name, 19, 21, 34) if icon_name == "cisco" else icon(icon_name, 22, 24, 28)]
    for i, line in enumerate(l for l in lines if l):
        out.append(f'<text x="70" y="{34 + i * 19}" font-family="{SANS}" font-size="14.5" font-weight="700" fill="{TEXT}">{escape(line)}</text>')
    out.append(mono_text(16, 86, meta, 11, MUTED)[0])
    t = stext.upper()
    cw = len(t) * 10 * MONO_W + (len(t) - 1) * 0.8 + 30
    out.append(f'<rect x="16.5" y="99.5" width="{cw:.0f}" height="19" rx="9.5" fill="{scolor}" fill-opacity=".1" stroke="{scolor}" stroke-opacity=".45"/>')
    out.append(f'<circle cx="27" cy="109" r="3" fill="{scolor}"/>')
    out.append(f'<text x="35" y="112.6" font-family="{MONO}" font-size="10" font-weight="600" letter-spacing=".8" fill="{scolor}" '
               f'textLength="{len(t) * 10 * MONO_W + (len(t) - 1) * 0.8:.1f}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>')
    label = f"{' '.join(l for l in lines if l)} — {meta} — {stext}"
    return svg(w, h, label, "\n".join(out))


def timeline() -> str:
    w, row, top = 840, 104, 34
    items = DATA["timeline"]
    h = top + row * len(items) - 6
    out = [frame(w, h)]
    lx = 236
    out.append(f'<path d="M{lx} {top + 10}V{top + row * (len(items) - 1) + 10}" stroke="{BORDER}" stroke-width="2"/>')
    alt = []
    for i, (period, color, title, org, tags) in enumerate(items):
        y = top + i * row
        out.append(mono_text(212, y + 15, period, 13, color, "end")[0])
        out.append(f'<circle cx="{lx}" cy="{y + 10}" r="7" fill="{BG}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<circle cx="{lx}" cy="{y + 10}" r="3" fill="{color}"/>')
        out.append(f'<text x="{lx + 26}" y="{y + 16}" font-family="{SANS}" font-size="17" font-weight="700" fill="{TEXT}">{escape(title)}</text>')
        out.append(f'<text x="{lx + 26}" y="{y + 39}" font-family="{SANS}" font-size="14" fill="{MUTED}">{escape(org)}</text>')
        x = lx + 26
        for tag in tags:
            tw = len(tag) * 11 * MONO_W
            out.append(f'<rect x="{x:.1f}" y="{y + 52}" width="{tw + 18:.1f}" height="22" rx="6" fill="{SURFACE}" stroke="{BORDER}"/>')
            out.append(mono_text(x + 9, y + 67, tag, 11, SOFT)[0])
            x += tw + 26
        alt.append(f"{period}: {title}, {org}")
    return svg(w, h, "Experiência e formação. " + "; ".join(alt), "\n".join(out))


def main() -> None:
    write("ui/whoami.svg", whoami())
    for key, label, glyph in DATA["buttons"]:
        write(f"ui/btn-{key}.svg", button(key, label, glyph))
    write("ui/legend.svg", legend())
    for key, (title, tiles) in DATA["stack"].items():
        write(f"ui/div-{key}.svg", divider(title))
        for tid, label, ic, level in tiles:
            write(f"stack/{tid}.svg", tile(label, ic, level))
    for cid, ic, lines, meta, status in DATA["certs"]:
        write(f"certs/{cid}.svg", cert(ic, lines, meta, status))
    write("ui/timeline.svg", timeline())
    print("ok:", ", ".join(sorted(str(p.relative_to(ASSETS)).replace("\\", "/") for d in ("ui", "stack", "certs")
                                  for p in (ASSETS / d).glob("*.svg"))))


if __name__ == "__main__":
    main()
