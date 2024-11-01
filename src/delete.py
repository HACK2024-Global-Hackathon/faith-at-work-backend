import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils.secret_manager import get_secret

import json
import requests

url = "http://localhost:8080/event/"


DOC_IDS = [
	# document ids that need to be deleted
]

try: 
    firebase_admin.initialize_app(
        credentials.Certificate(
            json.loads(get_secret("firestore-keyfile"))
        )
    )
except ValueError:
    """
    ValueError: The default Firebase app already exists.
    This means you called initialize_app() more than once without providing an app name as the second argument.
    In most cases you only need to call initialize_app() once.
    But if you do want to initialize multiple apps, pass a second argument to initialize_app() to give each app a unique name.
    """
    pass

db = firestore.client()

for doc_id in DOC_IDS:
	db.collection("activities").document(doc_id).delete()
