from pydantic import BaseModel


class Resource(BaseModel):
    source: str
    title: str
    description: str
    summary: str
    url: str
    category: str
