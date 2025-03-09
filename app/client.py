import streamlit as st
import logging
import os
from chat_manager import ChatManager
from request_handler import RequestHandler

# Log klasörünü oluştur
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Logging ayarları
log_file = os.path.join(log_dir, "client.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Client:
    def __init__(self):
        self.chat_manager = ChatManager()
        self.handler = RequestHandler()

    def render_chat(self):
        self.chat_manager.setup_sidebar()
        
        if not st.session_state.current_chat:
            st.write("🚀 Yeni bir sohbet başlatmak için '+ Yeni Chat' butonuna tıklayın.")
            return

        st.title(f"🤖 AI Asistan - {st.session_state.current_chat}")
        self.chat_manager.display_chats()

        user_input = st.text_input("💬 Mesajınızı yazın:", key="input_message")

        if st.button("Gönder"):
            if user_input:
                self.chat_manager.add_user_message(user_input)

                with st.spinner("⏳ Yanıt bekleniyor..."):
                    response = self.handler.send_request(user_input)
                    bot_response = response.get("response", "Cevap alınamadı.")

                logging.info(f"Kullanıcı: {user_input}, Bot: {bot_response}")
                self.chat_manager.add_bot_message(bot_response)

def main():
    client = Client()
    client.render_chat()

if __name__ == "__main__":
    main()
