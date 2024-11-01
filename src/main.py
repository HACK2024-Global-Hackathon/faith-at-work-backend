import os
import uvicorn
from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from time import time
from typing import Optional
from utils.events_manager import EventsManager
from schema.event import EventFilter, EventBase
from schema.profile import UserProfile
from functools import lru_cache

mgr = EventsManager()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limit: int, window: int):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        fingerprint = request.headers.get("X-Device-Fingerprint", "default_fingerprint")
        
        current_time = time()
        request_count, first_request_time = self.requests.get(fingerprint, (0, current_time))

        # Reset the count if the time window has passed
        if current_time - first_request_time > self.window:
            request_count = 0
            first_request_time = current_time

        if request_count >= self.limit:
            # raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "detail": "Rate limit exceeded",
                    # "allowed_requests": self.limit,
                    # "reset_after": int(self.window - (current_time - first_request_time)),
                },
            )

        # Update the request count and timestamp
        self.requests[fingerprint] = (request_count + 1, first_request_time)

        response = await call_next(request)
        return response

app = FastAPI(middleware=[
    Middleware(RateLimitMiddleware, limit=10, window=10)
])

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=10)
def load_data(
    latitude: float, 
    longitude: float, 
    interest_category: str, 
    limit=100,
):
    return mgr.get_relevant_events(
        event_filter=EventFilter(
            interest_category=interest_category,
            latitude=latitude,
            longitude=longitude,
        ),
        user_profile=UserProfile(
            primary_church="wesley_methodist",
            life_stage="married_with_kids",
            age_bracket="30-39",
            gender="male",
            industry="tech",
        ),
        limit=limit,
    )


@app.get("/")
async def root():
    return {"message": "Hallelujah!"}


@app.get("/events")
async def get_relevant_events(
    latitude: float, 
    longitude: float, 
    interest_category: str, 
    limit=100,
):
    return load_data(latitude, longitude, interest_category, limit=limit)


@app.get("/eventbrite_event")
async def get_event_by_id(event_id):
    return mgr.get_event(event_id)


@app.post("/event/")
async def create_event(event: EventBase):
    return mgr.create_event(event)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('PORT', '8080')), reload=True)
