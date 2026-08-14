# YOLO11n Smoke Test Sonucu

**Tarih:** 27 Temmuz 2026

- GPU: NVIDIA GeForce GTX 1650, 4 GB
- PyTorch: 2.11.0 + CUDA 12.8
- Ultralytics: 8.4.107
- Model: YOLO11n
- Eğitim örneklemi: birleşik train setinin %10'u
- Epoch: 5
- Görüntü boyutu: 512 px
- Batch: 4

## Son epoch metrikleri

| Metrik | Değer |
|---|---:|
| Precision | 0,561 |
| Recall | 0,242 |
| mAP50 | 0,231 |
| mAP50-95 | 0,136 |

Bu çalışma performans optimizasyonu değil; veri setinin, etiketlerin, CUDA ortamının ve eğitim pipeline'ının uçtan uca çalıştığını doğrulayan kısa bir testtir.

## Sınıf bazlı son validasyon

| Sınıf | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| forklift | 0,339 | 0,343 | 0,346 | 0,222 |
| person | 0,534 | 0,283 | 0,286 | 0,159 |
| pallet | 0,375 | 0,340 | 0,292 | 0,160 |
| pallet_truck | 1,000 | 0,000 | 0,002 | 0,001 |

`pallet_truck` sınıfı az örnekli olduğu için kısa testte öğrenilemedi. Tam eğitim sonrasında sınıf bazlı sonuç yeniden değerlendirilmelidir.
