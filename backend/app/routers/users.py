from fastapi import APIRouter, HTTPException
from app.schemas import UserSignUp, UserLogin
from app.database import supabase

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup")
async def signup(body: UserSignUp):
    try:
        response = supabase.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {"data": {"full_name": body.full_name}}
        })
        return {"message": "User created successfully", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(body: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password
        })
        return {
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")