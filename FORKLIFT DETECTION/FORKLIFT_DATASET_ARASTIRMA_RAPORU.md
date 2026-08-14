# Forklift Detection — Açık Kaynak Veri Seti Araştırma Raporu

**Araştırma tarihi:** 27 Temmuz 2026  
**Amaç:** Forklift nesne tespiti modeli için açık kaynak görüntü veri setlerini bulmak, kullanılabilirliklerini karşılaştırmak ve ortak bir eğitim veri seti oluşturma planı hazırlamak.

## Yönetici özeti

İlk eğitim için en güçlü ve lisans bilgisi açık kaynaklar:

1. **Forklift (Roboflow, forklift-4ulnu):** İndirilebilir v1 sürümünde 4.474 görüntü; `forklift` ve `person`; Public Domain.
2. **Warehouse (Roboflow):** Proje genelinde 5.183 görüntü; forklift, person, palletjack, pallets, stillage vb.; Public Domain.
3. **LOCO (Roboflow kopyası):** İndirilen v1 paketinde 1.128 görüntü; Forklift, Pallet, Pallet_truck, Small_load_carrier, Stillage; Public Domain.
4. **1000ware (Roboflow):** İndirilen v4 paketinde 1.083 görüntü; Box, ForkLift, Human ve Pallet; Public Domain.
5. **Forklift Object Detection (Hugging Face/Roboflow):** 421 görüntü; forklift ve person; CC BY 4.0.

İndirilen beş kaynağın doğrulanan toplamı **12.289 görüntüdür**. Ancak bu sayı kesin benzersiz görüntü sayısı değildir: Roboflow forkları/kopyaları ve farklı sürümler arasında tekrar bulunabilir. Eğitim öncesi perceptual-hash ile kopya temizliği zorunludur.

## Veri seti envanteri

