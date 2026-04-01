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

from reportlab.lib.utils import ImageReader

# PDF Oluşturma Fonksiyonu (Düzeltilmiş ve Optimize Edilmiş)
def create_pdf(image_bytes):
    # Resmi bellekten oku
    img_data = io.BytesIO(image_bytes)
    img = Image.open(img_data)
    img_width, img_height = img.size
    
    # ReportLab için ImageReader kullan (Hata giderildi)
    img_reader = ImageReader(img)
    
    buffer = io.BytesIO()
    # Sayfa boyutunu resmin boyutuna eşitle
    c = canvas.Canvas(buffer, pagesize=(img_width, img_height))
    
    # Resmi tam sayfa olarak yerleştir
    c.drawImage(img_reader, 0, 0, width=img_width, height=img_height)
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
        value="""Sen, kullanıcıların yüklediği görüntüleri boyama kitabı sayfalarına (color-book) dönüştürmek için tasarlanmış özel bir asistansın. 
Kullanıcı bir görüntü yüklediğinde, bu görüntünün stilini bir "boyama kitabı çizimi"ne dönüştür. 
1. **Siyah Beyaz:** Sadece siyah çizgiler ve beyaz arka plan kullan. Hiçbir renk, gri tonlama (shading) veya gölgeleme kullanma. 
2. **Net Çizgiler:** Görüntüdeki ana nesnelerin ve detayların kenarlarını belirgin, net ve temiz siyah çizgilerle çiz. 
3. **Beyaz Alanlar:** Tüm nesnelerin iç kısımları tamamen boş ve beyaz olmalıdır. 
4. **Basitlik:** Karmaşık dokuları ve gölgeleri kaldır. Sadece en önemli şekil ve çizgileri koru. 
5. **Yanıt:** Yalnızca dönüştürülmüş boyama kitabı resmini döndür. Metin açıklaması, karşılama mesajı veya açıklama ekleme. 
- Çıktı: Yalnızca boyama kitabı tarzında oluşturulmuş bir görüntü.""",
        height=300,
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

# Resim Boyutunu Optimize Etme (Token Tasarrufu İçin)
def optimize_image(image):
    # Maksimum 1024px genişlik/yükseklik boyama kitabı için yeterlidir
    max_size = (1024, 1024)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image

# Modeli oluştur
# Token tasarrufu için yapılandırma ekliyoruz
generation_config = {
    "temperature": 0.4, # Daha tutarlı sonuçlar için düşürüldü
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 2048, # Sadece resim döneceği için çok yüksek olmasına gerek yok
}

model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config
)

# Resim Yükleme
uploaded_file = st.file_uploader("Resim Yükle", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Orijinal", use_container_width=True)
    
    if st.button("✨ PDF Olarak Hazırla"):
        with st.spinner("Tokenlar optimize ediliyor ve işleniyor..."):
            try:
                # Resmi küçült (Token tasarrufu burada başlar)
                optimized_img = optimize_image(image)
                
                # Sadece gerekli veriyi gönder (Geçmişi gönderme!)
                response = model.generate_content([coloring_prompt, optimized_img])
                
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
