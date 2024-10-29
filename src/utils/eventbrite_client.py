import os
import requests
import json

EVENTBRITE_API_KEY = os.environ.get("EVENTBRITE_API_KEY", "")
EVENTBRITE_ORGANIZER_ID = os.environ.get("EVENTBRITE_ORGANIZER_ID", "")

def publish_event():
	headers = {
	  'Content-Type': 'application/json',
	  'Authorization': f'Bearer {EVENTBRITE_API_KEY}',
	}

	# Create an event draft
	url = f"https://www.eventbriteapi.com/v3/organizations/{EVENTBRITE_ORGANIZER_ID}/events/"

	payload = json.dumps({
	  "event": {
	    "name": {
	      "html": "My New Event3"
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

	response = requests.request("POST", url, headers=headers, data=payload)
	print(response.status_code)
	if response.status_code != 200:
		raise Exception(f"failed to create event draft: {response.text}")

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

	response = requests.request("POST", url, headers=headers, data=payload)
	print(response.status_code)
	if response.status_code != 200:
		raise Exception(f"failed to create ticket class: {response.text}")

	print(response.json())

	# Publish the event
	url = f"https://www.eventbriteapi.com/v3/events/{EVENT_ID}/publish/"

	payload = {}
	response = requests.request("POST", url, headers=headers, data={})

	print(response.status_code)
	if response.status_code != 200:
		raise Exception(f"failed to publish event: {response.text}")

	if not response.json()["published"]:
		raise Exception(f"failed to publish event: {response.text}")

	print(response.text)


import requests, urllib


MEDIA_UPLOAD_URL = 'https://www.eventbriteapi.com/v3/media/upload/'

def upload_file(filename):
    instructions_url = MEDIA_UPLOAD_URL + '?' + urllib.parse.urlencode({
        'type': 'image-event-logo',
        'token': EVENTBRITE_API_KEY
    })
    data = requests.get(instructions_url).json()
    post_args = data['upload_data']
    response = requests.post(data['upload_url'],
        data = post_args,
        files = {
            data['file_parameter_name']: open(filename)
        }
    )
    return response, data['upload_token']

response, upload_token = upload_file('../assets/th-300274662.jpg')
print(response.status_code)
print(response.text)
print(upload_token)
