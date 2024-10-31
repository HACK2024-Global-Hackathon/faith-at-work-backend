from pydantic import BaseModel

class EventFilter(BaseModel):
    interest_category: str
    latitude: float
    longitude: float


class EventBase(EventFilter):
    datetime_start: str
    datetime_end: str
    description: str
    image_url: str
    max_capacity: int = 5
    organizer: str = "#HACK2024"
    resource: str = "/resources/dXddxiQkQsHBJep7XT7Q"
    summary: str
    title: str


class Event(EventBase):
    geohash5: str
    geohash6: str
    geohash7: str
    eventbrite_url: str
        

class EventResult(Event):
    uuid: str
    distance_m: float
    relevance_score: float
