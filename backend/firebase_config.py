import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

firebase_config = json.loads(os.getenv("FIREBASE_CONFIG"))


if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()