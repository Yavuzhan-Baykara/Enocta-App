# server.py
from flask import Flask, request, jsonify

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
            return jsonify(response)

    def run(self):
        self.app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    server = Server()
    server.run()