import os
from openai import OpenAI
from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv
import streamlit as st
import hashlib
from datetime import datetime
from PIL import Image

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK Downloads
for resource in ['punkt', 'stopwords', 'wordnet']:
    nltk.download(resource, quiet=True)

# Environment setup
load_dotenv()
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), 
                       project=os.getenv("OPENAI_ORGANIZATION_ID"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = hashlib.sha256(os.getenv("ADMIN_PASSWORD").encode()).hexdigest()

# MongoDB setup
uri = f"mongodb+srv://{username}:{password}@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(uri)
db = mongo_client.chatbot
faq_collection = db.faq
messages_collection = db.messages

# ChatBot setup
chatbot = ChatBot('MyChatBot')
trainer = ListTrainer(chatbot)

# Utility functions
def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stopwords.words("german")]
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def compare_questions(question1, question2):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([question1, question2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

def find_best_match(question):
    all_faqs = faq_collection.find()
    return max(((faq, compare_questions(question, faq['question'])) for faq in all_faqs), key=lambda x: x[1])

def is_question_in_collection(question):
    best_match, similarity = find_best_match(question)
    return (similarity > 0.6, best_match['answer']) if similarity > 0.6 else (False, None)

def get_chatgpt_response(question):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

def add_faq(question, answer):
    if not is_question_in_collection(question)[0]:
        faq_collection.insert_one({'question': question, 'answer': answer})
        trainer.train([question,answer])
        return True
    return False

def get_all_faqs():
    return list(faq_collection.find())

def delete_faq(question):
    return faq_collection.delete_one({'question': question}).deleted_count > 0

def check_admin_credentials(username, password):
    return username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD

def send_message_to_admin(user_name, message):
    messages_collection.insert_one({
        'user_name': user_name,
        'essage': message,
        'timestamp': datetime.now(),
        'tatus': 'unread',
        'esponse': None
    })

def get_all_messages():
    return list(messages_collection.find().sort('timestamp', -1))

def respond_to_message(message_id, response):
    messages_collection.update_one(
        {'_id': message_id},
        {'$set': {'response': response, 'tatus': 'answered'}}
    )

def delete_message(message_id):
    messages_collection.delete_one({'_id': message_id})

# Streamlit UI functions
def display_chat_history(chat_history):
    for message in chat_history:
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

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

def chat_interface():
    st.title("🤖 Support Chat Bot")
    st.image("bot_image.jpeg", use_column_width=True)  # animated webp image

    st.header("Willkommen!")
    st.markdown("Hi! Ich bin Ihr Support Chat Bot. Wie kann ich Ihnen heute helfen?")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_help_form' not in st.session_state:
        st.session_state.show_help_form = False

    display_chat_history(st.session_state.chat_history)

    user_input = get_user_input()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Fragen 🚀"):
            if user_input:
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                is_similar, existing_answer = is_question_in_collection(user_input)
                response = existing_answer if is_similar else get_chatgpt_response(user_input)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.experimental_rerun()
    with col2:
        if st.button("Weitere Hilfe anfordern"):
            st.session_state.show_help_form = True
            st.experimental_rerun()

    if st.session_state.show_help_form:
        st.subheader("📮 Weitere Hilfe anfordern")
        user_name = st.text_input("Ihr Name:")
        email = st.text_input("Ihre E-Mail-Adresse:")
        subject = st.text_input("Betreff:")
        message = st.text_area("Ihre Nachricht:", height=150)

        if st.button("Anfrage senden 📤"):
            if user_name and email and subject and message:
                send_message_to_admin(user_name, f"E-Mail: {email}\nBetreff: {subject}\n\nNachricht: {message}")
                st.success("Ihre Anfrage wurde erfolgreich gesendet. Wir werden uns bald bei Ihnen melden.")
                st.session_state.show_help_form = False
            else:
                st.error("Bitte füllen Sie alle Felder aus.")

def display_faqs():
    faqs = get_all_faqs()
    st.header("📚 Häufige Themen")
    # Anzeigen der FAQs
    faqs = get_all_faqs()
    for faq in faqs:
        with st.expander(faq['question']):
            st.write(faq['answer'])
            
def admin_interface():
    if not st.session_state.get('admin_logged_in', False):
        st.header("👤 Admin Login")
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

def get_user_input():
    user_input = st.text_input("Ihre Frage oder Nachricht:")
    return user_input

def main():
    st.set_page_config(layout="wide", page_title="AI-Assistent Chat", page_icon="🤖")

    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_help_form' not in st.session_state:
        st.session_state.show_help_form = False

    st.sidebar.title("🤖 AI-Assistent")
    page = st.sidebar.selectbox("Navigation", ["Chat", "Admin", "FAQ"])

    if page == "Chat":
        chat_interface()
    elif page == "Admin":
        admin_interface()
    elif page == "FAQ":
        display_faqs()

if __name__ == "__main__":
    main()
