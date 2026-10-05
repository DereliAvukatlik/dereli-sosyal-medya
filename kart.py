# -*- coding: utf-8 -*-
"""
Dereli Avukatlik Burosu - Instagram hikaye karar karti (1080x1920)

Kullanim:
  python3 kart.py girdi.json cikti.png [--kaynak DEPO_ADRESI | --yerel KLASOR]

girdi.json alanlari:
  kurum   : "Yargitay Hukuk Genel Kurulu" (zorunlu)
  alan    : "Aile Hukuku" (istege bagli)
  soru    : kararin cevapladigi soru, tek cumle (zorunlu)
  ilke    : kararin ilkesi, tek cumle (zorunlu)
  kunye   : "E. 2024/123  K. 2025/456  T. 12.03.2025" (zorunlu)

Aylik kapak karti icin:
  tur     : "kapak"
  baslik  : "Ekim 2026"
  alt     : "Aylik Ictihat Notu" (istege bagli)
  liste   : ["Yargitay HGK - konu", ...] en fazla 6 satir
"""
import io, json, os, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

VARSAYILAN_KAYNAK = "https://raw.githubusercontent.com/DereliAvukatlik/dereli-sosyal-medya/main"

W, H = 1080, 1920
PETROL = (14, 59, 58)
KAGIT = (247, 244, 238)
KAGIT_SOLUK = (180, 192, 189)      # kagidin petrol uzerinde %70 karisimi
UST_SINIR, ALT_SINIR = 260, 1560    # hikaye guvenli alani (ust ~250 px, alt ~340 px bos)
YAN = 100                            # yan bosluk
METIN_GENISLIK = W - 2 * YAN

DOSYALAR = {
    "cinzel": "fonts/Cinzel-wght.ttf",
    "garamond": "fonts/EBGaramond-wght.ttf",
    "garamond_italik": "fonts/EBGaramond-Italic-wght.ttf",
    "mark": "logo/mark-kagit-seffaf.png",
}


def oku(kaynak, yerel, yol):
    if yerel:
        with open(os.path.join(yerel, yol), "rb") as f:
            return f.read()
    with urllib.request.urlopen(kaynak.rstrip("/") + "/" + yol, timeout=30) as r:
        return r.read()


