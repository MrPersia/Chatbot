from pymongo import MongoClient
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# db username: mohsen
# db password: yM9AckoSon6JVR2G

# Verbindungsdaten für MongoDB
uri = "mongodb+srv://mohsen:yM9AckoSon6JVR2G@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority&appName=Chatbot-Mohsen"

# Verbindung zur MongoDB herstellen
client = MongoClient(uri)

# Verbindung zur Datenbank und Sammlung herstellen
db = client.chatbot
faq_collection = db.faq

# ChatterBot-Instanz erstellen
# Parameter:
#   name (str): Name des ChatBots
chatbot = ChatBot('MyChatBot')

# Trainer für den ChatBot erstellen
# Parameter:
#   chatbot (ChatBot): Instanz des ChatBots
trainer = ListTrainer(chatbot)

# Alle Fragen und Antworten aus der MongoDB abrufen
faq_list = faq_collection.find()

# Trainiere den ChatBot mit den Fragen und Antworten aus der MongoDB
# Parameter:
#   faq (dict): Einzelne Frage und Antwort aus der MongoDB
for faq in faq_list:
    question = faq['question']
    answer = faq['answer']
    trainer.train([question, answer])

# Beispiel für das Hinzufügen einer neuen Frage und Antwort zur Datenbank
new_faq = {
    'question': 'Was ist der Sinn des Lebens?',
    'answer': 'Das ist eine philosophische Frage, auf die es viele Antworten gibt.'
}
faq_collection.insert_one(new_faq)

# Testen des ChatBots
# Parameter:
#   input_statement (str): Eingabe des Benutzers
# Rückgabe:
#   response (str): Antwort des ChatBots
response = chatbot.get_response('Was ist der Sinn des Lebens?')
print(response)