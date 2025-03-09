import requests
import os
from upload_s3 import upload_to_s3  # AWS S3 yükleme fonksiyonunu içe aktarıyoruz.
import uuid
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def text_to_speech_elevenlabs(text):
    """ ElevenLabs API'sini kullanarak metni sese dönüştür ve rastgele isimle kaydet. """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",  # Eleven Turbo v2.5 kullanılıyor
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        # ✅ Rastgele dosya ismi oluştur (output-<UUID>.mp3)
        output_file = f"output-{uuid.uuid4()}.mp3"

        with open(output_file, "wb") as f:
            f.write(response.content)

        # ✅ S3'e yükleyip URL'yi döndür
        s3_url = upload_to_s3(output_file)
        
        # ✅ İşlem tamamlandıktan sonra yerel dosyayı sil (Opsiyonel)
        os.remove(output_file)

        return s3_url

    else:
        raise Exception(f"ElevenLabs TTS error: {response.status_code} {response.text}")