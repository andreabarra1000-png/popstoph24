#!/usr/bin/env python3
"""Genera tutto il sito Pop Stop h24 da site.json + stock.json.

Uso (dalla cartella del repo):  python3 scripts/build_site.py
Per passare al dominio nuovo basta cambiare "base" in site.json (es. "https://popstoph24.it/")
e rilanciare: canonical, dati strutturati, sitemap e robots si aggiornano da soli.
"""
import json, re, html, os, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
STOCK = json.load(open(os.path.join(ROOT, "stock.json"), encoding="utf-8"))
BASE = S["base"].rstrip("/") + "/"
OGGI = datetime.date.today().isoformat()
PRODOTTI = STOCK["prodotti"]
NPROD = len(PRODOTTI)
E = html.escape

ORDINE = ["Energy drink", "Bibite", "Acqua", "Caffè e latte", "Patatine e snack salati",
          "Tramezzini e salato", "Dolci e cioccolato", "Caramelle e gomme", "Igiene e altro"]
ICONE = {"Energy drink": "⚡", "Bibite": "🥤", "Acqua": "💧", "Caffè e latte": "☕",
         "Patatine e snack salati": "🌶️", "Tramezzini e salato": "🥪", "Dolci e cioccolato": "🍫",
         "Caramelle e gomme": "🍬", "Igiene e altro": "🧴"}
MONDO = re.compile(r"dr pepper|\bus\b|high up|takis|355 ?ml|starbucks|skittles|oreo|m[e&]m'?s|lando|vr46", re.I)

INDIRIZZO_FULL = f'{S["indirizzo"]}, {S["cap"]} {S["citta"]} ({S["provincia"]})'
MAPS_DIR = f'https://www.google.com/maps/dir/?api=1&destination={quote(S["nome"]+" "+S["indirizzo"]+" "+S["citta"])}&destination_place_id={S["place_id"]}'
MAPS_EMBED = "https://www.google.com/maps?q=" + quote(f'PopStop H24, {S["indirizzo"]}, {S["cap"]} {S["citta"]} NA') + "&output=embed"
WAZE = "https://waze.com/ul?q=" + quote(f'{S["indirizzo"]} {S["citta"]}') + "&navigate=yes"
APPLE = "https://maps.apple.com/?q=" + quote(S["nome"]) + "&address=" + quote(INDIRIZZO_FULL)
REVIEW = f'https://search.google.com/local/writereview?placeid={S["place_id"]}'
WA = f'https://wa.me/{S["whatsapp"]}?text=' + quote("Ciao Pop Stop h24! ")
WA_ASS = f'https://wa.me/{S["whatsapp"]}?text=' + quote("Ciao Pop Stop h24, ho bisogno di assistenza. Macchina/ordine: ")
TEL = "tel:" + S["telefono"].replace(" ", "")
APP = S["app"]

def _norm_dr(x):
    import unicodedata
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower().replace("&", "e").replace("'", "")
    x = re.sub(r"(\d)\s*(ml|g|pz|x)\b", r"\1\2", x)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", x).split())

def deliveroo_map():
    """Collega ogni prodotto del sito alla sua scheda su Deliveroo (deliveroo.tsv: id<TAB>nome sul menu)."""
    righe = {}
    try:
        for l in open(os.path.join(ROOT, "deliveroo.tsv"), encoding="utf-8"):
            if "\t" in l:
                i, n = l.rstrip("\n").split("\t", 1)
                righe[_norm_dr(n)] = i
    except OSError:
        return {}
    out = {}
    for p in STOCK["prodotti"]:
        k = _norm_dr(p["n"])
        if k in righe:
            out[p["n"]] = righe[k]
            continue
        # nome sul menu senza grammatura: accetta solo se è l'inizio esatto del nome
        cand = [n for n in righe if len(n) >= 10 and (k.startswith(n + " ") or n.startswith(k + " "))]
        if cand:
            cand.sort(key=len, reverse=True)
            if len(cand) == 1 or len(cand[0]) > len(cand[1]):
                out[p["n"]] = righe[cand[0]]
    return out
DR = deliveroo_map()

ZONE = {
  "casoria": {"nome": "Casoria", "frase": "Casoria è attaccata a Casavatore",
    "vicino": "Da Casoria ci raggiungi in pochi minuti: siamo su Viale Guglielmo Marconi, a Casavatore.",
    "extra": "Studi fino a tardi, turno di notte, serata con gli amici a Casoria? Apri l'app, scrivi il tuo indirizzo e controlla se il tuo palazzo è nella zona di consegna."},
  "arzano": {"nome": "Arzano", "frase": "Arzano è a due passi da Casavatore",
    "vicino": "Da Arzano sei vicinissimo al nostro punto self-service di Viale Guglielmo Marconi 79/81, a Casavatore.",
    "extra": "Ad Arzano la notte è lunga e i negozi chiudono presto: noi no. Energy drink, acqua fresca, tramezzini e dolci sono sempre nelle macchine."},
  "secondigliano": {"nome": "Secondigliano", "frase": "Secondigliano confina con Casavatore",
    "vicino": "Da Secondigliano e dalla zona nord di Napoli arrivi a Casavatore in pochi minuti di auto o scooter.",
    "extra": "Per Napoli nord siamo il punto aperto 24 ore più comodo per uno spuntino, una bibita o qualcosa di urgente come acqua e igiene."},
  "afragola": {"nome": "Afragola", "frase": "Afragola è a pochi minuti da Casavatore",
    "vicino": "Da Afragola, passando per Casoria, arrivi a Casavatore in un quarto d'ora o poco più.",
    "extra": "Dopo una serata o un turno di notte ad Afragola, da noi trovi sempre bibite fresche, energy drink, tramezzini e dolci: e se l'app consegna al tuo indirizzo, te li portano a casa."},
  "casalnuovo": {"nome": "Casalnuovo di Napoli", "frase": "Casalnuovo è nell'area nord-est, non lontano da Casavatore",
    "vicino": "Da Casalnuovo di Napoli arrivi a Viale Guglielmo Marconi a Casavatore passando per Casoria.",
    "extra": "Studio fino a tardi, partita alla PlayStation o fame improvvisa a Casalnuovo? Controlla sull'app se consegniamo al tuo indirizzo: energy drink, patatine, Takis e snack dal mondo."},
  "scampia": {"nome": "Scampia", "frase": "Scampia è nella zona nord di Napoli, vicino a Casavatore",
    "vicino": "Da Scampia e Piscinola arrivi a Casavatore in pochi minuti, passando per Secondigliano.",
    "extra": "Quando a Scampia è tutto chiuso, i distributori di Pop Stop sono accesi: acqua, bibite, energy drink, dolci, tramezzini e prodotti utili, giorno e notte."},
  "miano": {"nome": "Miano", "frase": "Miano confina con Secondigliano, a due passi da Casavatore",
    "vicino": "Da Miano e dal Rione Don Guanella arrivi a Casavatore in pochi minuti di auto o scooter.",
    "extra": "Per chi vive a Miano siamo il punto aperto 24 ore più vicino nella zona nord: snack, bibite fredde e beni di prima necessità a qualsiasi ora."},
  "san-pietro-a-patierno": {"nome": "San Pietro a Patierno", "frase": "San Pietro a Patierno e Capodichino sono a pochi minuti",
    "vicino": "Da San Pietro a Patierno, Capodichino e dall'aeroporto passi da Casavatore in pochi minuti.",
    "extra": "Atterrato tardi a Capodichino o rientri dal lavoro di notte? Da noi trovi sempre bibite, acqua, snack e dolci, anche alle 4 del mattino."},
}

def rel(depth):
    return "../" * depth

def app_cards(cls="apps"):
    out = [f'<div class="{cls}">']
    for k, (nome, url) in APP.items():
        out.append(f'<a class="app {k}" href="{url}" rel="noopener" target="_blank" data-app="{k}"><div><small>Ordina su</small><h3>{nome}</h3></div><div class="go">Ordina ora <i>→</i></div></a>')
    out.append("</div>")
    return "".join(out)

def store_ld():
    return {
      "@type": "ConvenienceStore", "@id": BASE + "#negozio",
      "name": S["nome"], "alternateName": ["PopStop H24", "Pop Stop h24 Casavatore", "popstoph24"],
      "description": "Punto vendita self-service con distributori automatici aperto 24 ore su 24, 7 giorni su 7, a Casavatore (Napoli nord): energy drink, bibite, acqua, snack dolci e salati, tramezzini, caramelle, snack e bibite dal mondo e beni di prima necessità. Consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino.",
      "url": BASE, "image": BASE + "assets/og.png", "logo": BASE + "assets/icon-512.png",
      "telephone": S["telefono"], "vatID": "IT" + S.get("piva", ""),
      "geo": {"@type": "GeoCoordinates", "latitude": S["geo"][0], "longitude": S["geo"][1]},
      "address": {"@type": "PostalAddress", "streetAddress": S["indirizzo"], "addressLocality": S["citta"],
                  "postalCode": S["cap"], "addressRegion": S["provincia"], "addressCountry": "IT"},
      "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
          "opens": "00:00", "closes": "23:59"}],
      "areaServed": [{"@type": "City", "name": n} for n in ["Casavatore", "Casoria", "Arzano", "Afragola", "Casalnuovo di Napoli", "Napoli"]],
      "hasMap": f'https://www.google.com/maps/search/?api=1&query=PopStop%20H24&query_place_id={S["place_id"]}',
      "sameAs": list(S["social"].values()) + list(S.get("schede", {}).values()) + [u for _, u in APP.values()],
      "potentialAction": {"@type": "OrderAction", "target": [u for _, u in APP.values()],
                          "deliveryMethod": "http://purl.org/goodrelations/v1#DeliveryModeOwnFleet"},
      "keywords": "distributori automatici h24, aperto 24 ore, minimarket self-service, snack, bibite, energy drink, consegna a domicilio, Casavatore, Casoria, Napoli nord",
    }

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faq]}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + p} for i, (n, p) in enumerate(items)]}

