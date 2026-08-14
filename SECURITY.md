# Güvenlik

## Desteklenen kullanım

Bu proje varsayılan olarak yerel geliştirme için hazırlanmıştır. İnternete açık
bir kurulumda `.env.example` dosyasını temel alarak en az `API_KEY` ayarlanmalı,
HTTPS kullanılmalı ve ters proxy seviyesinde de istek/gövde sınırları
uygulanmalıdır.

## Uygulanan korumalar

- Görüntü ve videolarda MIME allowlist, gerçek içerik doğrulaması ve boyut sınırı
- Görüntü çözünürlüğü ile video çözünürlüğü/süresi için kaynak sınırları
- Kullanıcı dosya adları yerine rastgele geçici dosya adları
- Tamamlanan ve süresi dolan video işlerinin otomatik temizlenmesi
- İstek hızı ve eşzamanlı video işi sınırı
- İsteğe bağlı, sabit zamanlı karşılaştırılan `X-API-Key` denetimi
- CSP, clickjacking, MIME sniffing, referrer ve tarayıcı izin başlıkları
- API cevaplarında `no-store` önbellek politikası

## Sınırlar

Bu kontroller antivirüs, kullanıcı kimlik sistemi, hukuki KVKK değerlendirmesi
veya üretim altyapısı güvenliğinin yerine geçmez. Hassas/kurumsal kullanımda
dosya zararlı yazılım taraması, merkezi loglama, kimlik doğrulama, TLS sonlandırma
ve bağımsız güvenlik testi ayrıca uygulanmalıdır.

## Güvenlik bildirimi

Bir güvenlik sorunu bulursanız ayrıntıları herkese açık issue içinde kişisel veri
veya çalışan saldırı örneği paylaşmadan proje sahibiyle özel olarak paylaşın.

