from __future__ import annotations

import enum
import uuid
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    customer = "customer"
    reviewer = "reviewer"
    seller = "seller"
    admin = "admin"


class PlaceSource(str, enum.Enum):
    google = "google"
    internal = "internal"


class PlaceType(str, enum.Enum):
    restaurant = "restaurant"
    event = "event"
    activity = "activity"


class AuthenticityLabel(str, enum.Enum):
    authentic = "authentic"
    touristy = "touristy"


enum_values = lambda enum_cls: [item.value for item in enum_cls]


class User(Base):
    __tablename__ = "User"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_full_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    user_password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    user_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, values_callable=enum_values),
        nullable=False,
        default=UserRole.customer,
    )
    user_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    authenticity_votes = relationship("AuthenticityVote", back_populates="user", cascade="all, delete-orphan")


class Place(Base):
    __tablename__ = "Place"

    place_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_google_place_id: Mapped[Optional[str]] = mapped_column(Text, unique=True, nullable=True)
    place_source: Mapped[PlaceSource] = mapped_column(
        Enum(PlaceSource, native_enum=False, values_callable=enum_values),
        nullable=False,
        default=PlaceSource.google,
    )
    place_place_type: Mapped[PlaceType] = mapped_column(
        Enum(PlaceType, native_enum=False, values_callable=enum_values),
        nullable=False,
    )
    place_name: Mapped[str] = mapped_column(Text, nullable=False)
    place_formatted_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_neighborhood: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_lat: Mapped[float] = mapped_column(nullable=False)
    place_lng: Mapped[float] = mapped_column(nullable=False)
    place_price_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    place_phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_managed_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("User.user_id"), nullable=True
    )
    place_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    place_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("place_price_level IS NULL OR (place_price_level >= 1 AND place_price_level <= 4)", name="price_level_range"),
    )

    hours = relationship("PlaceHour", back_populates="place", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="place", cascade="all, delete-orphan")
    authenticity_votes = relationship("AuthenticityVote", back_populates="place", cascade="all, delete-orphan")
    tags = relationship("PlaceTag", back_populates="place", cascade="all, delete-orphan")
    promotions = relationship("Promotion", back_populates="place", cascade="all, delete-orphan")


class PlaceHour(Base):
    __tablename__ = "PlaceHour"

    place_hour_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), nullable=False)
    place_hour_day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    place_hour_open_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    place_hour_close_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    place_hour_is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (UniqueConstraint("place_id", "place_hour_day_of_week", name="uq_place_day"),)

    place = relationship("Place", back_populates="hours")


class Review(Base):
    __tablename__ = "Review"

    review_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("User.user_id"), nullable=False)
    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), nullable=False)
    review_rating_overall: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    review_rating_value: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    review_rating_vibe: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    review_rating_groupfit: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    review_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "place_id", name="uq_review_user_place"),
    )

    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")


class AuthenticityVote(Base):
    __tablename__ = "AuthenticityVote"

    authenticity_vote_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("User.user_id"), nullable=False)
    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), nullable=False)
    authenticity_vote_label: Mapped[AuthenticityLabel] = mapped_column(
        Enum(AuthenticityLabel, native_enum=False, values_callable=enum_values),
        nullable=False,
    )
    authenticity_vote_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "place_id", name="uq_auth_vote_user_place"),)

    user = relationship("User", back_populates="authenticity_votes")
    place = relationship("Place", back_populates="authenticity_votes")


class Tag(Base):
    __tablename__ = "Tag"

    tag_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tag_name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    place_tags = relationship("PlaceTag", back_populates="tag", cascade="all, delete-orphan")


class PlaceTag(Base):
    __tablename__ = "PlaceTag"

    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(String(36), ForeignKey("Tag.tag_id"), primary_key=True)

    place = relationship("Place", back_populates="tags")
    tag = relationship("Tag", back_populates="place_tags")


class Promotion(Base):
    __tablename__ = "Promotion"

    promotion_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), nullable=False)
    seller_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("User.user_id"), nullable=False)
    promotion_title: Mapped[str] = mapped_column(Text, nullable=False)
    promotion_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    promotion_boost_factor: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    promotion_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    promotion_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    promotion_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    place = relationship("Place", back_populates="promotions")


class WeatherSnapshot(Base):
    __tablename__ = "WeatherSnapshot"

    weather_snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    weather_snapshot_lat_bucket: Mapped[float] = mapped_column(nullable=False)
    weather_snapshot_lng_bucket: Mapped[float] = mapped_column(nullable=False)
    weather_snapshot_fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    weather_snapshot_data_json: Mapped[dict] = mapped_column(JSON, nullable=False)


class SavedList(Base):
    __tablename__ = "SavedList"

    saved_list_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("User.user_id"), nullable=False)
    saved_list_name: Mapped[str] = mapped_column(Text, nullable=False)
    saved_list_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "saved_list_name", name="uq_saved_list_user_name"),)

    user = relationship("User")
    items = relationship("SavedListItem", back_populates="saved_list", cascade="all, delete-orphan")


class SavedListItem(Base):
    __tablename__ = "SavedListItem"

    saved_list_id: Mapped[str] = mapped_column(String(36), ForeignKey("SavedList.saved_list_id"), primary_key=True)
    place_id: Mapped[str] = mapped_column(String(36), ForeignKey("Place.place_id"), primary_key=True)
    saved_list_item_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    saved_list = relationship("SavedList", back_populates="items")