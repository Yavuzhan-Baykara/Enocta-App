# streamlit_app.py
from client import Client

def main():
    client = Client()
    client.render()

if __name__ == "__main__":
    main()
