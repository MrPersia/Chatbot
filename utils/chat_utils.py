# utils/chat_utils.py
import streamlit as st
from utils.database import get_chatgpt_response, is_question_in_collection, send_message_to_admin, get_all_faqs

def chat_interface():
    st.image("bot_image.jpeg", use_column_width=True)
    st.header("Willkommen!")
    st.markdown("Hi! Ich bin Ihr Support Chat Bot. Wie kann ich Ihnen heute helfen?")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_help_form' not in st.session_state:
        st.session_state.show_help_form = False

    display_chat_history(st.session_state.chat_history)

    user_input = st.text_input("Ihre Frage oder Nachricht:")

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

def display_chat_history(chat_history):
    for message in chat_history:
        if message['role'] == 'user':
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

def display_faqs():
    faqs = get_all_faqs()
    st.header("📚 Häufige Themen")
    for faq in faqs:
        with st.expander(faq['question']):
            st.write(faq['answer'])
