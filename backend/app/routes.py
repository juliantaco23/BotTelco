# backend/app/routes.py

from fastapi import APIRouter, Request
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.services.product_service import ProductService

router = APIRouter()

chat_service = ChatService()
user_service = UserService()

@router.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data["username"]
    password = data["password"]
    success, message = user_service.register_user(username, password)
    return {"message": message}

@router.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data["username"]
    password = data["password"]
    success, message = user_service.authenticate_user(username, password)
    return {"message": message}

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data["user_id"]
    message = data["message"]
    response = chat_service.get_response(message, user_id)
    return {"response": response}