def faq_html(faq):
    return '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{a}</p></details>" for q, a in faq) + "</div>"

CAP = '''<g class="p-cap"><path d="M38 22 Q100 -30 162 22 Z" fill="#e8133b" stroke="#061219" stroke-width="5" stroke-linejoin="round"/><path d="M150 18 Q190 16 198 30 Q170 30 146 26 Z" fill="#c40f31" stroke="#061219" stroke-width="5" stroke-linejoin="round"/><circle cx="100" cy="-3" r="5" fill="#c40f31" stroke="#061219" stroke-width="3"/></g>'''

SCARPA_L = '''<g class="p-scarpa"><path d="M48 240 Q48 235 55 235 L70 235 Q75 242 87 245 Q93 249 88 255 L50 255 Q45 255 45 250 Z" fill="#fff" stroke="#061219" stroke-width="3.5" stroke-linejoin="round"/><path d="M46 251 L90 251" stroke="#2b59d9" stroke-width="3.5"/><path d="M53 247 Q67 249 80 240" fill="none" stroke="#e8133b" stroke-width="4.5" stroke-linecap="round"/></g>'''
SCARPA_R = '''<g class="p-scarpa"><path d="M118 240 Q118 235 125 235 L140 235 Q145 242 157 245 Q163 249 158 255 L120 255 Q115 255 115 250 Z" fill="#fff" stroke="#061219" stroke-width="3.5" stroke-linejoin="round"/><path d="M116 251 L160 251" stroke="#2b59d9" stroke-width="3.5"/><path d="M123 247 Q137 249 150 240" fill="none" stroke="#e8133b" stroke-width="4.5" stroke-linecap="round"/></g>'''

def pop_svg(cls="pop", label="POP, la mascotte di Pop Stop h24", cap=False):
    aria = f'role="img" aria-label="{E(label)}"' if label else 'aria-hidden="true"'
    return f'''<svg class="{cls}" viewBox="0 0 200 260" {aria}>
<ellipse class="p-ombra" cx="100" cy="250" rx="70" ry="8" fill="#000" opacity=".25"/>
<g class="p-legL"><rect x="52" y="222" width="26" height="26" rx="8" fill="#0b3b44"/>{SCARPA_L if cap else ''}</g>
<g class="p-legR"><rect x="122" y="222" width="26" height="26" rx="8" fill="#0b3b44"/>{SCARPA_R if cap else ''}</g>
<g class="p-body">
<g class="p-armL"><rect x="6" y="120" width="26" height="14" rx="7" fill="#05848A" stroke="#061219" stroke-width="4"/></g>
<g class="p-armR"><rect x="168" y="120" width="26" height="14" rx="7" fill="#05848A" stroke="#061219" stroke-width="4"/></g>
<rect x="24" y="14" width="152" height="220" rx="26" fill="#05848A" stroke="#061219" stroke-width="6"/>
<rect x="32" y="22" width="136" height="204" rx="20" fill="#19d6c8" opacity=".25"/>
<rect x="40" y="24" width="120" height="34" rx="12" fill="#061219"/>
<text x="100" y="50" text-anchor="middle" font-family="Bricolage,system-ui,sans-serif" font-weight="800" font-size="24" fill="#FFD23F">POP h24</text>
<g class="p-eyes"><ellipse cx="76" cy="84" rx="15" ry="17" fill="#fff" stroke="#061219" stroke-width="4"/><ellipse cx="124" cy="84" rx="15" ry="17" fill="#fff" stroke="#061219" stroke-width="4"/>
<g class="p-pup"><circle cx="79" cy="87" r="7" fill="#061219"/><circle cx="127" cy="87" r="7" fill="#061219"/><circle cx="82" cy="83" r="2.5" fill="#fff"/><circle cx="130" cy="83" r="2.5" fill="#fff"/></g></g>
<ellipse cx="58" cy="106" rx="9" ry="5" fill="#ff4f8b" opacity=".55"/><ellipse cx="142" cy="106" rx="9" ry="5" fill="#ff4f8b" opacity=".55"/>
<path class="p-mouth" d="M84 104 Q100 120 116 104" fill="#061219" stroke="#061219" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="40" y="126" width="92" height="92" rx="10" fill="#e9fbfb" stroke="#061219" stroke-width="4"/>
<g class="p-snack" stroke="#061219" stroke-width="2"><rect x="47" y="133" width="22" height="22" rx="4" fill="#ff4f8b"/><rect x="75" y="133" width="22" height="22" rx="4" fill="#FFD23F"/><rect x="103" y="133" width="22" height="22" rx="4" fill="#7b2ff7"/><rect x="47" y="161" width="22" height="22" rx="11" fill="#ff9a3c"/><rect x="75" y="161" width="22" height="22" rx="4" fill="#19d6c8"/><rect x="103" y="161" width="22" height="22" rx="11" fill="#3ee07a"/><rect x="47" y="189" width="22" height="22" rx="4" fill="#0b3d91"/><rect x="75" y="189" width="22" height="22" rx="11" fill="#ff5a4e"/><rect x="103" y="189" width="22" height="22" rx="4" fill="#FFD23F"/></g>
<rect x="138" y="126" width="24" height="92" rx="8" fill="#061219"/>
<g class="p-led" fill="#19d6c8"><circle cx="145" cy="138" r="3"/><circle cx="155" cy="138" r="3"/><circle cx="145" cy="148" r="3"/><circle cx="155" cy="148" r="3"/><circle cx="145" cy="158" r="3"/><circle cx="155" cy="158" r="3"/></g>
<rect x="142" y="172" width="16" height="6" rx="3" fill="#FFD23F"/><rect x="142" y="196" width="16" height="14" rx="4" fill="#0b3b44"/>
{CAP if cap else ''}</g></svg>'''

def tg_block(r):
    novi = [p["n"] for p in PRODOTTI if re.search(r"nutella peanut|winter edition|iced gummy|nutella biscuits natale|kinder joy tripack|takis", p["n"], re.I)][:5]
    presi = [n for n in S.get("piu_presi", []) if any(p["n"] == n for p in PRODOTTI)][:3]
    items = [
      "Sono le <b data-ora>24h</b> e Pop Stop è aperto",
      f"Nelle macchine ora: <b>{NPROD} prodotti</b>",
    ]
    if novi: items.append("Novità: " + " · ".join(E(n) for n in novi))
    if presi: items.append("I più presi: " + " · ".join(E(n) for n in presi))
    items += [
      "Consegna a domicilio con Glovo · Just Eat · Deliveroo · Alfonsino",
      f'Sfida POP: <a href="{r}gioco/">riempi le macchine prima delle 6 →</a>',
      f'Nuovo gioco: <a href="{r}gioco/corri/">Corri, POP, corri! 🏃</a>',
      f"Macchine aggiornate il {E(STOCK['aggiornato'])}",
    ]
    track = "".join(f"<span>{x}</span>" for x in items)
    return f'''<div class="tg" role="region" aria-label="Ultime notizie da Pop Stop h24">
  <span class="tg-lab"><i></i>ULTIM'ORA</span>
  <div class="tg-run"><div class="tg-track">{track}{track}</div></div>
</div>'''

NAV = [("Ordina", "consegna-a-domicilio/"), ("Cosa c'è", "prodotti/"), ("Snack dal mondo", "snack-americani-napoli/"), ("Gioca 🎮", "gioco/"),
       ("Come arrivare", "#vieni"), ("Assistenza", "#assistenza")]

def layout(path, title, desc, body, ld, depth, active=""):
    r = rel(depth)
    home = r or "./"
    nav = []
    for n, p in NAV:
        href = (home + p) if p.startswith("#") else r + p
        cur = ' aria-current="page"' if p == active else ""
        nav.append(f'<a href="{href}"{cur}>{n}</a>')
    graph = {"@context": "https://schema.org", "@graph": ld}
    cfg = {"stock": r + "stock.json", "ordine": ORDINE, "icone": ICONE, "img": IMG, "dr": DR, "drurl": APP["deliveroo"][1]}
    socials = "".join(f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in S["social"].items())
    zone_links = "".join(f'<a href="{r}zona/{k}/">{v["nome"]}</a>' for k, v in ZONE.items())
    return f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{path}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="google-site-verification" content="{S["google_verifica"]}">
<meta name="theme-color" content="#061219">
<meta name="geo.region" content="IT-NA"><meta name="geo.placename" content="Casavatore"><meta name="geo.position" content="{S["geo"][0]};{S["geo"][1]}"><meta name="ICBM" content="{S["geo"][0]}, {S["geo"][1]}">
<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Pop Stop h24">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r}assets/icon-180.png">
<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="preload" href="{r}assets/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/style.css">
<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>
</head>
<body{' class="pg-gioco"' if path.startswith("gioco") else ""}>
<a class="sr" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
  <a class="logo" href="{home}" aria-label="Pop Stop h24, home"><b>24</b><span>Pop Stop <em>h24</em></span></a>
  <nav class="nav" aria-label="Menu principale">{"".join(nav)}</nav>
  <a class="pill" href="{home}#vieni"><i></i>Aperto · <span data-ora>24h</span></a>
  <button class="burger" type="button" aria-label="Apri il menu" aria-expanded="false">☰</button>
