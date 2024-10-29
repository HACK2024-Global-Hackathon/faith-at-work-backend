import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils.geo_utils import encode, decode, euclidean_distance
from google.cloud.firestore_v1.base_query import FieldFilter


class FirestoreClient():
    def __init__(self):
        # Initialize the app with a service account, granting admin privileges
        cred = credentials.Certificate('/mnt/c/Users/tommy/.ssh/firestore.json')
        firebase_admin.initialize_app(cred)

        # Create a Firestore client
        self.db = firestore.client()

    def demo_get(self):
        # Specify the collection name you want to fetch documents from
        collection_name = 'test-collection'

        # Fetch all documents in the specified collection
        docs = self.db.collection(collection_name).stream()

        # Print out each document's ID and data
        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')

    def demo_geo(self):
        # self.db.collection('events').document("geotest").set({"geohash7": encode(37.7749, -122.4194, 6)})

        query = self.db.collection('events').where(filter=FieldFilter("geohash7", "==", encode(37.7749, -122.4194, 6)))
        limited_query = query.limit(5)
        docs = limited_query.stream()

        for doc in docs:
            print(doc.id, '->', doc.to_dict())

            event_lat, event_long = decode(doc.to_dict()["geohash7"])

            dist = euclidean_distance(37.8749, -122.4194, event_lat, event_long)
            print(dist)