"""Gera os selos de status usados na grade de projetos do README (assets/status/*.svg).

Mesmas cores dos selos das capas: verde = funcional/concluído, âmbar = WIP/em documentação, ciano = publicado.
Uso:  python brand/status.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "status"
SANS_MONO = "'JetBrains Mono', Consolas, 'Courier New', monospace"
STATUS = {
    "funcional": ("FUNCIONAL", "#6CC79A"),
    "concluido": ("CONCLUÍDO", "#6CC79A"),
    "em-documentacao": ("EM DOCUMENTAÇÃO", "#E0A030"),
    "wip": ("WIP · PROTÓTIPO", "#E0A030"),
    "publicado": ("PUBLICADO", "#5FB6C8"),
}


def pill(label: str, color: str) -> str:
    w = round(len(label) * 7.6 + 38)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="24" viewBox="0 0 {w} 24" role="img" aria-label="Status: {label.lower()}">
<title>Status: {label.lower()}</title>
<rect x="0.5" y="0.5" width="{w - 1}" height="23" rx="11.5" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-opacity="0.45"/>
<circle cx="13" cy="12" r="3.5" fill="{color}"/>
<text x="24" y="16.2" font-family="{SANS_MONO}" font-size="12" font-weight="600" letter-spacing="0.6" fill="{color}">{label}</text>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (label, color) in STATUS.items():
        (OUT / f"{key}.svg").write_text(pill(label, color), encoding="utf-8", newline="\n")
        print(OUT / f"{key}.svg")
