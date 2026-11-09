"""Builds the PORTFOLIO / LINKEDIN / EMAIL buttons shown under the card."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = {
    # simple outline icons drawn in a 24x24 box
    "portfolio": '<rect x="2" y="4" width="20" height="13" rx="1.5" fill="none" stroke="{c}" stroke-width="2"/>'
                 '<path d="M6 9l3 2-3 2M11 13h5M8 21h8M12 17v4" fill="none" stroke="{c}" stroke-width="2"/>',
    "linkedin": '<rect x="2" y="2" width="20" height="20" rx="3" fill="{c}"/>'
                '<path d="M7 10v7M7 7v.01M11 17v-7M11 13a3 3 0 0 1 6 0v4" fill="none" stroke="{bg}" stroke-width="2.2" stroke-linecap="round"/>',
    "email": '<rect x="2" y="5" width="20" height="14" rx="1.5" fill="none" stroke="{c}" stroke-width="2"/>'
             '<path d="M2 6l10 7 10-7" fill="none" stroke="{c}" stroke-width="2"/>',
}
BUTTONS = [("portfolio", "PORTFOLIO", "#ffa657"), ("linkedin", "LINKEDIN", "#a5d6ff"), ("email", "EMAIL", "#ffa657")]
THEMES = {"dark": dict(bg="#161b22", text="#c9d1d9", border="#30363d"),
          "light": dict(bg="#f6f8fa", text="#24292f", border="#d0d7de")}

for theme, t in THEMES.items():
    for key, label, accent in BUTTONS:
        accent = accent if theme == "dark" else {"#ffa657": "#953800", "#a5d6ff": "#0a3069"}[accent]
        icon = ICONS[key].format(c=accent, bg=t["bg"])
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="56" viewBox="0 0 320 56">
<rect x="1" y="1" width="318" height="54" rx="6" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>
<rect x="6" y="50" width="308" height="3" rx="1.5" fill="{accent}"/>
<g transform="translate({160 - (len(label) * 11 + 40) // 2},14)">{icon}</g>
<text x="{160 - (len(label) * 11 + 40) // 2 + 36}" y="34" font-family="ConsolasFallback,Consolas,Menlo,monospace" font-size="19" fill="{t["text"]}">{label}</text>
</svg>
'''
        (ROOT / "assets" / f"{key}-{theme}.svg").write_text(svg)
print("buttons built")
