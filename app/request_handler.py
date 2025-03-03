# request_handler.py
import requests

class RequestHandler:
    def __init__(self, server_url="http://127.0.0.1:5000/process"):
        self.server_url = server_url

    def send_request(self, text):
        payload = {"text": text}
        response = requests.post(self.server_url, json=payload)
        return response.json()