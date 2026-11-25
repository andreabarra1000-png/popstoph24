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

def link_map(file):
    """Collega i prodotti del sito agli id delle app (file: id<TAB>[altro id<TAB>]nome sul menu)."""
    righe = {}
    try:
        for l in open(os.path.join(ROOT, file), encoding="utf-8"):
            parti = l.rstrip("\n").split("\t")
            if len(parti) >= 2:
                righe[_norm_dr(parti[-1])] = "|".join(parti[:-1])
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

def deliveroo_map():
    return link_map("deliveroo.tsv")

DR = deliveroo_map()
GL = link_map("glovo.tsv")  # productId|externalId su Glovo

# Just Eat non ha link al singolo prodotto: si apre il menu già sulla categoria giusta (#categoria_<id>)
# Categorie Just Eat (dal 25/11 menu con 34 categorie specifiche, uguali su tutte le app).
# Ogni prodotto apre il menu Just Eat direttamente sulla sua categoria (#categoria_<id>).
JE_ID = {"Red Bull": "b139e3b7-8fb5-5494-a2c0-23533aa11ce7", "Monster Energy": "dfe7048e-7ed3-5048-90ad-e6056084c2fc",
  "Sport drink e altri energy": "b6d12098-7c72-55c4-ad1e-576d3d51fc5b", "Bambini e neonati": "3bcc4f29-3eea-585b-a500-d68683b1eb16",
  "Acqua": "73964126-f69f-5098-80e5-1d0e89a36c94", "Cocktail e alcolici": "dbee7b5e-d27e-5ad3-9675-5182d2ed9dba",
  "Coca-Cola e Pepsi": "beb29bd6-1df3-5a96-8a26-bc497bc5d336", "Bibite americane USA": "6c9d19db-d1c8-5e21-aff6-662be0bdc4fb",
  "Aranciate, limonate e gassate": "218b3485-3c38-553e-8847-5063f006e4cc", "Bibite giapponesi e asiatiche": "6696f0ef-2c46-5b47-a539-9c9a2d517602",
  "Tè freddi e succhi": "6e7e6a1d-ba4a-5ca3-992c-6aec92d93940", "Caffè e latte": "997718ad-4deb-5228-89b9-b14bcbeba93d",
  "Tramezzini e panini": "c51af73b-888e-57a8-ace7-3a25688e487b", "Insalate pronte": "d6b2a854-8a8c-5056-8583-fb50d3e6d85d",
  "Salumi e merende salate": "34e011ca-5e13-505a-87b8-9a273786878f", "Takis piccanti": "dfd7c3d6-5445-57ac-8978-6a7c80dbc716",
  "Crackers, grissini e salatini": "2c439142-c284-57bc-9bea-30c73636f717", "Pringles": "3f27ff45-6bf9-5854-b0af-010b7f712d41",
  "Patatine": "f53de7f2-7125-5b34-8b71-ba7ca7789b2c", "Nutella e creme spalmabili": "e81f7e88-46f8-55ac-ae33-37997332984e",
  "Merendine Kinder e Ferrero": "a5db38cb-c93f-5b3e-b969-a84b113ae367", "Mondo Kinder": "b70f9218-5c2e-551c-a8c8-30390fbf47ab",
  "Mochi giapponesi": "0590769c-fb11-5b0b-aa8e-bf32189121ab", "Cioccolato da condividere": "8181b9ad-8b0a-5ed6-b608-a09054e4ce05",
  "Barrette e snack al cioccolato": "9e7e63d1-c7fb-5dfe-95aa-ad3a3a0ac518", "Biscotti, merendine e colazione": "73e9327c-0d98-50c2-b294-9e313401f7b7",
  "Caramelle gommose": "e60a5345-7045-56e8-be0a-6d148b3e5890", "Gomme e mentine": "6814dbf3-f849-5ad2-bc57-2b0a71e94f36",
  "Birre": "e07c8038-87c2-528b-b423-a231b32df402", "Vini e Champagne": "5769d9ee-5432-50af-be47-ec9983e3efbd",
  "Salute e intimità": "3cab3211-ba1e-5ce3-9f7c-ad2f86164bd2", "Igiene e cura personale": "ced0dfa9-b84d-59ef-8289-23e6a4285422",
  "Casa e utili": "a793f426-4471-5dd2-a773-5bde86b06be7"}
# Stesse regole usate per riordinare i menu su Vado (la prima che corrisponde vince)
MENU_REGOLE = [
  ("Red Bull", r"^Red Bull"), ("Monster Energy", r"^Monster"), ("Sport drink e altri energy", r"Powerade|Squid Game Energy"),
  ("Bambini e neonati", r"Mellin|Plasmon|Humana|Frull[aà]|Latte Mio|San Benedetto Baby|Paw Patrol|Fruittella|Mentos Shampoo|Bath Bomb|Trudi|Estath[eé] Kids"),
  ("Acqua", r"Acqua|Lilia|Levissima|Ferrarelle Maxima"), ("Cocktail e alcolici", r"Breezer|Jack Daniel"),
  ("Coca-Cola e Pepsi", r"^CocaCola|^Pepsi"), ("Bibite americane USA", r"Dr Pepper|Fanta .*US"),
  ("Aranciate, limonate e gassate", r"Fanta|Sprite|Schweppes|Lemon Soda|Ferrarelle (Gassosa|Aranciata)"),
  ("Bibite giapponesi e asiatiche", r"High Up|Ocean Bomb"), ("Tè freddi e succhi", r"Estath|Th[eè] |Succoso|Sant[aà]l"),
  ("Caffè e latte", r"Starbucks|^Granarolo Latte|Latte Zymil|Nesquik Shake|Dalgona|Locatelli"),
  ("Tramezzini e panini", r"Tramezzino|Sandwich|Pan Soffice|Focaccina"), ("Insalate pronte", r"Insalatissime"),
  ("Salumi e merende salate", r"Un Due Tris|Irresistibili|Monetine|Salamini|Teneroni"), ("Takis piccanti", r"^Takis"),
  ("Crackers, grissini e salatini", r"Tuc|Cracker|Grissini|Crostini|Sticki|Cameo|Piselli|Aperisnack|Pop ?Corn|Pancarr"),
  ("Pringles", r"Pringles"), ("Patatine", r"San Carlo|Patatin|Cipster|Fonzies|Highlander"),
  ("Nutella e creme spalmabili", r"Nutella|Skippy"),
  ("Merendine Kinder e Ferrero", r"Pingu[iì]|Delice|Paradiso|Fiesta|Maxi King|Choco Fresh|Happy Hippo|Kinder Cereali|Kinder Cards|Kinder Crunchy"),
  ("Mondo Kinder", r"Kinder"), ("Mochi giapponesi", r"Mochi"),
  ("Cioccolato da condividere", r"Tavoletta|Rocher|Raffaello|Maltesers|Galak|Mini Wafers|Pralinate|Mikado|Pocket Coffee|KitKat Salted"),
  ("Barrette e snack al cioccolato", r"Twix|KitKat|Snickers|Bounty|Lion|Mars|MeM|Reese|Oro Ciok|Coco Pops|Fitness|Barretta|Milka Choco|Sperlari|Chamallows"),
  ("Biscotti, merendine e colazione", r"Ringo|Oreo|Baiocchi|Cornetto|Parmareggio|Milka Cookies|Kellogg"),
  ("Caramelle gommose", r"Haribo|Skittles|Frosty|Jelly Fruit|Gummy|Nerds|Dolcetto"), ("Gomme e mentine", r"Big Babol|Mentos|Vigorsol|Tic Tac"),
  ("Birre", r"Tennent|Beck|Peroni|Heineken|Corona|Birra"), ("Vini e Champagne", r"Prosecco|Mo[eë]t"),
  ("Salute e intimità", r"Control|Gravidanza|Urine|Alcotest|Cerotti|Amuchina"),
  ("Igiene e cura personale", r"Tempo|Tampax|Labello|Venus|Gillette|Salviettine|Spazzolino|Veet|Lines|Lycia"),
  ("Casa e utili", r"Sacchi|Bicchier|Piatti|Forchette|Coltell|Energizer|Scotch|Clipper|Carte da Gioco|Attak")]

