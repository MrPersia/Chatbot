# Home.py
import streamlit as st

st.set_page_config(layout="wide", page_title="AI-Assistent Chat", page_icon="🤖")
st.title("🤖 Willkommen beim AI-Assistent Chat")
st.write("""
Willkommen auf unserer AI-Assistent-Plattform! Hier finden Sie Unterstützung und Informationen zu verschiedenen Themen.

Nutzen Sie die Seitenleiste, um zwischen den verschiedenen Funktionen zu navigieren:

- 👤 Admin: Verwaltungsbereich für autorisierte Benutzer
- 💬 Chat: Interagieren Sie direkt mit unserem AI-Assistenten
- ❓ FAQ: Finden Sie Antworten auf häufig gestellte Fragen

Wir hoffen, dass Sie hier die Informationen finden, die Sie suchen!
""")

st.sidebar.success("Wählen Sie eine Seite oben aus.")
