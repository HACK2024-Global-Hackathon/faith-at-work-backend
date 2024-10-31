import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# import google.auth
from google.cloud import secretmanager
from google.cloud.firestore_v1.base_query import FieldFilter, Or

import json
import requests
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


    def get_event(self, eventbrite_event_id: str) -> dict:
        """
        {
            "name": {
                "text": "workshop1",
                "html": "workshop1"
            },
            "description": {
                "text": "workshop1",
                "html": "workshop1"
            },
            "url": "https://www.eventbrite.sg/e/workshop1-tickets-1068910523149",
            "start": {
                "timezone": "Asia/Singapore",
                "local": "2024-12-01T10:00:00",
                "utc": "2024-12-01T02:00:00Z"
            },
            "end": {
                "timezone": "Asia/Singapore",
                "local": "2024-12-01T13:00:00",
                "utc": "2024-12-01T05:00:00Z"
            },
            "organization_id": "2448287009931",
            "created": "2024-10-31T06:31:02Z",
            "changed": "2024-10-31T06:31:10Z",
            "published": "2024-10-31T06:31:10Z",
            "capacity": 5,
            "capacity_is_custom": true,
            "status": "live",
            "currency": "SGD",
            "listed": true,
            "shareable": true,
            "invite_only": false,
            "online_event": false,
            "show_remaining": true,
            "tx_time_limit": 1200,
            "hide_start_date": false,
            "hide_end_date": false,
            "locale": "en_US",
            "is_locked": false,
            "privacy_setting": "unlocked",
            "is_series": false,
            "is_series_parent": false,
            "inventory_type": "limited",
            "is_reserved_seating": false,
            "show_pick_a_seat": false,
            "show_seatmap_thumbnail": false,
            "show_colors_in_seatmap_thumbnail": false,
            "source": "api",
            "is_free": true,
            "version": null,
            "summary": "workshop1",
            "facebook_event_id": null,
            "logo_id": "888684053",
            "organizer_id": "100333404671",
            "venue_id": null,
            "category_id": null,
            "subcategory_id": null,
            "format_id": null,
            "id": "1068910523149",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/1068910523149/",
            "is_externally_ticketed": false,
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 1,
                        "y": 1
                    },
                    "width": 1280,
                    "height": 640
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F888684053%2F2434289105731%2F1%2Foriginal.20241031-063104?auto=format%2Ccompress&q=75&sharp=10&s=3aa2a2aacd285a9fcee04d75910077ee",
                    "width": 400,
                    "height": 266
                },
                "id": "888684053",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F888684053%2F2434289105731%2F1%2Foriginal.20241031-063104?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=1%2C1%2C1280%2C640&s=eedb650c5bce221ebcce9a4099ccb81b",
                "aspect_ratio": "2",
                "edge_color": null,
                "edge_color_set": true
            }
        }
        """
        return self.eventbrite_client.get_event(eventbrite_event_id)


    def create_event(self, event_base: EventBase) -> Event:
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

        results = []

        # query by more precise geohash first
        # geohash7: ±0.076 km (0.047 mi; 76 m)
        query = self.events_collection.where(
            filter=FieldFilter("geohash7", "==", encode(event_filter.latitude, event_filter.longitude, 7))
        ).limit(limit)

        docs = query.stream()
        for doc in docs:
            prepared_data = to_prepared_data(doc, event_filter)
            results.append(prepared_data)

        # geohash6: ±0.61 km (0.38 mi; 610 m)
        if len(results) < limit:
            query = self.events_collection.where(
                filter=FieldFilter("geohash6", "==", encode(event_filter.latitude, event_filter.longitude, 6))
            ).limit(limit)

            docs = query.stream()
            for doc in docs:
                prepared_data = to_prepared_data(doc, event_filter)
                results.append(prepared_data)

        # query by less precise geohash and broaden to interest_category match
        if len(results) < limit:
            query = self.events_collection.where(
                filter=Or(
                    [
                        # geohash5: ±2.4 km (1.5 mi; 2,400 m)
                        FieldFilter("geohash5", "==", encode(event_filter.latitude, event_filter.longitude, 5)),
                        FieldFilter("interest_category", "==", event_filter.interest_category),
                        FieldFilter("interest_category", "==", "fellowship"),
                    ]
                )
            ).limit(limit)
            
            docs = query.stream()
            for doc in docs:
                prepared_data = to_prepared_data(doc, event_filter)
                results.append(prepared_data)

        # remove duplicates 
        results = list({d.uuid: d for d in results}.values())

        # highest ranking results at the top of the list
        results = sorted(results[:limit], key=lambda e: e.relevance_score, reverse=True)
        
        if len(results) == 0:
            print("using fallback data...")
            return [
                to_prepared_data(self.events_collection.document("47G9mC5aeSkXx83mD0I2").get())
                # TODO: add more fallback events
            ]
        return results
