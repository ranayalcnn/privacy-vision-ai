# KVKK Safe Human Analysis API

Bu API, mevcut görüntü işleme modellerini HTTP üzerinden kullanılabilir hale
getirir. Fotoğraf, video ve tarayıcıdan alınan kamera karelerini destekler.

## 1. Kurulum

Proje ana klasöründe bir sanal ortam oluşturun:

```powershell
python -m venv .venv-api
.\.venv-api\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
```

Model ağırlıkları varsayılan olarak şu konumlarda aranır:

```text
blur_and_segment/yolov8n-face.pt
FORKLIFT DETECTION/models/forklift_yolo11n_quick_best.pt
```

Farklı dosyalar kullanılacaksa ortam değişkenleri ayarlanabilir:

```powershell
$env:FACE_MODEL_PATH="C:\models\face.pt"
$env:FORKLIFT_MODEL_PATH="C:\models\forklift.pt"
```

İnternete açık bir kurulumda API anahtarı ve güvenlik sınırları ayarlanabilir:

```powershell
$env:API_KEY="uzun-ve-rastgele-bir-anahtar"
$env:API_RATE_LIMIT_REQUESTS="240"
$env:API_RATE_LIMIT_WINDOW_SECONDS="60"
$env:API_VIDEO_JOB_TTL_SECONDS="3600"
```

`API_KEY` boş bırakılırsa yerel arayüz anahtarsız çalışır. Anahtar
ayarlandığında API isteklerinde `X-API-Key` başlığı gönderilmelidir.
Tamamlanan video işleri, varsayılan olarak bir saat sonra dosyalarıyla birlikte
otomatik temizlenir.

## 2. Çalıştırma

Komutu proje ana klasöründe çalıştırın:

```powershell
python -m uvicorn api.main:app --reload
```

Adresler:

- Kullanıcı arayüzü: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Sağlık kontrolü: `http://127.0.0.1:8000/health`

Ana sayfa teknik bilgi gerektirmeyen bir kullanım ekranıdır. Kullanıcı işlem
türünü seçer, fotoğrafı yükler ve sonucu aynı sayfada görür.

## 3. Kullanıcı arayüzüyle deneme

1. Tarayıcıda `http://127.0.0.1:8000` adresini açın.
2. Yüz gizleme, insan bulanıklaştırma, insan kaldırma, depo analizi veya vücut
   duruşu analizini seçin.
3. Fotoğraf/video yükleyin ya da `Canlı kamera` seçeneğiyle bir kare yakalayın.
4. Yeşil işlem düğmesine basıp sonucu bekleyin.
5. İşlenmiş görüntüyü `Sonucu indir` düğmesiyle kaydedin.

Video işlemleri her karede model çalıştırdığı için fotoğrafa göre daha uzun
sürer. İşlenen videolar tarayıcı uyumlu H.264 MP4 biçiminde döndürülür.

## 4. Swagger ile deneme

### Yüz anonimleştirme

1. `POST /api/v1/privacy/anonymize` endpoint'ini açın.
2. `Try it out` düğmesine basın.
3. `mode` olarak `soft_blur`, `mosaic` veya `color_shield` seçin.
4. JPEG, PNG veya WebP görüntüsü yükleyip `Execute` düğmesine basın.

Sonuç bir JPEG görüntüsüdür. `X-Face-Count` yüz sayısını,
`X-Fail-Safe-Applied` ise tüm kare bulanıklaştırmasının uygulanıp
uygulanmadığını gösterir.

### Forklift tespiti

1. `POST /api/v1/forklift/detect` endpoint'ini açın.
2. Görüntüyü yükleyip `Execute` düğmesine basın.

Sonuç; sınıf adı, güven değeri ve koordinatları içeren JSON'dur.

## 5. curl örnekleri

```powershell
curl.exe -X POST `
  "http://127.0.0.1:8000/api/v1/privacy/anonymize?mode=mosaic" `
  -F "file=@test.jpg" `
  --output protected.jpg
```

```powershell
curl.exe -X POST `
  "http://127.0.0.1:8000/api/v1/forklift/detect?confidence=0.25" `
  -H "X-API-Key: $env:API_KEY" `
  -F "file=@warehouse.jpg"
```

## Mimari

```text
api/main.py                 Uygulamayı ve endpoint gruplarını birleştirir
api/routers/                HTTP parametrelerini ve cevapları yönetir
api/services/               YOLO tahmini ve görüntü işlemesini yürütür
api/image_io.py             Dosya doğrulama, çözme ve JPEG kodlama yapar
api/config.py               Model yollarını ve yükleme sınırını yönetir
api/static/                 Hafif kullanıcı arayüzünü içerir
```

Modeller `LazyYoloModel` ile ilk tahmin sırasında yüklenir ve sonraki
isteklerde bellekteki aynı model kullanılır. YOLO işlemleri thread pool
üzerinde yürütüldüğü için FastAPI olay döngüsü bloke edilmez.

## Testler

Hızlı test paketi:

```powershell
python -m pytest -q
```

Beş örnek videoyu gerçek modellerle işleyen yavaş test paketi:

```powershell
$env:RUN_MODEL_E2E="1"
python -m pytest api/tests/test_video_demos_e2e.py -q
```
