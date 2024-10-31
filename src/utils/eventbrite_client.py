import os
import time
import arrow
import requests
import json
from uuid import uuid4
from typing import Optional

from schema.event import EventBase, Event
from schema.resource import Resource
from utils.geo_utils import encode


EVENTBRITE_API_KEY = os.environ.get("EVENTBRITE_API_KEY", "MYZF2ADC5S74OO76JFLO")
EVENTBRITE_ORGANIZER_ID = os.environ.get("EVENTBRITE_ORGANIZER_ID", "2448287009931")


class EventbriteClient():
    def __init__(self):
        self.headers = {
          'Content-Type': 'application/json',
          'Authorization': f'Bearer {EVENTBRITE_API_KEY}',
        }


    def get_event(self, event_id: str) -> dict:
        url = f"https://www.eventbriteapi.com/v3/events/{event_id}"
        response = requests.request("GET", url, headers=self.headers)
        response.raise_for_status()
        return response.json()  # TODO: pydantic model if needed


    def create_event(self, event_base: EventBase, resource: Optional[Resource] = None) -> Event:
        # Create an event draft
        url = f"https://www.eventbriteapi.com/v3/organizations/{EVENTBRITE_ORGANIZER_ID}/events/"

        summary = event_base.summary
        # Event summary. Limited to 140 characters.
        if len(summary) > 140:
            summary = summary[:136] + " ..."
        print(summary)

        payload = json.dumps({
          "event": {
            "name": {
              "html": event_base.title
            },
            "start": {
              "timezone": "Asia/Singapore",
              "utc": arrow.get(event_base.datetime_start, tzinfo="Asia/Singapore").to("UTC").format("YYYY-MM-DDTHH:mm:ss") + "Z"
            },
            "end": {
              "timezone": "Asia/Singapore",
              "utc": arrow.get(event_base.datetime_end, tzinfo="Asia/Singapore").to("UTC").format("YYYY-MM-DDTHH:mm:ss") + "Z"
            },
            "summary": summary,
            "currency": "SGD",
            "online_event": False,
            "listed": True,
            "shareable": True,
            "invite_only": False,
            "show_remaining": True,
            "capacity": event_base.max_capacity
          }
        })

        response = requests.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()

        response_data = response.json()

        EVENT_ID = response_data["id"]
        EVENT_URL = response_data["url"]

        # Create a ticket class
        url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/ticket_classes/"

        payload = json.dumps({
          "ticket_class": {
            "name": "Participant",
            "quantity_total": event_base.max_capacity,
            "free": True
          }
        })

        response = requests.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()

        # Get media upload instructions
        media_upload_url = "https://www.eventbriteapi.com/v3/media/upload/"
        upload_params = {
            'type': 'image-event-logo',
            'token': EVENTBRITE_API_KEY
        }
        
        response = requests.get(media_upload_url, params=upload_params)
        response.raise_for_status()
        media_upload_instructions = response.json()

        # Fetch from image host and upload the image to EventBrite
        response = requests.get(event_base.image_url)
        response.raise_for_status()

        temp_filename = f"{uuid4().hex}.jpg"
        with open(temp_filename, 'wb') as f:
            f.write(response.content)

        # wb+ (write binary and read binary) mode does not seem to work with EventBrite API, so we read the file as a separate step
        with open(temp_filename, 'rb') as temp_file_handle:
            response = requests.post(
                media_upload_instructions['upload_url'],
                data=media_upload_instructions['upload_data'],
                files={media_upload_instructions['file_parameter_name']: temp_file_handle},
            )
            response.raise_for_status()
        
        try:
            os.remove(temp_filename)
        except OSError:
            pass

        # Notify that the media was uploaded
        notify_url = media_upload_url + '?token=' + EVENTBRITE_API_KEY # TODO: properly URL encode token
        update_data = json.dumps({
            'upload_token': media_upload_instructions['upload_token'],
            'crop_mask': {'top_left': {'y':1, 'x':1}, 
            'width':1280, 
            'height':640
        }})
        response = requests.post(notify_url, headers=self.headers, data=update_data) 
        response.raise_for_status()

        # Assign the uploaded image to the event
        uploaded_image_id = response.json()['id']
        event_update_url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/"
        update_data = json.dumps({"event": {"logo_id": uploaded_image_id}})
        response = requests.post(event_update_url, headers=self.headers, data=update_data)
        response.raise_for_status()

        # Add more structured content in the "About this event" section
        # TODO: map suggested resources/videos from input or more dynamically
        if resource:
            url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/structured_content/1/"

            payload = json.dumps({
              "modules": [
                {
                  "type": "text",
                  "data": {
                    "body": {
                      "type": "text",
                      "text": f"<p>Join us for an exciting event!</p><p>For help with organizing, please check out <a href='{resource.url}'>these resources</a>.</p>"
                    }
                  }
                },
                {
                    "type": "video",
                    "data": {
                        "video": {
                            "url": "https://youtu.be/UNluWO_hlkY?si=Ob6UhowWqF-S9xF0",
                            "display_size": "large"
                        }
                    }
                }
              ],
              "purpose": "listing",
              "publish": True
            })

            response = requests.request("POST", url, headers=self.headers, data=payload)
            response.raise_for_status()

        return Event(
            eventbrite_event_id=EVENT_ID,
            eventbrite_url=EVENT_URL,
            geohash5=encode(event_base.latitude, event_base.longitude, 5),
            geohash6=encode(event_base.latitude, event_base.longitude, 6),
            geohash7=encode(event_base.latitude, event_base.longitude, 7),            
            **event_base.dict(),
        )
