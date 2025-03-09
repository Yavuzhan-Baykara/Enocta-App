import streamlit as st
import re

def extract_url(text):
    """Metin içindeki gerçek URL'yi çeker."""
    match = re.search(r"https?://[^\s]+", text)
    return match.group(0) if match else None

def create_link_buttons(references):
    st.markdown("🔗 **Kaynaklar:**")
    cols = st.columns(len(references))
    for i, link_text in enumerate(references):
        real_url = extract_url(link_text)
        if real_url:
            with cols[i]:
                st.markdown(
                    f'<a href="{real_url}" target="_blank" style="text-decoration:none;">'
                    f'<button style="background-color:#007BFF;color:white;border:none;padding:8px 15px;border-radius:5px;cursor:pointer;">🔗 Bağlantı</button>'
                    f'</a>',
                    unsafe_allow_html=True,
                )
