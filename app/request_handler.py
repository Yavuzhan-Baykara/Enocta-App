# request_handler.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.runpod_api import get_response

class RequestHandler:
    def __init__(self, server_url="http://127.0.0.1:5000/process"):
        self.server_url = server_url

    def send_request(self, text):
        return get_response(text)