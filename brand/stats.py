"""Gera as estatísticas reais do perfil a partir da API do GitHub.

Saídas (todas versionadas no repositório, sem serviço externo):
  assets/stats.svg          números da conta e linguagens por repositório
  README.md                 mesmo conteúdo em texto, entre <!-- stats:start --> e <!-- stats:end -->

Uso:  python brand/stats.py            (token de GITHUB_TOKEN ou, se ausente, de `gh auth token`)
Só usa a biblioteca padrão. Executado toda semana por .github/workflows/stats.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
from html import escape
from pathlib import Path

LOGIN = "Pedro-Osaka"
ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"

BG, SURFACE, BORDER = "#0F1419", "#151C23", "#2A3540"
TEXT, MUTED, CYAN, PETROL = "#E8ECF0", "#9AA7B4", "#5FB6C8", "#2B8A9E"
SANS = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'Courier New', monospace"
MONTHS = "jan fev mar abr mai jun jul ago set out nov dez".split()


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token", "-u", LOGIN], capture_output=True, text=True, check=True).stdout.strip()


def call(path: str, tok: str, body: dict | None = None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), r.headers


def commit_count(repo: str, tok: str) -> int:
    data, headers = call(f"/repos/{LOGIN}/{repo}/commits?per_page=1", tok)
    m = re.search(r'[?&]page=(\d+)>; rel="last"', headers.get("Link", ""))
    return int(m.group(1)) if m else len(data)


def collect(tok: str) -> dict:
    repos, _ = call(f"/users/{LOGIN}/repos?type=owner&per_page=100", tok)
    projects = [r for r in repos if not r["fork"] and not r["private"] and r["name"].lower() != LOGIN.lower()]
    langs: dict[str, int] = {}
    for r in projects:
        for name in call(f"/repos/{LOGIN}/{r['name']}/languages", tok)[0]:
            langs[name] = langs.get(name, 0) + 1
    commits = sum(commit_count(r["name"], tok) for r in repos if not r["fork"] and not r["private"])
    q = "query($l:String!){user(login:$l){createdAt contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"
    user = call("/graphql", tok, {"query": q, "variables": {"l": LOGIN}})[0]["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return {
        "projects": len(projects),
        "public_repos": len([r for r in repos if not r["private"]]),
        "commits": commits,
        "languages": sorted(langs.items(), key=lambda kv: (-kv[1], kv[0])),
        "contributions": cal["totalContributions"],
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
        "since": user["createdAt"][:7],
        "today": dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date().isoformat(),  # horário de Brasília
    }


def month_label(ym: str) -> str:
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]}/{y}"


def date_label(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def card(w: int, h: int, title: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/><rect width="8" height="{h}" fill="{PETROL}"/></g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="#222C36"/>
{body}
</svg>
"""


def mono(x, y, text, size, fill, anchor="start", weight=400):
    """Texto monoespaçado com largura fixa (textLength): igual em qualquer fonte de fallback."""
    tl = len(text) * size * 0.6
    return (f'<text x="{x:g}" y="{y:g}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')


def stats_svg(s: dict) -> str:
    w, h = 840, 268
    cells = [
        (str(s["projects"]), "projetos públicos", "sem o repo de perfil"),
        (str(s["commits"]), "commits", "repositórios públicos"),
        (str(s["contributions"]), "contribuições", f"12 meses · {s['active_days']} dias ativos"),
        (month_label(s["since"]), "na conta desde", f"github.com/{LOGIN}"),
    ]
    out = [f'<rect x="8" y="0" width="{w - 8}" height="42" fill="{SURFACE}" clip-path="url(#c)"/>',
           f'<path d="M8 42.5H{w}" stroke="#222C36"/>',
           mono(32, 26, "github analytics", 13, CYAN, weight=600),
           mono(w - 24, 26, f"API do GitHub · {date_label(s['today'])}", 12, "#5E6B78", "end")]
    cw = (w - 8) / 4
    for i, (num, lab, sub) in enumerate(cells):
        cx = 8 + cw * i + cw / 2
        if i:
            out.append(f'<path d="M{8 + cw * i:.1f} 66V170" stroke="{BORDER}"/>')
        size = 38 if len(num) <= 4 else 28
        out.append(f'<text x="{cx:.1f}" y="{112 if size == 38 else 108}" text-anchor="middle" font-family="{SANS}" '
                   f'font-size="{size}" font-weight="700" fill="{CYAN}">{escape(num)}</text>')
        out.append(f'<text x="{cx:.1f}" y="140" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="{TEXT}">{escape(lab)}</text>')
        out.append(mono(cx, 160, sub, 10.5, MUTED, "middle"))
    out.append(f'<path d="M32 192.5H{w - 24}" stroke="#222C36"/>')
    chips = [(name, n, len(f"{name} {n}") * 12 * 0.6 + 24) for name, n in s["languages"][:5]]
    label_w = len("linguagens · repos") * 11 * 0.6
    total = label_w + 18 + sum(c[2] for c in chips) + 8 * (len(chips) - 1)
    x = (w + 8 - total) / 2
    out.append(mono(x, 233, "linguagens · repos", 11, MUTED))
    x += label_w + 18
    for name, n, cw_ in chips:
        out.append(f'<rect x="{x:.1f}" y="214.5" width="{cw_:.1f}" height="26" rx="7" fill="{SURFACE}" stroke="{BORDER}"/>')
        out.append(mono(x + 12, 232, name, 12, "#C6D0DA"))
        out.append(mono(x + 12 + (len(name) + 1) * 12 * 0.6, 232, str(n), 12, CYAN, weight=600))
        x += cw_ + 8
    title = (f"Estatísticas de {LOGIN}: {s['projects']} projetos públicos, {s['commits']} commits, "
             f"{s['contributions']} contribuições em 12 meses")
    return card(w, h, title, "\n".join(out))


def readme_block(s: dict) -> str:
    langs = " · ".join(f"{n} ({c})" for n, c in s["languages"][:5])
    return (
        "<!-- stats:start -->\n"
        f"<sub>Em texto: **{s['projects']}** projetos públicos · **{s['commits']}** commits nos repositórios públicos · "
        f"**{s['contributions']}** contribuições em **{s['active_days']}** dias nos últimos 12 meses · conta criada em {month_label(s['since'])}. "
        f"Linguagens (nº de repositórios): {langs}. Gerado pela API do GitHub em {date_label(s['today'])}.</sub>\n"
        "<!-- stats:end -->"
    )


def main() -> int:
    s = collect(token())
    (ROOT / "assets" / "stats.svg").write_text(stats_svg(s), encoding="utf-8", newline="\n")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    new = re.sub(r"<!-- stats:start -->.*?<!-- stats:end -->", lambda _: readme_block(s), text, flags=re.S)
    readme.write_text(new, encoding="utf-8", newline="\n")
    print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
