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
      "areaServed": [{"@type": "City", "name": n} for n in ["Casavatore", "Casoria", "Arzano", "Napoli"]],
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

NAV = [("Ordina", "consegna-a-domicilio/"), ("Cosa c'è", "prodotti/"), ("Snack dal mondo", "snack-americani-napoli/"),
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
    cfg = {"stock": r + "stock.json", "ordine": ORDINE, "icone": ICONE, "img": IMG}
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
<body>
<a class="sr" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
  <a class="logo" href="{home}" aria-label="Pop Stop h24, home"><b>24</b><span>Pop Stop <em>h24</em></span></a>
  <nav class="nav" aria-label="Menu principale">{"".join(nav)}</nav>
  <a class="pill" href="{home}#vieni"><i></i>Aperto · <span data-ora>24h</span></a>
  <button class="burger" type="button" aria-label="Apri il menu" aria-expanded="false">☰</button>
</div></header>
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
  <div><h3>Sito</h3><a href="{home}">Home</a><a href="{r}consegna-a-domicilio/">Consegna a domicilio</a><a href="{r}prodotti/">Cosa c'è nelle macchine</a><a href="{r}snack-americani-napoli/">Snack dal mondo</a><a href="{REVIEW}" rel="noopener" target="_blank">Lascia una recensione</a></div>
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
  <a class="btn t wide" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Vieni a prenderlo ora</a>
  <p style="margin:8px 0 10px">Oppure fattelo portare a casa:</p>
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
      <p>Scrivici su WhatsApp con il numero della macchina, il prodotto e l'ora: ti rispondiamo il prima possibile e sistemiamo.</p>
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
            out.append(f'<a class="cat reveal" href="{r}prodotti/?cat={quote(c)}"><span class="e">{ICONE[c]}</span><b>{E(c)}</b><small>{cnt[c]} prodotti</small></a>')
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

def dove_txt(m):
    per = {}
    for mac, slot in m:
        per.setdefault(mac, []).append(str(slot))
    return " · ".join(f"Macchina {mac} n. {', '.join(sl)}" for mac, sl in sorted(per.items()))

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

def write(path, content):
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

def home():
    r = ""
    body = f'''
<section class="hero"><div class="sky"></div><div class="stars"></div><div class="wrap">
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
  {clock_svg()}
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

<section class="s"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">Come funziona</span><h2>Facile come un pop.</h2></div></div>
  <div class="steps">
    <div class="step reveal"><h3>Entra quando vuoi</h3><p>Giorno, notte, domenica o Capodanno: il punto self-service di Viale Marconi è sempre aperto.</p></div>
    <div class="step reveal"><h3>Scegli dalla macchina</h3><p>4 distributori con bibite fresche, energy drink, snack dolci e salati, tramezzini e prodotti utili.</p></div>
    <div class="step reveal"><h3>Oppure ordina da casa</h3><p>Su Glovo, Just Eat, Deliveroo o Alfonsino, quando l'app consegna nella tua zona.</p></div>
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
    ld = [store_ld(), {"@type": "WebSite", "@id": BASE + "#sito", "url": BASE, "name": "Pop Stop h24", "inLanguage": "it-IT",
          "publisher": {"@id": BASE + "#negozio"}}, faq_ld(FAQ_HOME)]
    write("index.html", layout("", "Pop Stop h24 Casavatore – distributori automatici aperti 24 ore e consegna a domicilio",
        f"Distributori automatici aperti 24 ore su 24 a Casavatore (Napoli nord), Viale Guglielmo Marconi 79/81: {NPROD} prodotti tra snack, bibite, energy drink e tramezzini. Consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino.",
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
        "Consegna a domicilio snack e bibite h24 a Casavatore, Casoria e Napoli nord | Pop Stop h24",
        "Ordina snack, bibite, energy drink, acqua e tramezzini a domicilio da Pop Stop h24 con Glovo, Just Eat, Deliveroo e Alfonsino. Casavatore, Casoria, Arzano, Secondigliano e Napoli nord.",
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
</div></section>
{visit_block(r, "Passa a prenderlo")}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), ("Cosa c'è nelle macchine", "prodotti/")]),
          {"@type": "ItemList", "name": "Prodotti nei distributori Pop Stop h24", "numberOfItems": NPROD,
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["n"]} for i, p in enumerate(PRODOTTI)]}]
    write("prodotti/index.html", layout("prodotti/",
        f"Cosa c'è nei distributori automatici h24 di Casavatore: {NPROD} prodotti | Pop Stop h24",
        "Energy drink, bibite, acqua, caffè Starbucks, patatine, Takis, tramezzini, Kinder, Nutella Peanut e caramelle: guarda cosa c'è ora nelle macchine di Pop Stop h24 a Casavatore.",
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
        "Snack e bibite americane a Napoli h24: Dr Pepper, Takis, Fanta USA | Pop Stop h24 Casavatore",
        f"Dove trovare Dr Pepper, Takis, Fanta americane, bibite asiatiche e Starbucks vicino Napoli a qualsiasi ora: {len(prods)} prodotti dal mondo nei distributori h24 di Pop Stop a Casavatore.",
        body, ld, d, "snack-americani-napoli/"))

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
        f"Aperto 24 ore vicino a {n}: snack e bibite a domicilio | Pop Stop h24",
        f"Cerchi un posto aperto di notte vicino a {n}? Pop Stop h24 a Casavatore: distributori automatici 24 ore su 24 e consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino.",
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
def tecnici():
    pages = ["", "consegna-a-domicilio/", "prodotti/", "snack-americani-napoli/"] + [f"zona/{k}/" for k in ZONE]
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

home(); consegna(); prodotti(); mondo()
for k, v in ZONE.items():
    zona(k, v)
page404(); tecnici()
print("ok:", NPROD, "prodotti, base", BASE)