| # | Veri seti | Platform | Görüntü sayısı | Sınıflar | Etiket/format | Lisans | Karar |
|---|---|---|---:|---|---|---|---|
| 1 | [Forklift v1](https://universe.roboflow.com/forklift-4ulnu/forklift-uo0vm/dataset/1) | Roboflow | **4.474 indirilebilir** (3.132 train / 896 valid / 446 test). Proje arayüzü 6.375 kaynak görüntü gösteriyor. | forklift, person | YOLO/COCO/VOC/TFRecord vb. dışa aktarım | Public Domain | **Ana kaynak** |
| 2 | [Warehouse](https://universe.roboflow.com/divya-tiwari-u2mrc/warehouse-vemit) | Roboflow | **5.183 proje görüntüsü**; model v3 sayfasında augmentasyonla 8.655 görüntü | forklift, person, palletjack, palletkack, pallets, stillage, `a` | Object detection; Roboflow dışa aktarımı | Public Domain | **Ana kaynak**, bozuk/tekrarlı sınıf adları düzeltilmeli |
| 3 | [1000ware](https://universe.roboflow.com/veeck/1000ware) | Roboflow | **1.276 proje görüntüsü**; indirilen v4 sürümü **1.083** (757 train / 222 valid / 104 test) | v4: Box, ForkLift, Human, Pallet | YOLOv8 | Public Domain | **Ana/yardımcı**, sınıflar birleştirilmeli |
| 4 | [LOCO](https://universe.roboflow.com/new-workspace-e6ojy/loco-foum7) | Roboflow | **1.128 indirilen v1** (788 train / 227 valid / 113 test); proje özeti 1.075 gösteriyor | Forklift, Pallet, Pallet_truck, Small_load_carrier, Stillage | YOLOv8 | Public Domain (Roboflow sayfası) | **Yardımcı**, orijinal kaynakla lisans/provenans kontrolü önerilir |
| 5 | [Forklift Object Detection](https://huggingface.co/datasets/keremberke/forklift-object-detection) | Hugging Face / Roboflow | **421** (295 train / 84 valid / 42 test) | forklift, person | COCO; HF `datasets` ile doğrudan yüklenebilir | **CC BY 4.0** | **Ana kaynak**, atıf kaydı tutulmalı |
| 6 | [Fahrzeuge](https://universe.roboflow.com/test-workspace-2m4il/fahrzeuge-xxfte) | Roboflow | **800** | forklift | Object detection | Public Domain | **Yardımcı**, kalite örneklemesi gerekli |
| 7 | [Forkliftdetection](https://universe.roboflow.com/opop/forkliftdetection) | Roboflow | **84** | forklift, person, forklift-side | Object detection | Public Domain | Küçük yardımcı kaynak |
| 8 | [YOLO - forklift](https://universe.roboflow.com/rhenan-nfpl8/yolo-forklift) | Roboflow | **126 proje görüntüsü**; eğitilen v3 sürümü 116 görüntü | forklift | Object detection | Public Domain | Küçük yardımcı kaynak |
| 9 | [Industrial Object Detection](https://www.kaggle.com/datasets/walidguirat/industrial-object-detection) | Kaggle | v2: **2.173 toplam**; forklift sınıfı **1.325 görüntü** | forklift, conveyor belt, industrial pallet, industrial shredder | YOLOv5 | **Belirsiz** | Lisans netleşmeden eğitime katma |
| 10 | [Forklift and People Detection](https://github.com/SelimSavas/forklift-and-people-detection-with-YOLOv5) | GitHub / Drive | **3.000** | forklift, person | YOLOv5 | **Belirtilmemiş** | Lisans/özgün kaynak izni netleşmeden kullanma |
| 11 | [SORDI.ai](https://sordi.ai/home) | SORDI / Kaggle | Tüm koleksiyon **1,5M+ sentetik görüntü**; forklift alt kümesi sayısı ana sayfada belirtilmiyor | Endüstriyel nesneler ve senaryolar | 2D, point cloud ve metadata | Site “open source” diyor; paket lisansı ayrıca kontrol edilmeli | Forklift alt kümesi ve lisans dosyası doğrulanırsa güçlü sentetik destek |
| 12 | [DoFOS](https://www.kaggle.com/datasets/amirberenji/dofos-detection-of-forklift-operating-state/data) | Kaggle | Görüntü değil; **639 zaman serisi gözlemi** | 7 forklift çalışma durumu | Üç eksenli ivme verisi | CC0-1.0 | Görsel detection için uygun değil |

## Kritik notlar

- **Aynı görüntülerin tekrar kullanılması olasıdır.** Özellikle Roboflow forkları, Hugging Face kopyaları ve GitHub projeleri ortak kök veri taşıyabilir.
- **Augmente edilmiş görüntüler ham görüntü sayısı gibi değerlendirilmemelidir.** Örneğin Warehouse v3’te 8.655 eğitim görüntüsü görünürken proje arayüzü 5.183 kaynak görüntü gösteriyor.
- **Public Domain etiketi tek başına görüntülerin tüm kaynak zincirini garanti etmez.** Ticari kullanım öncesi örnek bazlı provenans ve kullanım koşulu incelemesi yapılmalıdır.
- **Kaggle Industrial Object Detection** sayfasında lisans “Unknown” göründüğü için, yazılı izin veya açık lisans bulunmadan ana eğitim havuzuna alınmamalıdır.
- **GitHub 3.000 görüntülük set** ImageNet, Roboflow ve Kaggle’dan derlendiğini söylüyor; birleşik set için açık bir lisans sunmuyor.

## Birleştirme için önerilen sınıf şeması

İlk model için karmaşıklığı düşük tutmak üzere:

```yaml
names:
  0: forklift
  1: person
  2: pallet
  3: pallet_truck
```

Sınıf eşlemeleri:

| Kaynak etiketleri | Ortak etiket |
|---|---|
| forklift, Forklift, ForkLift, forklift-side | forklift |
| person, Human | person |
| pallet, pallets, industrial pallet | pallet |
| palletjack, palletkack, Pallet_truck | pallet_truck |

`forklift-side` etiketi gerçekten yalnızca yan görünüşü ifade ediyorsa ayrı sınıf değil, `forklift` sınıfına dönüştürülmelidir. `palletkack` açık bir yazım hatası gibi görünmektedir; görsel örnek kontrolünden sonra `pallet_truck` olarak eşlenmelidir.

## Önerilen uygulama planı

1. **Lisansı açık beş ana kaynağı indir:** Forklift v1, Warehouse, 1000ware, LOCO ve Hugging Face seti.
2. **Ham veriyi değişmeden sakla:** Her kaynak `data/raw/<source_name>/` altında ayrı tutulmalı.
3. **Formatları YOLO’ya çevir:** Tüm bounding-box etiketlerini aynı koordinat ve sınıf şemasına dönüştür.
4. **Kopyaları temizle:** Önce SHA-256 ile birebir, sonra pHash/CLIP benzerliği ile yakın kopyaları bul.
5. **Etiket kalite kontrolü yap:** Her kaynaktan rastgele en az 100 görüntü ve tüm küçük kutular incelenmeli.
6. **Split’i yeniden üret:** Aynı video/seri/kopya ailesi yalnızca tek split’te bulunmalı; öneri %80 train, %10 validation, %10 test.
7. **İki deney çalıştır:**  
   - Deney A: yalnız `forklift`  
   - Deney B: `forklift + person + pallet + pallet_truck`
8. **Başlangıç modeli:** YOLO11n veya YOLO11s, 640 px, pretrained ağırlık, 50–100 epoch; sonuçlara göre daha büyük modele geç.
9. **Şirket içi kamera verisiyle final fine-tune:** Açık kaynak veri başlangıç sağlar; gerçek kamera açısı, ışık ve forklift tipleri için yerel görüntü şarttır.

## ClickUp’a yapıştırılabilir kısa rapor

**Görev:** Forklift Detection açık kaynak dataset araştırması  
**Durum:** Araştırma tamamlandı, indirme/birleştirme bekliyor  
**Bulunan aday:** 12 kaynak  
**Önerilen ana kaynak:** 5 adet  
**İndirilen ana kaynakların doğrulanan toplamı:** 12.289 görüntü (deduplikasyon öncesi)  
**En büyük açık kaynak:** Roboflow Forklift v1 — 4.474 indirilebilir görüntü  
**Diğer ana kaynaklar:** Warehouse 5.183, 1000ware v4 1.083, LOCO v1 1.128, HF Forklift 421  
**Sınıflar:** forklift, person, pallet, pallet_truck  
**Risk:** Kaynaklar arası duplicate görüntüler; bazı setlerde belirsiz lisans ve bozuk sınıf isimleri  
**Sonraki adım:** Lisansı açık setleri indir, YOLO formatında birleştir, pHash ile deduplicate et, etiket QA yap, yeniden train/val/test split oluştur ve baseline YOLO eğitimi başlat.

## Kaynak doğrulama notu

Rakamlar 27 Temmuz 2026 tarihinde platformların görünen proje/veri seti sayfalarından alınmıştır. Dinamik platformlarda proje toplamı, dataset sürümü ve augmentasyonlu sürüm sayıları farklı olabilir; bu nedenle indirme sonrasında gerçek dosya ve annotation sayıları ayrıca otomatik olarak sayılmalıdır.
