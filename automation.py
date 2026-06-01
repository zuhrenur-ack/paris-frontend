import requests
from deep_translator import GoogleTranslator

# --- 1. BAĞLANTI VE ABONELİK AYARLARI ---
STRAPI_URL = "http://localhost:1337/api"
STRAPI_UPLOAD_URL = "http://localhost:1337/api/upload"

# ⚠️ KENDİ UZUN TOKEN ŞİFRENİ BURAYA YAPIŞTIR
STRAPI_TOKEN = "08921fb60a416ac5aa8b4671e01757786dc51d4f68ef6a28e029c57e7be908d2330543e433244cae89eb6856f963d67374ea5ebb9cd86ad53c6e24ce92f6120be25609a77ea619bd9e464a5320f98ef6acb9b3ae756be968ee0e45c84f570c8214ec8d14c07d1d75597c03dbd285900a754447350122818977c5af84b0ee11c9"

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
translator = GoogleTranslator(source='tr', target='en')

# --- 2. İZLENCEYE UYGUN VERİ LİSTESİ ---
mekanlar = [
    {
        "title": "Eyfel Kulesi",
        "desc": "Paris'in sembolü olan bu devasa demir kule, muhteşem bir şehir manzarası sunar.",
        "rating": 4.9,
        "prompt": "Eiffel Tower in Paris cinematic sunset view photorealistic"
    },
    {
        "title": "Louvre Müzesi",
        "desc": "Dünyanın en büyük sanat müzesidir. Cam piramidi ve Mona Lisa tablosuyla ünlüdür.",
        "rating": 4.8,
        "prompt": "The Louvre Museum glass pyramid at night in Paris 8k"
    },
    {
        "title": "Notre-Dame Katedrali",
        "desc": "Gotik mimarinin en güzel örneklerinden biri olan bu yapı, tarihi bir katedraldir.",
        "rating": 4.7,
        "prompt": "Notre-Dame Cathedral in Paris autumn realistic"
    },
    {
        "title": "Zafer Takı",
        "desc": "Napolyon tarafından yaptırılan, Paris'in en önemli tarihi anıtlarından biridir.",
        "rating": 4.6,
        "prompt": "Arc de Triomphe in Paris beautiful street lighting cinematic"
    }
]

print("🤖 İzlenceye Uygun Otomasyon Motoru Başlatılıyor...\n" + "-"*50)

# --- 3. ŞEHİR ID'SİNİ BULMA (İLİŞKİ İÇİN) ---
print("🔍 İlişkilendirme için Paris şehrinin ID'si aranıyor...")
city_id = 1  # Varsayılan değer
try:
    city_resp = requests.get(f"{STRAPI_URL}/cities?filters[Name][$eq]=Paris", headers=HEADERS)
    city_data = city_resp.json().get('data', [])
    if city_data:
        city_id = city_data[0]['id']
        print(f"   ✓ Paris Şehri Bulundu! ID: {city_id}")
except Exception as e:
    print(f"   ⚠️ Şehir ID'si alınamadı, varsayılan ID 1 kullanılacak.")

# --- 4. MEKAN DÖNGÜSÜ (OTOMASYON MOTORU) ---
for mekan in mekanlar:
    print(f"\n📍 İşleniyor: {mekan['title']}")
    
    # A. Zenginleştirme (Çeviri)
    en_desc = translator.translate(mekan['desc'])
    full_text = f"TR: {mekan['desc']}\nEN: {en_desc}"
    print(f"   ✓ İngilizce Çeviri Tamamlandı.")
    
    # B. Yapay Zeka Görsel Üretimi (Pollinations)
    img_url = f"https://image.pollinations.ai/prompt/{mekan['prompt'].replace(' ', '%20')}?width=1280&height=720&nologo=true"
    img_response = requests.get(img_url)
    
    # C. Dosya Yönetimi (Görseli Strapi Media Library'ye Yükleme)
    image_id = None
    try:
        files = {"files": (f"{mekan['title']}.jpg", img_response.content, "image/jpeg")}
        upload_resp = requests.post(STRAPI_UPLOAD_URL, files=files, headers=HEADERS)
        if upload_resp.status_code in [200, 201]:
            image_id = upload_resp.json()[0]['id']
            print("   ✅ Resim Strapi Media Library'ye API ile başarıyla yüklendi!")
    except Exception as e:
        print("   ❌ Resim Media Library'ye yüklenirken hata oluştu.")

    # D. API Entegrasyonu (Veriyi İlişkili Olarak Kaydetme)
    payload = {
        "data": {
            "Title": mekan['title'],
            "Description": full_text,
            "Rating": mekan['rating'],
            "city": city_id  # Burası mekanı şehre bağlıyor (İlişki)
        }
    }
    
    if image_id:
        payload["data"]["Image"] = image_id

    # Önce eski mükerrer kayıtları temizlemek yerine doğrudan yeni temiz kayıt ekleyelim
    response = requests.post(f"{STRAPI_URL}/places", json=payload, headers=HEADERS)
    if response.status_code in [200, 201]:
        print(f"   🎉 {mekan['title']} tüm gereksinimlerle Strapi'ye kaydedildi!")
    else:
        print(f"   ❌ Kayıt Hatası: {response.status_code}")

print("\n🚀 TÜM SİSTEM İZLENCEYE UYGUN ŞEKİLDE TAMAMLANDI!")