import requests
from deep_translator import GoogleTranslator

# --- 1. BAĞLANTI VE ABONELİK AYARLARI ---
STRAPI_URL = "https://paris-strapi-backend.onrender.com/api"
STRAPI_UPLOAD_URL = "https://paris-strapi-backend.onrender.com/api/upload"

STRAPI_TOKEN = "554e33116941e88b4dde35f177516d364bc625855777505cca8b83af1e3890e1d26e919d2da7c3d7a9658a9a94223dd231a435e2c7f5768762479ca58dd162e2eabb642fe8530c0828f27360f6a1cb898f3f909f19020d1b9473ee1d842a4391ac22ae0ad57ad98b9b926842347d32c714e6af6b32f8986d4e6fdd6a98329699"

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
translator = GoogleTranslator(source='tr', target='en')

# --- 2. VERİ LİSTESİ ---
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

print("🤖 Otomasyon Motoru Başlatılıyor...\n" + "-"*50)

# --- 3. ŞEHİR KONTROLÜ ---
print("🔍 Paris şehri bulut veritabanında aranıyor...")
city_id = None

try:
    city_resp = requests.get(f"{STRAPI_URL}/cities?filters[Name][$eq]=Paris", headers=HEADERS)
    city_data = city_resp.json().get('data', [])
    
    if city_data:
        city_id = city_data[0]['id']
        print(f"   ✓ Paris Şehri Zaten Var! ID: {city_id}")
    else:
        print("   ⚠️ Paris şehri bulunamadı! Otomatik oluşturuluyor...")
        city_payload = {
            "data": {
                "Name": "Paris",
                "Country": "Fransa",
                "Description": "Aşkın, sanatın ve modanın küresel başkenti."
            }
        }
        create_city_resp = requests.post(f"{STRAPI_URL}/cities", json=city_payload, headers=HEADERS)
        if create_city_resp.status_code in [200, 201]:
            res_json = create_city_resp.json().get('data', {})
            city_id = res_json.get('id') if isinstance(res_json, dict) else res_json[0].get('id')
            print(f"   ✅ Paris Şehri Bulutta Başarıyla Oluşturuldu! ID: {city_id}")
except Exception as e:
    print(f"   ❌ Şehir işlemlerinde hata oluştu.")

if not city_id:
    city_id = 1
    print("   ⚠️ Varsayılan ID: 1 kullanılacak.")

# --- 4. MEKAN DÖNGÜSÜ (EKRAN GÖRÜNTÜNDEKİ BİREBİR ALANLAR) ---
for mekan in mekanlar:
    print(f"\n📍 İşleniyor: {mekan['title']}")
    
    # A. Zenginleştirme (Çeviri)
    en_desc = translator.translate(mekan['desc'])
    full_text = f"TR: {mekan['desc']}\n\nEN: {en_desc}"
    print(f"   ✓ İngilizce Çeviri Tamamlandı.")
    
    # B. Yapay Ceka Görsel Üretimi (Pollinations)
    img_url = f"https://image.pollinations.ai/prompt/{mekan['prompt'].replace(' ', '%20')}?width=1280&height=720&nologo=true"
    img_response = requests.get(img_url)
    
    # C. Medya Yükleme
    image_id = None
    try:
        files = {"files": (f"{mekan['title']}.jpg", img_response.content, "image/jpeg")}
        upload_resp = requests.post(STRAPI_UPLOAD_URL, files=files, headers=HEADERS)
        if upload_resp.status_code in [200, 201]:
            image_id = upload_resp.json()[0]['id']
            print("   ✅ Resim Strapi Media Library'ye API ile başarıyla yüklendi!")
    except Exception as e:
        print("   ❌ Resim Media Library'ye yüklenirken hata oluştu.")

    # D. API ENTEGRASYONU (Senin ekranındaki büyük/küçük harf hassasiyeti)
    payload = {
        "data": {
            "Title": mekan['title'],         # Sende: Title (Büyük T)
            "Description": full_text,        # Sende: Description (Büyük D)
            "Rating": mekan['rating'],        # Sende: Rating (Büyük R)
            "city": city_id                  # Sende: city (Küçük c)
        }
    }
    
    if image_id:
        payload["data"]["Image"] = image_id  # Sende: Image (Büyük I)

    response = requests.post(f"{STRAPI_URL}/places", json=payload, headers=HEADERS)
    if response.status_code in [200, 201]:
        print(f"   🎉 {mekan['title']} tüm gereksinimlerle Strapi'ye kaydedildi!")
    else:
        print(f"   ❌ Kayıt Hatası: {response.status_code}")
        print(f"   📋 Sunucu Yanıtı: {response.text}")

print("\n🚀 TÜM BULUT VERİTABANI BAŞARIYLA DOLDURULDU!")