</div></header>
{"" if path.startswith("gioco") or path=="404.html" else tg_block(r)}
<main id="main">
{body}
</main>
<footer><div class="wrap cols">
  <div>
    <a class="logo" href="{home}"><b>24</b>Pop Stop <em>h24</em></a>
    <p style="margin-top:12px">Distributori automatici aperti 24 ore su 24, 7 giorni su 7.<br>{E(INDIRIZZO_FULL)}<br>
    <a href="{TEL}" style="display:inline">Tel. e WhatsApp {S["telefono_vis"]}</a></p>
    <div class="zones" style="margin-top:16px">{zone_links}</div>
  </div>
  <div><h3>Sito</h3><a href="{home}">Home</a><a href="{r}consegna-a-domicilio/">Consegna a domicilio</a><a href="{r}prodotti/">Cosa c'è nelle macchine</a><a href="{r}snack-americani-napoli/">Snack dal mondo</a><a href="{r}aperto-24-ore-napoli-nord/">Aperto di notte a Napoli nord</a><a href="{r}energy-drink-a-domicilio/">Energy drink a domicilio</a><a href="{r}gioco/">Il gioco di POP</a><a href="{r}gioco/corri/">Corri, POP, corri!</a><a href="{REVIEW}" rel="noopener" target="_blank">Lascia una recensione</a></div>
  <div><h3>Seguici</h3>{"".join(f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in S["social"].items())}</div>
  <div><h3>Trovaci anche su</h3>{"".join(f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in S.get("schede", {}).items())}</div>
</div>
<div class="wrap" style="margin-top:26px;font-size:.82rem">© {datetime.date.today().year} Enjoy Market S.r.l. · P.IVA {S.get("piva", "")} · Pop Stop h24 Casavatore · Le consegne a domicilio sono gestite dalle app partner quando il servizio è disponibile nella tua zona.</div>
</footer>
<nav class="dock" aria-label="Azioni rapide">
  <a class="d1" href="{r}consegna-a-domicilio/#app"><span>🛵</span>Ordina</a>
  <a class="d2" href="{MAPS_DIR}" rel="noopener" target="_blank"><span>📍</span>Portami</a>
  <a class="d3" href="{WA}" rel="noopener" target="_blank"><span>💬</span>WhatsApp</a>
</nav>
<div class="sheet" id="sheet" aria-hidden="true" role="dialog" aria-labelledby="sh-n"><div class="box">
  <button class="x" type="button" aria-label="Chiudi">✕</button>
  <div class="shtop"><span class="pimg big" id="sh-i"></span><div>
  <span class="eyebrow">Nelle macchine ora</span>
  <h3 id="sh-n">Prodotto</h3>
  <p id="sh-s">Disponibile</p></div></div>
  <p class="shm" id="sh-m"></p>
  <a class="btn y wide" id="sh-ord" href="{APP["deliveroo"][1]}" rel="noopener" target="_blank">🛵 Ordina questo prodotto a domicilio</a>
  <a class="btn t wide" href="{MAPS_DIR}" rel="noopener" target="_blank" style="margin-top:8px">📍 Vieni a prenderlo ora</a>
  <p style="margin:8px 0 10px">Oppure apri il negozio su un'altra app:</p>
  <div class="appsmini">{"".join(f'<a class="{k}" href="{u}" rel="noopener" target="_blank">{n}</a>' for k, (n, u) in APP.items())}</div>
  <p style="font-size:.85rem;margin:0">Il menu delle app può variare rispetto alle macchine.</p>
</div></div>
<script>window.POP={json.dumps(cfg, ensure_ascii=False)}</script>
<script src="{r}assets/app.js" defer></script>
</body>
</html>
'''

def clock_svg():
    ticks = []
    for i in range(60):
        big = i % 5 == 0
        y1 = 26 if big else 32
        ticks.append(f'<line class="tick{" big" if big else ""}" x1="200" y1="{y1}" x2="200" y2="44" transform="rotate({i*6} 200 200)"/>')
    return f'''<div class="clockbox" aria-hidden="true"><svg viewBox="0 0 400 400">
<circle cx="200" cy="200" r="190" fill="rgba(25,214,200,.05)"/><circle class="ring" cx="200" cy="200" r="186"/>
{"".join(ticks)}
<text class="c24" x="200" y="246" text-anchor="middle">24</text>
<line class="hand hh" x1="200" y1="200" x2="200" y2="112"/>
<line class="hand mh" x1="200" y1="200" x2="200" y2="70"/>
<line class="hand sh" x1="200" y1="222" x2="200" y2="58"/>
<circle cx="200" cy="200" r="11" fill="#ff4f8b"/></svg><div class="badge">Mai chiuso ✦</div></div>'''

def visit_block(r, titolo="Vieni da noi, a qualsiasi ora"):
    return f'''<section class="s" id="vieni"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Come arrivare</span><h2>{titolo}</h2></div>
  <p>Self-service con 4 distributori automatici, sempre accesi e sempre carichi. Anche di notte, la domenica e nei festivi.</p></div>
  <div class="visit">
    <div class="mapcard reveal" role="button" tabindex="0" data-src="{MAPS_EMBED}" aria-label="Mostra la mappa">
      <div class="mapgrid"></div><div class="in"><div class="pin">📍</div><b>Tocca per vedere la mappa</b><span style="color:var(--mut)">Pop Stop h24 · Casavatore</span></div>
    </div>
    <div class="reveal">
      <span class="eyebrow">Indirizzo</span>
      <p class="addr">{E(S["indirizzo"])}<br>{S["cap"]} {S["citta"]} (NA)</p>
      <p style="color:var(--mut)">Napoli nord, tra Casoria, Arzano e Secondigliano.</p>
      <div class="navs">
        <a href="{MAPS_DIR}" rel="noopener" target="_blank"><span>🗺️</span>Google Maps</a>
        <a href="{WAZE}" rel="noopener" target="_blank"><span>🚗</span>Waze</a>
        <a href="{APPLE}" rel="noopener" target="_blank"><span>🍎</span>Apple Mappe</a>
      </div>
      <div class="hours"><b>Aperto 24 ore su 24 · 7 giorni su 7</b><span>Lunedì–domenica 00:00–24:00, festivi compresi. Adesso sono le <strong data-ora>—</strong> e siamo aperti.</span></div>
    </div>
  </div>
</div></section>'''

def help_block():
    return f'''<section class="s alt" id="assistenza"><div class="wrap">
  <div class="duo">
    <div class="panel reveal"><span class="eyebrow">Assistenza</span><h2 style="font-size:2rem">La macchina non ha erogato?</h2>
      <p>Scrivici su WhatsApp dicendo quale macchina (per esempio «2ª da sinistra»), il prodotto e l'ora: ti rispondiamo il prima possibile e sistemiamo.</p>
      <a class="btn t wide" href="{WA_ASS}" rel="noopener" target="_blank">💬 Scrivici su WhatsApp</a>
      <a class="btn o wide" href="{TEL}">📞 Chiama {S["telefono_vis"]}</a></div>
    <div class="panel rev reveal"><span class="eyebrow">Ti siamo piaciuti?</span><div class="stars5">★★★★★</div>
      <h2 style="font-size:2rem">Lasciaci una recensione</h2>
      <p>Ci aiuta a farci trovare da chi cerca un posto aperto di notte. Bastano 10 secondi.</p>
      <a class="btn y wide" href="{REVIEW}" rel="noopener" target="_blank">⭐ Scrivi la recensione su Google</a></div>
  </div>