def menu_cat(nome):
    for c, rx in MENU_REGOLE:
        if re.search(rx, nome, re.I):
            return c
    return None

JE_CAT = {p["n"]: JE_ID[menu_cat(p["n"])] for p in PRODOTTI if menu_cat(p["n"])}

ZONE = {
  "casavatore": {"nome": "Casavatore", "frase": "Siamo proprio a Casavatore, in Viale Guglielmo Marconi 79/81",
    "vicino": "Pop Stop h24 è a Casavatore, sul Viale Guglielmo Marconi al civico 79/81: il punto h24 del paese, con 4 distributori sempre accesi.",
    "extra": "Se abiti a Casavatore ci arrivi a piedi in pochi minuti, a qualsiasi ora: acqua, bibite fredde, energy drink, snack, tramezzini e prodotti di prima necessità."},
  "napoli": {"nome": "Napoli", "frase": "Siamo a Casavatore, attaccati alla zona nord di Napoli",
    "vicino": "Per chi cerca un h24 a Napoli nord, Pop Stop è a Casavatore, al confine con Secondigliano, San Pietro a Patierno e Capodichino.",
    "extra": "Di notte, quando in città trovi quasi tutto chiuso, i nostri distributori sono accesi. Con Glovo, Deliveroo, Just Eat e Alfonsino consegniamo nelle zone coperte dalle app."},
  "capodichino": {"nome": "Capodichino", "frase": "Capodichino e l'aeroporto sono a pochi minuti da Casavatore",
    "vicino": "Dall'aeroporto di Capodichino e da Viale Maddalena arrivi a Casavatore in pochi minuti, passando per San Pietro a Patierno.",
    "extra": "Volo atterrato tardi, turno in aeroporto o viaggio all'alba? Da Pop Stop h24 trovi acqua, caffè freddo, energy drink e snack anche alle 4 del mattino."},
  "poggioreale": {"nome": "Poggioreale", "frase": "Poggioreale è nella zona est di Napoli, non lontano da Casavatore",
    "vicino": "Da Poggioreale e dal Centro Direzionale arrivi a Casavatore passando per Capodichino.",
    "extra": "Fame o sete di notte a Poggioreale? Controlla sull'app se consegniamo al tuo indirizzo, oppure passa dai nostri distributori sempre aperti."},
  "frattamaggiore": {"nome": "Frattamaggiore", "frase": "Frattamaggiore è a nord, passando per Arzano",
    "vicino": "Da Frattamaggiore arrivi a Casavatore in pochi minuti passando per Arzano e Casoria.",
    "extra": "A Frattamaggiore la sera chiude quasi tutto presto: da noi i distributori restano accesi con bibite, energy drink, patatine, Takis e snack dal mondo."},
  "grumo-nevano": {"nome": "Grumo Nevano", "frase": "Grumo Nevano è a nord, vicino a Frattamaggiore e Arzano",
    "vicino": "Da Grumo Nevano arrivi a Casavatore passando per Arzano, in un quarto d'ora o meno.",
    "extra": "Serata tra amici o studio fino a tardi a Grumo Nevano? Energy drink, snack e bibite fredde sono sempre nelle nostre macchine, e con le app te li portano dove arrivano."},
  "melito": {"nome": "Melito di Napoli", "frase": "Melito è a ovest, a pochi chilometri da Casavatore",
    "vicino": "Da Melito di Napoli arrivi a Casavatore passando per Arzano o per l'asse mediano.",
    "extra": "Per chi vive a Melito siamo un punto h24 comodo per acqua, bibite, energy drink, dolci e prodotti utili, giorno e notte."},
  "mugnano": {"nome": "Mugnano di Napoli", "frase": "Mugnano è a ovest, vicino a Melito e Secondigliano",
    "vicino": "Da Mugnano di Napoli arrivi a Casavatore passando per Secondigliano in pochi minuti di auto.",
    "extra": "Quando a Mugnano è tutto chiuso, Pop Stop h24 è aperto: snack, bibite fredde, tramezzini e beni di prima necessità a qualsiasi ora."},
  "cardito": {"nome": "Cardito", "frase": "Cardito è a nord, passando per Afragola o Frattamaggiore",
    "vicino": "Da Cardito arrivi a Casavatore passando per Afragola e Casoria.",
    "extra": "Turno di notte o viaggio all'alba da Cardito? Fermati da noi per acqua, caffè freddo, energy drink e qualcosa da mangiare."},
  "crispano": {"nome": "Crispano", "frase": "Crispano è a nord, vicino a Cardito e Frattamaggiore",
    "vicino": "Da Crispano arrivi a Casavatore passando per Frattamaggiore e Arzano.",
    "extra": "A Crispano di notte non c'è molto aperto: da Pop Stop h24 i distributori restano accesi 24 ore su 24, festivi compresi."},
  "sant-antimo": {"nome": "Sant'Antimo", "frase": "Sant'Antimo è a nord-ovest, passando per Arzano",
    "vicino": "Da Sant'Antimo arrivi a Casavatore passando per Casandrino e Arzano.",
    "extra": "Fame di notte a Sant'Antimo? Snack, Takis, bibite americane e giapponesi, energy drink e tramezzini ti aspettano nei nostri distributori."},
  "casandrino": {"nome": "Casandrino", "frase": "Casandrino è a nord-ovest, vicino ad Arzano",
    "vicino": "Da Casandrino arrivi a Casavatore passando per Arzano in pochi minuti.",
    "extra": "Per Casandrino siamo un punto h24 comodo per una bibita, un energy drink o uno snack a qualsiasi ora del giorno e della notte."},
  "volla": {"nome": "Volla", "frase": "Volla è a est, oltre Casalnuovo",
    "vicino": "Da Volla arrivi a Casavatore passando per Casalnuovo o per Poggioreale.",
    "extra": "Se a Volla cerchi qualcosa aperto di notte, controlla sull'app se consegniamo al tuo indirizzo o passa dai nostri distributori sempre accesi."},
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
      "url": BASE, "image": BASE + "assets/og-popstop.jpg", "logo": BASE + "assets/popstop-512.png",
      "telephone": S["telefono"], "vatID": "IT" + S.get("piva", ""),
      "geo": {"@type": "GeoCoordinates", "latitude": S["geo"][0], "longitude": S["geo"][1]},
      "address": {"@type": "PostalAddress", "streetAddress": S["indirizzo"], "addressLocality": S["citta"],
                  "postalCode": S["cap"], "addressRegion": S["provincia"], "addressCountry": "IT"},
      "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
          "opens": "00:00", "closes": "23:59"}],
      "areaServed": [{"@type": "City", "name": v["nome"]} for v in ZONE.values()],
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

