import streamlit as st
import requests

# 1. BAĞLANTI AYARLARI
STRAPI_BASE_URL = "https://paris-strapi-backend.onrender.com"
STRAPI_URL = f"{STRAPI_BASE_URL}/api"
STRAPI_TOKEN = st.secrets.get("STRAPI_TOKEN", "483e47724f7e55b4249a90db495d1635bd0c3d8f49ff6c846ba8e2fa290ea5fffd2120ecd582d9bc2f7db6263eef5b8e5173cc93d7529a55e2643ac1857567830bd58df7e457c130049990e2e8be0244ec75d0a3af5fb030eceb02756983e1f8990715385f04c1fc6c81621982146a7abe64c3ecfe453b830fb5134bf7547915")

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

# KODUN İÇİNDEKİ HAZIR REHBER AÇIKLAMALARI (SADELEŞTİRİLMİŞ)
HAZIR_ACIKLAMALAR = {
    "eyfel": "TR: 1889 yılında Dünya Fuarı için geçici olarak inşa edilen bu devasa demir kule, günümüzde Paris'in kalbi ve dünyanın en ikonik yapısıdır. Şehri kuş bakışı izlemek için en mükemmel noktadır.\n\nEN: Built in 1889 for the World's Fair, this giant iron tower is now the heart of Paris and the world's most iconic structure. It is the perfect spot to view the city from a bird's eye view.",
    "louvre": "TR: Dünyanın en büyük ve en çok ziyaret edilen sanat müzesidir. Tarihi bir saray olan bu yapıda, ünlü Mona Lisa tablosu dahil binlerce yıllık eşsiz sanat eserleri sergilenmektedir.\n\nEN: It is the world's largest and most visited art museum. Located in a historic palace, this structure exhibits thousands of years of unique artworks, including the famous Mona Lisa.",
    "notre": "TR: Gotik mimarinin dünyadaki en nadide örneği olan bu büyüleyici katedral, Seine Nehri'nin ortasındaki bir adada yer alır. Devasa gül pencereleri ve mistik atmosferiyle ünlüdür.\n\nEN: The finest example of Gothic architecture in the world, this fascinating cathedral is located on an island in the middle of the Seine River. It is famous for its massive rose windows and mystical atmosphere.",
    "zafer": "TR: Şanzelize Caddesi'nin başında gururla yükselen bu anıt, Fransız ordusunun zaferlerini taçlandırmak için inşa edilmiştir. Tepesine çıktığınızda Paris'in 12 büyük caddesinin birleşimini izleyebilirsiniz.\n\nEN: Rising proudly at the beginning of the Champs-Élysées Avenue, this monument was built to honor the victories of the French army. From its top, you can watch the intersection of Paris's 12 major avenues."
}

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
                name = attrs.get('Name', attrs.get('Title', attrs.get('title', 'Paris')))
                city_names.append(name)
                city_mapping[name] = c_id
except:
    pass

selected_city = st.selectbox("Lütfen bir şehir seçin:", city_names)
selected_city_id = city_mapping.get(selected_city)

st.write("---")

# 3. BULUTTAN MEKANLARI ÇEKME
try:
    places_resp = requests.get(f"{STRAPI_URL}/places?populate=*", headers=HEADERS)
    places_data = places_resp.json().get('data', [])
except:
    places_data = []

found_any = False

if places_data:
    for p in places_data:
        attrs = p.get('attributes', p)
        
        # Şehir ilişkisini çözme
        city_rel = attrs.get('city', {})
        linked_city_id = None
        if isinstance(city_rel, dict):
            city_data = city_rel.get('data')
            if city_data and isinstance(city_data, dict):
                linked_city_id = city_data.get('id')
            else:
                linked_city_id = city_rel.get('id')

        # Filtreleme
        if linked_city_id == selected_city_id or selected_city == "Paris":
            found_any = True
            
            # Süper Esnek Başlık ve Açıklama Yakalayıcı
            title = attrs.get('Title') or attrs.get('Name') or attrs.get('title') or attrs.get('name') or 'İsimsiz Mekan'
            
            desc_raw = attrs.get('Description') or attrs.get('description') or attrs.get('desc') or attrs.get('Desc') or ''
            desc = str(desc_raw).strip()
            
            rating = attrs.get('Rating', 0.0)
            
            # Hazır Rehber Yazılarını Eşleştirme Filtresi
            if not desc or desc == "None" or "EN:" not in desc:
                for anahtar, hazir_metin in HAZIR_ACIKLAMALAR.items():
                    if anahtar in title.lower():
                        desc = hazir_metin
                        break

            # Ultra Esnek Görsel URL Yakalama Sistemi
            img_url = None
            img_field = attrs.get('Image')
            
            if img_field:
                if isinstance(img_field, dict):
                    img_url = img_field.get('url')
                    if not img_url:
                        img_data = img_field.get('data')
                        if isinstance(img_data, dict):
                            img_attrs = img_data.get('attributes', {})
                            img_url = img_attrs.get('url', img_data.get('url'))
                elif isinstance(img_field, list) and len(img_field) > 0:
                    first_img = img_field[0]
                    if isinstance(first_img, dict):
                        img_url = first_img.get('url', first_img.get('attributes', {}).get('url'))

            # Linki tam adrese tamamlama güvencesi
            if img_url and isinstance(img_url, str):
                if img_url.startswith("/"):
                    img_url = f"{STRAPI_BASE_URL}{img_url}"
            else:
                img_url = None

            # Ekrana Şık Tasarımla Basma
            st.subheader(f"📍 {title}")
            st.write(f"⭐ **Puan:** {rating} / 5")
            
            # ÇÖKMEYİ ENGELLEYEN KORUMA KALKANI
            if img_url and img_url.startswith("http"):
                try:
                    st.image(img_url, use_container_width=True)
                except Exception as img_err:
                    st.info("Görsel sunucudan yüklenirken pas geçildi.")
            else:
                st.caption("📷 Bu mekan için henüz geçerli bir görsel yüklenmemiş.")

            # TÜM MEKANLARIN GELMESİNİ SAĞLAYAN GÜVENLİ DİL AYRIMI
            turkce_kisim = "Açıklama bulunmuyor."
            ingilizce_kisim = "English translation not found."

            if desc and desc != "None":
                if "EN:" in desc:
                    parçalar = desc.split("EN:")
                    turkce_kisim = parçalar[0].replace("TR:", "").strip()
                    ingilizce_kisim = parçalar[1].strip()
                else:
                    turkce_kisim = desc
            
            # Sitede yan yana açılır iki sekme oluşturuyoruz
            sekme_tr, sekme_en = st.tabs(["🇹🇷 Türkçe Açıklama", "🇬🇧 English Description"])
            
            with sekme_tr:
                st.write(turkce_kisim)
                
            with sekme_en:
                st.write(ingilizce_kisim)
                
            st.write("---")

if not found_any:
    st.warning("Bu şehre ait yayınlanmış ilişkili bir mekan bulunamadı. Lütfen otomasyon kodunu çalıştırın ve Strapi'den 'Publish' yapın.")