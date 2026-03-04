from fastapi import FastAPI
from app.routers import users

app = FastAPI(title="WhatToDo NYC")

app.include_router(users.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "WhatToDo NYC API is running"}