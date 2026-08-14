# Birleşik Forklift Veri Seti — Hazırlama Özeti

**Hazırlama tarihi:** 27 Temmuz 2026

## Sonuç

Beş kaynaktan alınan 12.289 görüntü ortak YOLO sınıf şemasına dönüştürüldü.

- Birebir aynı dosya: 80 görüntü kaldırıldı.
- Hedef sınıf içermeyen görüntüler: 4.838 adet bulundu; eğitim dengesini korumak için deterministik seçilen 500 negatif görüntü tutuldu.
- Yakın benzer adayı: 4.353 görüntü belirlendi ancak yanlış veri kaybını önlemek için otomatik silinmedi.
- Nihai veri seti: **7.871 görüntü**

## Split dağılımı

| Split | Görüntü | Boş/negatif etiket |
|---|---:|---:|
| Train | 6.366 | 411 |
| Validation | 748 | 43 |
| Test | 757 | 46 |
| **Toplam** | **7.871** | **500** |

## Nesne örneği dağılımı

| Sınıf | Bounding box |
|---|---:|
| forklift | 6.389 |
| person | 4.466 |
| pallet | 31.206 |
| pallet_truck | 717 |
| **Toplam** | **42.778** |

## Kalite kontrol sonucu

- Her görüntünün karşılık gelen YOLO etiket dosyası var.
- Sınıf ID’lerinin tamamı `0–3` aralığında.
- Bounding-box koordinatlarının tamamı `0–1` aralığında.
- Sıfır veya negatif boyutlu kutu yok.
- Bozuk/okunamayan görüntü yok.
- Split’ler arasında birebir aynı görüntü yok.
- Otomatik doğrulama sonucu: **başarılı**

## Sınıf şeması

```text
0: forklift
1: person
2: pallet
3: pallet_truck
```

## Dosyalar

- Dataset yapılandırması: `data/processed/data.yaml`
- Eğitim yapılandırması: `configs/train_yolo11n.yaml`
- Hazırlama scripti: `scripts/prepare_dataset.py`
- Doğrulama scripti: `scripts/validate_dataset.py`
- Makine tarafından okunabilir hazırlama raporu: `reports/dataset_preparation_report.json`
- Makine tarafından okunabilir doğrulama raporu: `reports/dataset_validation_report.json`

## Eğitim öncesi not

`pallet` sınıfı diğer sınıflardan belirgin şekilde daha fazla örneğe sahiptir. İlk baseline deneyinden sonra sınıf bazlı precision/recall incelenmeli; gerekirse palet yoğun görüntülere örnekleme sınırı uygulanmalıdır.
