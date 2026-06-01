import streamlit as st
import requests

st.set_page_config(page_title="YZ Destekli Gezi Rehberi", page_icon="🗼", layout="wide")

STRAPI_URL = "http://localhost:1337/api"
STRAPI_BASE = "http://localhost:1337"

st.title("🗼 Paris Yapay Zeka Destekli Gezi Rehberi")
st.caption("Strapi v5, Otomasyon Motoru ve Streamlit Entegrasyonu")

# Dil Seçimi
dil = st.selectbox("🌐 Dil Seçin / Select Language", ["Türkçe (TR)", "English (EN)"])
st.markdown("---")

# Şehirleri Çekme
try:
    cities_resp = requests.get(f"{STRAPI_URL}/cities")
    cities_list = [c['Name'] for c in cities_resp.json().get('data', [])]
except:
    cities_list = ["Paris"]

if not cities_list:
    cities_list = ["Paris"]

secilen_sehir = st.selectbox("🌆 Gezmek İstediğiniz Şehri Seçin:", cities_list)

# Mekanları Çekme
try:
    places_resp = requests.get(f"{STRAPI_URL}/places?filters[city][Name][$eq]={secilen_sehir}&populate=*")
    places_data = places_resp.json().get('data', [])
except:
    places_data = []

st.markdown("### 📍 Şehirdeki Turistik Mekanlar")

if not places_data:
    st.info("Bu şehre ait yayınlanmış ilişkili bir mekan bulunamadı. Lütfen otomasyon kodunu çalıştırın ve Strapi'den 'Publish' yapın.")
else:
    cols = st.columns(2)
    for idx, place in enumerate(places_data):
        with cols[idx % 2]:
            title = place.get('Title', 'İsimsiz Mekan')
            desc_text = place.get('Description', '')
            rating = place.get('Rating', 5.0)
            
            # Güvenli metin kontrolü (NoneType hatasını engelleyen kısım)
            if desc_text is None:
                desc_text = "Açıklama belirtilmemiş. / Description not provided."
            else:
                desc_text = str(desc_text)
            
            # Dil Ayıklaması
            if "TR" in dil:
                display_desc = desc_text.split("EN:")[0].replace("TR:", "").strip()
                rating_text = f"⭐ Puan: {rating} / 5.0"
                display_title = title
            else:
                display_desc = desc_text.split("EN:")[-1].strip() if "EN:" in desc_text else desc_text
                rating_text = f"⭐ Rating: {rating} / 5.0"
                en_titles = {"Eyfel Kulesi": "Eiffel Tower", "Louvre Müzesi": "Louvre Museum", "Notre-Dame Katedrali": "Notre-Dame Cathedral", "Zafer Takı": "Arc de Triomphe"}
                display_title = en_titles.get(title, title)

            st.subheader(display_title)
            
            # Resim Gösterimi
            image_data = place.get('Image', None)
            if image_data and 'url' in image_data:
                img_url = f"{STRAPI_BASE}{image_data['url']}"
                st.image(img_url, use_container_width=True)
            else:
                st.warning("Bu mekanın resmi Strapi Media Library'de bulunamadı.")
                
            st.write(display_desc)
            st.caption(rating_text)
            st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Zührenur - Final Ödevi Projesi © 2026")