from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/forklift_detection_modern_ozet.pdf"

W, H = A4
INK = colors.HexColor("#12212F")
MUTED = colors.HexColor("#647180")
ACCENT = colors.HexColor("#246BFD")
SOFT = colors.HexColor("#F3F6FA")
LINE = colors.HexColor("#DCE3EA")
GREEN = colors.HexColor("#0E8A6A")
WHITE = colors.white


def fonts():
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))


def text(c, value, x, y, size=10, color=INK, font="Arial"):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, value)


def wrapped(c, value, x, y, max_width, size=10, leading=15, color=INK):
    words = value.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(candidate, "Arial", size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        text(c, line, x, y, size, color)
        y -= leading
    return y


def rounded(c, x, y, width, height, fill, radius=10, stroke=None):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1 if stroke else 0)


def metric_card(c, x, y, width, value, label):
    rounded(c, x, y, width, 2.25 * cm, SOFT, 8, LINE)
    text(c, value, x + 0.42 * cm, y + 1.28 * cm, 20, GREEN, "Arial-Bold")
    text(c, label, x + 0.42 * cm, y + 0.58 * cm, 8.5, MUTED)


def section_title(c, number, title_value, x, y):
    rounded(c, x, y - 2, 0.7 * cm, 0.7 * cm, ACCENT, 7)
    text(c, number, x + 0.23 * cm, y + 0.14 * cm, 9, WHITE, "Arial-Bold")
    text(c, title_value, x + 1.0 * cm, y + 0.08 * cm, 13, INK, "Arial-Bold")


def footer(c, page):
    c.setStrokeColor(LINE)
    c.line(1.7 * cm, 1.35 * cm, W - 1.7 * cm, 1.35 * cm)
    text(c, "Forklift Detection", 1.7 * cm, 0.85 * cm, 8, MUTED)
    c.setFont("Arial", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, 0.85 * cm, f"{page} / 2")


def page_one(c):
    margin = 1.7 * cm
    rounded(c, margin, H - 2.0 * cm, 3.2 * cm, 0.65 * cm, ACCENT, 8)
    text(c, "TEKNİK ÖZET", margin + 0.35 * cm, H - 1.58 * cm, 8.5, WHITE, "Arial-Bold")
    text(c, "Forklift Detection", margin, H - 3.25 * cm, 28, INK, "Arial-Bold")
    text(c, "YOLO11s + ByteTrack ile algılama ve takip", margin, H - 4.0 * cm, 12, MUTED)

    gap = 0.35 * cm
    card_w = (W - 2 * margin - 2 * gap) / 3
    card_y = H - 7.0 * cm
    metric_card(c, margin, card_y, card_w, "6.805", "Eğitim görüntüsü")
    metric_card(c, margin + card_w + gap, card_y, card_w, "89,4%", "Forklift mAP50")
    metric_card(c, margin + 2 * (card_w + gap), card_y, card_w, "89,5%", "İnsan mAP50")

    section_title(c, "1", "Proje amacı", margin, H - 8.35 * cm)
    wrapped(
        c,
        "Açık kaynak forklift veri setlerini birleştirmek, güçlü bir nesne algılama modeli "
        "eğitmek ve forklift ile insanları video üzerinde kararlı biçimde takip etmek.",
        margin,
        H - 9.15 * cm,
        W - 2 * margin,
        10,
        15,
        INK,
    )

    section_title(c, "2", "Uygulanan yaklaşım", margin, H - 11.0 * cm)
    pipeline_y = H - 14.8 * cm
    items = [
        ("01", "Araştırma", "Roboflow, Hugging Face ve Pexels kaynakları"),
        ("02", "Veri hazırlama", "Tekrar temizleme, sınıf eşleme ve bölme"),
        ("03", "Eğitim", "YOLO11s, 512 px, 8 epoch, GTX 1650"),
        ("04", "Takip", "ByteTrack, kutu yumuşatma ve ID koruma"),
    ]
    item_w = (W - 2 * margin - 3 * gap) / 4
    for i, (num, title_value, desc) in enumerate(items):
        x = margin + i * (item_w + gap)
        rounded(c, x, pipeline_y, item_w, 3.25 * cm, WHITE, 9, LINE)
        text(c, num, x + 0.35 * cm, pipeline_y + 2.45 * cm, 9, ACCENT, "Arial-Bold")
        text(c, title_value, x + 0.35 * cm, pipeline_y + 1.72 * cm, 10, INK, "Arial-Bold")
        wrapped(c, desc, x + 0.35 * cm, pipeline_y + 1.15 * cm, item_w - 0.7 * cm, 7.7, 10, MUTED)

    rounded(c, margin, 6.25 * cm, W - 2 * margin, 2.2 * cm, SOFT, 9)
    text(c, "DEMO HAZIR", margin + 0.45 * cm, 7.72 * cm, 8, ACCENT, "Arial-Bold")
    text(
        c,
        "YOLO11s + ByteTrack ile çizgisiz takip videosu teslim edildi.",
        margin + 0.45 * cm,
        7.05 * cm,
        10,
        INK,
        "Arial-Bold",
    )
    text(
        c,
        "Dosya: forklift_yolo11s_gelistirilmis_takip.mp4",
        margin + 0.45 * cm,
        6.57 * cm,
        8.5,
        MUTED,
    )
    footer(c, 1)


