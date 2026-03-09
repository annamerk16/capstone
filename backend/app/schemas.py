from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import AuthenticityLabel, PlaceSource, PlaceType, UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    user_full_name: str
    user_email: EmailStr
    user_role: UserRole


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    user_email: EmailStr
    password: str


class UserOut(UserBase):
    user_id: str
    user_created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaceCreate(BaseModel):
    place_place_type: PlaceType
    place_name: str
    place_formatted_address: str | None = None
    place_neighborhood: str | None = None
    place_lat: float
    place_lng: float
    place_price_level: int | None = Field(default=None, ge=1, le=4)
    place_phone: str | None = None
    place_website: str | None = None


class PlaceOut(BaseModel):
    place_id: str
    place_google_place_id: str | None
    place_source: PlaceSource
    place_place_type: PlaceType
    place_name: str
    place_formatted_address: str | None
    place_neighborhood: str | None
    place_lat: float
    place_lng: float
    place_price_level: int | None
    place_phone: str | None
    place_website: str | None
    place_managed_by_user_id: str | None

    model_config = ConfigDict(from_attributes=True)


class PlaceSearchOut(BaseModel):
    items: list[PlaceOut]


class ReviewCreate(BaseModel):
    place_id: str
    rating_overall: int = Field(ge=1, le=5)
    rating_value: int | None = Field(default=None, ge=1, le=5)
    rating_vibe: int | None = Field(default=None, ge=1, le=5)
    rating_groupfit: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None


class ReviewOut(BaseModel):
    review_id: str
    user_id: str
    place_id: str
    review_rating_overall: int
    review_rating_value: int | None
    review_rating_vibe: int | None
    review_rating_groupfit: int | None
    review_comment: str | None
    review_created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthenticityVoteIn(BaseModel):
    place_id: str
    label: AuthenticityLabel


class AuthenticityOut(BaseModel):
    place_id: str
    authentic_count: int
    touristy_count: int
    score: float


class RecommendationRequest(BaseModel):
    keywords: str
    budget: int = Field(ge=1, le=4)
    group_size: int = Field(ge=1)
    preference: Literal["indoor", "outdoor", "either"]
    lat: float
    lng: float
    radius_km: float = Field(gt=0)


class RecommendationItem(BaseModel):
    place_id: str
    name: str
    price_level: int | None
    lat: float
    lng: float
    distance_km: float
    score: float
    why: str


class RecommendationResponse(BaseModel):
    results: list[RecommendationItem]