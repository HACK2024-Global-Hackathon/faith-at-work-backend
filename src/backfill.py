import requests
import json
import random

url = "http://localhost:8080/event/"

with open("./assets/demo_data.json", "r") as f:
	demo_data = json.loads(f.read())

random.shuffle(demo_data)
demo_data =random.sample(demo_data, 10000)
total = len(demo_data)

for i, d in enumerate(demo_data):
	print(f"dumping: {i}/{total}")
	url = "http://localhost:8080/event/"

	payload = json.dumps({
	  "datetime_start": d["datetime_start"],
	  "datetime_end": d["datetime_end"],
	  "description": "",
	  "image_url": d["image_url"],
	  "interest_category": d["interest_category"],
	  "latitude": d["latitude"],
	  "longitude": d["longitude"],
	  "summary": d["summary"],
	  "title": d["title"],
	  "organizer": d["organizer"]
	})
	headers = {
	  'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)
	response.raise_for_status()