def _popin(x, y, w, cap=False, rot=0, cls="pop gp"):
    """POP dentro una scena: svg annidato (viewBox 200x260)."""
    h = w * 1.3
    inner = pop_svg(cls, "", cap=cap).replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h:.0f}" ', 1)
    if rot:
        return f'<g transform="rotate({rot} {x + w/2} {y + h/2})">{inner}</g>'
    return inner

def game_art(k):
    """Disegno della card gioco in home: POP che fa quel gioco."""
    K = 'stroke="#061219" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'
    if k == "corri":
        sc = f'<path d="M0 182 H240" stroke="#ffd23f" stroke-width="6" stroke-dasharray="16 12" opacity=".7"/><circle cx="196" cy="40" r="20" fill="#ffd23f" opacity=".9"/>' \
             f'<g opacity=".8" stroke="#fff" stroke-width="5" stroke-linecap="round"><path d="M18 90 H52"/><path d="M8 112 H46"/><path d="M22 134 H50"/></g>' \
             + _popin(66, 22, 124, cap=True, rot=8, cls="pop gp corre") + \
             '<g fill="#fff" opacity=".7"><circle cx="70" cy="188" r="6"/><circle cx="54" cy="184" r="4"/><circle cx="42" cy="190" r="3"/></g>'
    elif k == "riempi":
        sc = f'<rect x="8" y="58" width="78" height="128" rx="10" fill="#0b3b44" {K}/><rect x="18" y="70" width="58" height="80" rx="6" fill="#e9fbfb" {K}/>' \
             '<g stroke="#061219" stroke-width="2"><rect x="24" y="76" width="14" height="14" rx="3" fill="#ff4f8b"/><rect x="42" y="76" width="14" height="14" rx="3" fill="#ffd23f"/><rect x="60" y="76" width="10" height="14" rx="3" fill="#7b2ff7"/><rect x="24" y="96" width="14" height="14" rx="3" fill="#19d6c8"/></g>' \
             + _popin(100, 30, 112) + \
             f'<g transform="rotate(-10 212 100)"><rect x="198" y="82" width="28" height="38" rx="5" fill="#3ee07a" {K}/><circle cx="212" cy="102" r="7" fill="#ff5a4e" stroke="#061219" stroke-width="3"/><path d="M218 82 L221 68 L230 64" fill="none" {K}/></g>' \
             '<text x="8" y="40" font-size="20" font-weight="800" fill="#fff" font-family="Bricolage,sans-serif">⏰ 5:59</text>'
    elif k == "squalo":
        sc = '<path d="M0 150 Q30 138 60 150 T120 150 T180 150 T240 150 V220 H0 Z" fill="#1f6feb" opacity=".9"/>' \
             + _popin(78, 30, 92) + \
             f'<path d="M40 150 Q120 178 200 150 L194 168 Q120 194 46 168 Z" fill="#ff9a3c" {K}/>' \
             f'<path d="M180 150 L204 104 L214 150 Z" fill="#5b6b7a" {K}/><path d="M0 172 Q30 162 60 172 T120 172 T180 172 T240 172" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>' \
             f'<g transform="rotate(20 30 120)"><rect x="20" y="104" width="18" height="30" rx="4" fill="#e8133b" {K}/></g>'
    elif k == "dino":
        sc = f'<path d="M150 190 V110 Q150 60 190 58 Q232 58 232 92 L232 104 Q218 112 206 104 L200 120 L200 190 Z" fill="#2e9e4f" {K}/>' \
             '<circle cx="206" cy="80" r="6" fill="#061219"/><path d="M212 98 l4 6 l4 -6 l4 6" fill="none" stroke="#fff" stroke-width="3"/>' \
             '<path d="M150 130 L132 134" stroke="#061219" stroke-width="5" stroke-linecap="round"/><path d="M150 150 L134 156" stroke="#061219" stroke-width="5" stroke-linecap="round"/>' \
             '<text x="168" y="54" font-size="24" font-family="sans-serif">💤</text>' \
             + _popin(18, 50, 100, rot=-6) + \
             '<path d="M0 196 H240" stroke="#5a3d1e" stroke-width="10"/>'
    elif k == "spazio":
        sc = '<g fill="#fff"><circle cx="20" cy="30" r="2"/><circle cx="60" cy="14" r="1.5"/><circle cx="220" cy="24" r="2"/><circle cx="200" cy="150" r="1.5"/><circle cx="30" cy="170" r="2"/></g>' \
             '<text x="186" y="70" font-size="26" font-family="sans-serif">⭐</text><text x="14" y="120" font-size="22" font-family="sans-serif">☄️</text>' \
             '<g transform="rotate(-14 120 110)">' \
             f'<path d="M92 196 Q100 230 108 196 Z" fill="#ff9a3c"/><path d="M132 196 Q140 230 148 196 Z" fill="#ff9a3c"/><path d="M96 196 Q100 214 104 196 Z" fill="#ffd23f"/><path d="M136 196 Q140 214 144 196 Z" fill="#ffd23f"/>' \
             f'<rect x="86" y="140" width="24" height="58" rx="10" fill="#c0c8d0" {K}/><rect x="130" y="140" width="24" height="58" rx="10" fill="#c0c8d0" {K}/>' \
             + _popin(70, 34, 100) + \
             f'<ellipse cx="120" cy="80" rx="64" ry="62" fill="#bfefff" opacity=".28" stroke="#fff" stroke-width="4"/></g>'
    elif k == "laser":
        sc = '<path d="M120 0 V40" stroke="#fff" stroke-width="4"/>' + _popin(78, 34, 84) + \
             '<rect x="101" y="63" width="18" height="10" rx="4" fill="#061219"/><rect x="121" y="63" width="18" height="10" rx="4" fill="#061219"/><path d="M118 66 H122" stroke="#061219" stroke-width="3"/>' + \
             '<g stroke="#ff2d3d" stroke-width="4" opacity=".95"><path d="M0 150 L240 120"/><path d="M0 190 L240 200"/><path d="M0 70 L60 240" stroke-dasharray="10 8"/></g>' \
             f'<rect x="96" y="196" width="48" height="14" rx="3" fill="#ffd23f" {K}/><text x="108" y="194" font-size="20" font-family="sans-serif">🍫</text>'
    else:  # fantasmi
        sc = f'<path d="M150 70 Q150 30 186 30 Q222 30 222 70 V130 L210 120 L198 132 L186 120 L174 132 L162 120 L150 130 Z" fill="#fff" {K}/>' \
             '<circle cx="176" cy="66" r="6" fill="#061219"/><circle cx="198" cy="66" r="6" fill="#061219"/><ellipse cx="187" cy="88" rx="7" ry="9" fill="#061219"/>' \
             + _popin(14, 50, 100) + \
             f'<path d="M112 140 L150 112" stroke="#061219" stroke-width="10" stroke-linecap="round"/><path d="M112 140 L150 112" stroke="#ffd23f" stroke-width="5" stroke-linecap="round"/>' \
             f'<path d="M148 104 L170 92 L176 114 L156 122 Z" fill="#c0c8d0" {K}/><g fill="#19d6c8" opacity=".6"><circle cx="164" cy="100" r="5"/><circle cx="150" cy="96" r="3"/></g>'
    return f'<svg class="gart" viewBox="0 0 240 220" aria-hidden="true">{sc}</svg>'

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
      f'POP al cinema: <a href="{r}gioco/spazio/">5 giochi nuovi 🎬</a>',
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
    cfg = {"stock": r + "stock.json", "ordine": ORDINE, "icone": ICONE, "img": IMG, "dr": DR, "drurl": APP["deliveroo"][1], "je": JE_CAT, "jeurl": APP["justeat"][1], "gl": GL, "glurl": APP["glovo"][1]}
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
<meta name="msvalidate.01" content="F8B0834C77434FD6B739C99472535122">
<meta name="theme-color" content="#061219">
<meta name="geo.region" content="IT-NA"><meta name="geo.placename" content="Casavatore"><meta name="geo.position" content="{S["geo"][0]};{S["geo"][1]}"><meta name="ICBM" content="{S["geo"][0]}, {S["geo"][1]}">
<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Pop Stop h24">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}assets/og-popstop.jpg"><meta property="og:image:secure_url" content="{BASE}assets/og-popstop.jpg">
<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Pop Stop h24: snack, bibite ed energy drink giorno e notte a Casavatore">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}assets/og-popstop.jpg">
<link rel="icon" href="{BASE}favicon.ico" sizes="48x48">
<link rel="icon" href="{r}assets/popstop-96.png" type="image/png" sizes="96x96">
<link rel="icon" href="{r}assets/popstop-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{r}assets/popstop-180.png">
<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="preload" href="{r}assets/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/style.css">
<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>
</head>
<body{' class="pg-gioco"' if path.startswith("gioco") else ""}>
<a class="sr" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
  <button class="burger" type="button" aria-label="Apri il menu" aria-expanded="false"><span class="ln" aria-hidden="true">☰</span><span class="bt">Home</span></button>
  <a class="logo" href="{home}" aria-label="Pop Stop h24, home"><img src="{r}assets/logo.png" alt="Pop Stop h24" width="218" height="186"></a>
  <nav class="nav" aria-label="Menu principale"><a class="nhome" href="{home}">🏠 Home</a>{"".join(nav)}</nav>
  <a class="pill" href="{home}#vieni"><i></i>Aperto · <span data-ora>24h</span></a>
