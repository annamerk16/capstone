from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import AuthenticityLabel, Place, PlaceTag
from app.schemas import RecommendationItem, RecommendationRequest
from app.utils.geo import haversine_km


@dataclass
class ScoreBreakdown:
    keyword_relevance: float
    distance_score: float
    price_fit: float
    group_fit: float
    review_strength: float
    authenticity_score: float
    promotion_boost: float


WEIGHTS = {
    "keyword_relevance": 0.25,
    "distance_score": 0.20,
    "price_fit": 0.18,
    "group_fit": 0.12,
    "review_strength": 0.15,
    "authenticity_score": 0.10,
    "promotion_boost": 0.00,
}


def get_recommendations(db: Session, req: RecommendationRequest) -> list[RecommendationItem]:
    candidates = _load_candidates(db)
    scored: list[tuple[RecommendationItem, float]] = []

    for place in candidates:
        distance_km = haversine_km(req.lat, req.lng, place.place_lat, place.place_lng)
        if distance_km > req.radius_km:
            continue
        if req.budget and place.place_price_level and place.place_price_level > req.budget:
            continue

        breakdown = _score_place(place=place, req=req, distance_km=distance_km)
        score = sum(WEIGHTS[key] * getattr(breakdown, key) for key in WEIGHTS)
        why = _build_why(breakdown)

        item = RecommendationItem(
            place_id=place.place_id,
            name=place.place_name,
            price_level=place.place_price_level,
            lat=place.place_lat,
            lng=place.place_lng,
            distance_km=round(distance_km, 2),
            score=round(score, 3),
            why=why,
        )
        scored.append((item, score))

    scored.sort(key=lambda entry: entry[1], reverse=True)
    return [item for item, _ in scored[:10]]


def _load_candidates(db: Session) -> list[Place]:
    query = (
        select(Place)
        .options(
            selectinload(Place.tags).selectinload(PlaceTag.tag),
            selectinload(Place.hours),
            selectinload(Place.reviews),
            selectinload(Place.authenticity_votes),
            selectinload(Place.promotions),
        )
        .order_by(Place.place_created_at.desc())
    )
    return list(db.scalars(query).all())


def _score_place(
    *,
    place: Place,
    req: RecommendationRequest,
    distance_km: float,
) -> ScoreBreakdown:
    return ScoreBreakdown(
        keyword_relevance=_keyword_relevance(place, req.keywords),
        distance_score=min(1.0, 1 / (distance_km + 0.1) / 2),
        price_fit=_price_fit(req.budget, place.place_price_level),
        group_fit=_group_fit(req.group_size, place),
        review_strength=_review_strength(place),
        authenticity_score=_authenticity_score(place),
        promotion_boost=_promotion_boost(place),
    )


def _keyword_relevance(place: Place, keywords: str) -> float:
    tokens = [t.strip().lower() for t in keywords.split() if t.strip()]
    if not tokens:
        return 0.0

    searchable = [place.place_name.lower()]
    if place.place_neighborhood:
        searchable.append(place.place_neighborhood.lower())
    for place_tag in place.tags:
        if place_tag.tag:
            searchable.append(place_tag.tag.tag_name.lower())
    combined = " ".join(searchable)

    hits = sum(1 for token in tokens if token in combined)
    return hits / len(tokens)


def _price_fit(budget: int, price_level: int | None) -> float:
    if price_level is None:
        return 0.5
    diff = abs(budget - price_level)
    return max(0.0, 1.0 - diff / 3)


def _group_fit(group_size: int, place: Place) -> float:
    if not place.reviews:
        return 0.5
    group_ratings = [r.review_rating_groupfit for r in place.reviews if r.review_rating_groupfit is not None]
    if not group_ratings:
        return 0.5
    avg_group = sum(group_ratings) / len(group_ratings)
    normalized = avg_group / 5
    if group_size >= 6:
        return min(1.0, normalized + 0.05)
    if group_size == 1:
        return max(0.0, normalized - 0.05)
    return normalized


def _review_strength(place: Place) -> float:
    if not place.reviews:
        return 0.4
    avg = sum(r.review_rating_overall for r in place.reviews) / len(place.reviews)
    volume_boost = min(0.2, len(place.reviews) * 0.02)
    return min(1.0, (avg / 5) + volume_boost)


def _authenticity_score(place: Place) -> float:
    if not place.authenticity_votes:
        return 0.5
    authentic = sum(1 for v in place.authenticity_votes if v.authenticity_vote_label == AuthenticityLabel.authentic)
    touristy = sum(1 for v in place.authenticity_votes if v.authenticity_vote_label == AuthenticityLabel.touristy)
    total = authentic + touristy
    if total == 0:
        return 0.5
    return authentic / total


def _promotion_boost(place: Place) -> float:
    now = datetime.now(timezone.utc)
    active = [p for p in place.promotions if p.promotion_start_at <= now <= p.promotion_end_at]
    if not active:
        return 0.0
    boost = max(float(p.promotion_boost_factor) for p in active)
    return min(1.0, (boost - 1.0) / 2.0)


def _build_why(breakdown: ScoreBreakdown) -> str:
    labels = {
        "keyword_relevance": "strong keyword match",
        "distance_score": "close by",
        "price_fit": "good value for budget",
        "group_fit": "group-friendly",
        "review_strength": "highly rated",
        "authenticity_score": "high authenticity",
        "promotion_boost": "active promotion",
    }
    factors = sorted(
        ((key, WEIGHTS[key] * getattr(breakdown, key)) for key in WEIGHTS),
        key=lambda item: item[1],
        reverse=True,
    )
    top = [labels[key] for key, value in factors if value > 0][:3]
    if not top:
        top = ["balanced fit"]
    return ", ".join(top)