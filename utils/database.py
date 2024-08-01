import os
from openai import OpenAI
from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv
import hashlib
from datetime import datetime
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
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stopwords.words("german")]
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def extract_keywords(text):
    return " ".join(preprocess_text(text))

def compare_questions(question1, question2):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([question1, question2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

def find_best_match(question):
    processed_question = extract_keywords(question)
    highest_similarity = 0.0
    best_match = None
    for faq in faq_collection.find():
        processed_faq_question = extract_keywords(faq['question'])
        similarity = compare_questions(processed_question, processed_faq_question)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = faq
    return best_match, highest_similarity

def is_question_in_collection(question):
    best_match, similarity = find_best_match(question)
    threshold = 0.7  # Adjusted threshold based on testing
    return (similarity > threshold, best_match['answer']) if similarity > threshold else (False, None)

def get_chatgpt_response(question):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Bitte beantworte die folgenden Fragen oder ähnliche Fragen ausschließlich mit den angegebenen Antworten. Wenn eine Frage nicht in diesem Katalog enthalten ist oder nicht genau übereinstimmt, antworte bitte frei.\n\nWarum sollte ich mich für eine Karriere als Data Analyst entscheiden? \nAntwort: Die Nachfrage nach Datenexperten wächst rapide. Bis 2025 werden in Europa rund 4 Millionen Datenexperten benötigt. Allein im Jahr 2021 wurden in Deutschland über 80.000 IT-Stellen ausgeschrieben. Besonders die Nachfrage nach Daten- und KI-Experten nimmt weiter zu. Eine Karriere im Datenbereich bietet jedoch mehr als nur eine sichere Zukunft. Als Datenexperte arbeitest du an bedeutungsvollen, gesellschaftlichen Themen, bist technisch versiert, kommunikativ und kreativ. Der Beruf ist vielfältig, lässt sich mit vielen anderen Berufen kombinieren und bietet ein gutes Einkommen. Das Wichtigste: Die Ausbildung ist mit unserer Unterstützung gut erlernbar.\n\nBin ich nach der Weiterbildung zum Data Analyst qualifiziert, in diesem Beruf zu arbeiten und kann den Quereinstieg wagen? \nAntwort: Nach erfolgreichem Abschluss unserer Weiterbildung erhältst du mehrere Abschlusszertifikate, die du bei Bewerbungen als Kompetenznachweis verwenden kannst. Der Arbeitsmarkt für Data Analysts ist derzeit sehr gefragt, was dir auch ohne einschlägige Berufserfahrung gute Chancen auf einen Einstieg bietet. Es gibt in nahezu jeder Branche Bedarf an Analytikern, die zwar unterschiedliche Jobtitel tragen, aber dieselben Fähigkeiten und Kenntnisse wie Data Analysts benötigen.\n\nWie viel verdienen Data Analysts? \nAntwort: Das Gehalt eines Data Analysts variiert je nach Branche, Unternehmen und Erfahrung. Laut Glassdoor liegt das durchschnittliche Gehalt eines Data Analysts bei 56.000 € pro Jahr. Der Bereich Data Science wächst stetig, wodurch Data Analysts immer gefragter werden und auch gehaltstechnisch gute Karrierechancen bieten.\n\nWas ist ein Bildungsgutschein? \nAntwort: Ein Bildungsgutschein bestätigt, dass ein Kostenträger wie die Agentur für Arbeit oder das Jobcenter die Kosten für eine berufliche Weiterbildung übernimmt. Der Bildungsgutschein wird im Gespräch mit einem Arbeitsvermittler beantragt, wobei geklärt wird, ob die Voraussetzungen für eine finanzielle Förderung erfüllt sind.\n\nWo beantrage ich einen Bildungsgutschein?\n Antwort: Wenn du arbeitslos bist und eine Weiterbildung bei DataSmart Point absolvieren möchtest, kannst du einen Bildungsgutschein über das Arbeitsamt, das Jobcenter oder die Arbeitsagentur beantragen. Mit diesem staatlichen Zuschuss kannst du die Kosten für die Teilnahme an unserem Programm komplett übernehmen lassen.\n\nWie beantrage ich den Bildungsgutschein?\n Antwort: Um einen Bildungsgutschein zu beantragen, vereinbart man einen Termin bei der Agentur für Arbeit oder dem Jobcenter. Während des Termins wird geklärt, ob Bedarf und Anspruch auf die finanzielle Förderung mit einem Bildungsgutschein besteht.\n\nWer hat Anspruch auf einen Bildungsgutschein? \nAntwort: Anspruch auf einen Bildungsgutschein haben Personen mit Wohnsitz in Deutschland, die arbeitslos sind, von Arbeitslosigkeit bedroht sind oder denen relevante Qualifikationen für ihren derzeitigen Beruf fehlen. Ob die Voraussetzungen für die Förderung mit einem Bildungsgutschein gegeben sind, entscheidet der zuständige Berater der Agentur für Arbeit oder des Jobcenters.\n\nWelche Weiterbildungen werden von der Agentur für Arbeit bezahlt? \nAntwort: Die Agentur für Arbeit bezahlt Weiterbildungen, Umschulungen und Ausbildungen in allen Branchen, vorausgesetzt, es besteht ein aktueller Bedarf auf dem Arbeitsmarkt. Der Bildungsträger muss zudem eine AZAV-Zertifizierung haben.\n\nWas ist eine AZAV-Zertifizierung? \nAntwort: AZAV-zertifizierte Bildungsträger erfüllen die Voraussetzungen der Verordnung und Akkreditierung von Arbeitsförderung nach dem Dritten Sozialgesetzbuch und können somit Bildungsgutscheine einlösen. DataSmart Point ist AZAV-zertifiziert.\n\nWie sieht ein Bildungsgutschein aus? \nAntwort: Der Bildungsgutschein ist ein offizielles Dokument, das die Rahmenbedingungen für eine berufliche Weiterbildung festhält. Auf dem Bildungsgutschein sind folgende Informationen vermerkt: Gültigkeitsdauer, Kosten, Weiterbildungsdauer, Bildungsziel, Unterrichtsart, Weiterbildungsstätte, Weiterbildungsort.\n\nGibt es einen Bildungsgutschein für berufstätige Menschen?\n Antwort: Für berufstätige Menschen kommt ein Bildungsgutschein nur in Frage, wenn sie von Arbeitslosigkeit bedroht sind, weil beispielsweise ein Arbeitsvertrag endet, eine Kündigung bevorsteht oder ihnen die beruflichen Qualifikationen fehlen, um den Beruf weiterhin auszuführen."},
            {"role": "user", "content": question}
        ],
        temperature=0.05,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content.strip()

def add_faq(question, answer):
    if not is_question_in_collection(question)[0]:
        faq_collection.insert_one({'question': question, 'answer': answer})
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
        'message': message,
        'timestamp': datetime.now(),
        'status': 'unread',
        'response': None
    })

def get_all_messages():
    return list(messages_collection.find().sort('timestamp', -1))

def respond_to_message(message_id, response):
    messages_collection.update_one(
        {'_id': message_id},
        {'$set': {'response': response, 'status': 'answered'}}
    )

def delete_message(message_id):
    messages_collection.delete_one({'_id': message_id})
