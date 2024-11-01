import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils.secret_manager import get_secret

import json
import requests

url = "http://localhost:8080/event/"

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
src_collection = db.collection('activities_golden_dataset')

docs = src_collection.stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
    src_data = doc.to_dict()

    payload = json.dumps({
      "datetime_start": src_data["datetime_start"],
      "datetime_end": src_data["datetime_end"],
      "description": src_data["description"],
      "image_url": src_data["image_url"],
      "interest_category": src_data["interest_category"],
      "latitude": src_data["latitude"],
      "longitude": src_data["longitude"],
      "summary": src_data["summary"],
      "title": src_data["title"],
      "organizer": src_data["organizer"]
    })
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    print(response.json())
