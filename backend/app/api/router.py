from fastapi import APIRouter

from app.api.routers import auth, places, recommendations

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(places.router, tags=["places"])
api_router.include_router(recommendations.router, tags=["recommendations"])
