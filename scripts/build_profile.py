"""Builds the terminal-style profile cards (dark_mode.svg and light_mode.svg).

Run locally:      python scripts/build_profile.py
Run in Actions:   GITHUB_TOKEN is set, so live stats are fetched first.
If fetching fails, the last saved numbers in stats.json are used.
"""
import json
import math
import os
import urllib.request
from html import escape
from pathlib import Path

USER = "Bilal-Bangash"
ROOT = Path(__file__).resolve().parent.parent
STATS_FILE = ROOT / "stats.json"
WIDTH = 60  # characters per info line

# ---------------------------------------------------------------- content
INFO = [
    ("header", "bilal@bangash"),
    ("kv", "Host", "vGreens · Essen, Germany"),
    ("kv", "Kernel", "Senior Full-Stack Engineer"),
    ("kv", "Uptime", "7+ years shipping production code"),
    ("kv", "Industries", "HealthTech, AgTech, AI SaaS"),
    ("blank",),
    ("kv", "Languages.Programming", "TypeScript, JavaScript, Python"),
    ("kv", "Languages.Computer", "HTML, CSS, GraphQL, JSON, YAML"),
    ("kv", "Languages.Real", "English, Urdu, Pashto, German"),
    ("blank",),
    ("kv", "Stack.Frontend", "React, Next.js, React Native"),
    ("kv", "Stack.Backend", "Node.js, NestJS, GraphQL"),
    ("kv", "Stack.AI", "Claude & OpenAI APIs, tool use"),
    ("kv", "Stack.Testing", "Jest"),
    ("blank",),
    ("header", "- Contact"),
    ("kv", "Email", "muhammadbilalbangash@hotmail.com"),
    ("kv", "LinkedIn", "mbbangash"),
    ("kv", "Portfolio", "mbbangash.com"),
    ("blank",),
    ("header", "- GitHub Stats"),
    ("stats",),
]

THEMES = {
    "dark": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff",
                 dots="#616e7f", accent="#3fb950", art="#c9d1d9"),
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069",
                  dots="#c2cfde", accent="#1a7f37", art="#24292f"),
}


# ---------------------------------------------------------------- art
def torus(W=46, H=24, A=1.4, B=0.0, R1=0.85, R2=2.1, K2=6.0):
    """Shaded ASCII torus, lit from above."""
    K1 = W * K2 * 3 / (8 * (R1 + R2))
    out = [[" "] * W for _ in range(H)]
    zbuf = [[0.0] * W for _ in range(H)]
    ramp = ".,-~:;=!*#$@"
    cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
    t = 0.0
    while t < 2 * math.pi:
        ct, st = math.cos(t), math.sin(t)
        p = 0.0
        while p < 2 * math.pi:
            cp, sp = math.cos(p), math.sin(p)
            cx, cy = R2 + R1 * ct, R1 * st
            x = cx * (cB * cp + sA * sB * sp) - cy * cA * sB
            y = cx * (sB * cp - sA * cB * sp) + cy * cA * cB
            ooz = 1 / (K2 + cA * cx * sp + cy * sA)
            xp, yp = int(W / 2 + K1 * ooz * x), int(H / 2 - K1 * ooz * y * 0.5)
            lum = cp * ct * sB - cA * ct * sp - sA * st + cB * (cA * st - ct * sA * sp)
            if 0 <= xp < W and 0 <= yp < H and ooz > zbuf[yp][xp]:
                zbuf[yp][xp] = ooz
                out[yp][xp] = ramp[min(11, max(0, int(lum * 8)))] if lum > 0 else "."
            p += 0.012
        t += 0.03
    lines = ["".join(r).rstrip() for r in out]
    lines = [l for l in lines if l.strip()]
    indent = min(len(l) - len(l.lstrip()) for l in lines)
    return [l[indent:] for l in lines]


