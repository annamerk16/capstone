from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models import Place, PlaceSource, PlaceTag, User, UserRole
from app.schemas import PlaceCreate, PlaceOut, PlaceSearchOut

router = APIRouter()


@router.get("/places/search", response_model=PlaceSearchOut)
def search_places(
    query: str | None = Query(default=None),
    neighborhood: str | None = Query(default=None),
    price_level: int | None = Query(default=None, ge=1, le=4),
    place_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PlaceSearchOut:
    places = list(
        db.scalars(
            select(Place)
            .options(selectinload(Place.tags).selectinload(PlaceTag.tag))
            .order_by(Place.place_created_at.desc())
        ).all()
    )

    filtered: list[Place] = []
    for place in places:
        if query and query.lower() not in place.place_name.lower():
            continue
        if neighborhood and place.place_neighborhood and neighborhood.lower() not in place.place_neighborhood.lower():
            continue
        if price_level and place.place_price_level and place.place_price_level != price_level:
            continue
        if place_type and place.place_place_type.value != place_type.lower():
            continue
        filtered.append(place)

    return PlaceSearchOut(items=[PlaceOut.model_validate(p) for p in filtered])


@router.get("/places/{place_id}", response_model=PlaceOut)
def get_place(place_id: str, db: Session = Depends(get_db)) -> PlaceOut:
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return PlaceOut.model_validate(place)


@router.post("/places", response_model=PlaceOut)
def create_place(
    payload: PlaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.seller, UserRole.admin)),
) -> PlaceOut:
    place = Place(
        place_source=PlaceSource.internal,
        place_place_type=payload.place_place_type,
        place_name=payload.place_name,
        place_formatted_address=payload.place_formatted_address,
        place_neighborhood=payload.place_neighborhood,
        place_lat=payload.place_lat,
        place_lng=payload.place_lng,
        place_price_level=payload.place_price_level,
        place_phone=payload.place_phone,
        place_website=payload.place_website,
        place_managed_by_user_id=current_user.user_id if current_user.user_role == UserRole.seller else None,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return PlaceOut.model_validate(place)


@router.get("/places", response_model=PlaceSearchOut)
def list_places(db: Session = Depends(get_db)) -> PlaceSearchOut:
    places = list(
        db.scalars(
            select(Place).order_by(Place.place_created_at.desc())
        ).all()
    )
    return PlaceSearchOut(items=[PlaceOut.model_validate(p) for p in places])