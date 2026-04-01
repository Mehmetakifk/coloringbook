# Gemini Sohbet Uygulaması

Bu uygulama, Google Gemini API'sini kullanarak kendi özel sohbet arayüzünüzü oluşturmanıza olanak tanır.

## Kurulum

1.  Python yüklü olduğundan emin olun.
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install streamlit google-generativeai python-dotenv
    ```
3.  `.env` dosyasını düzenleyin ve `GOOGLE_API_KEY` kısmına kendi API anahtarınızı yapıştırın. (API anahtarını [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden alabilirsiniz.)

## Çalıştırma

Uygulamayı başlatmak için terminalde şu komutu çalıştırın:

```bash
python -m streamlit run app.py
```

## Özellikler

*   **System Instruction**: Modelin karakterini ve davranışını belirleyebilirsiniz.
*   **Sohbet Geçmişi**: Uygulama oturum boyunca geçmişi hatırlar.
*   **Akış Desteği**: Yanıtlar gerçek zamanlı olarak gelir.