</div></header>
{"" if path.startswith("gioco") or path=="404.html" else tg_block(r)}
<main id="main">
{body}
</main>
<footer><div class="wrap cols">
  <div>
    <a class="logo" href="{home}"><img src="{r}assets/logo.png" alt="Pop Stop h24" width="218" height="186" style="height:72px;width:auto"></a>
    <p style="margin-top:12px">Distributori automatici aperti 24 ore su 24, 7 giorni su 7.<br>{E(INDIRIZZO_FULL)}<br>
    <a href="{TEL}" style="display:inline">Tel. e WhatsApp {S["telefono_vis"]}</a></p>
    <div class="zones" style="margin-top:16px">{zone_links}</div>
  </div>
  <div><h3>Sito</h3><a href="{home}">Home</a><a href="{r}consegna-a-domicilio/">Consegna a domicilio</a><a href="{r}prodotti/">Cosa c'è nelle macchine</a><a href="{r}snack-americani-napoli/">Snack dal mondo</a><a href="{r}aperto-24-ore-napoli-nord/">Aperto di notte a Napoli nord</a><a href="{r}energy-drink-a-domicilio/">Energy drink a domicilio</a><a href="{r}gioco/">Il gioco di POP</a><a href="{r}gioco/corri/">Corri, POP, corri!</a><a href="{r}gioco/spazio/">POP al cinema</a><a href="{REVIEW}" rel="noopener" target="_blank">Lascia una recensione</a></div>
  <div><h3>Cerchi…</h3>{"".join(f'<a href="{r}{k}/">{E(n)}</a>' for k, n in TEMI_NOMI.items())}</div>
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
  <p style="margin:8px 0 10px">Oppure ordinalo con un'altra app:</p>
  <div class="appsmini">{"".join(f'<a class="{k}" data-app="{k}" href="{u}" rel="noopener" target="_blank">{n}</a>' for k, (n, u) in APP.items())}</div>
  <p class="apphint" id="sh-hint"></p>
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
    return (f'<li><button type="button" class="pc" data-c="{E(p["c"])}" data-p="{E(p["n"])}" data-s="{p["s"]}" data-i="{p.get("i","")}" data-d="{E(d)}">'
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
        content = re.sub(r'assets/(app\.js|style\.css|gioco\.js|corri\.js|film\.js)"', lambda m: f'assets/{m.group(1)}?v={_ver(m.group(1))}"', content)
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
    <h1>Distributori automatici aperti <span class="n">24 ore</span> a Casavatore</h1>
    <p class="lead"><strong>Snack, bibite, energy drink e beni di prima necessità</strong> a qualsiasi ora. Vieni in Viale Marconi o fattelo portare a casa con le app di consegna.</p>
    <div class="infobox">
      <p class="ib-top"><span class="kicker">● Casavatore · Napoli nord</span><span class="now">🕓 Sono le <span data-ora>—</span>. <span data-frase style="color:#fff">Siamo aperti.</span></span></p>
      <div class="facts"><span><b>24/7</b> anche nei festivi</span><span><b data-count>{NPROD}</b> prodotti in macchina</span><span><b>4</b> app di consegna</span></div>
    </div>
    <div class="ctas">
      <a class="btn y" href="consegna-a-domicilio/#app">🛵 Ordina a domicilio</a>
      <a class="btn t" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a>
      <a class="btn o" href="prodotti/">🍫 Cosa c'è ora</a>
    </div>
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

<section class="s giochisub" id="giochi"><div class="wrap">
  <div class="giochi3 reveal"><h2>🎮 I giochi di POP</h2>
  <p class="g3sub">7 giochi gratis, si gioca subito dal telefono. Scorri e scegli! 👉</p>
  <div class="gtasti">{"".join(f'<a class="gtasto g{i}" href="{h}">{game_art(h.split("/")[1] or "riempi")}<b>{E(t)}</b><small>{E(g)}</small><span class="gplay">▶ Gioca</span></a>' for i, (h, e, t, g) in enumerate([("gioco/corri/", "🏃", "Corri, POP, corri!", "Platform"), ("gioco/", "🧃", "Riempi le macchine", "Prima delle 6")] + [(f"gioco/{k}/", e, t, g) for k, e, t, g, *_ in FILM]))}</div>
</div>
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
    write("index.html", layout("", "Pop Stop h24 Casavatore | H24 aperto 24 ore su 24 a Napoli nord",
        f"L'h24 di Casavatore, Casoria, Arzano e Napoli nord: distributori aperti 24 ore con {NPROD} prodotti tra snack, bibite, energy drink e tramezzini. Consegna con Glovo, Just Eat, Deliveroo e Alfonsino.",
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
  "distributori-automatici-napoli": {
    "titolo": "Distributori automatici a Napoli nord aperti 24 ore | Pop Stop h24",
    "desc": "Distributori automatici h24 a Casavatore, a due passi da Casoria, Arzano e Secondigliano: bibite, energy drink, snack, tramezzini e prodotti utili, giorno e notte. Paghi con carta o contanti.",
    "kicker": "🏪 Self-service h24", "h1": "Distributori automatici a Napoli nord, aperti 24 ore",
    "lead": "Pop Stop h24 è un punto self-service con 4 distributori automatici in Viale Guglielmo Marconi 79/81 a Casavatore. Non chiude mai: entri, scegli e paghi direttamente alla macchina, a qualsiasi ora.",
    "rx": r".", "max": 24,
    "lista": "Una parte di quello che trovi nelle macchine",
    "testo": ["Nei 4 distributori ci sono più di 150 prodotti: acqua e bibite fredde, Red Bull e Monster, caffè freddi Starbucks, patatine e Takis, tramezzini e merende salate, cioccolato, caramelle e prodotti di prima necessità come fazzoletti, assorbenti e preservativi.",
              "Le macchine sono controllate e ricaricate ogni giorno: sul sito vedi cosa c'è davvero in questo momento e in quale distributore si trova.",
              "Siamo sulla strada tra Casavatore e Casoria, comodi da Arzano, Secondigliano, San Pietro a Patierno, Capodichino e da tutta Napoli nord. Se non puoi passare, molti prodotti li trovi anche su Glovo, Just Eat, Deliveroo e Alfonsino."],
    "faq": [("Dove sono i distributori automatici h24 di Pop Stop?", "In Viale Guglielmo Marconi 79/81, 80020 Casavatore (NA), vicino a Casoria e Arzano."),
            ("Sono davvero aperti di notte?", "Sì, 24 ore su 24, 7 giorni su 7, anche nei festivi."),
            ("Come si paga ai distributori?", "Direttamente alla macchina, con carta, bancomat, smartphone o contanti."),
            ("Cosa si trova nei distributori?", "Bibite, acqua, energy drink, caffè freddi, snack dolci e salati, tramezzini, caramelle e prodotti di prima necessità.")]},
  "market-24-ore-napoli": {
    "titolo": "Market aperto 24 ore a Napoli nord, anche di notte | Pop Stop h24",
    "desc": "Cerchi un minimarket aperto 24 ore vicino a Napoli? Pop Stop h24 a Casavatore è sempre aperto: bibite, snack, acqua, tramezzini e beni di prima necessità a qualsiasi ora.",
    "kicker": "🌙 Sempre aperto", "h1": "Un market aperto 24 ore a Napoli nord",
    "lead": "Quando il supermercato è chiuso e hai bisogno di qualcosa adesso, Pop Stop h24 a Casavatore c'è: un piccolo market self-service sempre aperto, con le cose che servono davvero di sera e di notte.",
    "rx": r"acqua|tramezzino|pan soffice|un due tris|tempo|tampax|lycia|control|gillette|veet|coca|latte", "max": 24,
    "lista": "Le cose che servono a qualsiasi ora",
    "testo": ["Acqua, latte, una bibita, qualcosa da mangiare al volo, fazzoletti, assorbenti, rasoi, preservativi: nelle nostre macchine trovi i beni di prima necessità anche alle 2 di notte, la domenica e nei giorni di festa.",
              "Non è un supermercato completo: è un punto rapido, sempre acceso, per quando tutto il resto è chiuso. In due minuti prendi quello che ti serve e vai.",
              "Se preferisci non uscire, ordina dal negozio Pop Stop h24 su Glovo, Just Eat, Deliveroo o Alfonsino: il rider passa da noi e te lo porta a casa, quando l'app consegna nella tua zona."],
    "faq": [("C'è un market aperto 24 ore vicino a Casoria e Casavatore?", "Sì: Pop Stop h24, in Viale Guglielmo Marconi 79/81 a Casavatore, è un punto self-service aperto 24 ore su 24."),
            ("Posso comprare beni di prima necessità di notte?", "Sì: acqua, latte, fazzoletti, assorbenti, rasoi e preservativi sono nelle macchine a qualsiasi ora."),
            ("Fate consegne a domicilio?", "Sì, tramite Glovo, Just Eat, Deliveroo e Alfonsino, quando l'app è attiva nella tua zona.")]},
  "snack-di-notte-napoli": {
    "titolo": "Snack di notte a Napoli: dove mangiare qualcosa a tarda notte | Pop Stop",
    "desc": "Fame di notte a Napoli nord? Da Pop Stop h24 a Casavatore trovi snack, patatine, cioccolato, tramezzini e bibite fredde a qualsiasi ora, anche a domicilio con le app.",
    "kicker": "🍫 Fame notturna", "h1": "Snack di notte a Napoli nord: siamo aperti",
    "lead": "È mezzanotte passata, hai fame e i bar sono chiusi. Da Pop Stop h24 a Casavatore le macchine sono accese: patatine, Takis, Kinder, tramezzini e una bibita fredda, quando vuoi.",
    "rx": r"takis|pringles|kinder bueno|twix|kitkat|snickers|tramezzino|nutella|oreo|haribo", "max": 24,
    "lista": "Gli snack preferiti di notte",
    "testo": ["Dopo il lavoro, dopo una serata, durante lo studio o una partita alla console: gli snack più presi di notte sono Takis e Pringles, Kinder Bueno, KitKat, Twix e i tramezzini Beretta, insieme a un energy drink o a una Coca-Cola.",
              "Puoi passare in Viale Guglielmo Marconi 79/81 a qualsiasi ora, oppure ordinare dall'app di consegna che preferisci, quando il servizio notturno è disponibile nella tua zona."],
    "faq": [("Dove trovo snack di notte vicino a Napoli?", "Da Pop Stop h24 a Casavatore: i distributori sono aperti 24 ore su 24."),
            ("Posso ordinare snack a domicilio di notte?", "Sì, con Glovo, Deliveroo o Alfonsino, quando hanno rider disponibili nella tua zona. Just Eat consegna fino a mezzanotte.")]},
  "takis-napoli": {
    "titolo": "Takis a Napoli: Fuego e Blue Heat, anche di notte | Pop Stop h24",
    "desc": "Dove comprare i Takis a Napoli? Da Pop Stop h24 a Casavatore: Takis Fuego, Blue Heat e altri gusti nei distributori aperti 24 ore, o a domicilio con Glovo, Just Eat e Deliveroo.",
    "kicker": "🌶️ Takis", "h1": "Takis a Napoli, sempre disponibili",
    "lead": "I Takis, le chips di tortilla arrotolate e super piccanti diventate famose su TikTok, li trovi da Pop Stop h24 a Casavatore: Fuego al chili e lime, Blue Heat e gli altri gusti che arrivano, a qualsiasi ora.",
    "rx": r"takis|pringles hot|piccant", "max": 12,
    "lista": "I Takis nelle macchine adesso",
    "testo": ["Takis Fuego è il più famoso: chili e lime, piccantezza alta. Blue Heat ha lo stesso carattere ma colora la lingua di blu, perfetto per le sfide con gli amici.",
              "Li trovi nei distributori di Viale Guglielmo Marconi 79/81 a Casavatore, vicino a Casoria e Napoli nord, oppure a domicilio dal negozio Pop Stop h24 sulle app di consegna. Abbinali a una bibita fredda: ne avrai bisogno."],
    "faq": [("Dove comprare i Takis a Napoli?", "Da Pop Stop h24 in Viale Guglielmo Marconi 79/81 a Casavatore, nei distributori aperti 24 ore, o a domicilio con Glovo, Just Eat e Deliveroo."),
            ("Quali gusti di Takis ci sono?", "Di solito Fuego e Blue Heat in due formati; sul sito vedi i gusti disponibili adesso.")]},
  "dr-pepper-napoli": {
    "titolo": "Dr Pepper a Napoli: Cherry, Vanilla Float e gusti USA | Pop Stop h24",
    "desc": "Dove trovare il Dr Pepper a Napoli? Da Pop Stop h24 a Casavatore: Dr Pepper Cherry, Vanilla Float, Creamy Coconut e lattine USA, h24 e a domicilio.",
    "kicker": "🥤 Dr Pepper", "h1": "Dr Pepper a Napoli: tutti i gusti, anche di notte",
    "lead": "Il Dr Pepper, la bibita americana con 23 aromi, da noi c'è in tante versioni: Cherry, Cherry Crush, Cream Swirl, Creamy Coconut, Vanilla Float, Blackberry e l'Original in lattina USA.",
    "rx": r"dr pepper|fanta .*us", "max": 20,
    "lista": "Dr Pepper e bibite USA nelle macchine",
    "testo": ["Molti gusti sono edizioni americane da 355 ml che nei supermercati italiani non si trovano: arrivano a rotazione, quindi qui sopra vedi quelli disponibili in questo momento.",
              "Insieme al Dr Pepper trovi anche le Fanta americane (Peach, Pineapple, Strawberry, Grape, Berry) e le bibite giapponesi. Passa a Casavatore a qualsiasi ora o ordinali a domicilio."],
    "faq": [("Dove si compra il Dr Pepper a Napoli?", "Da Pop Stop h24 a Casavatore, nei distributori aperti 24 ore o a domicilio con le app di consegna."),
            ("Avete i Dr Pepper americani?", "Sì, diverse lattine USA da 355 ml come Original, Vanilla Float, Cherry e Blackberry, a rotazione.")]},
  "bibite-giapponesi-napoli": {
    "titolo": "Bibite giapponesi e ramune a Napoli, aperto 24 ore | Pop Stop h24",
    "desc": "Bibite giapponesi e asiatiche a Napoli: ramune High Up, Ocean Bomb e gusti introvabili da Pop Stop h24 a Casavatore, nei distributori h24 e a domicilio.",
    "kicker": "🍡 Dal Giappone", "h1": "Bibite giapponesi e ramune a Napoli",
    "lead": "Ramune all'uva, fragola daifuku, limone e miele con i supereroi Marvel, Transformers e Kuromi: le bibite asiatiche che vedi nei video le trovi da Pop Stop h24 a Casavatore.",
    "rx": r"high up|ocean bomb|mochi", "max": 20,
    "lista": "Bibite asiatiche nelle macchine adesso",
    "testo": ["Le lattine High Up sono bibite frizzanti dai gusti tipici giapponesi, come wagashi e daifuku, con grafiche da collezione. Arrivano a rotazione: qui vedi quelle disponibili adesso.",
              "Sono un'idea perfetta per un regalo strano o una sfida tra amici. Le trovi nei distributori di Viale Guglielmo Marconi 79/81 o a domicilio con le app."],
    "faq": [("Dove trovo bibite giapponesi a Napoli?", "Da Pop Stop h24 a Casavatore: lattine High Up e altre bibite asiatiche nei distributori aperti 24 ore."),
            ("Le consegnate a domicilio?", "Sì, con Glovo, Just Eat, Deliveroo e Alfonsino, quando l'app consegna nella tua zona.")]},
  "acqua-a-domicilio-napoli": {
    "titolo": "Acqua a domicilio a Casavatore e Casoria, anche di notte | Pop Stop",
    "desc": "Acqua fresca a domicilio o nei distributori h24 di Pop Stop a Casavatore: Sorgesana, Ferrarelle, Electa e Fiji da mezzo litro, giorno e notte, con Glovo, Just Eat e Deliveroo.",
    "kicker": "💧 Acqua", "h1": "Acqua fresca a domicilio o h24 a Casavatore",
    "lead": "Acqua naturale e frizzante sempre fredda nelle nostre macchine, anche di notte: Sorgesana, Ferrarelle, Electa e Fiji in bottiglietta, da prendere al volo o da farsi portare a casa.",
    "rx": r"acqua|ferrarelle maxima|levissima|lilia", "max": 12,
    "lista": "L'acqua nelle macchine adesso",
    "testo": ["L'acqua è il prodotto che prendete di più, di giorno e soprattutto di notte. Per questo i distributori ne sono sempre pieni.",
              "Se ti serve a domicilio, aggiungila a un ordine su Glovo, Just Eat, Deliveroo o Alfonsino dal negozio Pop Stop h24."],
    "faq": [("Dove trovo acqua di notte a Casavatore?", "Nei distributori di Pop Stop h24 in Viale Guglielmo Marconi 79/81, aperti 24 ore su 24."),
            ("Consegnate l'acqua a domicilio?", "Sì, tramite le app di consegna quando il servizio è attivo nella tua zona.")]},
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

TEMI_NOMI = {"distributori-automatici-napoli": "Distributori automatici a Napoli nord", "market-24-ore-napoli": "Market aperto 24 ore",
  "snack-di-notte-napoli": "Snack di notte", "takis-napoli": "Takis a Napoli", "dr-pepper-napoli": "Dr Pepper a Napoli",
  "bibite-giapponesi-napoli": "Bibite giapponesi", "acqua-a-domicilio-napoli": "Acqua a domicilio",
  "aperto-24-ore-napoli-nord": "Aperto di notte a Napoli nord", "energy-drink-a-domicilio": "Energy drink a domicilio"}

def altri_temi(slug, r):
    return " · ".join(f'<a href="{r}{k}/">{E(n)}</a>' for k, n in TEMI_NOMI.items() if k != slug)

def tema(slug, t):
    d = 1; r = rel(d)
    prods = [p for p in PRODOTTI if re.search(t["rx"], p["n"], re.I)][:t.get("max", 999)]
    faq = t.get("faq", [])
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
  <div class="prose" style="margin-top:22px"><p>Vedi anche: {altri_temi(slug, r)}</p></div>
</div></section>
<section class="s alt" id="app"><div class="wrap">
  <div class="head"><div><span class="eyebrow">Consegna a domicilio</span><h2>Scegli la tua app</h2></div><p>Quando l'app consegna al tuo indirizzo.</p></div>
  {app_cards()}
  <div style="margin-top:22px">{zones_block(r)}</div>
</div></section>
{('<section class="s"><div class="wrap"><div class="head"><div><span class="eyebrow">Domande frequenti</span><h2>Domande e risposte</h2></div></div>' + faq_html(faq) + '</div></section>') if faq else ""}
{visit_block(r)}'''
    ld = [store_ld(), crumbs_ld([("Home", ""), (t["h1"], slug + "/")])] + ([faq_ld(faq)] + [] if faq else []) + [
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
      (f"C'è un h24 a {n} o vicino?", f"Sì: Pop Stop h24, in {E(INDIRIZZO_FULL)}. {z['frase']}. È aperto 24 ore su 24, 7 giorni su 7, festivi compresi, e consegna con Glovo, Just Eat, Deliveroo e Alfonsino."),
      (f"C'è un posto aperto 24 ore vicino a {n}?", f"Sì: Pop Stop h24, in {E(INDIRIZZO_FULL)}. {z['frase']}: distributori automatici aperti giorno e notte, 7 giorni su 7."),
      (f"Pop Stop h24 consegna a {n}?", f"Consegniamo con Glovo, Just Eat, Deliveroo e Alfonsino quando l'app è disponibile al tuo indirizzo di {n}. Inserisci l'indirizzo nell'app per vedere se arriviamo."),
      (f"Cosa posso comprare di notte a {n}?", "Energy drink, bibite, acqua, patatine, Takis, tramezzini, dolci, caramelle e prodotti utili come igiene personale: tutto quello che c'è nelle nostre macchine."),
    ]
    body = f'''
<div class="wrap crumbs"><a href="{r}">Home</a> › <a href="{r}consegna-a-domicilio/">Consegna</a> › {E(n)}</div>
<section class="page-hero"><div class="wrap">
  <span class="kicker">📍 h24 {E(n)} · Napoli nord</span>
  <h1>H24 a {E(n)}: aperto 24 ore su 24, anche a domicilio</h1>
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
        f"H24 {n}: aperto 24 ore, snack e bibite anche di notte | Pop Stop h24",
        f"Cerchi un h24 a {n}? Pop Stop h24 è aperto 24 ore su 24 a Casavatore, con distributori automatici e consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino.",
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
  {gtabs(r, "gioco/")}
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
  {gtabs(r, "gioco/corri/")}
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

FILM = [
  ("squalo", "🦈", "Arriva la pinna!", "Mare aperto", "POP è sul canotto in mezzo al mare e qualcosa con una pinna gira intorno a lui. Schiva le pinne, prendi le lattine che galleggiano e tieniti stretto.",
   ["👆 <b>Trascina</b> il dito (o usa ← →) per spostare il canotto.", "🥤 Prendi le <b>lattine</b>: 10 punti l'una. La boa rossa ti ridà un cuore.", "🦈 Evita le <b>pinne</b>: hai 3 cuori e il mare si fa sempre più affollato."], "Action", "il gioco del mare con le pinne"),
  ("dino", "🦖", "Il parco dei dinosauri", "Avventura preistorica", "Il distributore h24 è dall'altra parte del recinto, ma dietro c'è un dinosauro enorme. Avanza solo quando dorme e resta immobile quando ti guarda.",
   ["👆 <b>Tieni premuto</b> (o →) per far camminare POP, lascia per fermarti.", "🥤 Se il <b>bicchiere trema</b> il dinosauro sta per girarsi: il semaforo diventa rosso.", "🍫 Raccogli i cioccolatini e arriva alla macchina per passare al recinto dopo."], "Stealth", "il gioco del parco dei dinosauri"),
  ("spazio", "🚀", "POP nello spazio", "Viaggio tra le stelle", "POP ha indossato il casco ed è partito col jetpack per portare snack in tutta la galassia. Vola tra gli asteroidi e raccogli le stelle.",
   ["👆 <b>Tieni premuto</b> (o barra spaziatrice) per accendere il jetpack e salire, lascia per scendere.", "⭐ Prendi le <b>stelle</b>: 10 punti l'una, più vai lontano più punti fai.", "☄️ Evita gli <b>asteroidi</b> e il fondo dello schermo: hai 3 cuori."], "Arcade", "il gioco di POP nello spazio"),
  ("laser", "🕶️", "Missione: snack impossibile", "Spionaggio", "Nel caveau più protetto della città c'è uno snack da recuperare. POP scende appeso a una corda dal lucernario: i laser si accendono e si spengono, e alcuni si muovono.",
   ["👆 <b>Tieni premuto</b> (o ↓) per calare POP con la corda, lascia per risalire.", "🔴 Passa quando i <b>laser sono spenti</b> (tratteggiati): se ne tocchi uno scatta l'allarme.", "🍫 Prendi lo snack sul piedistallo e torna su: ogni colpo è più difficile."], "Puzzle", "il gioco della missione nel caveau"),
  ("fantasmi", "👻", "Acchiappa i fantasmi", "Casa infestata", "La vecchia villa è piena di fantasmi che si affacciano alle finestre. POP ha un aspirapolvere speciale e 60 secondi per liberare la casa.",
   ["👆 <b>Tocca</b> i fantasmi quando escono dalle finestre: più ne prendi di fila, più punti.", "✨ I fantasmi <b>luccicanti</b> valgono il triplo.", "🐈‍⬛ Non toccare il <b>gatto nero</b>: ti costa un cuore."], "Arcade", "il gioco dei fantasmi"),
]

def gtabs(r, cur):
    voci = [("gioco/", "🧃 Riempi le macchine"), ("gioco/corri/", "🏃 Corri, POP, corri!")] + [(f"gioco/{k}/", f"{e} {t}") for k, e, t, *_ in FILM]
    return '<nav class="gtabs" aria-label="I giochi di POP">' + "".join(f'<a href="{r}{u}"' + (' aria-current="page"' if u == cur else '') + f'>{t}</a>' for u, t in voci) + '</nav>'

def film():
    r = rel(2)
    for i, (k, e, tit, gen, intro, how, genre, nome) in enumerate(FILM):
        altri = [f for f in FILM if f[0] != k][:2]
        body = f'''
<div class="corri film" id="corri" data-film="{k}">
  {gtabs(r, f"gioco/{k}/")}
  <section class="cover fuori" id="c-start">
      <span class="sticker p">POP al cinema · {E(gen)}</span>
      <h1>{e} {E(tit)}</h1>
      <p>{E(intro)}</p>
      <div class="how">{"".join(f"<div>{h}</div>" for h in how)}</div>
      <button class="btn y" type="button" data-via>▶ Gioca</button>
      <p class="crec" id="c-best"></p>
    </section>
  <div class="cwrap">
    <canvas id="c-can" aria-label="Gioco {E(tit)} con POP"></canvas>
    <div class="chud" aria-live="off"><span id="c-cuori">❤️❤️❤️</span><span>🏆 <b id="c-punti">0</b></span><span>{ {"squalo":"🥤","dino":"🚧","spazio":"⭐","laser":"🍫","fantasmi":"👻"}[k]} <b id="c-extra">0</b></span><button id="c-audio" type="button" aria-label="Togli i suoni">🔊</button></div>
    <div class="cbanner" id="c-banner"></div>
    <section class="cover" id="c-end" hidden>
      <h2 id="c-tit">Fine!</h2>
      <p class="score" id="c-fin"></p>
      <p class="crec" id="c-record"></p>
      <div class="row"><button class="btn y" type="button" data-via>🔁 Rigioca</button><a class="btn wa" id="c-share" href="#" rel="noopener" target="_blank">💬 Sfida un amico</a></div>
    </section>
  </div>
  <div class="cdopo">
    <p>Dopo il film, lo snack. Le macchine vere sono aperte 24 ore su 24 in Viale Marconi a Casavatore.</p>
    <div class="row"><a class="btn t" href="{r}consegna-a-domicilio/#app">🛵 Ordina a domicilio</a><a class="btn o" href="{MAPS_DIR}" rel="noopener" target="_blank">📍 Portami da Pop Stop</a>{"".join(f'<a class="btn" href="{r}gioco/{a[0]}/">{a[1]} {E(a[2])}</a>' for a in altri)}</div>
  </div>
</div>
<script src="{r}assets/film.js" defer></script>'''
        ld = [crumbs_ld([("Home", ""), ("Gioco", "gioco/"), (tit, f"gioco/{k}/")]),
              {"@type": "VideoGame", "name": f"{tit} – il gioco di POP, Pop Stop h24", "url": BASE + f"gioco/{k}/", "inLanguage": "it-IT",
               "genre": [genre], "gamePlatform": "Web browser", "applicationCategory": "Game", "operatingSystem": "Any",
               "description": f"Mini gioco gratuito di Pop Stop h24: {intro}",
               "publisher": {"@id": BASE + "#negozio"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
        write(f"gioco/{k}/index.html", layout(f"gioco/{k}/", f"Gioco: {tit} | Pop Stop h24",
            f"{intro[:120].rsplit(' ',1)[0]}… Gioca gratis dal telefono con POP, la mascotte di Pop Stop h24.",
            body, ld, 2, active="gioco/"))

def redirect(slug, url):
    write(f"{slug}/index.html", f'''<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pop Stop h24</title><meta http-equiv="refresh" content="0;url={E(url)}"><link rel="canonical" href="{E(url)}"></head>
<body style="background:#061219;color:#fff;font-family:sans-serif;text-align:center;padding:60px 20px"><p>Un attimo…</p><p><a style="color:#ffd23f" href="{E(url)}">Tocca qui se non si apre da solo</a></p>
<script>location.replace({json.dumps(url)})</script></body></html>''')

def tecnici():
    pages = ["", "consegna-a-domicilio/", "prodotti/", "snack-americani-napoli/", "gioco/", "gioco/corri/"] + [f"gioco/{f[0]}/" for f in FILM] + [f"{k}/" for k in TEMI] + [f"prodotti/{CAT_SLUG[c]}/" for c in ORDINE if any(p["c"] == c for p in PRODOTTI)] + [f"zona/{k}/" for k in ZONE]
    urls = "".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{OGGI}</lastmod></url>\n" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /scripts/\nSitemap: {BASE}sitemap.xml\n")
    write("manifest.webmanifest", json.dumps({"name": "Pop Stop h24 Casavatore", "short_name": "Pop Stop", "start_url": "./", "display": "standalone",
        "background_color": "#061219", "theme_color": "#061219", "lang": "it",
        "icons": [{"src": "assets/popstop-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/popstop-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False, indent=1))
    cats = ", ".join(f"{c} ({sum(1 for p in PRODOTTI if p['c']==c)})" for c in ORDINE)
    write("llms.txt", f"""# Pop Stop h24 – Casavatore (Napoli)

> Punto vendita self-service con distributori automatici aperto 24 ore su 24, 7 giorni su 7, festivi compresi, in {INDIRIZZO_FULL}. Consegna a domicilio con Glovo, Just Eat, Deliveroo e Alfonsino quando l'app è disponibile.

- Telefono e WhatsApp: {S['telefono_vis']}
- Zone vicine e di consegna: Casavatore, Casoria, Arzano, Secondigliano, San Pietro a Patierno, Napoli nord
- Prodotti ({NPROD}): {cats}
- Specialità: bibite e snack dal mondo (Dr Pepper, Fanta USA, Takis, High Up, Starbucks), Nutella Peanut
- Sito: {BASE} · Prodotti: {BASE}prodotti/ · Consegna: {BASE}consegna-a-domicilio/
""")

home(); consegna(); prodotti(); mondo(); gioco(); corri(); film()
for k, v in TEMI.items():
    tema(k, v)
for c in ORDINE:
    if any(p["c"] == c for p in PRODOTTI):
        categoria(c)
for k, v in ZONE.items():
    zona(k, v)
page404(); tecnici()
redirect("recensione", REVIEW); redirect("instagram", S["social"]["Instagram"]); redirect("tiktok", S["social"]["TikTok"])
print("ok:", NPROD, "prodotti, base", BASE)
