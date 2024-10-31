from pydantic import BaseModel


class UserProfile(BaseModel):
    primary_church: str
    life_stage: str
    age_bracket: str
    gender: str
    industry: str


class OrganizerProfile(BaseModel):
	pass
