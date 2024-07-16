import os
from openai import OpenAI
from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv
import streamlit as st
import hashlib
from datetime import datetime

# Neue Importe für die Textverarbeitung
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Herunterladen der notwendigen NLTK-Daten
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Laden der Umgebungsvariablen
load_dotenv()

# Laden der Verbindungsdaten aus den Umgebungsvariablen
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), 
                       project=os.getenv("OPENAI_ORGANIZATION_ID"))

# Admin-Anmeldedaten (aus Umgebungsvariablen geladen)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = hashlib.sha256(os.getenv("ADMIN_PASSWORD").encode()).hexdigest()

# MongoDB-Verbindungs-URI
uri = f"mongodb+srv://{username}:{password}@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority"

# Verbindung zu MongoDB herstellen
mongo_client = MongoClient(uri)

# Verbindung zur Datenbank und den Sammlungen herstellen
db = mongo_client.chatbot
faq_collection = db.faq
messages_collection = db.messages

# ChatterBot-Instanz erstellen
chatbot = ChatBot('MyChatBot')

# Trainer für den ChatBot
trainer = ListTrainer(chatbot)

# Funktion zum Extrahieren wichtiger Stichwörter aus einem Text
def extract_keywords(text):
    # Text in Kleinbuchstaben umwandeln und in Wörter aufteilen
    tokens = word_tokenize(text.lower())
    # Nur alphabetische Tokens behalten
    tokens = [token for token in tokens if token.isalpha()]
    # Stoppwörter entfernen
    tokens = [token for token in tokens if token not in stopwords.words("german")]
    # Lemmatisierung durchführen (Wörter auf Grundform zurückführen)
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmas

# Funktion zum Vergleichen von Fragen basierend auf Stichwörtern
def compare_questions(question1, question2):
    # TF-IDF-Vektorisierung der Fragen
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([question1, question2])
    # Berechnung der Cosinus-Ähnlichkeit
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return similarity

# Überarbeitete Funktion zur Überprüfung, ob eine ähnliche Frage in der Sammlung existiert
def is_question_in_collection(question):
    all_faqs = faq_collection.find()
    for faq in all_faqs:
        similarity = compare_questions(question, faq['question'])
        if similarity > 0.7:  # Schwellenwert für die Ähnlichkeit
            return True, faq['answer']
    return False, None

# Funktion zum Erhalten einer Antwort von ChatGPT mittels Chat Completion API
def get_chatgpt_response(question):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

# Funktion zum Hinzufügen einer neuen FAQ
def add_faq(question, answer):
    if not is_question_in_collection(question)[0]:
        faq_collection.insert_one({'question': question, 'answer': answer})
        trainer.train([question, answer])
        return True
    return False

# Funktion zum Abrufen aller FAQs
def get_all_faqs():
    return list(faq_collection.find())

# Funktion zum Löschen einer FAQ
def delete_faq(question):
    result = faq_collection.delete_one({'question': question})
    return result.deleted_count > 0

# Funktion zur Überprüfung der Admin-Anmeldedaten
def check_admin_credentials(username, password):
    return username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD

# Funktion zum Senden einer Nachricht an den Admin
def send_message_to_admin(user_name, message):
    messages_collection.insert_one({
        'user_name': user_name,
        'message': message,
        'timestamp': datetime.now(),
        'status': 'unread',
        'response': None
    })

# Funktion zum Abrufen aller Nachrichten
def get_all_messages():
    return list(messages_collection.find().sort('timestamp', -1))

# Funktion zum Antworten auf eine Nachricht
def respond_to_message(message_id, response):
    messages_collection.update_one(
        {'_id': message_id},
        {'$set': {'response': response, 'status': 'answered'}}
    )

# Funktion zum Löschen einer Nachricht
def delete_message(message_id):
    messages_collection.delete_one({'_id': message_id})

