import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from time import time
from typing import Optional
from utils.firestore_client import FirestoreClient

fc = FirestoreClient()


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


@app.get("/")
async def root():
    return {"message": "Hallelujah!"}


@app.get("/events")
async def get_events(latitude: float, longitude: float, category: str, primary_church: str, age_bracket: str = "30-39", gender: str = "male", limit=5):
    return fc.get_nearest_events(
        latitude,
        longitude,
        category,
        primary_church,
        age_bracket,
        gender,
        limit=limit
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('PORT', '8080')), reload=True)
