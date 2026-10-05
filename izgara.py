# -*- coding: utf-8 -*-
"""
Dereli Avukatlik Burosu - Instagram izgara satiri (3 gonderi)

Her kare kendi icinde tamamlanan bir paneldir; hicbir yazi iki kareye tasmaz.
Gorunur alan 1080x1440 (3:4); yuklenen dosya 1152x1440 (4:5), iki yanda
Instagram'in izgarada kirpacagi 36 px pay vardir.

Kullanim:
  python3 izgara.py girdi.json CIKTI_KLASORU [--kaynak DEPO | --yerel KLASOR]
  (kart.py ayni klasorde olmalidir)

Triptik:   {"tur": "triptik", "kurum": "...", "alan": "...", "kunye": "...",
            "soru": "...", "ilke": "..."}
Kurumsal:  {"tur": "kurumsal", "baslik": "5 Nisan", "alt": "Avukatlar Gunu",
            "metin": "tek cumle"}

Cikti: 01_sag.jpg, 02_orta.jpg, 03_sol.jpg  (bu sirayla paylasilir)
"""
import io, json, os, sys
from PIL import Image, ImageDraw
import kart as K

GW, GH = 1080, 1440        # izgarada gorunen alan
PAY = 36                   # her yanda kirpma payi
UW = GW + 2 * PAY          # yuklenen genislik (1152)
IC = 110                   # panel ic boslugu
GEN = GW - 2 * IC
TAS = (102, 129, 126)


def tuval(renk):
    return Image.new("RGB", (GW, GH), renk)


def kaydet(panel, zemin, yol):
    up = Image.new("RGB", (UW, GH), zemin)
    up.paste(panel, (PAY, 0))
    up.save(yol, "JPEG", quality=95, subsampling=0)