</div></section>'''

def cats_block(r):
    cnt = {}
    for p in PRODOTTI:
        cnt[p["c"]] = cnt.get(p["c"], 0) + 1
    out = []
    for c in ORDINE:
        if c in cnt:
            out.append(f'<a class="cat reveal" href="{r}prodotti/{CAT_SLUG[c]}/"><span class="e">{ICONE[c]}</span><b>{E(c)}</b><small>{cnt[c]} prodotti</small></a>')
    return '<div class="cats">' + "".join(out) + "</div>"

def trova(rx):
    return [p for p in PRODOTTI if re.search(rx, p["n"], re.I)]

def fimg(p):
    return f'<img class="fi" src="{IMG.format(p["i"])}" alt="" loading="lazy" onerror="this.remove()">' if p.get("i") else ""

def feat_block(r):
    np = trova(r"nutella peanut")
    dp = trova(r"dr pepper")
    tk = trova(r"takis")
    rb = trova(r"red bull")
    cards = []
    if np:
        cards.append(f'<button class="fcard f1 reveal" type="button" data-p="{E(np[0]["n"])}" data-s="{np[0]["s"]}" data-i="{np[0].get("i","")}" data-d="{E(dove_txt(np[0].get("m",[])))}">{fimg(np[0])}<span class="tag">Novità</span><h3>Nutella Peanut</h3><p>Nutella con arachidi: da noi la trovi a qualsiasi ora.</p></button>')
    if dp:
        cards.append(f'<a class="fcard f2 reveal" href="{r}snack-americani-napoli/">{fimg(dp[0])}<span class="tag">USA</span><h3>{len(dp)} gusti di Dr Pepper</h3><p>Cherry, Vanilla Float, Blackberry, Creamy Coconut e altri.</p></a>')
    if tk:
        cards.append(f'<a class="fcard f3 reveal" href="{r}prodotti/?q=takis">{fimg(tk[0])}<span class="tag">Piccante</span><h3>Takis Fuego e Blue Heat</h3><p>Le tortillas arrotolate più piccanti, sempre in macchina.</p></a>')
    if rb:
        cards.append(f'<a class="fcard f4 reveal" href="{r}prodotti/?cat=Energy%20drink">{fimg(rb[0])}<span class="tag">Energia</span><h3>{len(rb)} Red Bull diverse</h3><p>Più Monster e Powerade: la notte è lunga.</p></a>')
    return '<div class="feat">' + "".join(cards) + "</div>"

def zones_block(r):
    return '<div class="zones">' + "".join(f'<a href="{r}zona/{k}/">📍 {v["nome"]}</a>' for k, v in ZONE.items()) + f'<a href="{r}consegna-a-domicilio/">🛵 Tutte le zone di consegna</a></div>'

IMG = "https://rs-menus-api.roocdn.com/images/{}/image.jpeg?width=320&height=320&fit=contain&auto=webp&format=webp"

# Le macchine non hanno numeri: si indicano per posizione guardandole di fronte
POSIZIONE = {1: "1ª macchina da sinistra", 2: "2ª macchina da sinistra", 3: "2ª macchina da destra", 4: "1ª macchina da destra"}

def dove_txt(m):
    per = {}
    for mac, slot in m:
        per.setdefault(mac, []).append(str(slot))
    return " · ".join(f"{POSIZIONE.get(mac, f'Macchina {mac}')} · n. {', '.join(sl)}" for mac, sl in sorted(per.items()))

def card(p):
    img = (f'<img src="{IMG.format(p["i"])}" alt="{E(p["n"])}" loading="lazy" width="160" height="160" onerror="this.replaceWith(Object.assign(document.createElement(\'span\'),{{className:\'ph\',textContent:\'{ICONE.get(p["c"],"🛒")}\'}}))">'
           if p.get("i") else f'<span class="ph">{ICONE.get(p["c"], "🛒")}</span>')
    d = dove_txt(p.get("m", []))
    st = "Ultimi pezzi" if p["s"] == "ultimi" else "Disponibile"
    return (f'<li><button type="button" class="pc" data-p="{E(p["n"])}" data-s="{p["s"]}" data-i="{p.get("i","")}" data-d="{E(d)}">'
            f'<span class="pimg">{img}</span><span class="pn">{E(p["n"])}</span>'
            f'<span class="pm">📍 {E(d)}</span><span class="st{" u" if p["s"]=="ultimi" else ""}">{st}</span></button></li>')

def plist_static(prods):
    g = {}
    for p in prods:
        g.setdefault(p["c"], []).append(p)
    out = []
    for c in ORDINE:
        if c not in g:
            continue
        out.append(f'<div class="group"><h2>{ICONE[c]} {E(c)}</h2><ul class="plist">{"".join(card(p) for p in g[c])}</ul></div>')
    return "".join(out)

def _ver(nome):
    import hashlib
    try: return hashlib.md5(open(os.path.join(ROOT, "assets", nome), "rb").read()).hexdigest()[:8]
    except OSError: return "1"

def write(path, content):
    if path.endswith(".html"):
        content = re.sub(r'assets/(app\.js|style\.css|gioco\.js|corri\.js)"', lambda m: f'assets/{m.group(1)}?v={_ver(m.group(1))}"', content)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

# ---------------- HOME ----------------
FAQ_HOME = [
  ("Pop Stop h24 è aperto anche di notte?", "Sì. I distributori automatici di Viale Guglielmo Marconi 79/81 a Casavatore sono accesi 24 ore su 24, 7 giorni su 7, anche la domenica, a Natale, a Capodanno e in tutti i festivi."),
  ("Cosa si trova nei distributori?", f"Oltre {NPROD//10*10} prodotti: energy drink (Red Bull, Monster, Powerade), bibite e bibite americane come Dr Pepper e Fanta USA, acqua, caffè freddi Starbucks, patatine e Takis, tramezzini, cioccolato, Kinder, caramelle Haribo e prodotti di prima necessità. L'elenco aggiornato è nella pagina «Cosa c'è nelle macchine»."),
  ("Fate consegna a domicilio?", "Sì, tramite Glovo, Just Eat, Deliveroo e Alfonsino, quando l'app è disponibile nella tua zona. Consegniamo a Casavatore e dintorni: Casoria, Arzano, Secondigliano e Napoli nord. Apri l'app, inserisci il tuo indirizzo e cerca Pop Stop h24."),
  ("Dove trovo Dr Pepper, Takis e snack americani vicino Napoli?", "Da Pop Stop h24 a Casavatore, a qualsiasi ora: abbiamo diversi gusti di Dr Pepper, Fanta americane, Takis Fuego e Blue Heat, bibite asiatiche High Up e caffè Starbucks pronti."),
  ("La macchina non mi ha dato il prodotto: cosa faccio?", f"Scrivici su WhatsApp al {S['telefono_vis']} indicando la macchina, il prodotto e l'ora dell'acquisto: ti rispondiamo il prima possibile."),
  ("Dove si trova Pop Stop h24?", f"In {E(INDIRIZZO_FULL)}, nella zona nord di Napoli, vicino a Casoria, Arzano e Secondigliano. Puoi aprire il percorso con Google Maps, Waze o Apple Mappe da questo sito."),
]

TICKER = "".join(f"<span>{t}</span>" for t in ["Aperto 24/7 ✦", "Snack dal mondo ✦", "Energy drink ✦", "Tramezzini ✦", "Anche di notte ✦", "Ordina sulle app ✦", "Casavatore ✦"])

def home():
    r = ""
    body = f'''
<section class="hero"><div class="sky"></div><div class="stars"></div><div class="hfloat" aria-hidden="true"><span>🥤</span><span>⚡</span><span>🍫</span><span>🍟</span><span>🥪</span><span>🍬</span><span>💧</span></div><div class="wrap">
  <div>
    <span class="kicker">● Casavatore · Napoli nord</span>
    <h1>Distributori automatici aperti <span class="n">24 ore</span> a Casavatore</h1>
    <p class="lead"><strong>Snack, bibite, energy drink e beni di prima necessità</strong> a qualsiasi ora. Vieni in Viale Marconi o fattelo portare a casa con le app di consegna.</p>
    <p class="now">Sono le <span data-ora>—</span>. <span data-frase style="color:#fff">Siamo aperti.</span></p>
    <div class="ctas">
      <a class="btn y" href="consegna-a-domicilio/#app">🛵 Ordina a domicilio</a>
      <a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a>
      <a class="btn o" href="prodotti/">🍫 Cosa c'è ora</a>
    </div>
    <div class="facts"><span><b>24/7</b> anche nei festivi</span><span><b data-count>{NPROD}</b> prodotti in macchina</span><span><b>4</b> app di consegna</span></div>
  </div>
  <a class="popwrap corsa" href="gioco/corri/" aria-label="Gioca con POP: Corri, POP, corri!">
    <div class="bubble" data-pop-frasi>Corri, POP, corri! 🏃</div>
    <div class="scena" aria-hidden="true">
      <div class="fondo f-parco"><i class="collina c1"></i><i class="collina c2"></i><i class="albero">🌳</i></div>
      <div class="fondo f-deserto"><svg viewBox="0 0 400 200" preserveAspectRatio="xMidYMax slice"><circle cx="300" cy="70" r="34" fill="#ffcf5a"/><path d="M0 200 L0 150 L30 150 L38 90 L70 90 L78 150 L130 150 L136 110 L150 104 L162 110 L168 150 L240 150 L248 70 L290 70 L298 150 L400 150 L400 200 Z" fill="#b5482c"/><path d="M0 200 L0 168 L400 162 L400 200 Z" fill="#8a3320"/></svg></div>
      <div class="fondo f-mare"><i class="onda"></i><i class="barca">🚢</i><i class="pioggia"></i></div>
      <i class="nuvola n1"></i><i class="nuvola n2"></i>
      <i class="piuma">🪶</i>
      <i class="cosa k1"><svg viewBox="0 0 90 56"><rect x="4" y="18" width="82" height="9" rx="3" fill="#8a5a2b" stroke="#061219" stroke-width="2.5"/><rect x="4" y="30" width="82" height="7" rx="3" fill="#8a5a2b" stroke="#061219" stroke-width="2.5"/><rect x="10" y="37" width="6" height="18" fill="#3b2a1a"/><rect x="74" y="37" width="6" height="18" fill="#3b2a1a"/><rect x="50" y="6" width="26" height="13" rx="2" fill="#6b3a1f" stroke="#061219" stroke-width="2"/><rect x="50" y="6" width="26" height="4" fill="#e8133b"/></svg></i>
      <i class="cosa k2">🏓</i><i class="cosa k3">🦐</i><i class="cosa k4">🏈</i><i class="cosa k5">🍫</i>
      <i class="strada"></i>
      <span class="tappa"><b>Alabama</b><b>Coast to coast</b><b>A pesca di gamberi</b></span>
    </div>
    <div class="corridore">{pop_svg("pop hero run", cap=True)}<b class="dust d1"></b><b class="dust d2"></b><b class="dust d3"></b></div>
    <div class="contakm">🏃 POP corre da <b data-giorni>75</b> giorni senza fermarsi · <b data-km>14.400</b> km</div>
    <span class="sticker p playme">🎮 Toccami e gioca!</span>
  </a>
