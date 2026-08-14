# Forklift Detection

Forklift, insan, palet ve palet taşıma aracı tespiti için veri hazırlama ve model eğitimi projesi.

## Klasörler

- `data/raw/`: İndirilen veri setlerinin değiştirilmemiş halleri
- `data/interim/`: Format dönüşümü ve kalite kontrolü yapılan ara veriler
- `data/processed/`: Birleştirilmiş YOLO veri seti
- `configs/`: Eğitim ve veri seti ayarları
- `scripts/`: İndirme, dönüştürme, deduplikasyon ve eğitim betikleri
- `models/`: Eğitilmiş model ağırlıkları
- `runs/`: Eğitim ve değerlendirme çıktıları
- `reports/`: Araştırma, kalite kontrolü ve deney raporları

## Hedef sınıflar

```text
0: forklift
1: person
2: pallet
3: pallet_truck
```

## Güncel durum

- Beş açık kaynak veri seti indirildi: 12.289 ham görüntü.
- Ortak sınıf şemasıyla birleştirilmiş ve doğrulanmış YOLO veri seti hazırlandı.
- Nihai veri seti: 7.871 görüntü ve 42.778 bounding box.
- Otomatik kalite kontrolü başarılı.

Sıradaki aşama gerekli Python paketlerini kurarak YOLO11n baseline eğitimini başlatmaktır.
