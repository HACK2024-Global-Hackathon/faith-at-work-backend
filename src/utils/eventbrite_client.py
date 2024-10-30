import os
import requests
import json

EVENTBRITE_API_KEY = os.environ.get("EVENTBRITE_API_KEY", "MYZF2ADC5S74OO76JFLO")
EVENTBRITE_ORGANIZER_ID = os.environ.get("EVENTBRITE_ORGANIZER_ID", "2448287009931")


class EventbriteClient():
    def __init__(self):
        self.headers = {
          'Content-Type': 'application/json',
          'Authorization': f'Bearer {EVENTBRITE_API_KEY}',
        }

    def create_event(self):
        # Create an event draft
        url = f"https://www.eventbriteapi.com/v3/organizations/{EVENTBRITE_ORGANIZER_ID}/events/"

        payload = json.dumps({
          "event": {
            "name": {
              "html": "My New Event4"
            },
            "start": {
              "timezone": "Asia/Singapore",
              "utc": "2024-12-01T02:00:00Z"
            },
            "end": {
              "timezone": "Asia/Singapore",
              "utc": "2024-12-01T05:00:00Z"
            },
            "summary": "my summary",
            "currency": "SGD",
            "online_event": False,
            "listed": True,
            "shareable": True,
            "invite_only": False,
            "show_remaining": True,
            "capacity": 5
          }
        })

        response = requests.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()
        print(response.json())

        EVENT_ID = response.json()["id"]

        # Create a ticket class
        url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/ticket_classes/"

        payload = json.dumps({
          "ticket_class": {
            "name": "Participant",
            "quantity_total": 5,
            "free": True
          }
        })

        response = requests.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()
        print(response.json())

        # Publish the event
        url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/publish/"

        payload = {}
        response = requests.request("POST", url, headers=self.headers, data={})
        response.raise_for_status()
        print(response.status_code)

        if not response.json()["published"]:
            raise Exception(f"failed to publish event: {response.reason}")

        print(response.json())

        # Get media upload instructions
        media_upload_url = "https://www.eventbriteapi.com/v3/media/upload/"
        upload_params = {
            'type': 'image-event-logo',
            'token': EVENTBRITE_API_KEY
        }
        
        response = requests.get(media_upload_url, params=upload_params)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)

        # Upload the image from file
        upload_url = response_data['upload_url']
        print(f"upload_url: {upload_url}")
        file_param_name = response_data['file_parameter_name']
        print(file_param_name)
        
        with open('../assets/1483741-381095183.jpg', 'rb') as img_file:
            file_data = {file_param_name: img_file}

            upload_response = requests.post(
                upload_url,
                data=response_data['upload_data'],
                files=file_data
            )
            upload_response.raise_for_status()
        
        # Notify that the media was uploaded
        notify_url = media_upload_url + '?token=' + EVENTBRITE_API_KEY # TODO: properly URL encode token
        update_data = json.dumps({'upload_token': response_data['upload_token'], 'crop_mask': {'top_left': {'y':1, 'x':1}, 'width':1280, 'height':640}})
        update_response = requests.post(notify_url, headers=self.headers, data=update_data) 
        update_response.raise_for_status()

        # Assign the uploaded image to the event
        uploaded_image_id = update_response.json()['id']
        event_update_url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/"
        update_data = json.dumps({"event": {"logo_id": uploaded_image_id}})
        response = requests.post(event_update_url, headers=self.headers, data=update_data)
        response.raise_for_status()

        return response.json()