</div></section>

<section class="s" id="ordina"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Consegna a domicilio</span><h2>Fame? Te lo portiamo noi.</h2></div>
  <p>Scegli la tua app preferita, inserisci l'indirizzo e ordina dal negozio Pop Stop h24. Consegniamo a Casavatore, Casoria, Arzano e Napoli nord quando l'app è disponibile.</p></div>
  {app_cards()}
  <div style="margin-top:22px">{zones_block(r)}</div>
</div></section>

<section class="s alt" id="macchine"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Nelle macchine adesso</span><h2>Cosa c'è da Pop Stop</h2></div>
  <p>Le macchine si ricaricano di continuo. Tocca una categoria per vedere tutti i prodotti disponibili.</p></div>
  {cats_block(r)}
  {feat_block(r)}
  <div style="margin-top:24px"><a class="btn o" href="prodotti/">Vedi tutti i {NPROD} prodotti →</a></div>
</div></section>
{presi_block(r)}

<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Come funziona</span><h2>Facile come un pop.</h2></div></div>
  <div class="steps">
    <div class="step reveal"><h3>Entra quando vuoi</h3><p>Giorno, notte, domenica o Capodanno: il punto self-service di Viale Marconi è sempre aperto.</p></div>
    <div class="step reveal"><h3>Scegli dalla macchina</h3><p>4 distributori con bibite fresche, energy drink, snack dolci e salati, tramezzini e prodotti utili.</p></div>
    <div class="step reveal"><h3>Oppure ordina da casa</h3><p>Su Glovo, Just Eat, Deliveroo o Alfonsino, quando l'app consegna nella tua zona.</p></div>
  </div>
</div></section>

<section class="s"><div class="wrap">
  <div class="giochi2 reveal"><h2>🎮 I giochi di POP</h2>
  <a class="gamecta" href="gioco/">{pop_svg("pop saluta", "")}<div><span class="sticker">Gioco 1</span><h3 style="margin-top:10px">Riempi le macchine prima delle 6!</h3><p>Aiuta POP a caricare i distributori prima che arrivi la fila del mattino.</p></div><span class="btn">🧃 Gioca</span></a>
  <a class="gamecta" href="gioco/corri/">{pop_svg("pop saluta", "", cap=True)}<div><span class="sticker p">Nuovo</span><h3 style="margin-top:10px">Corri, POP, corri!</h3><p>POP non si ferma mai: salta, prendi i cioccolatini, evita granchi e buche.</p></div><span class="btn">🏃 Gioca</span></a>
</div>
</div></section>

{visit_block(r)}
{help_block()}

<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Domande frequenti</span><h2>Tutto su Pop Stop h24</h2></div></div>
  {faq_html(FAQ_HOME)}
</div></section>

<section class="s alt"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Social</span><h2>Seguici: reel nuovi ogni giorno</h2></div></div>
  <div class="socials">{"".join(f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in S["social"].items())}</div>
