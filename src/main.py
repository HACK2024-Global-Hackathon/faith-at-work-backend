import os
import uvicorn
from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
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

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hallelujah!"}


@app.get("/events")
async def get_events(
    latitude: float, 
    longitude: float, 
    interest_category: str, 
    limit=5,
):
    return fc.get_nearest_events(
        latitude=latitude,
        longitude=longitude,
        interest_category=interest_category,
        primary_church="wesley_methodist",
        life_stage="single_without_kids",
        gender="female",
        age_bracket="30-39",
        limit=limit,
    )


# from pydantic import BaseModel

# class Event(BaseModel):
#     title: str
#     summary: str
#     description: str = None
#     ticket_count: int = 5


# @app.post("/event")
# async def create_event(event: Event):

# from fastapi import File, UploadFile, Form

# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...), event: Event = Form(...)):
#     if file.content_type not in ('image/jpg', 'image/jpeg'):
#         raise HTTPException(status_code=400, detail="Invalid file type. Only JPG files are allowed.")

#     return {"info": f"File '{file.filename}' uploaded successfully!"}


# from fastapi import Form, File, UploadFile
# from pydantic import BaseModel

# class Event(BaseModel):
#     title: str

# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...), event: Event = Form(...)):
#     if file.content_type not in ('image/jpg', 'image/jpeg'):
#         raise HTTPException(status_code=400, detail="Invalid file type. Only JPG files are allowed.")

#     print(type(event))
#     return {"filename": file.filename, "status": event}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('PORT', '8080')), reload=True)
