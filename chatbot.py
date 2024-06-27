# # chatbot.py

# Verbindung mit dem MongoDB-Client
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://mohsen:yM9AckoSon6JVR2G@chatbot-mohsen.ns8oyv4.mongodb.net/?retryWrites=true&w=majority&appName=Chatbot-Mohsen"
client = MongoClient(uri)

# Verbinden und Überprüfen
try:
    client.admin.command('ping')
    print("Erfolgreich mit MongoDB verbunden!")
except Exception as e:
    print("Verbindung zu MongoDB fehlgeschlagen:", e)




# # from chatterbot import ChatBot
# # from chatterbot.trainers import ListTrainer

# # chatbot = ChatBot("Chatpot")

# # trainer = ListTrainer(chatbot)
# # trainer.train([
# #     "Hi",
# #     "Welcome, friend 🤗",
# # ])
# # trainer.train([
# #     "Are you a plant?",
# #     "No, I'm the pot below the plant!",
# # ])

# # exit_conditions = (":q", "quit", "exit")
# # while True:
# #     query = input("> ")
# #     if query in exit_conditions:
# #         break
# #     else:
# #         print(f"🪴 {chatbot.get_response(query)}")



