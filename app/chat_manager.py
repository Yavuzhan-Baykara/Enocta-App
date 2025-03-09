import streamlit as st
import logging
from link_handler import create_link_buttons
from audio_handler import play_audio

class ChatManager:
    def __init__(self):
        if "chats" not in st.session_state:
            st.session_state.chats = {}
            st.session_state.current_chat = None

    def setup_sidebar(self):
        st.sidebar.title("💬 Sohbetler")
        if st.sidebar.button("+ Yeni Chat", use_container_width=True):
            new_chat_id = f"Chat {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_chat_id] = []
            st.session_state.current_chat = new_chat_id
            logging.info(f"Yeni sohbet başlatıldı: {new_chat_id}")
            st.rerun()

        for chat_id in st.session_state.chats.keys():
            if st.sidebar.button(chat_id, use_container_width=True):
                st.session_state.current_chat = chat_id
                st.rerun()

    def display_chats(self):
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chats[st.session_state.current_chat]:
                if chat["sender"] == "user":
                    st.markdown(f"**👤 Siz:** {chat['text']}")
                else:
                    bot_response = chat["text"]
                    output_text = bot_response.get("output", "Cevap alınamadı.")
                    references = bot_response.get("references", [])
                    voice_url = bot_response.get("voice_url", None)

                    st.markdown(f"**🤖 Bot:**\n\n{output_text}")

                    if references:
                        create_link_buttons(references)

                    if voice_url:
                        play_audio(voice_url)

    def add_user_message(self, message):
        st.session_state.chats[st.session_state.current_chat].append({"sender": "user", "text": message})

    def add_bot_message(self, response):
        st.session_state.chats[st.session_state.current_chat].append({"sender": "bot", "text": response})
        st.rerun()
