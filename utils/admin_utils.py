import streamlit as st
from utils.database import check_admin_credentials, get_all_messages, respond_to_message, delete_message, get_all_faqs, add_faq, delete_faq

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