# Admin-Panel
def admin_panel():
    st.header("Admin-Panel")

    admin_action = st.selectbox("Wählen Sie eine Aktion", ["FAQs verwalten", "Nachrichten verwalten"])

    if admin_action == "FAQs verwalten":
        faq_action = st.selectbox("FAQ-Aktion auswählen", ["FAQs anzeigen", "FAQ hinzufügen", "FAQ löschen"])

        if faq_action == "FAQs anzeigen":
            faqs = get_all_faqs()
            for faq in faqs:
                st.subheader(faq['question'])
                st.write(faq['answer'])
                st.write("---")

        elif faq_action == "FAQ hinzufügen":
            new_question = st.text_input("Neue Frage eingeben:")
            new_answer = st.text_area("Antwort eingeben:")
            if st.button("FAQ hinzufügen"):
                if add_faq(new_question, new_answer):
                    st.success("FAQ erfolgreich hinzugefügt!")
                else:
                    st.error("FAQ existiert bereits!")

        elif faq_action == "FAQ löschen":
            faqs = get_all_faqs()
            questions = [faq['question'] for faq in faqs]
            question_to_delete = st.selectbox("Wählen Sie die zu löschende Frage:", questions)
            if st.button("FAQ löschen"):
                if delete_faq(question_to_delete):
                    st.success("FAQ erfolgreich gelöscht!")
                else:
                    st.error("Löschen der FAQ fehlgeschlagen!")

    elif admin_action == "Nachrichten verwalten":
        messages = get_all_messages()
        for message in messages:
            st.subheader(f"Nachricht von {message['user_name']}")
            st.write(f"Gesendet am: {message['timestamp']}")
            st.write(f"Status: {'Beantwortet' if message['status'] == 'answered' else 'Ungelesen'}")
            st.write(f"Nachricht: {message['message']}")
            if message.get('response'):
                st.write(f"Antwort: {message['response']}")
            else:
                response = st.text_area(f"Antwort für {message['user_name']}:", key=str(message['_id']))
                if st.button(f"Antworten an {message['user_name']}", key=f"btn_{message['_id']}"):
                    respond_to_message(message['_id'], response)
                    st.success("Antwort gesendet!")
                    st.experimental_rerun()
            if st.button(f"Nachricht löschen", key=f"del_{message['_id']}"):
                delete_message(message['_id'])
                st.success("Nachricht gelöscht!")
                st.experimental_rerun()
            st.write("---")

# Streamlit-App
def main():
    st.title("Chatbot mit FAQ und Direktnachrichten")

    # Initialisierung des Session-Zustands
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Seitenleiste für die Navigation
    page = st.sidebar.selectbox("Wählen Sie eine Seite", ["Chat", "Admin"])

    if page == "Chat":
        st.header("Häufig gestellte Fragen (FAQ)")

        # Anzeigen der FAQs
        faqs = get_all_faqs()
        for faq in faqs:
            with st.expander(faq['question']):
                st.write(faq['answer'])

        st.header("Chat")
        st.write("Wenn Ihre Frage nicht in den FAQs beantwortet wurde, stellen Sie sie hier:")
        user_input = st.text_input("Stellen Sie Ihre Frage:")
        if user_input:
            is_similar, existing_answer = is_question_in_collection(user_input)
            if is_similar:
                st.text_area("Antwort:", value=existing_answer, height=200, max_chars=None, key=None)
            else:
                response = get_chatgpt_response(user_input)
                st.text_area("Antwort:", value=str(response), height=200, max_chars=None, key=None)

        st.header("Nachricht an Admin senden")
        user_name = st.text_input("Ihr Name:")
        user_message = st.text_area("Ihre Nachricht an den Admin:")
        if st.button("Nachricht senden"):
            if user_name and user_message:
                send_message_to_admin(user_name, user_message)
                st.success("Nachricht erfolgreich gesendet!")
            else:
                st.error("Bitte geben Sie Ihren Namen und eine Nachricht ein.")

    elif page == "Admin":
        if not st.session_state.admin_logged_in:
            st.header("Admin Login")
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            if st.button("Login"):
                if check_admin_credentials(username, password):
                    st.session_state.admin_logged_in = True
                    st.success("Login erfolgreich!")
                    st.experimental_rerun()
                else:
                    st.error("Ungültige Anmeldedaten")
        else:
            admin_panel()
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()
