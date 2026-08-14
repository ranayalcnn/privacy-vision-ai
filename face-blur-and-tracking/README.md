# Face Blur and Tracking

Bu klasör, silinmiş çalışma ağacındaki orijinal video yüz bulanıklaştırma ve ByteTrack kaynaklarının geri yüklenmiş sürümüdür.

## İki ayrı kullanım

- **Canlı kamera:** `realtime_pipeline/` içindeki düşük gecikmeli yüz takip sistemi ve web API'deki `/api/v1/privacy/live` uç noktası kullanılır.
- **Kayıtlı video:** Bu klasördeki YOLO yüz algılama ve kalıcı ByteTrack kişi takibi ile web API'deki `/api/v1/privacy/anonymize-video` akışı kullanılır.

Modeller projedeki ortak dosyalardan yüklenir; aynı büyük model dosyaları tekrar kopyalanmaz.

```powershell
python face-blur-and-tracking/main.py video.mp4 --output sonuc.mp4
```

Pencereyi kapatmak için `q` tuşuna basın. Web arayüzünde video yüklendiğinde sonuç ayrıca sayfanın kendi sonuç alanında gösterilir.

## El hareketiyle kontrol

Eski el hareketi davranışı `realtime_pipeline/hand_control.py` kaynak alınarak yalnızca canlı kamera modunda sunulur. El sıkıştırma hareketi blur durumunu değiştirir; bir, iki ve üç parmak sırasıyla blur, mozaik ve renk kalkanı modlarını seçer.
