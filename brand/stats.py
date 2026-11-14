"""Gera as estatísticas reais do perfil a partir da API do GitHub.

Saídas (todas versionadas no repositório, sem serviço externo):
  assets/sections/analytics(-mobile).svg   painel GitHub Analytics (desktop / celular)
  README.md                 mesmo conteúdo em texto, entre <!-- stats:start --> e <!-- stats:end -->

Uso:  python brand/stats.py            (token de GITHUB_TOKEN ou, se ausente, de `gh auth token`)
Só usa a biblioteca padrão e os módulos de brand/ (components, sections). Executado toda semana por .github/workflows/stats.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

LOGIN = "Pedro-Osaka"
ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"

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


LANG_ICONS = {"Python": "python", "PowerShell": "powershell", "JavaScript": "javascript", "TypeScript": "typescript",
              "HTML": "html5", "CSS": "css3"}


def analytics_svg(s: dict, mobile: bool = False) -> str:
    """Painel GitHub Analytics no estilo do topo.

    Destaque para o que ajuda a ler o perfil (projetos, atividade recente, tempo de conta);
    commits ficam numa linha secundária, sem número grande. Linguagens contadas por projeto
    ("aparece em 4 de 6"), nunca em porcentagem de bytes.
    """
    from components import BORDER as BD, CYAN as CY, DIM, MUTED as MU, SOFT, SURFACE as SF, TEXT as TX, icon, mono_text
    from sections import panel, sans

    metrics = [
        (str(s["projects"]), "projetos públicos", "sem contar o repositório de perfil"),
        (str(s["contributions"]), "contribuições", f"últimos 12 meses · {s['active_days']} dias ativos"),
        (month_label(s["since"]), "na conta desde", f"github.com/{LOGIN}"),
    ]
    langs = s["languages"][:5]
    n = max(1, s["projects"])
    if mobile:
        w, pad, head = 720, 34, 50
        f_num, f_lab, f_sub, row = 46, 23, 18, 96
        top = head + 30
        body_h = len(metrics) * row + 40 + 44 + len(langs) * 56
        h = top + body_h + 34
    else:
        w, pad, head = 1280, 40, 48
        f_num, f_lab, f_sub, row = 42, 20, 15, 86
        top = head + 30
        h = top + max(len(metrics) * row + 44, 40 + len(langs) * 50) + 26
    # no celular a data sai do cabeçalho (sobreporia o comando) e vai para a linha de commits
    out, _ = panel(w, h, f"pedro@infra:~$ gh api users/{LOGIN}", mobile, "" if mobile else f"atualizado {date_label(s['today'])}")
    x0 = 10 + pad
    for i, (num, lab, sub) in enumerate(metrics):
        y = top + i * row
        size = f_num if len(num) <= 4 else round(f_num * 0.72)
        out.append(sans(x0, y + f_num * 0.92, num, size, CY, 700))
        lx = x0 + (190 if mobile else 180)
        out.append(sans(lx, y + f_lab + 6, lab, f_lab, TX, 600))
        out.append(mono_text(lx, y + f_lab + 14 + f_sub, sub, f_sub, MU)[0])
        if i < len(metrics) - 1:
            out.append(f'<path d="M{x0} {y + row - 14}H{(w - 34) if mobile else 620}" stroke="{BD}" stroke-dasharray="3 5"/>')
    cy = top + len(metrics) * row
    commits = f"{s['commits']} commits nos repositórios públicos"
    if mobile:
        commits += f" · atualizado {date_label(s['today'])}"
    out.append(mono_text(x0, cy + (8 if mobile else 6), commits, f_sub, DIM)[0])
    if mobile:
        ly = cy + 40 + 30
        out.append(f'<path d="M{x0} {ly - 30}H{w - 34}" stroke="{BD}"/>')
        lx0, bar_x, bar_w, step, f_name, f_val, isz = x0, x0 + 240, 300, 56, 22, 18, 30
    else:
        out.append(f'<path d="M660 {top - 6}V{h - 26}" stroke="{BD}"/>')
        ly = top + 6
        lx0, bar_x, bar_w, step, f_name, f_val, isz = 700, 900, 230, 50, 18, 14, 26
    out.append(mono_text(lx0, ly, "linguagens · em quantos projetos aparecem", f_val, MU)[0])
    for i, (name, cnt) in enumerate(langs):
        y = ly + 26 + i * step
        ic = LANG_ICONS.get(name)
        if ic:
            out.append(icon(ic, lx0, y, isz))
        out.append(sans(lx0 + isz + 14, y + isz * 0.74, name, f_name, TX, 500))
        by = y + isz / 2 - 5
        out.append(f'<rect x="{bar_x}" y="{by:.1f}" width="{bar_w}" height="10" rx="5" fill="{SF}" stroke="{BD}"/>')
        out.append(f'<rect x="{bar_x}" y="{by:.1f}" width="{bar_w * cnt / n:.1f}" height="10" rx="5" fill="{CY}"/>')
        out.append(mono_text(bar_x + bar_w + 16, y + isz * 0.72, f"{cnt} de {n}", f_val, SOFT)[0])
    title = (f"GitHub Analytics de {LOGIN}: {s['projects']} projetos públicos; {s['contributions']} contribuições em "
             f"{s['active_days']} dias nos últimos 12 meses; na conta desde {month_label(s['since'])}; "
             f"{s['commits']} commits nos repositórios públicos. Linguagens por projeto: "
             + ", ".join(f"{nm} em {c} de {n}" for nm, c in langs) + ".")
    from components import svg
    return svg(w, h, title, "\n".join(out))


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
    out = ROOT / "assets" / "sections"
    out.mkdir(parents=True, exist_ok=True)
    (out / "analytics.svg").write_text(analytics_svg(s), encoding="utf-8", newline="\n")
    (out / "analytics-mobile.svg").write_text(analytics_svg(s, mobile=True), encoding="utf-8", newline="\n")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    new = re.sub(r"<!-- stats:start -->.*?<!-- stats:end -->", lambda _: readme_block(s), text, flags=re.S)
    readme.write_text(new, encoding="utf-8", newline="\n")
    print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
