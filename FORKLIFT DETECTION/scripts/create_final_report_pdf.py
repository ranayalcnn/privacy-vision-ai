from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output/pdf"
OUTPUT = OUTPUT_DIR / "forklift_detection_final_raporu.pdf"
CONTACT_SHEET = ROOT / "reports/multi_video_selected_contact_sheet.jpg"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2E74B5")
LIGHT_BLUE = colors.HexColor("#E8F1F8")
LIGHT_GRAY = colors.HexColor("#F3F5F7")
MID_GRAY = colors.HexColor("#667085")
GREEN = colors.HexColor("#147D64")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "ReportTitle",
            fontName="Arial-Bold",
            fontSize=27,
            leading=32,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            "Subtitle",
            fontName="Arial",
            fontSize=13,
            leading=18,
            textColor=MID_GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "H1x",
            fontName="Arial-Bold",
            fontSize=16,
            leading=20,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "H2x",
            fontName="Arial-Bold",
            fontSize=12,
            leading=15,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            "Bodyx",
            fontName="Arial",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#202124"),
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            "Smallx",
            fontName="Arial",
            fontSize=8,
            leading=11,
            textColor=MID_GRAY,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "Metric",
            fontName="Arial-Bold",
            fontSize=19,
            leading=22,
            textColor=GREEN,
            alignment=TA_CENTER,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            "MetricLabel",
            fontName="Arial",
            fontSize=8,
            leading=10,
            textColor=MID_GRAY,
            alignment=TA_CENTER,
        )
    )
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFont("Arial", 8)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(2 * cm, height - 1.15 * cm, "Forklift Detection - Teknik Sonuç Raporu")
    canvas.drawRightString(width - 2 * cm, 1.05 * cm, f"Sayfa {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#D7DEE5"))
    canvas.line(2 * cm, height - 1.35 * cm, width - 2 * cm, height - 1.35 * cm)
    canvas.restoreState()


def styled_table(data, widths, header=True, font_size=8.5):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5DF")),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, LIGHT_GRAY]),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ]
    table.setStyle(TableStyle(commands))
    return table


def bullet(text, styles):
    return Paragraph(f"• {text}", styles["Bodyx"])


