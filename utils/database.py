import os
from openai import OpenAI
from pymongo import MongoClient
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

