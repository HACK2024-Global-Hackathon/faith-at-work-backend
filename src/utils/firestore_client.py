import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# import google.auth
from google.cloud import secretmanager
from google.cloud.firestore_v1.base_query import FieldFilter

import json
from typing import List, Dict

from utils.geo_utils import encode, decode, euclidean_distance


class FirestoreClient():
    def __init__(self):
        # Initialize the app with a service account, granting admin privileges
        # credentials, project_id = google.auth.default()
        client = secretmanager.SecretManagerServiceClient()
        secret_name = "projects/392395172966/secrets/firestore-keyfile/versions/1"
        response = client.access_secret_version(request={"name": secret_name})

        # Parse the JSON content
        json_data = response.payload.data.decode("utf-8")
        secrets = json.loads(json_data)
        # print(secrets)

        cred = credentials.Certificate(secrets)

        try: 
            firebase_admin.initialize_app(cred)
        except ValueError:
            """
            ValueError: The default Firebase app already exists.
            This means you called initialize_app() more than once without providing an app name as the second argument.
            In most cases you only need to call initialize_app() once.
            But if you do want to initialize multiple apps, pass a second argument to initialize_app() to give each app a unique name.
            """
            pass

        # Create a Firestore client
        self.db = firestore.client()

    def get_nearest_events(
            self,
            latitude: float,
            longitude: float,
            interest_category: str,
            primary_church: str,
            life_stage: str, 
            age_bracket: str,
            gender: str,
            limit: int = 5
        ) -> List[Dict[str, str]]:

        query = self.db.collection('events').where(filter=FieldFilter("geohash7", "==", encode(latitude, longitude, 6))).limit(limit)
        results = []
        docs = query.stream()
        for doc in docs:
            d = doc.to_dict()
            latitude, longitude = decode(d["geohash7"])
            results.append(
                {
                    "uuid": doc.id,
                    "geohash7": d["geohash7"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "interest_category": d.get("interest_category"),
                    "image": d.get("image"),
                    "image_url": d.get("image_url"),
                    "title": d.get("title"),
                    "summary": d.get("summary"),
                    "description": d.get("description"),
                    "source": d.get("source"),
                    "eventbrite_url": d.get("eventbrite_url"),
                }
            )
        if len(results) == 0:
            return [
                {
                    "uuid": None,
                    "geohash7": None,
                    "latitude": latitude,
                    "longitude": longitude,
                    "interest_category": interest_category,
                    "image": None,
                    "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F880368853%2F297979351972%2F1%2Foriginal.20241022-081741?w=940&auto=format%2Ccompress&q=75&sharp=10&s=aa7f1da5ed9c94642ef715f8dc2097d0",
                    "title": "#HACK2024 Showcase Saturday",
                    "summary": "See first-hand the innovative solutions that the teams have worked on for #HACK2024!",
                    "description": "Does your church or organisation face these issues?    Reaching more youths    Meeting community felt needs with other churches    Engaging donors and volunteers    Marketplace outreach & discipleshipFind out how tech can help!#HACK is the largest global Christian hackathon. Attended by thousands over 50 over cities, the Singapore chapter came together to define issues and derive creative solutions for these Kingdom challenges.We invite you to come and see first-hand the prototypes and the solutions, and discover new ways of growth in your ministry!",
                    "source": "Indigitous Singapore",
                    "eventbrite_url": "https://www.eventbrite.com/e/hack2024-showcase-saturday-tickets-1054556018439?utm-campaign=social&utm-content=attendeeshare&utm-medium=discovery&utm-term=listing&utm-source=cp&aff=ebdsshcopyurl",
                },
                # TODO: add more fallback events
            ]
        return results
