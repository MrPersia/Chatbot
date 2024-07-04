import os
import openai
from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load connection data from environment variables
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
openai.api_key = os.getenv("OPENAI_API_KEY")

# MongoDB connection URI
uri = f"mongodb+srv://{username}:{password}@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)

# Connect to database and collection
db = client.chatbot
faq_collection = db.faq

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

# Neue FAQs in die MongoDB einfügen und den ChatBot damit trainieren
new_faqs = [
    {
        'question': 'Warum sollte ich mich für eine Karriere als Data Analyst entscheiden?',
        'answer': (
            'Die Nachfrage nach Datenexperten wächst rapide. Bis 2025 werden in Europa rund 4 Millionen '
            'Datenexperten benötigt. Allein im Jahr 2021 wurden in Deutschland über 80.000 IT-Stellen ausgeschrieben. '
            'Besonders die Nachfrage nach Daten- und KI-Experten nimmt weiter zu.\n\n'
            'Eine Karriere im Datenbereich bietet jedoch mehr als nur eine sichere Zukunft. Als Datenexperte arbeitest du an '
            'bedeutungsvollen, gesellschaftlichen Themen, bist technisch versiert, kommunikativ und kreativ. Der Beruf ist '
            'vielfältig, lässt sich mit vielen anderen Berufen kombinieren und bietet ein gutes Einkommen. Das Wichtigste: '
            'Die Ausbildung ist mit unserer Unterstützung gut erlernbar.'
        )
    },
    {
        'question': 'Bin ich nach der Weiterbildung zum Data Analyst qualifiziert, in diesem Beruf zu arbeiten und kann den Quereinstieg wagen?',
        'answer': (
            'Nach erfolgreichem Abschluss unserer Weiterbildung erhältst du mehrere Abschlusszertifikate, die du bei Bewerbungen '
            'als Kompetenznachweis verwenden kannst. Der Arbeitsmarkt für Data Analysts ist derzeit sehr gefragt, was dir auch '
            'ohne einschlägige Berufserfahrung gute Chancen auf einen Einstieg bietet. Es gibt in nahezu jeder Branche Bedarf an '
            'Analytikern, die zwar unterschiedliche Jobtitel tragen, aber dieselben Fähigkeiten und Kenntnisse wie Data Analysts '
            'benötigen.'
        )
    },
    {
        'question': 'Wie viel verdienen Data Analysts?',
        'answer': (
            'Das Gehalt eines Data Analysts variiert je nach Branche, Unternehmen und Erfahrung. Laut Glassdoor liegt das '
            'durchschnittliche Gehalt eines Data Analysts bei 56.000 € pro Jahr. Der Bereich Data Science wächst stetig, wodurch '
            'Data Analysts immer gefragter werden und auch gehaltstechnisch gute Karrierechancen bieten.'
        )
    },
    {
        'question': 'Was ist ein Bildungsgutschein?',
        'answer': (
            'Ein Bildungsgutschein bestätigt, dass ein Kostenträger wie die Agentur für Arbeit oder das Jobcenter die Kosten für '
            'eine berufliche Weiterbildung übernimmt. Der Bildungsgutschein wird im Gespräch mit einem Arbeitsvermittler beantragt, '
            'wobei geklärt wird, ob die Voraussetzungen für eine finanzielle Förderung erfüllt sind.'
        )
    },
    {
        'question': 'Wo beantrage ich einen Bildungsgutschein?',
        'answer': (
            'Wenn du arbeitslos bist und eine Weiterbildung bei DataSmart Point absolvieren möchtest, kannst du einen Bildungsgutschein '
            'über das Arbeitsamt, das Jobcenter oder die Arbeitsagentur beantragen. Mit diesem staatlichen Zuschuss kannst du die '
            'Kosten für die Teilnahme an unserem Programm komplett übernehmen lassen.'
        )
    },
    {
        'question': 'Wie beantrage ich den Bildungsgutschein?',
        'answer': (
            'Um einen Bildungsgutschein zu beantragen, vereinbart man einen Termin bei der Agentur für Arbeit oder dem Jobcenter. '
            'Während des Termins wird geklärt, ob Bedarf und Anspruch auf die finanzielle Förderung mit einem Bildungsgutschein besteht.'
        )
    },
    {
        'question': 'Wer hat Anspruch auf einen Bildungsgutschein?',
        'answer': (
            'Anspruch auf einen Bildungsgutschein haben Personen mit Wohnsitz in Deutschland, die arbeitslos sind, von Arbeitslosigkeit '
            'bedroht sind oder denen relevante Qualifikationen für ihren derzeitigen Beruf fehlen. Ob die Voraussetzungen für die '
            'Förderung mit einem Bildungsgutschein gegeben sind, entscheidet der zuständige Berater der Agentur für Arbeit oder des '
            'Jobcenters.'
        )
    },
    {
        'question': 'Welche Weiterbildungen werden von der Agentur für Arbeit bezahlt?',
        'answer': (
            'Die Agentur für Arbeit bezahlt Weiterbildungen, Umschulungen und Ausbildungen in allen Branchen, vorausgesetzt, es besteht '
            'ein aktueller Bedarf auf dem Arbeitsmarkt. Der Bildungsträger muss zudem eine AZAV-Zertifizierung haben.'
        )
    },
    {
        'question': 'Was ist eine AZAV-Zertifizierung?',
        'answer': (
            'AZAV-zertifizierte Bildungsträger erfüllen die Voraussetzungen der Verordnung und Akkreditierung von Arbeitsförderung '
            'nach dem Dritten Sozialgesetzbuch und können somit Bildungsgutscheine einlösen. DataSmart Point ist AZAV-zertifiziert.'
        )
    },
    {
        'question': 'Wie sieht ein Bildungsgutschein aus?',
        'answer': (
            'Der Bildungsgutschein ist ein offizielles Dokument, das die Rahmenbedingungen für eine berufliche Weiterbildung festhält. '
            'Auf dem Bildungsgutschein sind folgende Informationen vermerkt:\n\n'
            '- Gültigkeitsdauer\n'
            '- Kosten\n'
            '- Weiterbildungsdauer\n'
            '- Bildungsziel\n'
            '- Unterrichtsart\n'
            '- Weiterbildungsstätte\n'
            '- Weiterbildungsort'
        )
    },
    {
        'question': 'Gibt es einen Bildungsgutschein für berufstätige Menschen?',
        'answer': (
            'Für berufstätige Menschen kommt ein Bildungsgutschein nur in Frage, wenn sie von Arbeitslosigkeit bedroht sind, weil '
            'beispielsweise ein Arbeitsvertrag endet, eine Kündigung bevorsteht oder ihnen die beruflichen Qualifikationen fehlen, '
            'um den Beruf weiterhin auszuführen.'
        )
    }
]