</div></section>'''
    ld = [store_ld(), {"@type": "WebSite", "@id": BASE + "#sito", "url": BASE, "name": "Pop Stop h24", "alternateName": ["PopStop H24", "Pop Stop h24 Casavatore", "popstoph24"], "inLanguage": "it-IT",
          "publisher": {"@id": BASE + "#negozio"}}, faq_ld(FAQ_HOME)]
    write("index.html", layout("", "Pop Stop h24 Casavatore | Distributori aperti 24 ore su 24",
        f"Distributori automatici aperti 24 ore a Casavatore (Napoli nord): {NPROD} prodotti tra snack, bibite, energy drink e tramezzini. Consegna con Glovo, Just Eat e Deliveroo.",
        body, ld, 0))

# ---------------- CONSEGNA ----------------
FAQ_DEL = [
  ("In quali zone consegnate?", "A Casavatore e nei comuni e quartieri vicini come Casoria, Arzano, Secondigliano, San Pietro a Patierno e Napoli nord. La copertura esatta la decide l'app: inserisci il tuo indirizzo per vedere se arriviamo."),
  ("Consegnate anche di notte?", "Il nostro menu delivery è sempre aperto. Gli orari di consegna dipendono dall'app e dai rider disponibili nella tua zona: se l'app ti mostra Pop Stop h24 aperto, puoi ordinare."),
  ("Su quali app trovo Pop Stop h24?", "Glovo, Just Eat, Deliveroo e Alfonsino. Da questa pagina apri direttamente il nostro negozio su ognuna."),
  ("C'è un ordine minimo?", "L'ordine minimo e il costo di consegna li vedi nell'app che usi: possono cambiare da un'app all'altra e in base alle promozioni attive."),
  ("Cosa posso ordinare?", "Gli stessi prodotti delle macchine: energy drink, bibite, acqua, snack dolci e salati, tramezzini, caramelle e prodotti di prima necessità."),
]

def consegna():
    d = 1; r = rel(d)
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › Consegna a domicilio</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">🛵 Delivery · Casavatore e Napoli nord</span>
  <h1>Consegna a domicilio di snack e bibite, a qualsiasi ora</h1>
  <p class="lead">Red Bull, Monster, acqua, Coca-Cola, Takis, Kinder, tramezzini e tutto quello che c'è nelle nostre macchine, direttamente a casa tua. Scegli l'app:</p>
</div></section>
<section class="s" id="app" style="padding-top:10px"><div class="wrap">
  {app_cards()}
  <p class="note">Le consegne sono fatte dai rider delle app quando il servizio è disponibile nel tuo indirizzo. Prezzi, ordine minimo e costi di consegna sono quelli mostrati nell'app.</p>
</div></section>
<section class="s alt"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">In 3 passi</span><h2>Ordinare è un attimo</h2></div></div>
  <div class="steps">
    <div class="step reveal"><h3>Apri la tua app</h3><p>Tocca Glovo, Just Eat, Deliveroo o Alfonsino qui sopra: si apre direttamente il negozio Pop Stop h24.</p></div>
    <div class="step reveal"><h3>Metti l'indirizzo</h3><p>Se il tuo indirizzo è in zona, vedi il menu completo con le foto di ogni prodotto.</p></div>
    <div class="step reveal"><h3>Ordina e rilassati</h3><p>Prepariamo l'ordine e il rider te lo porta. Anche quando tutto il resto è chiuso.</p></div>
  </div>
</div></section>
<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Zone</span><h2>Dove arriviamo</h2></div><p>Siamo a Casavatore, nel cuore di Napoli nord. Guarda la pagina della tua zona:</p></div>
  {zones_block(r)}
</div></section>
<section class="s alt"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Domande</span><h2>Consegna: le risposte</h2></div></div>
  {faq_html(FAQ_DEL)}
</div></section>
{help_block()}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Consegna a domicilio", "consegna-a-domicilio/")]), faq_ld(FAQ_DEL),
          {"@type": "Service", "name": "Consegna a domicilio Pop Stop h24", "serviceType": "Consegna a domicilio di snack e bevande",
           "provider": {"@id": BASE + "#negozio"}, "areaServed": ["Casavatore", "Casoria", "Arzano", "Secondigliano", "Napoli"]}]
    write("consegna-a-domicilio/index.html", layout("consegna-a-domicilio/",
        "Snack e bibite a domicilio a Casavatore e Casoria | Pop Stop h24",
        "Snack, bibite, energy drink, acqua e tramezzini a domicilio da Pop Stop h24 con Glovo, Just Eat, Deliveroo e Alfonsino: Casavatore, Casoria, Arzano e Napoli nord.",
        body, ld, d, "consegna-a-domicilio/"))

# ---------------- PRODOTTI ----------------
def prodotti():
    d = 1; r = rel(d)
    chips = "".join(f'<a class="chip" href="?cat={quote(c)}">{ICONE[c]} {E(c)}</a>' for c in ORDINE if any(p["c"] == c for p in PRODOTTI))
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › Cosa c'è nelle macchine</div>
<section class="page-hero" style="padding-bottom:0"><div class="wrap">
  <span class="kicker">🍫 Disponibilità dal vivo</span>
  <h1>Cosa c'è nelle macchine</h1>
  <p class="lead">Tutti i prodotti nei distributori di Pop Stop h24 a Casavatore. Tocca un prodotto per venire a prenderlo o ordinarlo a casa.</p>
</div></section>
<section class="s" style="padding-top:0"><div class="wrap">
  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="Cerca: Red Bull, Takis, acqua, Kinder…" aria-label="Cerca un prodotto" autocomplete="off">
    <div class="chips" id="chips">{chips}</div>
  </div>
  <p class="upd" id="agg">{NPROD} prodotti nelle macchine · aggiornato il {E(STOCK["aggiornato"])}</p>
  <div id="prodotti">{plist_static(PRODOTTI)}</div>
  <p class="note">«Ultimi pezzi» vuol dire che potrebbero finire presto. Non trovi quello che cerchi? <a href="{WA}" rel="noopener" target="_blank">Chiedicelo su WhatsApp</a>.</p>
  <div class="head" style="margin-top:40px"><div><span class="eyebrow">Per categoria</span><h2>Sfoglia per categoria</h2></div></div>
  <div class="zones">{"".join(f'<a href="{CAT_SLUG[c]}/">{ICONE[c]} {E(c)}</a>' for c in ORDINE if any(p["c"] == c for p in PRODOTTI))}</div>
</div></section>
{visit_block(r, "Passa a prenderlo")}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Cosa c'è nelle macchine", "prodotti/")]),
          {"@type": "ItemList", "name": "Prodotti nei distributori Pop Stop h24", "numberOfItems": NPROD,
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(PRODOTTI)]}]
    write("prodotti/index.html", layout("prodotti/",
        f"Cosa c'è nei distributori h24 di Casavatore: {NPROD} prodotti | Pop Stop",
        "Energy drink, bibite, acqua, Starbucks, patatine, Takis, tramezzini, Kinder e Nutella Peanut: cosa c'è ora nelle macchine di Pop Stop h24 a Casavatore, con foto e posizione.",
        body, ld, d, "prodotti/"))

# ---------------- SNACK DAL MONDO ----------------
def mondo():
    d = 1; r = rel(d)
    prods = [p for p in PRODOTTI if MONDO.search(p["n"])]
    np = trova(r"nutella peanut")
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › Snack dal mondo</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">🌎 USA · Messico · Asia</span>
  <h1>Snack e bibite americane a Napoli, aperti 24 ore</h1>
  <p class="lead">Cerchi Dr Pepper, Takis, Fanta americane o bibite asiatiche vicino Napoli? Da Pop Stop h24 a Casavatore ne trovi {len(prods)}, a qualsiasi ora del giorno e della notte.</p>
  <div class="ctas"><a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami lì</a><a class="btn y" href="{r}consegna-a-domicilio/#app">🛵 Fatteli portare a casa</a></div>
</div></section>
<section class="s" style="padding-top:10px"><div class="wrap">
  {plist_static(prods)}
  {"<div class='feat' style='margin-top:30px'><button class='fcard f1' type='button' data-p='"+E(np[0]['n'])+"' data-s='"+np[0]['s']+"' data-i='"+np[0].get('i','')+"' data-d='"+E(dove_txt(np[0].get('m',[])))+"'>"+fimg(np[0])+"<span class='tag'>Novità</span><h3>E c'è anche la Nutella Peanut</h3><p>La Nutella con le arachidi: da noi la trovi sempre, anche di notte.</p></button></div>" if np else ""}
  <div class="prose" style="margin-top:34px">
    <h2>Perché da Pop Stop</h2>
    <p>Gli snack dal mondo di solito si trovano solo in pochi negozi specializzati, con orari da negozio. Nei nostri distributori di Viale Guglielmo Marconi 79/81 li trovi 24 ore su 24, 7 giorni su 7: Dr Pepper in tanti gusti (anche le versioni americane da 355 ml), Fanta USA come Grape, Strawberry, Peach e Pineapple, Takis Fuego e Blue Heat, le bibite High Up e i caffè Starbucks pronti da bere.</p>
    <p>Gli assortimenti cambiano con i carichi: l'elenco qui sopra si aggiorna con quello che c'è davvero nelle macchine.</p>
  </div>
</div></section>
{help_block()}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Snack dal mondo", "snack-americani-napoli/")]),
          {"@type": "ItemList", "name": "Snack e bibite dal mondo da Pop Stop h24", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(prods)]}]
    write("snack-americani-napoli/index.html", layout("snack-americani-napoli/",
        "Snack americani a Napoli h24: Dr Pepper, Takis, Fanta USA | Pop Stop",
        f"Dr Pepper, Takis, Fanta americane, bibite asiatiche e Starbucks vicino Napoli a qualsiasi ora: {len(prods)} prodotti dal mondo nei distributori h24 di Pop Stop a Casavatore.",
        body, ld, d, "snack-americani-napoli/"))

# ---------------- PAGINE A TEMA ----------------
TEMI = {
  "aperto-24-ore-napoli-nord": {
    "titolo": "Aperto di notte a Napoli nord, 24 ore su 24 | Pop Stop h24",
    "desc": "Un posto aperto di notte a Napoli nord, Casoria o Casavatore: Pop Stop h24, distributori automatici 24 ore su 24 con bibite, acqua, energy drink, snack e tramezzini.",
    "kicker": "🌙 Aperto anche di notte", "h1": "Aperto 24 ore a Napoli nord: anche alle 3 di notte",
    "lead": "Bar chiusi, supermercati chiusi, distributori di benzina con lo shop spento? A Casavatore c'è Pop Stop h24: 4 distributori automatici sempre accesi, 365 giorni l'anno, festivi e Capodanno compresi.",
    "rx": r"acqua|red bull|monster|coca|tramezzino|pan soffice|control|lycia|tampax|gillette",
    "lista": "Le cose più utili di notte",
    "testo": ["Di notte servono soprattutto acqua, una bibita fredda, un energy drink per il turno o il viaggio, qualcosa da mangiare come un tramezzino o uno snack, e a volte prodotti di prima necessità: da noi ci sono tutti, nelle macchine di Viale Guglielmo Marconi 79/81.",
              "Siamo comodi per chi arriva da Casoria, Arzano, Secondigliano, Capodichino, Afragola e da tutta la zona nord di Napoli. Si paga direttamente alla macchina.",
              "Se non vuoi uscire, ordina su Glovo, Just Eat, Deliveroo o Alfonsino: le consegne dipendono dagli orari e dalla zona coperta dall'app."]},
  "energy-drink-a-domicilio": {
    "titolo": "Energy drink a domicilio a Casavatore, anche di notte | Pop Stop",
    "desc": "Red Bull, Monster e Powerade a domicilio con Glovo, Just Eat e Deliveroo, o nei distributori aperti 24 ore di Pop Stop h24 a Casavatore. Anche le edizioni speciali.",
    "kicker": "⚡ Energy drink", "h1": "Energy drink a domicilio o h24 a Casavatore",
    "lead": "Red Bull in tante edizioni, Monster, Powerade e bevande per lo sport: nei nostri distributori ci sono sempre, e con le app di consegna te li portano a casa quando il servizio è attivo nella tua zona.",
    "rx": r"red bull|monster|powerade",
    "lista": "Gli energy drink nelle macchine adesso",
    "testo": ["Le edizioni colorate di Red Bull cambiano spesso: qui sopra vedi quelle che ci sono davvero adesso nelle macchine, con la posizione esatta.",
              "Per lo studio, il lavoro di notte, la palestra o un viaggio lungo: passa da Viale Guglielmo Marconi 79/81 a Casavatore a qualsiasi ora, oppure ordina dall'app."]},
}

def tema(slug, t):
    d = 1; r = rel(d)
    prods = [p for p in PRODOTTI if re.search(t["rx"], p["n"], re.I)]
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › {E(t["h1"])}</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">{t["kicker"]}</span>
  <h1>{E(t["h1"])}</h1>
  <p class="lead">{E(t["lead"])}</p>
  <div class="ctas"><a class="btn y" href="{r}consegna-a-domicilio/#app">🛵 Ordina a domicilio</a><a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a></div>
</div></section>
<section class="s" style="padding-top:10px"><div class="wrap">
  <div class="head"><div><span class="eyebrow">Nelle macchine adesso</span><h2>{E(t["lista"])}</h2></div></div>
  {plist_static(prods)}
  <div class="prose" style="margin-top:34px">{"".join("<p>"+E(x)+"</p>" for x in t["testo"])}</div>
</div></section>
<section class="s alt" id="app"><div class="wrap">
  <div class="head"><div><span class="eyebrow">Consegna a domicilio</span><h2>Scegli la tua app</h2></div><p>Quando l'app consegna al tuo indirizzo.</p></div>
  {app_cards()}
  <div style="margin-top:22px">{zones_block(r)}</div>
</div></section>
{visit_block(r)}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), (t["h1"], slug + "/")]),
          {"@type": "ItemList", "name": t["lista"], "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(prods)]}]
    write(f"{slug}/index.html", layout(f"{slug}/", t["titolo"], t["desc"], body, ld, d))

def presi_block(r):
    nomi = S.get("piu_presi", [])
    trov = []
    for n in nomi:
        for p in PRODOTTI:
            if p["n"].lower() == n.lower():
                trov.append(p); break
    if not trov: return ""
    return f'''<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">I più presi</span><h2>I preferiti di Casavatore 🔥</h2></div>
  <p>I prodotti più venduti nelle nostre macchine nell'ultimo mese. Toccane uno: vedi dov'è e ordinalo sulle app.</p></div>
  <ul class="plist">{"".join(card(p) for p in trov[:12])}</ul>
