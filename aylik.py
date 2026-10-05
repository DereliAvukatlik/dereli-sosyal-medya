# -*- coding: utf-8 -*-
"""
Dereli Avukatlik Burosu - LinkedIn aylik ictihat notu (PDF, 1080x1350 sayfalar)

Kullanim:
  python3 aylik.py girdi.json cikti.pdf [--kaynak DEPO_ADRESI | --yerel KLASOR]
  (kart.py ayni klasorde olmalidir)

girdi.json:
{
  "ay": "Ekim 2026",
  "kararlar": [
    {"kurum": "...", "alan": "...", "konu": "kisa baslik",
     "soru": "tek cumle", "ilke": "tek cumle",
     "degerlendirme": "en fazla ~90 kelime", "kunye": "E. ... K. ... T. ..."}
  ]
}
"""
import io, json, sys
from PIL import Image, ImageDraw
import kart as K

W, H = 1080, 1350
YAN = 100
GEN = W - 2 * YAN


def sayfa_kapak(ay, liste, f):
    img = Image.new("RGB", (W, H), K.PETROL)
    c = ImageDraw.Draw(img)
    mark = Image.open(io.BytesIO(f["mark"])).convert("RGBA")
    mh = 130
    mark = mark.resize((round(mark.width * mh / mark.height), mh), Image.LANCZOS)
    y = 150
    img.paste(mark, ((W - mark.width) // 2, y), mark)
    y += mh + 36
    K.aralikli_yaz(c, (W / 2, y), "DERELİ AVUKATLIK BÜROSU", K.yazi_tipi(f["cinzel"], 28, 500), K.KAGIT_SOLUK, 6)
    y += 90
    c.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=K.KAGIT_SOLUK, width=2)
    y += 80
    K.aralikli_yaz(c, (W / 2, y), "AYLIK İÇTİHAT NOTU", K.yazi_tipi(f["cinzel"], 36, 500), K.KAGIT_SOLUK, 5)
    y += 70
    K.aralikli_yaz(c, (W / 2, y), K.tr_buyuk(ay), K.yazi_tipi(f["cinzel"], 96, 600), K.KAGIT, 4)
    y += 170
    fl = K.yazi_tipi(f["garamond"], 34, 400)
    for m in liste:
        for s in K.satirla(c, m, fl, GEN):
            c.text((W / 2, y), s, font=fl, fill=K.KAGIT, anchor="ma")
            y += 44
        y += 18
    if y > H - 80:
        raise SystemExit("HATA: kapak listesi sigmiyor; konu basliklarini kisaltin.")
    return img


def sayfa_karar(k, no, toplam, f):
    img = Image.new("RGB", (W, H), K.KAGIT)
    c = ImageDraw.Draw(img)
    y = 90
    fk = K.yazi_tipi(f["cinzel"], 30, 600)
    for s in K.satirla(c, K.tr_buyuk(k["kurum"]), fk, GEN, 3):
        K.aralikli_yaz(c, (W / 2, y), s, fk, K.PETROL, 3)
        y += 42
    if k.get("alan"):
        K.aralikli_yaz(c, (W / 2, y + 4), K.tr_buyuk(k["alan"]), K.yazi_tipi(f["cinzel"], 22, 500), (102, 129, 126), 5)
        y += 40
    y += 24
    c.line([(W / 2 - 50, y), (W / 2 + 50, y)], fill=(102, 129, 126), width=2)
    y += 40

    alt_sinir = H - 150
    for olcek in [x / 100 for x in range(100, 59, -4)]:
        f_konu = K.yazi_tipi(f["garamond"], round(54 * olcek), 600)
        f_soru = K.yazi_tipi(f["garamond_italik"], round(34 * olcek), 400)
        f_ilke = K.yazi_tipi(f["garamond"], round(40 * olcek), 600)
        f_deg = K.yazi_tipi(f["garamond"], round(32 * olcek), 400)
        bloklar = [
            (K.satirla(c, k["konu"], f_konu, GEN), f_konu, K.PETROL, round(64 * olcek), 26, "ma"),
            (K.satirla(c, k["soru"], f_soru, GEN), f_soru, (102, 129, 126), round(46 * olcek), 26, "ma"),
            (K.satirla(c, k["ilke"], f_ilke, GEN), f_ilke, K.PETROL, round(54 * olcek), 34, "ma"),
            (K.satirla(c, k["degerlendirme"], f_deg, GEN), f_deg, (40, 48, 47), round(46 * olcek), 0, "la"),
        ]
        toplam_h = sum(len(b[0]) * b[3] + b[4] for b in bloklar)
        if y + toplam_h <= alt_sinir:
            break
    else:
        raise SystemExit(f"HATA: {no}. karar sayfasina sigmiyor; degerlendirmeyi kisaltin.")

    for satirlar, font, renk, lh, sonra, anc in bloklar:
        for s in satirlar:
            x = W / 2 if anc == "ma" else YAN
            c.text((x, y), s, font=font, fill=renk, anchor=anc)
            y += lh
        y += sonra

    fkn = K.yazi_tipi(f["garamond"], 26, 400)
    c.line([(YAN, H - 120), (W - YAN, H - 120)], fill=(200, 205, 200), width=1)
    c.text((YAN, H - 98), k["kunye"], font=fkn, fill=(102, 129, 126), anchor="la")
    c.text((W - YAN, H - 98), f"{no}/{toplam}", font=fkn, fill=(102, 129, 126), anchor="ra")
    return img


def sayfa_son(f):
    img = Image.new("RGB", (W, H), K.PETROL)
    c = ImageDraw.Draw(img)
    mark = Image.open(io.BytesIO(f["mark"])).convert("RGBA")
    mh = 150
    mark = mark.resize((round(mark.width * mh / mark.height), mh), Image.LANCZOS)
    y = H // 2 - 170
    img.paste(mark, ((W - mark.width) // 2, y), mark)
    y += mh + 40
    K.aralikli_yaz(c, (W / 2, y), "DERELİ AVUKATLIK BÜROSU", K.yazi_tipi(f["cinzel"], 32, 500), K.KAGIT, 6)
    y += 90
    fn = K.yazi_tipi(f["garamond_italik"], 30, 400)
    for s in K.satirla(c, "Karar künyeleri ilgili yargı mercilerinin resmî yayınlarına dayanmaktadır.", fn, GEN):
        c.text((W / 2, y), s, font=fn, fill=K.KAGIT_SOLUK, anchor="ma")
        y += 42
    return img


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    kaynak, yerel = K.VARSAYILAN_KAYNAK, None
    if "--kaynak" in a:
        kaynak = a[a.index("--kaynak") + 1]
    if "--yerel" in a:
        yerel = a[a.index("--yerel") + 1]
    veri = json.load(open(a[0], encoding="utf-8"))
    kararlar = veri["kararlar"]
    if not 2 <= len(kararlar) <= 8:
        raise SystemExit("HATA: aylik notta 2-8 karar olmalidir.")
    for i, k in enumerate(kararlar, 1):
        for alan in ("kurum", "konu", "soru", "ilke", "degerlendirme", "kunye"):
            if not k.get(alan):
                raise SystemExit(f"HATA: {i}. kararda '{alan}' bos.")
    f = {k: K.oku(kaynak, yerel, v) for k, v in K.DOSYALAR.items()}
    liste = [f'{k["kurum"]}: {k["konu"]}' for k in kararlar]
    sayfalar = [sayfa_kapak(veri["ay"], liste, f)]
    sayfalar += [sayfa_karar(k, i, len(kararlar), f) for i, k in enumerate(kararlar, 1)]
    sayfalar.append(sayfa_son(f))
    sayfalar[0].save(a[1], "PDF", save_all=True, append_images=sayfalar[1:], resolution=144)
    print("PDF olusturuldu:", a[1], "-", len(sayfalar), "sayfa")


if __name__ == "__main__":
    main()
