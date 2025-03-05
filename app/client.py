import streamlit as st
from request_handler import RequestHandler

class Client:
    def __init__(self):
        self.handler = RequestHandler()

    def render_chat(self):
        # Eğer oturumda kayıtlı sohbetler yoksa başlat
        if "chats" not in st.session_state:
            st.session_state.chats = {}  # Bütün sohbetleri saklayacak
            st.session_state.current_chat = None  # O an hangi sohbetin açık olduğu

        # **Yeni Sohbet Butonu (Sol Sidebar'da)**
        st.sidebar.title("Sohbetler")
        if st.sidebar.button("+ Yeni Chat"):
            new_chat_id = f"Chat {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_chat_id] = []  # Yeni sohbet için boş liste
            st.session_state.current_chat = new_chat_id  # Yeni sohbeti aktif yap
            st.rerun()

        # **Mevcut Sohbetler Listesi (Daha Geniş ve Uzun Butonlar)**
        for chat_id in st.session_state.chats.keys():
            if st.sidebar.button(chat_id, use_container_width=True):
                st.session_state.current_chat = chat_id
                st.rerun()

        # Eğer aktif sohbet yoksa kullanıcıyı yönlendir
        if not st.session_state.current_chat:
            st.write("Yeni bir sohbet başlatmak için '+ Yeni Chat' butonuna tıklayın.")
            return

        # **Başlığı "Leadership Coach" olarak değiştir**
        st.title(f"Leadership Coach - {st.session_state.current_chat}")

        # Sohbet kutusunun genişliğini artır (Punto Büyütüldü)
        chat_container = st.container()
        with chat_container:
            for i, chat in enumerate(st.session_state.chats[st.session_state.current_chat]):
                if chat["sender"] == "user":
                    st.markdown(f"<p style='font-size:18px;'><b>Siz:</b> {chat['text']}</p>", unsafe_allow_html=True)
                else:
                    col1, col2 = st.columns([9, 1])  # Sağ tarafa küçük ikon koymak için
                    with col1:
                        st.markdown(f"<p style='font-size:18px;'><b>Bot:</b> {chat['text']}</p>", unsafe_allow_html=True)
                    with col2:
                        if st.button("🔊", key=f"audio_{i}"):  # Ses butonu (şimdilik boş)
                            st.write("Ses çıkışı çalınacak (MP3 eklenecek)")

        # **Mesaj Gönderme Alanı**
        user_input = st.text_input("Mesajınızı yazın:", key="input_message")
        if st.button("Gönder"):
            if user_input:
                # Kullanıcı mesajını aktif sohbete ekle
                st.session_state.chats[st.session_state.current_chat].append(
                    {"sender": "user", "text": user_input}
                )
                # Bot'tan yanıt al
                response = self.handler.send_request(user_input)
                bot_response = response.get("response", "Cevap alınamadı.")
                st.session_state.chats[st.session_state.current_chat].append(
                    {"sender": "bot", "text": bot_response}
                )
                st.rerun()
                