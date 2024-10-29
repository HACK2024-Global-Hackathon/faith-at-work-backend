import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils.geo_utils import encode, decode, euclidean_distance
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import List, Dict


class FirestoreClient():
    def __init__(self):
        # Initialize the app with a service account, granting admin privileges
        cred = credentials.Certificate('/mnt/c/Users/tommy/.ssh/firestore.json')

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
            category: str,
            primary_church: str,
            age_bracket: str,
            gender: str,
            limit: int = 5
        ) -> List[Dict[str, str]]:

        query = self.db.collection('events').where(filter=FieldFilter("geohash7", "==", encode(latitude, longitude, 6))).limit(limit)
        results = []
        docs = query.stream()
        for doc in docs:
            d = doc.to_dict()
            print(dir(doc))
            print(d)
            results.append(
                {
                    "uuid": doc.id,
                    "geohash7": d["geohash7"],
                    # "image": d["image"]
                    # "title": d["title"]
                    # "summary": d["summary"],
                    # "eventbrite_url": d["eventbrite_url"],
                }
            )
        return results
