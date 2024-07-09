import os
import openai
from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv
import streamlit as st
import hashlib
from datetime import datetime

# Load environment variables
load_dotenv()

# Load connection data from environment variables
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
openai.api_key = os.getenv("OPENAI_API_KEY")
organization_id = os.getenv("OPENAI_ORGANIZATION_ID")

# Admin credentials (loaded from environment variables)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = hashlib.sha256(os.getenv("ADMIN_PASSWORD").encode()).hexdigest()

# MongoDB connection URI
uri = f"mongodb+srv://{username}:{password}@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)

# Connect to database and collections
db = client.chatbot
faq_collection = db.faq
messages_collection = db.messages

# Create ChatterBot instance
chatbot = ChatBot('MyChatBot')

# Trainer for the ChatBot
trainer = ListTrainer(chatbot)

# Function to check if question is already in the collection
def is_question_in_collection(question):
    return faq_collection.find_one({'question': question}) is not None

# Function to get a response from ChatGPT using Chat Completion API
def get_chatgpt_response(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            organization=organization_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        return "Entschuldigung, ich kann im Moment keine weiteren Fragen beantworten. Bitte versuchen Sie es später erneut."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Es gab ein Problem bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es später erneut."

# Function to add a new FAQ
def add_faq(question, answer):
    if not is_question_in_collection(question):
        faq_collection.insert_one({'question': question, 'answer': answer})
        trainer.train([question, answer])
        return True
    return False

# Function to get all FAQs
def get_all_faqs():
    return list(faq_collection.find())

# Function to delete an FAQ
def delete_faq(question):
    result = faq_collection.delete_one({'question': question})
    return result.deleted_count > 0

# Function to check admin credentials
def check_admin_credentials(username, password):
    return username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD

# Function to send a message to admin
def send_message_to_admin(user_name, message):
    messages_collection.insert_one({
        'user_name': user_name,
        'message': message,
        'timestamp': datetime.now(),
        'status': 'unread',
        'response': None
    })

# Function to get all messages
def get_all_messages():
    return list(messages_collection.find().sort('timestamp', -1))

# Function to respond to a message
def respond_to_message(message_id, response):
    messages_collection.update_one(
        {'_id': message_id},
        {'$set': {'response': response, 'status': 'answered'}}
    )

# Function to delete a message
def delete_message(message_id):
    messages_collection.delete_one({'_id': message_id})

# Admin panel
def admin_panel():
    st.header("Admin Panel")
    
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
            if message['response']:
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

# Streamlit app
def main():
    st.title("Chatbot mit FAQ und Direktnachrichten")

    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Sidebar for navigation
    page = st.sidebar.selectbox("Wählen Sie eine Seite", ["Chat", "Admin"])

    if page == "Chat":
        st.header("Häufig gestellte Fragen (FAQ)")
        
        # Display FAQs
        faqs = get_all_faqs()
        for faq in faqs:
            with st.expander(faq['question']):
                st.write(faq['answer'])
        
        st.header("Chat")
        st.write("Wenn Ihre Frage nicht in den FAQs beantwortet wurde, stellen Sie sie hier:")
        user_input = st.text_input("Stellen Sie Ihre Frage:")
        if user_input:
            if is_question_in_collection(user_input):
                response = chatbot.get_response(user_input)
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
