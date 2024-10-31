import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# import google.auth
from google.cloud import secretmanager
from google.cloud.firestore_v1.base_query import FieldFilter, Or

import json
from typing import List, Dict

from utils.geo_utils import encode, decode, euclidean_distance
from utils.eventbrite_client import EventbriteClient
from utils.ranking import calculate_relevance_score
from schema.event import EventBase, Event, EventResult, EventFilter
from schema.profile import UserProfile


def to_prepared_data(doc, event_filter: EventFilter) -> EventResult:
    event = Event(**doc.to_dict())
    elat, elong = decode(event.geohash7)
    dist_m = euclidean_distance(event_filter.latitude, event_filter.longitude, elat, elong)

    return EventResult(
        uuid=doc.id,
        distance_m=dist_m,
        relevance_score=calculate_relevance_score(dist_m, event_filter, event),
        **event.dict(),
    )


class EventsManager():
    def __init__(self):
        client = secretmanager.SecretManagerServiceClient()
        secret_name = "projects/392395172966/secrets/firestore-keyfile/versions/1"
        response = client.access_secret_version(request={"name": secret_name})
        json_data = response.payload.data.decode("utf-8")
        secrets = json.loads(json_data)

        try: 
            firebase_admin.initialize_app(credentials.Certificate(secrets))
        except ValueError:
            """
            ValueError: The default Firebase app already exists.
            This means you called initialize_app() more than once without providing an app name as the second argument.
            In most cases you only need to call initialize_app() once.
            But if you do want to initialize multiple apps, pass a second argument to initialize_app() to give each app a unique name.
            """
            pass

        self.db = firestore.client()
        self.events_collection = self.db.collection('events_tmp')

        self.eventbrite_client = EventbriteClient()


    def create_event(self, event_base: EventBase):
        event = self.eventbrite_client.create_event(event_base)
        print(event.dict())
        self.events_collection.document().set(event.dict())
        return event


    def get_relevant_events(
            self,
            event_filter: EventFilter,
            user_profile: UserProfile,
            limit: int = 100
        ) -> List[EventResult]:

        query = self.events_collection.where(
            filter=Or(
                [
                    FieldFilter("geohash5", "==", encode(event_filter.latitude, event_filter.longitude, 5)),
                    FieldFilter("interest_category", "==", event_filter.interest_category),
                ]
            )
        ).limit(limit)
        results = []
        docs = query.stream()
        for doc in docs:
            prepared_data = to_prepared_data(doc, event_filter)
            results.append(prepared_data)

        # highest ranking results at the top of the list
        results = sorted(results, key=lambda e: e.relevance_score, reverse=True)
        
        if len(results) == 0:
            print("using fallback data...")
            return [
                to_prepared_data(self.events_collection.document("47G9mC5aeSkXx83mD0I2").get())
                # TODO: add more fallback events
            ]
        return results
