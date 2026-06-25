import firebase_admin
from firebase_admin import credentials, firestore
import os

KEY_PATH = "serviceAccountKey.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection("responses").stream()
count = 0
for doc in docs:
    doc.reference.delete()
    count += 1

print(f"Удалено {count} ответов.")
