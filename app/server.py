from flask import Flask, request, jsonify
import os
import logging

# Logging ayarları
log_file = os.path.join(os.path.dirname(__file__), "logs/server.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/process", methods=["POST"])
        def process_request():
            data = request.get_json()
            user_input = data.get("text", "")
            
            response = {"response": f"Received: {user_input}"}
            logging.info(f"Gelen istek: {user_input}")  # Log bırak

            return jsonify(response)

    def run(self):
        logging.info("Flask Sunucusu Başlatıldı")
        self.app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    server = Server()
    server.run()