</div></section>'''

# ---------------- CATEGORIE ----------------
CAT_SLUG = {"Energy drink": "energy-drink", "Bibite": "bibite", "Acqua": "acqua", "Caffè e latte": "caffe-e-latte",
            "Patatine e snack salati": "patatine-e-snack-salati", "Tramezzini e salato": "tramezzini",
            "Dolci e cioccolato": "dolci-e-cioccolato", "Caramelle e gomme": "caramelle-e-gomme", "Igiene e altro": "igiene-e-prima-necessita"}
CAT_TXT = {
  "Energy drink": ("Energy drink h24 a Casavatore", "Red Bull in tante edizioni, Monster e Powerade sempre freschi nei distributori: per il turno di notte, lo studio, la palestra o il viaggio."),
  "Bibite": ("Bibite fresche h24 a Casavatore", "Coca-Cola, Fanta, Sprite, Pepsi, Estathé, Schweppes, Dr Pepper e bibite americane e asiatiche, fredde a qualsiasi ora."),
  "Acqua": ("Acqua fresca 24 ore su 24 a Casavatore", "Acqua naturale e frizzante sempre disponibile, giorno e notte, anche nei festivi: dalla bottiglietta classica alla Fiji."),
  "Caffè e latte": ("Caffè freddo, latte e bevande al latte h24", "Starbucks pronti da bere, latte, latte e cioccolato e shake: per la colazione presto o la pausa di notte."),
  "Patatine e snack salati": ("Patatine e snack salati h24 a Casavatore", "Pringles, San Carlo, Takis piccanti e tanti snack salati, nelle macchine a qualsiasi ora."),
  "Tramezzini e salato": ("Tramezzini e snack salati h24 a Casavatore", "Tramezzini pronti, salamini, Un Due Tris e snack salati per quando hai fame davvero, anche alle 3 di notte."),
  "Dolci e cioccolato": ("Dolci, cioccolato e merendine h24 a Casavatore", "Kinder, Nutella, KitKat, Twix, Oreo, Ringo e tante merendine: la voglia di dolce non ha orari, e noi nemmeno."),
  "Caramelle e gomme": ("Caramelle e chewing gum h24 a Casavatore", "Haribo, Skittles, Tic Tac, Vigorsol, Big Babol e caramelle dal mondo, sempre nei distributori."),
  "Igiene e altro": ("Prodotti di prima necessità h24 a Casavatore", "Assorbenti, rasoi, preservativi e prodotti utili quando le farmacie e i negozi sono chiusi, 24 ore su 24."),
}

def categoria(c):
    slug = CAT_SLUG[c]; d = 2; r = rel(d)
    prods = [p for p in PRODOTTI if p["c"] == c]
    h1, intro = CAT_TXT[c]
    altre = "".join(f'<a href="{r}prodotti/{CAT_SLUG[x]}/">{ICONE[x]} {E(x)}</a>' for x in ORDINE if x != c)
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › <a href="{r}prodotti/">Cosa c'è</a> › {E(c)}</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">{ICONE[c]} {E(c)} · {len(prods)} prodotti</span>
  <h1>{E(h1)}</h1>
  <p class="lead">{E(intro)} Li trovi nelle macchine di Viale Guglielmo Marconi 79/81, oppure a casa tua con le app di consegna quando sono disponibili nella tua zona.</p>
  <div class="ctas"><a class="btn y" href="{r}consegna-a-domicilio/#app">🛵 Ordina a domicilio</a><a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a></div>
</div></section>
<section class="s" style="padding-top:10px"><div class="wrap">
  <p class="upd">Aggiornato il {E(STOCK["aggiornato"])} con quello che c'è davvero nelle macchine. Tocca un prodotto per vedere in quale macchina si trova.</p>
  <ul class="plist">{"".join(card(p) for p in prods)}</ul>
  <div class="head" style="margin-top:40px"><div><span class="eyebrow">Altre categorie</span><h2>Cos'altro c'è</h2></div></div>
  <div class="zones">{altre}</div>
</div></section>
{visit_block(r)}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Cosa c'è nelle macchine", "prodotti/"), (c, f"prodotti/{slug}/")]),
          {"@type": "ItemList", "name": f"{c} da Pop Stop h24", "numberOfItems": len(prods),
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(prods)]}]
    tit = f"{h1} | Pop Stop"
    desc = f"{intro} {len(prods)} prodotti nei distributori di Pop Stop h24, Casavatore."
    write(f"prodotti/{slug}/index.html", layout(f"prodotti/{slug}/", tit, desc if len(desc) <= 158 else desc[:155].rsplit(" ", 1)[0].rstrip(",:;") + "…", body, ld, d))

# ---------------- ZONE ----------------
def zona(slug, z):
    d = 2; r = rel(d); n = z["nome"]
    faq = [
      (f"C'è un posto aperto 24 ore vicino a {n}?", f"Sì: Pop Stop h24, in {E(INDIRIZZO_FULL)}. {z['frase']}: distributori automatici aperti giorno e notte, 7 giorni su 7."),
      (f"Pop Stop h24 consegna a {n}?", f"Consegniamo con Glovo, Just Eat, Deliveroo e Alfonsino quando l'app è disponibile al tuo indirizzo di {n}. Inserisci l'indirizzo nell'app per vedere se arriviamo."),
      (f"Cosa posso comprare di notte a {n}?", "Energy drink, bibite, acqua, patatine, Takis, tramezzini, dolci, caramelle e prodotti utili come igiene personale: tutto quello che c'è nelle nostre macchine."),
    ]
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › <a href="{r}consegna-a-domicilio/">Consegna</a> › {E(n)}</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">📍 {E(n)} · Napoli nord</span>
  <h1>Aperto 24 ore vicino a {E(n)}: snack e bibite a domicilio o in sede</h1>
  <p class="lead">{E(z["vicino"])} {E(z["extra"])}</p>
  <div class="ctas"><a class="btn y" href="#app">🛵 Ordina a {E(n)}</a><a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a></div>
</div></section>
<section class="s" id="app" style="padding-top:10px"><div class="wrap">
  <div class="head"><div><span class="eyebrow">Consegna a {E(n)}</span><h2>Scegli la tua app</h2></div><p>Disponibile quando l'app consegna al tuo indirizzo.</p></div>
  {app_cards()}
</div></section>
<section class="s alt"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Sempre in macchina</span><h2>Cosa trovi</h2></div></div>
  {cats_block(r)}
</div></section>
{visit_block(r, "Da " + E(n) + " a Pop Stop in pochi minuti")}
<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Domande</span><h2>{E(n)}: le risposte</h2></div></div>
  {faq_html(faq)}
  <div style="margin-top:26px">{zones_block(r)}</div>
</div></section>'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Consegna a domicilio", "consegna-a-domicilio/"), (n, f"zona/{slug}/")]), faq_ld(faq)]
    write(f"zona/{slug}/index.html", layout(f"zona/{slug}/",
        f"Aperto 24 ore vicino a {n} | Pop Stop h24",
        f"Aperto di notte vicino a {n}: Pop Stop h24 a Casavatore, distributori automatici 24 ore su 24 e consegna con Glovo, Just Eat e Deliveroo.",
        body, ld, d))

# ---------------- 404 ----------------
def page404():
    # 404 servita da qualsiasi percorso: link assoluti
    body = f'''<section class="page-hero"><div class="wrap" style="text-align:center;padding:60px 20px">
<div style="font-size:5rem">🫧</div><h1>Questa pagina ha fatto «pop»</h1>
<p class="lead" style="margin:0 auto 26px">Non esiste più, ma noi siamo sempre aperti.</p>
<div class="ctas" style="justify-content:center"><a class="btn y" href="{BASE}">Torna alla home</a><a class="btn t" href="{BASE}consegna-a-domicilio/">Ordina a domicilio</a></div>
</div></section>'''
    html_ = layout("404.html", "Pagina non trovata | Pop Stop h24", "Pagina non trovata.", body, [store_ld()], 0)
    html_ = html_.replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
    html_ = re.sub(r'<link rel="canonical"[^>]*>\n', '', html_)
    # percorsi assoluti per css/js/icone
    html_ = re.sub(r'(href|src)="(?!https?:|tel:|#|mailto:)([^"]*)"', lambda m: f'{m.group(1)}="{BASE}{m.group(2).lstrip("./")}"' , html_)
    html_ = html_.replace('"stock": "stock.json"', f'"stock": "{BASE}stock.json"')
    write("404.html", html_)

# ---------------- file tecnici ----------------
def gioco():
    r = rel(1)
    body = f'''
<div class="gioco" id="gioco">
  <nav class="gtabs" aria-label="I giochi di POP"><a href="{r}gioco/" aria-current="page">🧃 Riempi le macchine</a><a href="{r}gioco/corri/">🏃 Corri, POP, corri!</a></nav>
  <section class="gscreen" id="g-start">
    <div class="gfloat" aria-hidden="true"><span>🥤</span><span>⚡</span><span>🍫</span><span>🍟</span><span>🥪</span><span>💧</span><span>🍬</span><span>☕</span></div>
    <img class="pop" src="{r}assets/pop.svg" alt="POP, la mascotte di Pop Stop h24" width="220" height="286">
    <span class="sticker p">Gioco di POP</span>
    <h1>Riempi le macchine prima delle 6!</h1>
    <p>Sono le 5 del mattino: alle 6 arriva la fila di chi va a lavoro. Aiuta POP a riempire tutti gli scomparti vuoti dei 4 distributori prima che suoni l'ora. Occhio: anche di notte c'è chi ha fame e svuota gli scomparti!</p>
    <div class="how">
      <div>1️⃣ Tocca un prodotto nel <b>carrello</b> a destra.</div>
      <div>2️⃣ Tocca uno <b>scomparto vuoto</b> dello stesso prodotto: si illumina di giallo.</div>
      <div>3️⃣ Riempi tutto prima delle 6: più sei veloce, più punti fai. Se sbagli perdi tempo!</div>
    </div>
    <button class="btn y" type="button" data-via>▶ Gioca</button>
    <p id="g-best" style="margin-top:14px;font-weight:700;color:var(--y)"></p>
  </section>

  <section id="g-play" hidden>
    <div class="gsky" id="g-sky" aria-hidden="true"><i class="sun"></i><i class="moon"></i><b class="st"></b></div>
    <div class="ghud">
      <div class="box clock"><small>Ora</small><span id="g-ora">05:00</span></div>
      <div class="box"><small>Livello</small><span id="g-liv">1</span></div>
      <div class="box"><small>Punti</small><span id="g-punti">0</span></div>
      <button id="g-audio" type="button" aria-label="Togli i suoni">🔊</button>
      <div class="gbar" id="g-bar"><i></i></div>
      <div class="gcombo" id="g-combo" aria-live="polite"></div>
    </div>
    <div class="gstage">
      <div class="ggrid" id="g-grid"></div>
      <div class="gtray"><h3>Carrello</h3><div id="g-tray" style="display:flex;flex-direction:column;gap:8px"></div></div>
    </div>
  </section>

  <section class="gscreen gend" id="g-end" hidden>
    <img class="pop" src="{r}assets/pop.svg" alt="" width="220" height="286">
    <h2 id="g-tit" style="font-size:clamp(1.8rem,7vw,2.8rem)">Sono le 6!</h2>
    <p class="score" id="g-fin"></p>
    <p id="g-record" style="font-weight:800;color:var(--y)"></p>
    <div class="row">
      <button class="btn y" type="button" data-via>🔁 Rigioca</button>
      <a class="btn wa" id="g-share" href="#" rel="noopener" target="_blank">💬 Sfida un amico</a>
    </div>
    <p style="margin-top:26px">Ti è venuta fame? Le macchine vere sono piene e aperte 24 ore su 24.</p>
    <div class="row">
      <a class="btn t" href="{r}consegna-a-domicilio/#app">🛵 Ordina a domicilio</a>
      <a class="btn o" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a>
    </div>
  </section>
  <img class="gpop" id="g-pop" src="{r}assets/pop.svg" alt="" width="74" height="96">
  <div class="fum" id="g-fumetto" aria-live="polite"></div>
