import os
import requests
import time
import logging

# Log klasörünü oluştur
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Logging ayarları
log_file = os.path.join(log_dir, "runpod_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Key ve Endpoint URL
API_KEY = "rpa_UB50I7IZR6I58PENVCB1TMO9DVEWVNSPZ5YXA7271gdmi3"
API_URL = "https://api.runpod.ai/v2/91ohp2xhr7elg9/run"
RUNPOD_URL = "91ohp2xhr7elg9"
def get_response(user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "input": {
            "text": user_input,
            "max_tokens": 512
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            request_id = response_data.get("id", None)
            logging.info(f"✅ API isteği alındı: ID {request_id}")

            if not request_id:
                return {"response": "API'den geçerli bir ID alınamadı."}

            result_url = f"https://api.runpod.ai/v2/{RUNPOD_URL}/status/{request_id}"

            while True:
                result_response = requests.get(result_url, headers=headers)

                if result_response.status_code == 200:
                    result_data = result_response.json()
                    status = result_data.get("status", "")

                    if status == "COMPLETED":
                        logging.info("✅ API işlemi tamamlandı.")
                        return {"response": result_data.get("output", "Sonuç alınamadı.")}

                    elif status == "FAILED":
                        logging.error("❌ API işlemi başarısız oldu.")
                        return {"response": "API işlemi başarısız oldu."}

                    else:
                        logging.info(f"⏳ API işlemi devam ediyor... ({status})")

                else:
                    logging.warning(f"⚠️ Sonuç sorgulama başarısız: {result_response.text}")

                time.sleep(3)

        else:
            logging.error(f"❌ API isteği başarısız! HTTP {response.status_code}")
            return {"response": f"Hata! HTTP {response.status_code}"}

    except requests.exceptions.RequestException as e:
        logging.error(f"⚠️ API'ye bağlanırken hata oluştu: {e}")
        return {"response": "Bağlantı hatası! API çalışıyor mu?"}