def page_two(c):
    margin = 1.7 * cm
    text(c, "Sonuçlar ve teslim özeti", margin, H - 2.1 * cm, 22, INK, "Arial-Bold")
    text(c, "Nihai model, önceki YOLO11n sürümünü geçti.", margin, H - 2.85 * cm, 10.5, MUTED)

    section_title(c, "3", "Veri özeti", margin, H - 4.15 * cm)
    table_x, table_y = margin, H - 8.0 * cm
    table_w = W - 2 * margin
    row_h = 0.72 * cm
    rows = [
        ("Ham veri", "12.289 görüntü"),
        ("Temiz temel veri", "7.871 görüntü"),
        ("Nihai eğitim", "6.805 görüntü"),
        ("Video geliştirmesi", "5 video - 600 aday kare"),
        ("Eğitime eklenen", "129 pozitif + 100 negatif"),
    ]
    for i, (label, value) in enumerate(rows):
        y = table_y + (len(rows) - 1 - i) * row_h
        c.setFillColor(SOFT if i % 2 else WHITE)
        c.rect(table_x, y, table_w, row_h, fill=1, stroke=0)
        c.setStrokeColor(LINE)
        c.line(table_x, y, table_x + table_w, y)
        text(c, label, table_x + 0.35 * cm, y + 0.24 * cm, 9, MUTED)
        text(c, value, table_x + 7.7 * cm, y + 0.24 * cm, 9, INK, "Arial-Bold")
    c.setStrokeColor(LINE)
    c.rect(table_x, table_y, table_w, len(rows) * row_h, fill=0, stroke=1)

    section_title(c, "4", "Model performansı", margin, H - 9.3 * cm)
    headers = ["Sınıf", "Precision", "Recall", "mAP50", "mAP50-95"]
    values = [
        ["Forklift", "0,816", "0,883", "0,894", "0,779"],
        ["İnsan", "0,864", "0,855", "0,895", "0,560"],
        ["Genel", "0,643", "0,535", "0,564", "0,410"],
    ]
    col_w = (W - 2 * margin) / 5
    top = H - 10.15 * cm
    c.setFillColor(INK)
    c.roundRect(margin, top - 0.72 * cm, W - 2 * margin, 0.72 * cm, 6, fill=1, stroke=0)
    for i, header in enumerate(headers):
        text(c, header, margin + i * col_w + 0.25 * cm, top - 0.46 * cm, 8, WHITE, "Arial-Bold")
    for row_i, row in enumerate(values):
        y = top - (row_i + 2) * 0.72 * cm
        c.setFillColor(SOFT if row_i % 2 else WHITE)
        c.rect(margin, y, W - 2 * margin, 0.72 * cm, fill=1, stroke=0)
        for col_i, value in enumerate(row):
            text(
                c,
                value,
                margin + col_i * col_w + 0.25 * cm,
                y + 0.24 * cm,
                8.5,
                GREEN if col_i == 3 else INK,
                "Arial-Bold" if col_i in (0, 3) else "Arial",
            )

    section_title(c, "5", "Teslim durumu", margin, H - 14.4 * cm)
    checks = [
        "Açık kaynak araştırması ve kaynak envanteri tamamlandı.",
        "Veri setleri birleştirildi ve doğrulandı.",
        "YOLO11s modeli eğitildi; ByteTrack entegrasyonu yapıldı.",
        "Çizgisiz demo videosu ve en iyi model ağırlığı hazırlandı.",
    ]
    y = H - 15.25 * cm
    for item in checks:
        c.setFillColor(GREEN)
        c.circle(margin + 0.16 * cm, y + 0.08 * cm, 0.13 * cm, fill=1, stroke=0)
        text(c, item, margin + 0.55 * cm, y, 9.5, INK)
        y -= 0.72 * cm

    rounded(c, margin, 3.2 * cm, W - 2 * margin, 2.15 * cm, SOFT, 9)
    text(c, "SONRAKİ ADIM", margin + 0.45 * cm, 4.68 * cm, 8, ACCENT, "Arial-Bold")
    wrapped(
        c,
        "Gerçek kamera videosu temin edildiğinde saha testi yapılmalı. Üretim kullanımı için "
        "farklı kamera ve depo koşullarından doğrulanmış yeni kareler eklenmelidir.",
        margin + 0.45 * cm,
        4.15 * cm,
        W - 2 * margin - 0.9 * cm,
        9.5,
        14,
        INK,
    )
    footer(c, 2)


def main():
    fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Forklift Detection - Modern Özet")
    c.setAuthor("Forklift Detection Projesi")
    page_one(c)
    c.showPage()
    page_two(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