def tr_buyuk(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def yazi_tipi(veri, boyut, agirlik):
    f = ImageFont.truetype(io.BytesIO(veri), boyut)
    try:
        f.set_variation_by_axes([agirlik])
    except Exception:
        pass
    return f


def satirla(ciz, metin, font, genislik, aralik=0):
    kelimeler, satirlar, mevcut = metin.split(), [], ""
    for k in kelimeler:
        deneme = (mevcut + " " + k).strip()
        if ciz.textlength(deneme, font=font) + aralik * len(deneme) <= genislik:
            mevcut = deneme
        else:
            if mevcut:
                satirlar.append(mevcut)
            mevcut = k
    if mevcut:
        satirlar.append(mevcut)
    return satirlar


def aralikli_yaz(ciz, xy_merkez, metin, font, renk, aralik):
    x_toplam = sum(ciz.textlength(c, font=font) for c in metin) + aralik * (len(metin) - 1)
    x = xy_merkez[0] - x_toplam / 2
    for c in metin:
        ciz.text((x, xy_merkez[1]), c, font=font, fill=renk)
        x += ciz.textlength(c, font=font) + aralik


def ciz_kart(veri, f, cikti):
    img = Image.new("RGB", (W, H), PETROL)
    ciz = ImageDraw.Draw(img)
    y = UST_SINIR

    # Mark
    mark = Image.open(io.BytesIO(f["mark"])).convert("RGBA")
    mh = 120
    mark = mark.resize((round(mark.width * mh / mark.height), mh), Image.LANCZOS)
    img.paste(mark, ((W - mark.width) // 2, y), mark)
    y += mh + 34

    # Buro adi
    f_buro = yazi_tipi(f["cinzel"], 28, 500)
    aralikli_yaz(ciz, (W / 2, y), "DERELİ AVUKATLIK BÜROSU", f_buro, KAGIT_SOLUK, 6)
    y += 40 + 50

    # Ince cizgi
    ciz.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=KAGIT_SOLUK, width=2)
    y += 60

    # Kurum
    f_kurum = yazi_tipi(f["cinzel"], 38, 600)
    for s in satirla(ciz, tr_buyuk(veri["kurum"]), f_kurum, METIN_GENISLIK, 3):
        aralikli_yaz(ciz, (W / 2, y), s, f_kurum, KAGIT, 3)
        y += 52
    if veri.get("alan"):
        f_alan = yazi_tipi(f["cinzel"], 26, 500)
        aralikli_yaz(ciz, (W / 2, y + 6), tr_buyuk(veri["alan"]), f_alan, KAGIT_SOLUK, 5)
        y += 46
    y += 50

    # Soru + ilke + kunye: kalan alana sigacak en buyuk boyutu bul
    f_kunye = yazi_tipi(f["garamond"], 32, 400)
    kunye_satir = satirla(ciz, veri["kunye"], f_kunye, METIN_GENISLIK)
    kunye_h = len(kunye_satir) * 44
    alan_ust, alan_alt = y, ALT_SINIR - kunye_h - 70

    for olcek in [x / 100 for x in range(100, 59, -4)]:
        f_soru = yazi_tipi(f["garamond_italik"], round(48 * olcek), 400)
        f_ilke = yazi_tipi(f["garamond"], round(66 * olcek), 500)
        s_satir = satirla(ciz, veri["soru"], f_soru, METIN_GENISLIK)
        i_satir = satirla(ciz, veri["ilke"], f_ilke, METIN_GENISLIK)
        s_lh, i_lh = round(64 * olcek), round(86 * olcek)
        toplam = len(s_satir) * s_lh + 70 + len(i_satir) * i_lh
        if toplam <= alan_alt - alan_ust:
            break
    else:
        raise SystemExit("HATA: metin kart alanina sigmiyor; soru ve ilke kisaltilmali.")

    y = alan_ust + max(0, ((alan_alt - alan_ust) - toplam) // 3)
    for s in s_satir:
        ciz.text((W / 2, y), s, font=f_soru, fill=KAGIT_SOLUK, anchor="ma")
        y += s_lh
    y += 30
    ciz.line([(W / 2 - 30, y), (W / 2 + 30, y)], fill=KAGIT_SOLUK, width=2)
    y += 40
    for s in i_satir:
        ciz.text((W / 2, y), s, font=f_ilke, fill=KAGIT, anchor="ma")
        y += i_lh

    # Kunye (alt guvenli sinirin hemen ustunde)
    y = ALT_SINIR - kunye_h
    for s in kunye_satir:
        ciz.text((W / 2, y), s, font=f_kunye, fill=KAGIT_SOLUK, anchor="ma")
        y += 44

    img.save(cikti, "PNG", optimize=True)


def ciz_kapak(veri, f, cikti):
    img = Image.new("RGB", (W, H), PETROL)
    ciz = ImageDraw.Draw(img)
    y = UST_SINIR
    mark = Image.open(io.BytesIO(f["mark"])).convert("RGBA")
    mh = 120
    mark = mark.resize((round(mark.width * mh / mark.height), mh), Image.LANCZOS)
    img.paste(mark, ((W - mark.width) // 2, y), mark)
    y += mh + 34
    aralikli_yaz(ciz, (W / 2, y), "DERELİ AVUKATLIK BÜROSU", yazi_tipi(f["cinzel"], 28, 500), KAGIT_SOLUK, 6)
    y += 90
    ciz.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=KAGIT_SOLUK, width=2)
    y += 90
    aralikli_yaz(ciz, (W / 2, y), tr_buyuk(veri.get("alt", "Aylık İçtihat Notu")), yazi_tipi(f["cinzel"], 34, 500), KAGIT_SOLUK, 5)
    y += 70
    f_bas = yazi_tipi(f["cinzel"], 92, 600)
    for s_ in satirla(ciz, tr_buyuk(veri["baslik"]), f_bas, METIN_GENISLIK, 4):
        aralikli_yaz(ciz, (W / 2, y), s_, f_bas, KAGIT, 4)
        y += 115
    y += 70
    f_lis = yazi_tipi(f["garamond"], 38, 400)
    for madde in veri.get("liste", [])[:6]:
        for s_ in satirla(ciz, madde, f_lis, METIN_GENISLIK):
            if y > ALT_SINIR - 50:
                raise SystemExit("HATA: kapak listesi sigmiyor; maddeleri kisaltin.")
            ciz.text((W / 2, y), s_, font=f_lis, fill=KAGIT, anchor="ma")
            y += 50
        y += 26
    img.save(cikti, "PNG", optimize=True)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    kaynak, yerel = VARSAYILAN_KAYNAK, None
    if "--kaynak" in a:
        kaynak = a[a.index("--kaynak") + 1]
    if "--yerel" in a:
        yerel = a[a.index("--yerel") + 1]
    with open(a[0], encoding="utf-8") as fh:
        veri = json.load(fh)
    dosyalar = {k: oku(kaynak, yerel, v) for k, v in DOSYALAR.items()}
    if veri.get("tur") == "kapak":
        if not veri.get("baslik"):
            raise SystemExit("HATA: 'baslik' alani bos.")
        ciz_kapak(veri, dosyalar, a[1])
    else:
        for alan in ("kurum", "soru", "ilke", "kunye"):
            if not veri.get(alan):
                raise SystemExit(f"HATA: '{alan}' alani bos.")
        ciz_kart(veri, dosyalar, a[1])
    print("Kart olusturuldu:", a[1])


if __name__ == "__main__":
    main()
