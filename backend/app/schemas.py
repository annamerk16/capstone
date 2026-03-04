from pydantic import BaseModel, EmailStr
from typing import Optional

# Auth schemas
class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Place schemas 
class PlaceCreate(BaseModel):
    place_name: str
    place_lat: float
    place_lng: float
    place_place_type: Optional[str] = "restaurant"
    place_neighborhood: Optional[str] = None
    place_price_level: Optional[int] = None
