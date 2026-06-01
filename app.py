import streamlit as st
import requests

# 1. BAĞLANTI AYARLARI (Gelişmiş ayarlardan veya yedek olarak buradaki tokenla çalışır)
STRAPI_URL = st.secrets.get("STRAPI_URL", "https://paris-strapi-backend.onrender.com/api")
STRAPI_TOKEN = st.secrets.get("STRAPI_TOKEN", "483e47724f7e55b4249a90db495d1635bd0c3d8f49ff6c846ba8e2fa290ea5fffd2120ecd582d9bc2f7db6263eef5b8e5173cc93d7529a55e2643ac1857567830bd58df7e457c130049990e2e8be0244ec75d0a3af5fb030eceb02756983e1f8990715385f04c1fc6c81621982146a7abe64c3ecfe453b830fb5134bf7547915")

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

st.set_page_config(page_title="Paris Gezi Rehberi", page_icon="🗼", layout="centered")
st.title("🗼 Yapay Zekâ Destekli Paris Gezi Rehberi")
st.write("Otomasyon tarafından yüklenen ve yapay zekayla zenginleştirilen canlı mekanlar:")

# 2. BULUTTAN ŞEHİRLERİ ÇEKME
city_names = ["Paris"]
city_mapping = {"Paris": 1}

try:
    cities_resp = requests.get(f"{STRAPI_URL}/cities", headers=HEADERS)
    if cities_resp.status_code == 200:
        cities_data = cities_resp.json().get('data', [])
        if cities_data:
            city_names = []
            city_mapping = {}
            for c in cities_data:
                c_id = c.get('id')
                attrs = c.get('attributes', c)
                # Sende Name veya Title olabilir, ikisini de kontrol ediyoruz
                name = attrs.get('Name', attrs.get('Title', attrs.get('title', 'Paris')))
                city_names.append(name)
                city_mapping[name] = c_id
except:
    pass

selected_city = st.selectbox("Lütfen bir şehir seçin:", city_names)
selected_city_id = city_mapping.get(selected_city)

st.write("---")

# 3. BULUTTAN MEKANLARI ÇEKME (?populate=* ile resim ve şehir bağını zorla getiriyoruz)
try:
    places_resp = requests.get(f"{STRAPI_URL}/places?populate=*", headers=HEADERS)
    places_data = places_resp.json().get('data', [])
except:
    places_data = []

found_any = False

if places_data:
    for p in places_data:
        attrs = p.get('attributes', p)
        
        # Şehir ilişkisini çözme (Strapi v4 ve v5 uyumlu)
        city_rel = attrs.get('city', {})
        linked_city_id = None
        if isinstance(city_rel, dict):
            city_data = city_rel.get('data')
            if city_data and isinstance(city_data, dict):
                linked_city_id = city_data.get('id')
            else:
                linked_city_id = city_rel.get('id')

        # Filtreleme: Mekan seçili şehre aitse ekrana bas
        if linked_city_id == selected_city_id or selected_city == "Paris":
            found_any = True
            
            # Sizin formdaki tam alan isimleri (Büyük harf duyarlı)
            title = attrs.get('Title', 'İsimsiz Mekan')
            desc = attrs.get('Description', 'Açıklama bulunmuyor.')
            rating = attrs.get('Rating', 0.0)
            
            # Görsel URL'sini hatasız çekme mimarisi
            img_url = None
            img_field = attrs.get('Image')
            if img_field and isinstance(img_field, dict):
                img_data = img_field.get('data')
                if img_data and isinstance(img_data, dict):
                    img_attrs = img_data.get('attributes', img_data)
                    img_url = img_attrs.get('url')
                elif 'url' in img_field:
                    img_url = img_field.get('url')

            # Ekrana Şık Bir Tasarımla Basma
            st.subheader(f"📍 {title}")
            st.write(f"⭐ **Puan:** {rating} / 5")
            
            if img_url:
                st.image(img_url, use_container_width=True)
                
            st.markdown(desc)
            st.write("---")

if not found_any:
    st.warning("Bu şehre ait yayınlanmış ilişkili bir mekan bulunamadı. Lütfen otomasyon kodunu çalıştırın ve Strapi'den 'Publish' yapın.")