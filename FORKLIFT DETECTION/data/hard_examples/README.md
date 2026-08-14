# Zor örnekler

Bu klasörde üretim/test videolarında modelin hata yaptığı kısa bölümler tutulur.

`forklift_warehouse_8s_15s/` bölümü şu hataları içerir:

- Forklift gövdesi hareket ederken kutunun kaybolması
- Forklift mast/direk kısmının ayrı veya çok büyük forklift kutusu olarak algılanması
- Operatörün kısmi görünümünde person kutusunun kesilmesi

Bu kareler eğitim setine eklenmeden önce `forklift` ve `person` kutuları elle doğrulanmalıdır. Yanlış pseudo-label ile yeniden eğitim yapılmamalıdır.