for new_faq in new_faqs:
    question = new_faq['question']
    if not is_question_in_collection(question):
        faq_collection.insert_one(new_faq)
        trainer.train([question, new_faq['answer']])
        print(f"Frage '{question}' wurde zur Sammlung hinzugefügt.")
    else:
        print(f"Frage '{question}' ist bereits in der Sammlung vorhanden und wurde nicht hinzugefügt.")


# Funktion zum Anzeigen und Beantworten von Fragen
def display_and_answer_questions():
    # Alle Fragen abrufen und dem Benutzer anzeigen
    questions = [faq['question'] for faq in faq_collection.find()]
    print("Bitte wählen Sie eine der folgenden Fragen aus oder stellen Sie eine eigene Frage:")
    for idx, question in enumerate(questions, start=1):
        print(f"{idx}. {question}")
    print(f"{len(questions) + 1}. Eigene Frage stellen")

    while True:
        try:
            # Benutzerauswahl abfragen
            selection = int(input("\nGeben Sie die Nummer der gewünschten Frage ein oder stellen Sie eine eigene Frage: ")) - 1

            # Wenn Benutzer eine eigene Frage stellt
            if selection == len(questions):
                user_question = input("\nGeben Sie Ihre Frage ein: ")
                if is_question_in_collection(user_question):
                    response = chatbot.get_response(user_question)
                else:
                    response = get_chatgpt_response(user_question)
                break  # Aus der Schleife ausbrechen, wenn die Eingabe gültig war

            # Wenn der Benutzer eine vorhandene Frage auswählt
            elif 0 <= selection < len(questions):
                selected_question = questions[selection]
                response = chatbot.get_response(selected_question)
                break  # Aus der Schleife ausbrechen, wenn die Eingabe gültig war

            else:
                print("Ungültige Auswahl. Bitte geben Sie eine gültige Nummer ein.")

        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Nummer ein.")

    # Antwort anzeigen
    print(f"\nAntwort: {response}")

# Hauptmenü
while True:
    print("\nWas möchten Sie tun?")
    print("1. Frage auswählen und beantworten")
    print("2. Beenden")

    try:
        choice = int(input("\nGeben Sie die Nummer Ihrer Wahl ein: "))

        if choice == 1:
            display_and_answer_questions()
        elif choice == 2:
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie eine Nummer ein.")
