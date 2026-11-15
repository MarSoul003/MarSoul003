"""Genera coding-type.svg con la actividad pública de GitHub (solo stdlib)."""
import json, math, os, sys, urllib.request, collections, datetime as dt
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
    if r.get("language") and not r.get("fork"): langs[r["language"]] += 1
n = len(dates)
peak = max(hours, key=hours.get) if hours else 12
if 5 <= peak < 12: kind = "Madrugadora"
elif 12 <= peak < 18: kind = "Diurna"
elif 18 <= peak < 22: kind = "Vespertina"
else: kind = "Noctámbula"
top = sorted(days.values(), reverse=True)
busy = sum(top[:max(1, len(top)//10)]) * 100 // n if n else 0
PAL = ["#8B7FD6", "#5BBF9A", "#E58FB0", "#E0B040", "#7FB2E5", "#B7A6F0"]
mx = max(hours.values()) if hours else 1
rad = ""
for h in range(24):
    a = (h / 24) * 2 * math.pi - math.pi / 2
    L = 12 + 46 * (hours.get(h, 0) / mx)
    x1, y1 = 460 + 34 * math.cos(a), 125 + 34 * math.sin(a)
    x2, y2 = 460 + (34 + L) * math.cos(a), 125 + (34 + L) * math.sin(a)
    op = 0.25 + 0.75 * hours.get(h, 0) / mx
    rad += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#8B7FD6" stroke-opacity="{op:.2f}" stroke-width="6" stroke-linecap="round"/>'
wm = max(wd.values()) if wd else 1
bars = ""
for i, l in enumerate("LMMJVSD"):
    h = 6 + 56 * wd.get(i, 0) / wm
    bars += f'<rect x="{640+i*26}" y="{100-h:.0f}" width="16" height="{h:.0f}" rx="4" fill="{"#5BBF9A" if i<5 else "#B7A6F0"}"/><text x="{648+i*26}" y="116" text-anchor="middle" class="m" font-size="10" fill="#9CA3AF">{l}</text>'
tl = sum(langs.values()) or 1
seg, lg, x = "", "", 640
for i, (k, v) in enumerate(langs.most_common(4)):
    w = 160 * v / tl
    seg += f'<rect x="{x:.0f}" y="146" width="{w:.0f}" height="8" fill="{PAL[i]}"/>'; x += w
    lg += f'<circle cx="{644+(i%2)*90}" cy="{172+(i//2)*16}" r="4" fill="{PAL[i]}"/><text x="{652+(i%2)*90}" y="{176+(i//2)*16}" class="m" font-size="11" fill="#4B5563">{k} {v*100//tl}%</text>'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="250" viewBox="0 0 860 250"><style>.t{{font-family:-apple-system,Inter,Segoe UI,Helvetica,Arial,sans-serif}}.m{{font-family:SF Mono,Menlo,Consolas,monospace}}</style>
<rect x=".5" y=".5" width="859" height="249" rx="16" fill="#F7F5FD" stroke="#E5E0F5"/>
<text x="36" y="50" class="m" font-size="12" letter-spacing="2" fill="#9CA3AF">TIPO DE CODIFICACIÓN</text>
<text x="36" y="96" class="t" font-size="34" font-weight="800" fill="#1F2937">{kind}</text>
<text x="36" y="128" class="t" font-size="14" fill="#4B5563">Pico de commits a las {peak}:00</text>
<text x="36" y="150" class="t" font-size="14" fill="#4B5563">{busy}% de commits en el 10% de días más activos</text>
<rect x="36" y="172" width="{len(repos)*0+120}" height="28" rx="14" fill="#fff" stroke="#E5E0F5"/><text x="52" y="190" class="m" font-size="12" fill="#374151">{len(repos)} repos</text>
<rect x="166" y="172" width="150" height="28" rx="14" fill="#fff" stroke="#E5E0F5"/><text x="182" y="190" class="m" font-size="12" fill="#374151">{len(langs)} lenguajes</text>
<text x="36" y="228" class="m" font-size="11" fill="#9CA3AF">{n} commits públicos · actualizado {dt.date.today()}</text>
<circle cx="460" cy="125" r="100" fill="none" stroke="#E5E0F5"/><text x="460" y="122" text-anchor="middle" class="t" font-size="20" font-weight="700" fill="#1F2937">{peak}h</text><text x="460" y="138" text-anchor="middle" class="m" font-size="10" fill="#9CA3AF">pico</text>
{rad}
<text x="640" y="50" class="t" font-size="12" fill="#4B5563">Semana</text>{bars}
<text x="640" y="140" class="t" font-size="12" fill="#4B5563">Lenguajes</text>{seg}{lg}
</svg>'''
open("coding-type.svg", "w").write(svg)
print("ok", n, "commits", dict(langs))
