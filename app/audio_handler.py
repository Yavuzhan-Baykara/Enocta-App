import streamlit as st
import logging

def play_audio(voice_url):
    """Ses dosyasını Streamlit içinde oynatır. Hata olursa log kaydı bırakır."""
    try:
        if "quota_exceeded" not in voice_url and "detected_unusual_activity" not in voice_url:
            st.audio(voice_url, format="audio/mp3")
        else:
            logging.warning(f"Ses dosyası oynatılamadı: {voice_url}")
    except Exception as e:
        logging.error(f"Ses çalma sırasında hata oluştu: {e}")