def mark_yapistir(img, f, yuk, y, renk="kagit"):
    mark = Image.open(io.BytesIO(f["mark"])).convert("RGBA")
    if renk == "petrol":
        r, g, b, a = mark.split()
        mark = Image.merge("RGBA", (r.point(lambda _: K.PETROL[0]), g.point(lambda _: K.PETROL[1]),
                                    b.point(lambda _: K.PETROL[2]), a))
    mark = mark.resize((round(mark.width * yuk / mark.height), yuk), Image.LANCZOS)
    img.paste(mark, ((GW - mark.width) // 2, y), mark)


def sigdir(c, metin, font_veri, agirlik, buyuk, kucuk, satir_kat, yukseklik):
    for boy in range(buyuk, kucuk - 1, -4):
        f = K.yazi_tipi(font_veri, boy, agirlik)
        s = K.satirla(c, metin, f, GEN)
        if len(s) * round(boy * satir_kat) <= yukseklik:
            return f, s, round(boy * satir_kat)
    raise SystemExit("HATA: metin panele sigmiyor; kisaltin.")


def ortala_yaz(c, satirlar, font, lh, renk, y_merkez):
    y = y_merkez - len(satirlar) * lh / 2
    for s in satirlar:
        c.text((GW / 2, y), s, font=font, fill=renk, anchor="ma")
        y += lh


def triptik(v, f):
    # Sol: kurum + alan + kunye (petrol)
    sol = tuval(K.PETROL); c = ImageDraw.Draw(sol)
    mark_yapistir(sol, f, 110, 260)
    fk = K.yazi_tipi(f["cinzel"], 50, 600)
    y = 520
    for s in K.satirla(c, K.tr_buyuk(v["kurum"]), fk, GEN, 3):
        K.aralikli_yaz(c, (GW / 2, y), s, fk, K.KAGIT, 3); y += 70
    if v.get("alan"):
        y += 20
        K.aralikli_yaz(c, (GW / 2, y), K.tr_buyuk(v["alan"]), K.yazi_tipi(f["cinzel"], 34, 500), K.KAGIT_SOLUK, 5); y += 60
    y += 40
    c.line([(GW / 2 - 60, y), (GW / 2 + 60, y)], fill=K.KAGIT_SOLUK, width=2); y += 50
    fkn = K.yazi_tipi(f["garamond"], 40, 400)
    for s in K.satirla(c, v["kunye"], fkn, GEN):
        c.text((GW / 2, y), s, font=fkn, fill=K.KAGIT_SOLUK, anchor="ma"); y += 54
    if y > GH - 120:
        raise SystemExit("HATA: sol panel sigmiyor.")

    # Orta: soru (kagit zemin)
    orta = tuval(K.KAGIT); c = ImageDraw.Draw(orta)
    fs, ss, lh = sigdir(c, v["soru"], f["garamond_italik"], 400, 76, 48, 1.3, GH - 2 * 260)
    ortala_yaz(c, ss, fs, lh, K.PETROL, GH / 2)

    # Sag: ilke (petrol)
    sag = tuval(K.PETROL); c = ImageDraw.Draw(sag)
    fi, si, lh = sigdir(c, v["ilke"], f["garamond"], 600, 72, 46, 1.3, GH - 2 * 260)
    ortala_yaz(c, si, fi, lh, K.KAGIT, GH / 2)
    return (sol, K.PETROL), (orta, K.KAGIT), (sag, K.PETROL)


def kurumsal(v, f):
    sol = tuval(K.PETROL); c = ImageDraw.Draw(sol)
    mark_yapistir(sol, f, 300, GH // 2 - 230)
    K.aralikli_yaz(c, (GW / 2, GH // 2 + 140), "DERELİ", K.yazi_tipi(f["cinzel"], 72, 600), K.KAGIT, 10)
    K.aralikli_yaz(c, (GW / 2, GH // 2 + 250), "AVUKATLIK BÜROSU", K.yazi_tipi(f["cinzel"], 34, 500), K.KAGIT_SOLUK, 8)

    orta = tuval(K.KAGIT); c = ImageDraw.Draw(orta)
    fb, sb, lh = sigdir(c, K.tr_buyuk(v["baslik"]), f["cinzel"], 600, 120, 64, 1.2, 520)
    y = GH / 2 - (len(sb) * lh) / 2 - (40 if v.get("alt") else 0)
    for s in sb:
        K.aralikli_yaz(c, (GW / 2, y), s, fb, K.PETROL, 4); y += lh
    if v.get("alt"):
        y += 30
        fa, sa, lha = sigdir(c, K.tr_buyuk(v["alt"]), f["cinzel"], 500, 46, 30, 1.3, 200)
        for s in sa:
            K.aralikli_yaz(c, (GW / 2, y), s, fa, TAS, 5); y += lha

    sag = tuval(K.PETROL); c = ImageDraw.Draw(sag)
    fm, sm, lh = sigdir(c, v["metin"], f["garamond_italik"], 400, 64, 42, 1.35, GH - 2 * 300)
    ortala_yaz(c, sm, fm, lh, K.KAGIT, GH / 2)
    return (sol, K.PETROL), (orta, K.KAGIT), (sag, K.PETROL)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    kaynak, yerel = K.VARSAYILAN_KAYNAK, None
    if "--kaynak" in a:
        kaynak = a[a.index("--kaynak") + 1]
    if "--yerel" in a:
        yerel = a[a.index("--yerel") + 1]
    v = json.load(open(a[0], encoding="utf-8"))
    f = {k: K.oku(kaynak, yerel, p) for k, p in K.DOSYALAR.items()}
    if v.get("tur") == "triptik":
        for alan in ("kurum", "kunye", "soru", "ilke"):
            if not v.get(alan):
                raise SystemExit(f"HATA: '{alan}' bos.")
        sol, orta, sag = triptik(v, f)
    elif v.get("tur") == "kurumsal":
        for alan in ("baslik", "metin"):
            if not v.get(alan):
                raise SystemExit(f"HATA: '{alan}' bos.")
        sol, orta, sag = kurumsal(v, f)
    else:
        raise SystemExit("HATA: tur 'triptik' veya 'kurumsal' olmali.")
    os.makedirs(a[1], exist_ok=True)
    for ad, (panel, zemin) in (("01_sag", sag), ("02_orta", orta), ("03_sol", sol)):
        kaydet(panel, zemin, os.path.join(a[1], ad + ".jpg"))
    print("Izgara satiri olusturuldu:", a[1], "(01_sag, 02_orta, 03_sol sirasiyla paylasin)")


if __name__ == "__main__":
    main()
