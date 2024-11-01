import haversine as hs
from haversine import Unit

import pygeohash as pgh
from typing import Tuple

GOOGLE_MAPS_API_KEY = None # populate this if we are willing to pay for Google Maps API


def encode(latitude: float, longitude: float, precision) -> str:
    return pgh.encode(latitude, longitude, precision=precision)


def decode(geohash: str) -> Tuple[float]:
    return pgh.decode(geohash)


def get_walking_estimate_haversine(latA, longA, latB, longB) -> float:
    distance_m = hs.haversine((latA, longA), (latB, longB), unit=Unit.METERS)
    est_meters_per_second = 0.8  # TODO: this can be adjusted based on age bracket of the user

    return {
        "distance_m": distance_m,
        "walking_time_mins": (distance_m / est_meters_per_second) / 60.0
    }


def get_walking_estimate_google(latA, longA, latB, longB):
    """
    Compute the walking details between point A to point B, using Google Routes API
    Pricing: https://developers.google.com/maps/documentation/routes/usage-and-billing

    Example response:
    {
        "distance_m": 123.4,
        "walking_time_mins": 1.2
    }
    """
    import requests
    import json

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    payload = json.dumps({
      "origin": {
        "location": {
          "latLng": {
            "latitude": latA,
            "longitude": longA
          }
        }
      },
      "destination": {
        "location": {
          "latLng": {
            "latitude": latB,
            "longitude": longB
          }
        }
      },
      "travelMode": "WALK",
      "computeAlternativeRoutes": False
    })
    headers = {
      'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
      'X-Goog-FieldMask': 'routes.distanceMeters,routes.duration',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    response_data = response.json()
    return {
        "distance_m": response_data.distanceMeters,
        "walking_time_mins": response_data.duration / 60.0
    }
