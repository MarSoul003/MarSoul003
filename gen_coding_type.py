"""Genera coding-type.svg con la actividad pública de GitHub (solo stdlib)."""
import json, math, os, sys, urllib.request, collections, datetime as dt
# Edita esta lista con otros lenguajes/herramientas que usas fuera de repos publicos
EXTRAS = ["PHP", "Liquid", "JavaScript", "TypeScript", "HTML", "CSS", "SQL"]
USER = sys.argv[1] if len(sys.argv) > 1 else "MarSoul003"
TOKEN = os.environ.get("GITHUB_TOKEN")
def api(url):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "coding-type"}
    if TOKEN: h["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h)) as r: return json.load(r)
commits = []
for p in range(1, 6):
    d = api(f"https://api.github.com/search/commits?q=author:{USER}&sort=author-date&per_page=100&page={p}")
    commits += d.get("items", [])
    if len(d.get("items", [])) < 100: break
dates = [dt.datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00")) for c in commits]
hours = collections.Counter(d.hour for d in dates)
wd = collections.Counter(d.weekday() for d in dates)
days = collections.Counter(d.date() for d in dates)
repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
langs = collections.Counter()
for r in repos:
    if r.get("language"): langs[r["language"]] += 1
n = len(dates)
peak = max(hours, key=hours.get) if hours else 12
kind = "Madrugadora" if 5 <= peak < 12 else "Diurna" if 12 <= peak < 18 else "Vespertina" if 18 <= peak < 22 else "Noctámbula"
top = sorted(days.values(), reverse=True)
busy = sum(top[:max(1, len(top)//10)]) * 100 // n if n else 0
PAL = ["#8B7FD6", "#5BBF9A", "#E58FB0", "#E0B040"]
mx = max(hours.values()) if hours else 1
CX, CY = 320, 345
rad = ""
for h in range(24):
    a = (h / 24) * 2 * math.pi - math.pi / 2
    L = 14 + 52 * (hours.get(h, 0) / mx)
    x1, y1 = CX + 40 * math.cos(a), CY + 40 * math.sin(a)
    x2, y2 = CX + (40 + L) * math.cos(a), CY + (40 + L) * math.sin(a)
    op = 0.25 + 0.75 * hours.get(h, 0) / mx
    rad += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#8B7FD6" stroke-opacity="{op:.2f}" stroke-width="7" stroke-linecap="round"/>'
for h, l in ((0, "00"), (6, "06"), (12, "12"), (18, "18")):
    a = (h / 24) * 2 * math.pi - math.pi / 2
    rad += f'<text x="{CX+118*math.cos(a):.0f}" y="{CY+118*math.sin(a)+4:.0f}" text-anchor="middle" class="m sub" font-size="12">{l}</text>'
wm = max(wd.values()) if wd else 1
bars = ""
for i, l in enumerate("LMMJVSD"):
    h = 8 + 70 * wd.get(i, 0) / wm
    bars += f'<rect x="{36+i*38}" y="{570-h:.0f}" width="24" height="{h:.0f}" rx="6" fill="{"#5BBF9A" if i<5 else "#B7A6F0"}"/><text x="{48+i*38}" y="590" text-anchor="middle" class="m sub" font-size="12">{l}</text>'
tl = sum(langs.values()) or 1
auto = [k for k, _ in langs.most_common(3)]
extras = [e for e in EXTRAS if e not in langs]
bw = 280 - (24 if extras else 0)
seg, lg, x = "", "", 340
for i, k in enumerate(auto):
    v = langs[k]; w = bw * v / tl
    seg += f'<rect x="{x:.0f}" y="506" width="{w:.0f}" height="10" fill="{PAL[i]}"/>'; x += w
    lg += f'<circle cx="348" cy="{540+i*22}" r="5" fill="{PAL[i]}"/><text x="360" y="{545+i*22}" class="m mut" font-size="14">{k} {v*100//tl}%</text>'
if extras:
    seg += f'<rect x="{x:.0f}" y="506" width="{620-x:.0f}" height="10" fill="#D9D4EE"/>'
    row = 540 + len(auto) * 22
    lg += f'<circle cx="348" cy="{row}" r="5" fill="#D9D4EE"/><text x="360" y="{row+5}" class="m mut" font-size="14">Otros</text>'
    lines, cur = [], ""
    for e in extras:
        t = (cur + " · " + e) if cur else e
        if len(t) > 30: lines.append(cur); cur = e
        else: cur = t
    lines.append(cur)
    for j, ln in enumerate(lines[:3]):
        lg += f'<text x="348" y="{row+24+j*17}" class="m sub" font-size="12">{ln}</text>'
H = 660
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{H}" viewBox="0 0 640 {H}"><style>.t{{font-family:-apple-system,Inter,Segoe UI,Helvetica,Arial,sans-serif}}.m{{font-family:SF Mono,Menlo,Consolas,monospace}}
.ink{{fill:#1F2937}}.mut{{fill:#4B5563}}.sub{{fill:#6B7280}}.panel{{fill:#F7F5FD;stroke:#E5E0F5}}.chip{{fill:#fff;stroke:#E5E0F5}}.ring{{stroke:#E5E0F5}}
@media (prefers-color-scheme:dark){{.ink{{fill:#F3F1FA}}.mut{{fill:#C9C5DA}}.sub{{fill:#A29FB3}}.panel{{fill:#211E2C;stroke:#322E42}}.chip{{fill:#2A2638;stroke:#3F3A66}}.ring{{stroke:#322E42}}}}</style>
<rect x=".5" y=".5" width="639" height="{H-1}" rx="22" class="panel"/>
<text x="36" y="50" class="m sub" font-size="14" letter-spacing="2">TIPO DE CODIFICACIÓN</text>
<text x="36" y="102" class="t ink" font-size="44" font-weight="800">{kind}</text>
<text x="36" y="136" class="t mut" font-size="18">Pico de commits a las {peak}:00</text>
<text x="36" y="162" class="t mut" font-size="18">{busy}% de commits en el 10% de días más activos</text>
<rect x="36" y="180" width="118" height="32" rx="16" class="chip"/><text x="52" y="201" class="m mut" font-size="14">{len(repos)} repos</text>
<rect x="164" y="180" width="150" height="32" rx="16" class="chip"/><text x="180" y="201" class="m mut" font-size="14">{len(langs)} lenguajes</text>
<circle cx="{CX}" cy="{CY}" r="100" fill="none" class="ring"/><text x="{CX}" y="{CY-2}" text-anchor="middle" class="t ink" font-size="26" font-weight="700">{peak}h</text><text x="{CX}" y="{CY+16}" text-anchor="middle" class="m sub" font-size="12">pico</text>{rad}
<text x="36" y="488" class="t mut" font-size="15">Semana</text>{bars}
<text x="340" y="488" class="t mut" font-size="15">Lenguajes</text>{seg}{lg}
<text x="36" y="640" class="m sub" font-size="12">{n} commits públicos · actualizado {dt.date.today()}</text>
</svg>'''
open("coding-type.svg", "w").write(svg)
print("ok", n, "commits", dict(langs))

# ---------- versión ancha (escritorio) ----------
WX, WY = 460, 125
wrad = ""
for h in range(24):
    a = (h / 24) * 2 * math.pi - math.pi / 2
    L = 12 + 46 * (hours.get(h, 0) / mx)
    x1, y1 = WX + 34 * math.cos(a), WY + 34 * math.sin(a)
    x2, y2 = WX + (34 + L) * math.cos(a), WY + (34 + L) * math.sin(a)
    op = 0.25 + 0.75 * hours.get(h, 0) / mx
    wrad += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#8B7FD6" stroke-opacity="{op:.2f}" stroke-width="6" stroke-linecap="round"/>'
for h, l in ((0, "00"), (6, "06"), (12, "12"), (18, "18")):
    a = (h / 24) * 2 * math.pi - math.pi / 2
    wrad += f'<text x="{WX+112*math.cos(a):.0f}" y="{WY+112*math.sin(a)+4:.0f}" text-anchor="middle" class="m sub" font-size="11">{l}</text>'
wbars = ""
for i, l in enumerate("LMMJVSD"):
    h = 6 + 56 * wd.get(i, 0) / wm
    wbars += f'<rect x="{640+i*26}" y="{100-h:.0f}" width="16" height="{h:.0f}" rx="4" fill="{"#5BBF9A" if i<5 else "#B7A6F0"}"/><text x="{648+i*26}" y="116" text-anchor="middle" class="m sub" font-size="10">{l}</text>'
wseg, wlg, x = "", "", 640
bw2 = 160 - (14 if extras else 0)
for i, k in enumerate(auto):
    v = langs[k]; w = bw2 * v / tl
    wseg += f'<rect x="{x:.0f}" y="146" width="{w:.0f}" height="8" fill="{PAL[i]}"/>'; x += w
    wlg += f'<circle cx="{644+(i%2)*90}" cy="{172+(i//2)*16}" r="4" fill="{PAL[i]}"/><text x="{652+(i%2)*90}" y="{176+(i//2)*16}" class="m mut" font-size="11">{k} {v*100//tl}%</text>'
if extras:
    wseg += f'<rect x="{x:.0f}" y="146" width="{800-x:.0f}" height="8" fill="#D9D4EE"/>'
    r2 = 172 + ((len(auto) + 1) // 2) * 16
    wlg += f'<circle cx="644" cy="{r2}" r="4" fill="#D9D4EE"/><text x="652" y="{r2+4}" class="m mut" font-size="11">Otros</text>'
    wl, cur = [], ""
    for e in extras:
        t = (cur + " · " + e) if cur else e
        if len(t) > 24: wl.append(cur); cur = e
        else: cur = t
    wl.append(cur)
    for j, ln in enumerate(wl[:3]):
        wlg += f'<text x="652" y="{r2+18+j*13}" class="m sub" font-size="10">{ln}</text>'
wide = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="250" viewBox="0 0 860 250"><style>.t{{font-family:-apple-system,Inter,Segoe UI,Helvetica,Arial,sans-serif}}.m{{font-family:SF Mono,Menlo,Consolas,monospace}}
.ink{{fill:#1F2937}}.mut{{fill:#4B5563}}.sub{{fill:#6B7280}}.panel{{fill:#F7F5FD;stroke:#E5E0F5}}.chip{{fill:#fff;stroke:#E5E0F5}}.ring{{stroke:#E5E0F5}}
@media (prefers-color-scheme:dark){{.ink{{fill:#F3F1FA}}.mut{{fill:#C9C5DA}}.sub{{fill:#A29FB3}}.panel{{fill:#211E2C;stroke:#322E42}}.chip{{fill:#2A2638;stroke:#3F3A66}}.ring{{stroke:#322E42}}}}</style>
<rect x=".5" y=".5" width="859" height="249" rx="16" class="panel"/>
<text x="36" y="50" class="m sub" font-size="12" letter-spacing="2">TIPO DE CODIFICACIÓN</text>
<text x="36" y="96" class="t ink" font-size="34" font-weight="800">{kind}</text>
<text x="36" y="128" class="t mut" font-size="14">Pico de commits a las {peak}:00</text>
<text x="36" y="150" class="t mut" font-size="14">{busy}% de commits en el 10% de días más activos</text>
<rect x="36" y="172" width="100" height="28" rx="14" class="chip"/><text x="52" y="190" class="m mut" font-size="12">{len(repos)} repos</text>
<rect x="146" y="172" width="130" height="28" rx="14" class="chip"/><text x="162" y="190" class="m mut" font-size="12">{len(langs)} lenguajes</text>
<text x="36" y="228" class="m sub" font-size="11">{n} commits públicos · actualizado {dt.date.today()}</text>
<circle cx="{WX}" cy="{WY}" r="100" fill="none" class="ring"/><text x="{WX}" y="{WY-3}" text-anchor="middle" class="t ink" font-size="20" font-weight="700">{peak}h</text><text x="{WX}" y="{WY+13}" text-anchor="middle" class="m sub" font-size="10">pico</text>{wrad}
<text x="640" y="50" class="t mut" font-size="12">Semana</text>{wbars}
<text x="640" y="140" class="t mut" font-size="12">Lenguajes</text>{wseg}{wlg}
</svg>'''
open("coding-type-wide.svg", "w").write(wide)
