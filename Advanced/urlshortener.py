import hashlib
import json
import os
import socket
import threading
from urllib.parse import urlparse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

# Constants
HOST = '127.0.0.1'
PORT = 65432
DATABASE_FILE = 'url_database.json'

# Load or initialize the URL database
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'w') as db_file:
        json.dump({}, db_file)

# URL Database Class
class URLDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.load_database()

    def load_database(self):
        with open(self.db_file, 'r') as db_file:
            self.data = json.load(db_file)

    def save_database(self):
        with open(self.db_file, 'w') as db_file:
            json.dump(self.data, db_file)

    def add_url(self, long_url):
        short_url = self.shorten_url(long_url)
        self.data[short_url] = long_url
        self.save_database()
        return short_url

    def shorten_url(self, long_url):
        # Create a unique hash for the URL
        return hashlib.md5(long_url.encode()).hexdigest()[:6]

    def get_url(self, short_url):
        return self.data.get(short_url, None)

# Simple Machine Learning Model for URL Classification
class URLClassifier:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.model = MultinomialNB()
        self.train_model()

    def train_model(self):
        # Sample data for training
        data = [
            ("http://example.com", 0),  # benign
            ("http://malicious.com", 1),  # malicious
        ]
        X, y = zip(*data)
        X = self.vectorizer.fit_transform(X)
        self.model.fit(X, y)

    def predict(self, url):
        X = self.vectorizer.transform([url])
        return self.model.predict(X)[0]

# URL Shortening Service
class URLShortenerService:
    def __init__(self):
        self.database = URLDatabase(DATABASE_FILE)
        self.classifier = URLClassifier()

    def handle_request(self, conn):
        with conn:
            data = conn.recv(1024).decode()
            if not data:
                return
            request = json.loads(data)
            action = request.get('action')
            url = request.get('url')

            if action == 'shorten':
                if self.classifier.predict(url) == 1:
                    response = {'error': 'Malicious URL detected!'}
                else:
                    short_url = self.database.add_url(url)
                    response = {'short_url': short_url}
            elif action == 'retrieve':
                long_url = self.database.get_url(url)
                response = {'long_url': long_url} if long_url else {'error': 'URL not found.'}
            else:
                response = {'error': 'Invalid action.'}

            conn.sendall(json.dumps(response).encode())

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f'Server started at {HOST}:{PORT}')
            while True:
                conn, addr = s.accept()
                print(f'Connected by {addr}')
                threading.Thread(target=self.handle_request, args=(conn,)).start()

if __name__ == "__main__":
    service = URLShortenerService()
    service.start_server()
