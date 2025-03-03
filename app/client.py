# client.py
import streamlit as st
from request_handler import RequestHandler

class Client:
    def __init__(self):
        self.handler = RequestHandler()
        self.text_input = ""
        self.search_enabled = False

    def render(self):
        st.title("AI Chatbot")
        self.text_input = st.text_input("Enter text:")
        self.search_enabled = st.checkbox("Enable Web Search")
        if st.button("Send"):
            response = self.handler.send_request(self.text_input)
            st.write("Response:", response["response"])