</div>
<script src="{r}assets/gioco.js" defer></script>'''
    ld = [crumbs_ld([("Home", ""), ("Gioco", "gioco/")]),
          {"@type": "VideoGame", "name": "Riempi le macchine – il gioco di POP", "url": BASE + "gioco/", "inLanguage": "it-IT",
           "genre": "Arcade", "gamePlatform": "Web browser", "applicationCategory": "Game", "operatingSystem": "Any",
           "description": "Mini gioco gratuito di Pop Stop h24: aiuta la mascotte POP a riempire i distributori automatici prima delle 6 del mattino.",
           "publisher": {"@id": BASE + "#negozio"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    write("gioco/index.html", layout("gioco/", "Gioco: Riempi le macchine prima delle 6! | Pop Stop",
        "Il mini gioco gratuito di Pop Stop h24: aiuta POP a riempire i distributori automatici prima che arrivi la fila del mattino. Gioca dal telefono e sfida gli amici.",
        body, ld, 1, active="gioco/"))

def corri():
    r = rel(2)
    base = pop_svg("pop", "", cap=True).replace('<svg class="pop" viewBox="0 0 200 260"', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -34 216 300" width="216" height="300"')
    for i, (a, b) in enumerate([(-28, 22), (22, -28), (0, 0)]):
        f = base.replace('<g class="p-legL">', f'<g class="p-legL" transform="rotate({a} 65 226)">').replace('<g class="p-legR">', f'<g class="p-legR" transform="rotate({b} 135 226)">')
        f = f.replace('<g class="p-armL">', f'<g class="p-armL" transform="rotate({b} 30 127)">').replace('<g class="p-armR">', f'<g class="p-armR" transform="rotate({a} 170 127)">')
        write(f"assets/pop-corsa-{i}.svg", f)
    body = f'''
<div class="corri" id="corri">
  <nav class="gtabs" aria-label="I giochi di POP"><a href="{r}gioco/">🧃 Riempi le macchine</a><a href="{r}gioco/corri/" aria-current="page">🏃 Corri, POP, corri!</a></nav>
  <section class="cover fuori" id="c-start">
      <span class="sticker p">Nuovo gioco di POP</span>
      <h1>Corri, POP, corri!</h1>
      <p>POP ha messo le scarpe da corsa e non si ferma più: dall'Alabama al deserto fino al mare in tempesta. Salta, raccogli i cioccolatini e non cadere!</p>
      <div class="how">
        <div>👆 <b>Tocca</b> (o barra spaziatrice) per saltare: tieni premuto per saltare più in alto, tocca di nuovo in aria per il <b>doppio salto</b>.</div>
        <div>🍫 Prendi i cioccolatini e colpisci da sotto le <b>scatole</b>: dentro ce ne sono altri.</div>
        <div>🦀 Salta <b>sopra</b> ai granchi per farli fuori. Evita panchine, palloni e buche: hai 3 cuori.</div>
      </div>
      <button class="btn y" type="button" data-via>▶ Corri!</button>
      <p class="crec" id="c-best"></p>
    </section>
  <div class="cwrap">
    <canvas id="c-can" aria-label="Gioco Corri POP: POP corre senza fermarsi, tocca lo schermo per saltare"></canvas>
    <div class="chud" aria-live="off"><span id="c-cuori">❤️❤️❤️</span><span>🍫 <b id="c-ciocc">0</b></span><span>🏃 <b id="c-metri">0</b> m</span><button id="c-audio" type="button" aria-label="Togli i suoni">🔊</button></div>
    <button class="csalta" id="c-salta" type="button" aria-label="Salta">⬆<small>SALTA</small></button>
    <div class="cbanner" id="c-banner"></div>

    <section class="cover" id="c-end" hidden>
      <h2 id="c-tit">Ti sei fermato!</h2>
      <p class="score" id="c-fin"></p>
      <p class="crec" id="c-record"></p>
      <div class="row"><button class="btn y" type="button" data-via>🔁 Ricorri</button><a class="btn wa" id="c-share" href="#" rel="noopener" target="_blank">💬 Sfida un amico</a></div>
    </section>
  </div>
  <div class="cdopo">
    <p>Tutta questa corsa mette fame. Le macchine vere sono piene e aperte 24 ore su 24.</p>
    <div class="row"><a class="btn t" href="{r}consegna-a-domicilio/#app">🛵 Ordina a domicilio</a><a class="btn o" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a><a class="btn" href="{r}gioco/">🎮 Riempi le macchine</a></div>
  </div>
</div>
<script src="{r}assets/corri.js" defer></script>'''
    ld = [crumbs_ld([("Home", ""), ("Gioco", "gioco/"), ("Corri POP", "gioco/corri/")]),
          {"@type": "VideoGame", "name": "Corri POP – il gioco di Pop Stop h24", "url": BASE + "gioco/corri/", "inLanguage": "it-IT",
           "genre": ["Platform", "Endless runner"], "gamePlatform": "Web browser", "applicationCategory": "Game", "operatingSystem": "Any",
           "description": "Mini gioco gratuito a piattaforme di Pop Stop h24: la mascotte POP corre senza fermarsi, salta, raccoglie cioccolatini ed evita gli ostacoli.",
           "publisher": {"@id": BASE + "#negozio"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    write("gioco/corri/index.html", layout("gioco/corri/", "Gioco: Corri, POP, corri! | Pop Stop h24",
        "Il gioco a piattaforme gratuito di Pop Stop h24: POP corre senza mai fermarsi, salta, prende i cioccolatini e sfida gli amici. Si gioca dal telefono.",
        body, ld, 2, active="gioco/"))

def tecnici():
    pages = ["", "consegna-a-domicilio/", "prodotti/", "snack-americani-napoli/", "gioco/", "gioco/corri/"] + [f"{k}/" for k in TEMI] + [f"prodotti/{CAT_SLUG[c]}/" for c in ORDINE if any(p["c"] == c for p in PRODOTTI)] + [f"zona/{k}/" for k in ZONE]
    urls = "".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{OGGI}</lastmod></url>\n" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /scripts/\nSitemap: {BASE}sitemap.xml\n")
    write("manifest.webmanifest", json.dumps({"name": "Pop Stop h24 Casavatore", "short_name": "Pop Stop", "start_url": "./", "display": "standalone",
        "background_color": "#061219", "theme_color": "#061219", "lang": "it",
        "icons": [{"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False, indent=1))
    cats = ", ".join(f"{c} ({sum(1 for p in PRODOTTI if p['c']==c)})" for c in ORDINE)
    write("llms.txt", f"""# Pop Stop h24 – Casavatore (Napoli)

> Punto vendita self-service con distributori automatici aperto 24 ore su 24, 7 giorni su 7, festivi compresi, in {INDIRIZZO_FULL}. Consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino quando l'app è disponibile.

- Telefono e WhatsApp: {S['telefono_vis']}
- Zone vicine e di consegna: Casavatore, Casoria, Arzano, Secondigliano, San Pietro a Patierno, Napoli nord
- Prodotti ({NPROD}): {cats}
- Specialità: bibite e snack dal mondo (Dr Pepper, Fanta USA, Takis, High Up, Starbucks), Nutella Peanut
- Sito: {BASE} · Prodotti: {BASE}prodotti/ · Consegna: {BASE}consegna-a-domicilio/
""")

home(); consegna(); prodotti(); mondo(); gioco(); corri()
for k, v in TEMI.items():
    tema(k, v)
for c in ORDINE:
    if any(p["c"] == c for p in PRODOTTI):
        categoria(c)
for k, v in ZONE.items():
    zona(k, v)
page404(); tecnici()
print("ok:", NPROD, "prodotti, base", BASE)
