import os
import sys
import logging

# Üst klasördeki `runpod_api.py` dosyasını çağırabilmek için path ekleme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.runpod_api import get_response

# Logging ayarları
log_file = os.path.join(os.path.dirname(__file__), "logs/request.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RequestHandler:
    def __init__(self):
        pass

    def send_request(self, text):
        logging.info(f"Kullanıcıdan gelen istek: {text}")
        return get_response(text)
