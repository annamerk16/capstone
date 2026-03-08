from fastapi import APIRouter, HTTPException, Depends
from app.schemas import PlaceCreate
from app.database import supabase
from app.auth import get_current_user
from app.google_places import seed_places_from_google

router = APIRouter(prefix="/places", tags=["places"])

@router.post("/")
async def create_place(body: PlaceCreate, current_user=Depends(get_current_user)):
    try:
        response = supabase.table("Place").insert({
            "place_name": body.place_name,
            "place_lat": body.place_lat,
            "place_lng": body.place_lng,
            "place_place_type": body.place_place_type,
            "place_neighborhood": body.place_neighborhood,
            "place_price_level": body.place_price_level,
        }).execute()
        return {"message": "Place created successfully", "place": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def get_places(
    neighborhood: str = None,
    price_level: int = None,
    place_type: str = None
):
    try:
        query = supabase.table("Place").select("*")
        if neighborhood:
            query = query.eq("place_neighborhood", neighborhood)
        if price_level:
            query = query.eq("place_price_level", price_level)
        if place_type:
            query = query.eq("place_place_type", place_type)
        response = query.execute()
        return {"places": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{place_id}")
async def get_place(place_id: str):
    try:
        response = supabase.table("Place").select("*").eq("place_id", place_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Place not found")
        return {"place": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/seed")
async def seed_places(
    query: str = "restaurants in NYC",
    max_results: int = 20,
    current_user=Depends(get_current_user)
):
    try:
        result = seed_places_from_google(query, max_results)
        return {
            "message": f"Seeded {len(result['inserted'])} places",
            "inserted": result["inserted"],
            "skipped": result["skipped"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))