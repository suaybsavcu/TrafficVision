# TrafficVision 🚦

Trafik kamerası görüntüsünden/videosundan **gerçek zamanlı araç sayımı, hız tahmini ve şerit yoğunluk analizi** yapan bir bilgisayarlı görü sistemi.

## 🎯 Amaç
Diyarbakır gibi bir şehirde belediye/akıllı şehir projelerine örnek teşkil edecek, düşük maliyetli bir trafik analiz prototipi geliştirmek (NASA Space Apps / akıllı şehir temalı sunumlar için de uygun).

## 🧠 Yaklaşım
1. **Tespit:** YOLOv8 (nano/small) ile araç tespiti (araba, kamyon, otobüs, motosiklet sınıfları)
2. **Takip:** ByteTrack / DeepSORT ile araçların kare kare takibi (aynı aracı tekrar saymamak için)
3. **Sayım:** Tanımlı bir sanal çizgiyi geçen araçların sayılması
4. **Hız tahmini:** Piksel/zaman oranı + kamera kalibrasyonu ile yaklaşık hız hesaplama
5. **Yoğunluk haritası:** Zaman bazlı ısı haritası (hangi saatte hangi şerit daha yoğun)

## 🛠 Teknoloji Yığını
| Katman | Araç |
|---|---|
| Nesne tespiti | Ultralytics YOLOv8 |
| Takip | ByteTrack |
| Görüntü işleme | OpenCV |
| Dashboard | Streamlit + Plotly |
| Depolama | SQLite (sayım kayıtları) |

## 📁 Proje Yapısı
```
trafficvision/
├── videos/                     # test videoları
├── src/
│   ├── detector.py              # YOLOv8 wrapper
│   ├── tracker.py                # ByteTrack entegrasyonu
│   ├── speed_estimator.py
│   ├── counter.py                 # sanal çizgi geçiş sayacı
│   └── main.py
├── dashboard/
│   └── app.py                     # Streamlit canlı dashboard
├── requirements.txt
└── README.md
```

## 🚀 Kurulum
```bash
git clone https://github.com/<kullanici-adi>/trafficvision.git
cd trafficvision
pip install -r requirements.txt

python src/main.py --source videos/kavsak_ornek.mp4 --line-position 0.6

streamlit run dashboard/app.py
```

## 📊 Hedef Metrikler
- Araç sayım doğruluğu: ≥ %90 (manuel sayımla karşılaştırma)
- Gerçek zamanlı işleme: ≥ 15 FPS (GPU'suz orta seviye donanımda)

## 🗺 Yol Haritası
- [ ] Trafik ışığı ihlali tespiti
- [ ] Yaya geçidi güvenlik analizi
- [ ] Çoklu kamera senkronizasyonu

## 📄 Lisans
MIT
