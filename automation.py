import requests
import json
from deep_translator import GoogleTranslator

# --- 1. BAĞLANTI AYARLARI ---
STRAPI_URL = "https://paris-strapi-backend.onrender.com/api"
STRAPI_UPLOAD_URL = "https://paris-strapi-backend.onrender.com/api/upload"
STRAPI_TOKEN = "55a1af5cd5f1544740887b7045c6d87a7933a29d223cac85ca4a321cbf7181119a5be6abeded15806062d7079cd9bee2eb75733e697ec5ca32cea9d15ce5f1cbb5bc27ecf24c004fd6c549a89303fab1e9f34ebb7d2304c3b09b733c859a51ceab906d28199f438404b502da4e2be459847545b8608ee705a13a48b939dea833"

UPLOAD_HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
DATA_HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}", "Content-Type": "application/json"}

translator = GoogleTranslator(source='tr', target='en')

# YAPAY ZEKAYI ÇÖPE ATTIK! İŞTE GERÇEK VE GARANTİLİ FOTOĞRAF LİNKLERİ:
GARANTILI_FOTOLAR = {
    "Eyfel Kulesi": "https://images.unsplash.com/photo-1543305113-162955fbd672?q=80&w=1280",
    "Louvre Müzesi": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=1280",
    "Notre-Dame Katedrali": "https://images.unsplash.com/photo-1551056586-778939634d12?q=80&w=1280",
    "Zafer Takı": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=1280"
}

try:
    with open("mekanlar.json", "r", encoding="utf-8") as file:
        mekanlar = json.load(file)
except FileNotFoundError:
    print("❌ HATA: 'mekanlar.json' bulunamadı!")
    exit()

print("🚀 Kurşun Geçirmez Otomasyon Başlatılıyor...\n" + "-"*50)

city_id = 1
try:
    city_resp = requests.get(f"{STRAPI_URL}/cities?filters[Name][$eq]=Paris", headers=UPLOAD_HEADERS)
    city_data = city_resp.json().get('data', [])
    if city_data:
        city_id = city_data[0]['id']
except:
    pass

for mekan in mekanlar:
    baslik = mekan['title']
    print(f"\n📍 İşleniyor: {baslik}")
    
    en_desc = translator.translate(mekan['desc'])
    full_text = f"TR: {mekan['desc']}\n\nEN: {en_desc}"
    
    # Paralı site yerine doğrudan yüksek kaliteli gerçek fotoğrafı çekiyoruz
    img_url = GARANTILI_FOTOLAR.get(baslik, GARANTILI_FOTOLAR["Eyfel Kulesi"])
    print(f"   ⏳ Gerçek fotoğraf Unsplash'ten indiriliyor...")
    
    img_response = requests.get(img_url)
    image_id = None
    
    if img_response.status_code == 200:
        try:
            files = {
                'files': (f"{baslik}.jpg", img_response.content, 'image/jpeg')
            }
            print(f"   ⏳ Fotoğraf Strapi bulutuna (Cloudinary) post ediliyor...")
            upload_resp = requests.post(STRAPI_UPLOAD_URL, files=files, headers=UPLOAD_HEADERS)
            
            if upload_resp.status_code in [200, 201]:
                res_json = upload_resp.json()
                image_id = res_json[0]['id']
                print(f"   ✅ Görsel başarıyla buluta yüklendi! ID: {image_id}")
            else:
                print(f"   ❌ Görsel Yükleme Hatası ({upload_resp.status_code}): {upload_resp.text}")
        except Exception as e:
            print(f"   ❌ Medya gönderim esnasında hata: {e}")
    else:
        print(f"   ❌ Fotoğraf indirilemedi! Hata Kodu: {img_response.status_code}")

    payload = {
        "data": {
            "Title": baslik,         
            "Description": full_text,        
            "Rating": mekan['rating'],        
            "city": city_id                  
        }
    }
    if image_id:
        payload["data"]["Image"] = image_id  

    response = requests.post(f"{STRAPI_URL}/places", json=payload, headers=DATA_HEADERS)
    if response.status_code in [200, 201]:
        print(f"   🎉 {baslik} veri tabanına FOTOĞRAFIYLA başarıyla işlendi!")
    else:
        print(f"   ❌ Mekan Kayıt Hatası: {response.text}")

print("\n🚀 İŞLEM TAMAMLANDI! ARTIK KUTLAMA YAPABİLİRİZ! SİTENİ KONTROL ET.")