# ---------------------------------------------------------------- stats
def gh(url, data=None):
    headers = {"User-Agent": "profile-card-builder", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_stats():
    user = gh(f"https://api.github.com/users/{USER}")
    repos = gh(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    commits = gh(f"https://api.github.com/search/commits?q=author:{USER}&per_page=1")
    stats = {
        "repos": user["public_repos"],
        "followers": user["followers"],
        "stars": sum(r["stargazers_count"] for r in repos),
        "commits": commits["total_count"],
    }
    if os.environ.get("GITHUB_TOKEN"):  # GraphQL needs a token
        q = {"query": f'{{user(login:"{USER}"){{contributionsCollection{{contributionCalendar{{totalContributions}}}}}}}}'}
        res = gh("https://api.github.com/graphql", q)
        stats["contributions"] = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    return stats


def load_stats():
    saved = json.loads(STATS_FILE.read_text()) if STATS_FILE.exists() else {}
    try:
        saved.update(fetch_stats())
        STATS_FILE.write_text(json.dumps(saved, indent=2) + "\n")
    except Exception as e:  # keep the last good numbers
        print(f"Stats fetch failed, using saved values: {e}")
    return saved


# ---------------------------------------------------------------- svg
def kv_line(key, value, width=WIDTH):
    dots = max(2, width - len(key) - len(value) - 5)
    return [(". ", "dots"), (key, "key"), (":", "text"), (" " + "." * dots + " ", "dots"), (value, "value")]


def pair_line(k1, v1, k2, v2):
    left_w, right_w = 30, WIDTH - 33
    d1 = max(2, left_w - len(k1) - len(v1) - 5)
    d2 = max(2, right_w - len(k2) - len(v2) - 3)
    return [(". ", "dots"), (k1, "key"), (":", "text"), (" " + "." * d1 + " ", "dots"), (v1, "value"),
            (" | ", "text"), (k2, "key"), (":", "text"), (" " + "." * d2 + " ", "dots"), (v2, "value")]


def header_line(title):
    return [(title, "key" if "@" in title else "text"), (" " + "—" * (WIDTH - len(title) - 1), "text")]


def info_lines(stats):
    fmt = lambda n: f"{n:,}" if isinstance(n, int) else "-"
    lines = []
    for item in INFO:
        kind = item[0]
        if kind == "header":
            lines.append(header_line(item[1]))
        elif kind == "kv":
            lines.append(kv_line(item[1], item[2]))
        elif kind == "blank":
            lines.append([(". ", "dots")])
        elif kind == "stats":
            lines.append(pair_line("Repos", fmt(stats.get("repos")), "Stars", fmt(stats.get("stars"))))
            lines.append(pair_line("Commits", fmt(stats.get("commits")), "Followers", fmt(stats.get("followers"))))
            if "contributions" in stats:
                lines.append(kv_line("Contributions (last year)", fmt(stats["contributions"])))
    return lines


def load_art(theme):
    """ASCII portrait in assets/portrait-<theme>.txt; falls back to a torus."""
    f = ROOT / "assets" / f"portrait-{theme}.txt"
    if f.exists():
        return f.read_text(encoding="utf-8").rstrip("\n").split("\n"), 13, 16
    return torus(), 16, 20


def svg(theme, stats):
    c = THEMES[theme]
    art, art_fs, art_lh = load_art(theme)
    info = info_lines(stats)
    lh, top = 20, 30
    height = max(top + lh * len(info), top + art_lh * len(art)) + 20
    art_top = top + max(0, (lh * len(info) - art_lh * len(art)) // 2)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,Menlo,monospace" '
        f'width="985px" height="{height}px" font-size="16px">',
        "<style>@font-face{src:local('Consolas'),local('Consolas Bold');font-family:'ConsolasFallback';"
        "font-display:swap;-webkit-size-adjust:109%;size-adjust:109%;}"
        f".key{{fill:{c['key']};}}.value{{fill:{c['value']};}}.dots{{fill:{c['dots']};}}"
        f".text{{fill:{c['text']};}}text,tspan{{white-space:pre;}}</style>",
        f'<rect width="985px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
        f'<text x="15" y="{art_top}" fill="{c["art"]}" font-size="{art_fs}px" class="ascii">',
    ]
    for i, line in enumerate(art):
        out.append(f'<tspan x="15" y="{art_top + i * art_lh}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="390" y="{top}" fill="{c["text"]}">')
    for i, parts in enumerate(info):
        spans = "".join(f'<tspan class="{cls}">{escape(txt)}</tspan>' for txt, cls in parts)
        out.append(f'<tspan x="390" y="{top + i * lh}">{spans}</tspan>')
    out.append("</text></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    stats = load_stats()
    for theme in THEMES:
        (ROOT / f"{theme}_mode.svg").write_text(svg(theme, stats), encoding="utf-8")
    print("Built cards with", stats)
