import streamlit as st

# Seitenkonfiguration
st.set_page_config(layout="wide", page_title="AI-Assistant Chat Plattform", page_icon="🤖")

# Festlegung der Farben
bg_color = "#FFFFFF"  # Weißer Hintergrund für Light Mode
text_color = "#000000"  # Schwarzer Text für Light Mode
logo_color = "#007BFF"  # Blau für Icons

# Seitenhintergrundfarbe anpassen
st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {bg_color};
    }}
    </style>
    """, unsafe_allow_html=True)

st.sidebar.success("Wählen Sie eine Seite oben aus.")

# Seitenleiste
st.sidebar.markdown("<h2 style='text-align: center;'>📬 Kontakt : Mohsen Sabziyan</h2>", unsafe_allow_html=True)

# Blaue Icons
cols = st.sidebar.columns(3)
with cols[0]:
    st.markdown(f"[![GitHub](https://img.icons8.com/ios-glyphs/60/{logo_color[1:]}/github.png)](https://github.com/MrPersia)")
with cols[1]:
    st.markdown(f"[![LinkedIn](https://img.icons8.com/ios-glyphs/60/{logo_color[1:]}/linkedin.png)](https://www.linkedin.com/in/mohsen-sabziyan-7a3b17221/)")
with cols[2]:
    st.markdown(f"[![E-Mail](https://img.icons8.com/ios-glyphs/60/{logo_color[1:]}/email.png)](mailto:sabziyanmohsen@gmail.com)")

# Hauptinhalt
st.title("🤖 Willkommen zur AI-Assistent Chat Plattform")
st.image("Home_bot_image.jpeg", use_column_width=True)

st.write(f"""
Ich bin Mohsen Sabziyan, ein engagierter Datenanalyst. 
Diese KI-Chatplattform wurde entwickelt, um Ihnen modernste Lösungen im Bereich der künstlichen Intelligenz und Datenanalyse zu bieten. 

Mit Hilfe fortschrittlicher NLP-Technologien ermöglicht diese Plattform natürliche und intuitive Gespräche 
und verbessert kontinuierlich die Benutzererfahrung durch ein lernfähiges System.
""", color=text_color)

st.markdown("---")
st.subheader("🔍 Navigation")
st.write(f"""
Verwenden Sie die Seitenleiste, um durch die Plattform zu navigieren:
- 👤 **Admin-Bereich**: Verwaltung und Konfiguration (nur für autorisierte Benutzer)
- 💬 **Chat**: Schreiben Sie direkt mit unserem AI-Assistenten und erhalten Sie in Echtzeit Antworten auf Ihre Fragen.
- ❓ **FAQ**: Antworten auf häufig gestellte Fragen
""", color=text_color)

st.markdown("---")
st.write(f"© 2024 Mohsen Sabziyan. Alle Rechte vorbehalten.", color=text_color)