def build() -> None:
    register_fonts()
    styles = make_styles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.75 * cm,
        bottomMargin=1.6 * cm,
        title="Forklift Detection Teknik Sonuç Raporu",
        author="Forklift Detection Projesi",
    )
    story = []

    story += [
        Spacer(1, 3.1 * cm),
        Paragraph("FORKLIFT DETECTION", styles["ReportTitle"]),
        Paragraph("Veri Araştırması, Model Eğitimi ve Nesne Takibi", styles["Subtitle"]),
        Spacer(1, 0.6 * cm),
    ]
    metrics = Table(
        [
            [
                Paragraph("6.805", styles["Metric"]),
                Paragraph("%89,4", styles["Metric"]),
                Paragraph("%89,5", styles["Metric"]),
            ],
            [
                Paragraph("Eğitim görüntüsü", styles["MetricLabel"]),
                Paragraph("Forklift mAP50", styles["MetricLabel"]),
                Paragraph("İnsan mAP50", styles["MetricLabel"]),
            ],
        ],
        colWidths=[5.2 * cm] * 3,
    )
    metrics.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#B8CEE0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3E1EC")),
                ("TOPPADDING", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ]
        )
    )
    story += [
        metrics,
        Spacer(1, 1.2 * cm),
        Paragraph("Proje Özeti", styles["H1x"]),
        Paragraph(
            "Bu çalışma; açık kaynak forklift veri setlerinin araştırılması, uygun kaynakların "
            "birleştirilmesi, YOLO tabanlı nesne algılama modelinin eğitilmesi ve ByteTrack ile "
            "video üzerinde takip yapılmasını kapsamaktadır. Nihai model forklift ve insan "
            "sınıflarında güçlü sonuç üretmiş, örnek video çıktısı teslim edilmiştir.",
            styles["Bodyx"],
        ),
        Paragraph("<b>Nihai çözüm:</b> YOLO11s + ByteTrack", styles["Bodyx"]),
        Paragraph("<b>Tarih:</b> 28 Temmuz 2026", styles["Bodyx"]),
        PageBreak(),
    ]

    story += [Paragraph("1. Veri Kaynakları ve Araştırma", styles["H1x"])]
    source_data = [
        ["Kaynak", "Platform", "Görüntü", "Lisans", "Karar"],
        ["Forklift v1", "Roboflow", "4.474", "Public Domain", "Ana kaynak"],
        ["Warehouse", "Roboflow", "5.183", "Public Domain", "Ana kaynak"],
        ["1000ware v4", "Roboflow", "1.083", "Public Domain", "Ana kaynak"],
        ["LOCO v1", "Roboflow", "1.128", "Public Domain", "Yardımcı"],
        ["Forklift Object Detection", "Hugging Face", "421", "CC BY 4.0", "Ana kaynak"],
    ]
    story += [
        styled_table(source_data, [4.4 * cm, 2.8 * cm, 2 * cm, 2.8 * cm, 3.7 * cm]),
        Spacer(1, 0.35 * cm),
        Paragraph(
            "Ham veri toplamı 12.289 görüntüdür. Lisansı belirsiz Kaggle ve GitHub kaynakları "
            "araştırma envanterine alınmış ancak eğitime dahil edilmemiştir.",
            styles["Smallx"],
        ),
        Paragraph("2. Veri Hazırlama", styles["H1x"]),
    ]
    prep_data = [
        ["İşlem", "Sonuç"],
        ["Ham görüntü", "12.289"],
        ["Silinen kesin kopya", "80"],
        ["Tutulan negatif görüntü", "500"],
        ["Temel temiz veri", "7.871"],
        ["Temel bölünüm", "6.366 train / 748 val / 757 test"],
        ["Çoklu video eklemesi", "129 pozitif + 100 negatif"],
        ["Nihai eğitim görüntüsü", "6.805"],
    ]
    story += [
        styled_table(prep_data, [8.7 * cm, 7 * cm]),
        Paragraph("Hedef sınıflar", styles["H2x"]),
        bullet("forklift: 6.389 örnek", styles),
        bullet("person: 4.466 örnek", styles),
        bullet("pallet: 31.206 örnek", styles),
        bullet("pallet_truck: 717 örnek", styles),
        PageBreak(),
    ]

    story += [
        Paragraph("3. Video Tabanlı Zor Örnek Geliştirmesi", styles["H1x"]),
        Paragraph(
            "Pexels üzerinde ücretsiz kullanıma açık beş farklı forklift videosu seçildi. "
            "Dış mekân, depo koridoru, önden ve yandan görünüm, farklı renkler, operatör ve "
            "palet etkileşimi gibi koşullar kapsandı. Her videodan hareket ve netlik puanına "
            "göre 120 kare seçilerek 600 aday kare oluşturuldu.",
            styles["Bodyx"],
        ),
    ]
    if CONTACT_SHEET.exists():
        image = Image(str(CONTACT_SHEET), width=16.7 * cm, height=3.13 * cm)
        story += [
            image,
            Paragraph("Şekil 1. Beş farklı videodan seçilen örnek kareler.", styles["Smallx"]),
        ]
    story += [
        Paragraph("Ön etiket temizleme", styles["H2x"]),
        bullet("Düşük güvenli ve aşırı büyük kutular reddedildi.", styles),
        bullet("0,30 güven eşiği ve kutu geometrisi filtreleri uygulandı.", styles),
        bullet("129 yüksek güvenli pozitif ve 100 dengeli negatif kare eğitime eklendi.", styles),
        Paragraph("4. Eğitim Süreci", styles["H1x"]),
    ]
    train_data = [
        ["Aşama", "Model", "Epoch / Veri", "Genel mAP50"],
        ["Hızlı temel model", "YOLO11n", "10 epoch / %25", "0,526"],
        ["Zor örnek fine-tune", "YOLO11n", "10 epoch", "0,545"],
        ["Nihai model", "YOLO11s", "8 epoch / %50", "0,564"],
    ]
    story += [
        styled_table(train_data, [4.3 * cm, 3.3 * cm, 4.7 * cm, 3.4 * cm]),
        Spacer(1, 0.3 * cm),
        Paragraph(
            "Eğitim NVIDIA GeForce GTX 1650 (4 GB) üzerinde 512 piksel giriş boyutu ve "
            "batch 4 ile gerçekleştirilmiştir. Nihai model, daha güçlü YOLO11s mimarisi "
            "ve çoklu video örnekleri sayesinde önceki sürümü geçmiştir.",
            styles["Bodyx"],
        ),
        PageBreak(),
    ]

    story += [
        Paragraph("5. Nihai Sonuçlar", styles["H1x"]),
    ]
    result_data = [
        ["Sınıf", "Precision", "Recall", "mAP50", "mAP50-95"],
        ["Forklift", "0,816", "0,883", "0,894", "0,779"],
        ["Person", "0,864", "0,855", "0,895", "0,560"],
        ["Pallet", "0,893", "0,410", "0,465", "0,300"],
        ["Pallet truck", "0,000", "0,000", "0,000", "0,000"],
        ["Genel", "0,643", "0,535", "0,564", "0,410"],
    ]
    story += [
        styled_table(result_data, [4.2 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm, 3.1 * cm]),
        Spacer(1, 0.4 * cm),
        Paragraph(
            "<b>Değerlendirme:</b> Ana hedefler olan forklift ve insan sınıflarında mAP50 "
            "yaklaşık %89,5 düzeyindedir. Palet kamyonu sınıfında örnek sayısı ve çeşitlilik "
            "yetersiz kaldığı için bu sınıf üretim kullanımına hazır değildir.",
            styles["Bodyx"],
        ),
        Paragraph("6. Takip ve Demo", styles["H1x"]),
        Paragraph(
            "Nesne takibi ByteTrack ile uygulanmıştır. Kısa süreli algılama kayıpları için "
            "kutu yumuşatma ve kısa boşluk koruması kullanılmış, ID sıçramalarında anlamsız "
            "çizgiler oluşmaması için hareket izi çizimi kapatılmıştır.",
            styles["Bodyx"],
        ),
        Paragraph("7. Sonuç ve Öneriler", styles["H1x"]),
        bullet("Ana görev tamamlanmış ve çalışan demo videosu üretilmiştir.", styles),
        bullet("Gerçek kamera videosu temin edildiğinde saha doğrulaması yapılmalıdır.", styles),
        bullet("Üretim için farklı depo/kamera koşullarından 2.000-5.000 doğrulanmış kare hedeflenmelidir.", styles),
        bullet("Pallet truck sınıfı kullanılacaksa bu sınıfa özel yeni veri toplanmalıdır.", styles),
        Paragraph("Kaynak Bağlantıları", styles["H2x"]),
    ]
    links = [
        ("Roboflow Forklift v1", "https://universe.roboflow.com/forklift-4ulnu/forklift-uo0vm/dataset/1"),
        ("Roboflow Warehouse", "https://universe.roboflow.com/divya-tiwari-u2mrc/warehouse-vemit"),
        ("Roboflow 1000ware v4", "https://universe.roboflow.com/veeck/1000ware/dataset/4"),
        ("Roboflow LOCO v1", "https://universe.roboflow.com/new-workspace-e6ojy/loco-foum7/dataset/1"),
        ("Hugging Face Forklift Object Detection", "https://huggingface.co/datasets/keremberke/forklift-object-detection"),
        ("Pexels Forklift Videoları", "https://www.pexels.com/search/videos/forklift/"),
    ]
    for label, url in links:
        story.append(Paragraph(f'• <link href="{url}" color="#2E74B5">{label}</link>', styles["Smallx"]))

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
