# Sito Pop Stop h24 Casavatore

Sito statico generato da `scripts/build_site.py` (dati in `site.json` e `stock.json`).

- Aggiornare il sito: `python3 scripts/build_site.py`, poi commit e push su `main`.
- Cambiare dominio (es. popstoph24.it): cambiare `base` in `site.json`, rilanciare lo script, aggiungere il file `CNAME`.
- Prodotti: `stock.json` (creato da `scripts/build_stock.py`); le pagine leggono anche lo stock dal vivo.
- Immagini (icone, og.png): `scripts/make_images.py` (serve il font Bricolage in TTF in /tmp).
- NON cancellare `google57e3e5a06b2aaae4.html` (verifica Search Console).
- Foto prodotti: `immagini.json` (nome prodotto → id foto del menu Deliveroo del negozio). Prodotto nuovo senza foto = icona della categoria.
- Macchine: TCN41 = Macchina 1, TCN42 = 2, TCN43 = 3, TCN44 = 4; "n." = numero di selezione (slot) su Vado.
- Aggiornare lo stock: salvare il documento `stock/macchine` dell'app inventario in un file e lanciare `python3 scripts/build_stock.py file.json > stock.json`, poi `build_site.py`.
