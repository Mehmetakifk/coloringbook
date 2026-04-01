import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# .env dosyasını yükle
load_dotenv()

# Sayfa yapılandırması
st.set_page_config(page_title="Boyama Kitabı Oluşturucu", page_icon="🎨")

# PDF Oluşturma Fonksiyonu (Sadece Resim Odaklı)
def create_pdf(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    img_width, img_height = img.size
    
    buffer = io.BytesIO()
    # Sayfa boyutunu resmin boyutuna eşitle
    c = canvas.Canvas(buffer, pagesize=(img_width, img_height))
    
    # Resmi tam sayfa olarak yerleştir (kenar boşluğu olmadan)
    c.drawImage(io.BytesIO(image_bytes), 0, 0, width=img_width, height=img_height)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Yan panel: Ayarlar
with st.sidebar:
    st.title("🎨 Boyama Ayarları")
    api_key = st.text_input("Gemini API Anahtarı", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    
    model_name = "nano-banana-pro-preview"
    st.info(f"Model: **{model_name}**")
    
    coloring_prompt = st.text_area(
        "Boyama Kitabı Promptu", 
        value="Bu resmi bir çocuk boyama kitabı sayfasına dönüştür. Sadece kalın, net siyah çizgiler kullan, tüm renkleri çıkar, arka planı tamamen beyaz yap. Çıktı olarak sadece resmi ver.",
        help="Resmi dönüştürürken kullanılacak ana talimat."
    )
    
    if st.button("🔄 Yeni Başlat"):
        st.rerun()

st.title("🖌️ Boyama PDF Oluşturucu")
st.write("Resmi yükleyin, boyama sayfasına dönüşsün ve PDF olarak alın.")
st.markdown("---")

# API Anahtarı kontrolü
if not api_key:
    st.warning("Lütfen yan panelden API anahtarınızı girin.")
    st.stop()

# Gemini'yi yapılandır
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name=model_name)

# Resim Yükleme
uploaded_file = st.file_uploader("Resim Yükle", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Orijinal", use_container_width=True)
    
    if st.button("✨ PDF Olarak Hazırla"):
        with st.spinner("İşleniyor..."):
            try:
                response = model.generate_content([coloring_prompt, image])
                
                generated_image_bytes = None
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image_bytes = part.inline_data.data
                        break
                    elif hasattr(part, 'image'):
                        generated_image_bytes = part.image.data
                        break
                
                with col2:
                    if generated_image_bytes:
                        st.image(generated_image_bytes, caption="Sonuç", use_container_width=True)
                        
                        # PDF Oluştur (Sadece resim)
                        pdf_file = create_pdf(generated_image_bytes)
                        st.download_button(
                            label="📥 SADECE ÇIKTIYI PDF İNDİR",
                            data=pdf_file,
                            file_name="boyama_cikti.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("PDF Hazır!")
                    else:
                        st.error("Model resim üretemedi, metin yanıtı verdi.")
                        st.write(response.text)
                
            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.markdown("---")
st.caption("Bu araç sadece yüklediğiniz görselin boyama versiyonunu içeren bir PDF üretir.")
