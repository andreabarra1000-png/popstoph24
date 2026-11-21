#!/usr/bin/env python3
"""Crea favicon, icone e immagine di anteprima (og.png). Serve un TTF di Bricolage 800/500 in /tmp."""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
B800, B500 = "/tmp/bric800.ttf", "/tmp/bric500.ttf"
T, NEON, Y, P, BG = (5,132,138), (25,214,200), (255,210,63), (255,79,139), (6,18,25)

def icon(sz):
    im = Image.new("RGB", (sz, sz), BG); d = ImageDraw.Draw(im)
    m = int(sz*.1); d.rounded_rectangle([m, m, sz-m, sz-m], radius=int(sz*.22), fill=T)
    f = ImageFont.truetype(B800, int(sz*.42)); d.text((sz/2, sz/2+sz*.02), "24", font=f, fill="white", anchor="mm")
    return im
for s in (180, 192, 512): icon(s).save(f"{A}/icon-{s}.png", optimize=True)
open(f"{A}/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#05848A"/><text x="32" y="43" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="30" text-anchor="middle" fill="#fff">24</text></svg>')

W, H = 1200, 630
im = Image.new("RGB", (W, H), BG)
glow = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(glow)
g.ellipse([700, -250, 1450, 450], fill=(8, 80, 85)); g.ellipse([-300, 380, 400, 900], fill=(70, 20, 45))
im = glow.filter(ImageFilter.GaussianBlur(120))
d = ImageDraw.Draw(im)
cx, cy, r = 945, 315, 205
ring = Image.new("RGBA", (W, H), (0,0,0,0)); rd = ImageDraw.Draw(ring)
rd.ellipse([cx-r, cy-r, cx+r, cy+r], outline=NEON+(255,), width=12)
im.paste(ring.filter(ImageFilter.GaussianBlur(14)), (0,0), ring.filter(ImageFilter.GaussianBlur(14)))
d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=NEON, width=7)
d.text((cx, cy+10), "24", font=ImageFont.truetype(B800, 190), fill="white", anchor="mm")
d.text((70, 120), "Pop Stop h24", font=ImageFont.truetype(B800, 92), fill="white")
d.text((72, 235), "Sempre aperto.", font=ImageFont.truetype(B800, 70), fill=NEON)
d.text((72, 340), "Distributori automatici 24/7", font=ImageFont.truetype(B500, 40), fill=(220,236,238))
d.text((72, 392), "e consegna a domicilio", font=ImageFont.truetype(B500, 40), fill=(220,236,238))
d.rounded_rectangle([70, 480, 610, 548], radius=22, fill=Y)
d.text((340, 514), "Casavatore · Viale Marconi 79/81", font=ImageFont.truetype(B800, 28), fill=(20,32,43), anchor="mm")
im.save(f"{A}/og.png", optimize=True)
print("immagini ok")
