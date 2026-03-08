import requests
import os
from app.database import GOOGLE_PLACES_API_KEY

def search_nyc_restaurants(query: str = "restaurants in NYC", max_results: int = 20):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY,
        "type": "restaurant"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("status") != "OK":
        raise Exception(f"Google Places API error: {data.get('status')}")
    
    places = []
    for result in data.get("results", [])[:max_results]:
        place = {
            "place_google_place_id": result.get("place_id"),
            "place_source": "google",
            "place_place_type": "restaurant",
            "place_name": result.get("name"),
            "place_formatted_address": result.get("formatted_address"),
            "place_lat": result["geometry"]["location"]["lat"],
            "place_lng": result["geometry"]["location"]["lng"],
            "place_price_level": result.get("price_level"),
        }
        places.append(place)
    
    return places


def seed_places_from_google(query: str = "restaurants in NYC", max_results: int = 20):
    from app.database import supabase
    
    places = search_nyc_restaurants(query, max_results)
    
    inserted = []
    skipped = []
    
    for place in places:
        existing = supabase.table("Place").select("place_id").eq(
            "place_google_place_id", place["place_google_place_id"]
        ).execute()
        
        if existing.data:
            skipped.append(place["place_name"])
            continue
        
        result = supabase.table("Place").insert(place).execute()
        inserted.append(place["place_name"])
    
    return {"inserted": inserted, "skipped": skipped}