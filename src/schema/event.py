from pydantic import BaseModel
from typing import Union, Dict, Optional

from schema.resource import Resource


class EventFilter(BaseModel):
    interest_category: str
    latitude: float
    longitude: float


class EventBase(EventFilter):
    datetime_start: str
    datetime_end: str
    description: Optional[str] = None
    image_url: str
    max_capacity: int = 5
    organizer: str
    resource: Union[str, Resource] = "resources/dXddxiQkQsHBJep7XT7Q"
    summary: str
    title: str


class Event(EventBase):
    eventbrite_event_id: Optional[str] = None
    eventbrite_url: Optional[str] = None
    geohash5: str
    geohash6: str
    geohash7: str
     

class EventResult(Event):
    uuid: str
    distance_m: float
    walking_time_mins: float
    relevance_score: float
