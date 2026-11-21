#!/usr/bin/env python3
"""Crea stock.json per il sito a partire dal documento stock/macchine dell'app inventario.

Uso: python3 scripts/build_stock.py macchine.json > stock.json
macchine.json = il documento stock/macchine così com'è ({"macchine": {"TCN41": [{"n","q",...}]}, "updatedAt": ...}).
Sul sito vanno solo nome, categoria e stato (disponibile / ultimi pezzi): niente prezzi, niente alcolici.
"""
import json, re, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ALCOL = re.compile(r"birra|heineken|corona|tennent|peroni|beck|prosecco|mo[eë]t|champagne|bacardi|breezer|jack daniel|vino", re.I)
CATEGORIE = [
    ("Energy drink", r"red bull|monster|powerade"),
    ("Acqua", r"acqua|fiji|electa|san benedetto baby"),
    ("Bibite", r"coca|pepsi|fanta|sprite|schweppes|dr pepper|estath|th[eè] |sant[aà]l|lemon soda|high up"),
    ("Caffè e latte", r"starbucks|granarolo|zymil|locatelli|nesquik shake"),
    ("Tramezzini e salato", r"tramezzino|pan soffice|beretta|citterio|un due tris|salamini|monetine|focaccina"),
    ("Patatine e snack salati", r"pringles|takis|san carlo|dixi|patatin"),
    ("Caramelle e gomme", r"haribo|skittles|vigorsol|tic tac|big babol|jelly|chamallows|mentos"),
    ("Igiene e altro", r"gillette|tampax|lycia|veet|control"),
]

def categoria(nome):
    for cat, rx in CATEGORIE:
        if re.search(rx, nome, re.I):
            return cat
    return "Dolci e cioccolato"

def pulisci(nome):
    n = re.sub(r"\s+", " ", nome).strip()
    return n[:1].upper() + n[1:] if n.isupper() is False else n.title()

def main(path):
    doc = json.load(open(path, encoding="utf-8"))
    tot = {}
    for slots in doc.get("macchine", {}).values():
        for s in slots:
            n, q = s.get("n", "").strip(), int(s.get("q") or 0)
            if not n or q <= 0 or ALCOL.search(n):
                continue
            k = pulisci(n)
            tot[k] = tot.get(k, 0) + q
    prodotti = [{"n": n, "c": categoria(n), "s": "ultimi" if q <= 2 else "ok"} for n, q in sorted(tot.items(), key=lambda x: x[0].lower())]
    upd = doc.get("updatedAt")
    try:
        dt = datetime.fromisoformat(upd.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Rome"))
        quando = dt.strftime("%d/%m alle %H:%M")
    except Exception:
        quando = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m alle %H:%M")
    json.dump({"aggiornato": quando, "prodotti": prodotti}, sys.stdout, ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
    main(sys.argv[1])
