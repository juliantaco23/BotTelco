from fastapi import APIRouter, Request
from app.services import ChatService, UserService
import os
from dotenv import load_dotenv

load_dotenv()

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
    session_history = chat_service.get_session_history(user_id)
    session_history.add_message({"role": "user", "content": message})
    response = chat_service.get_response(message, user_id)
    session_history.add_message({"role": "assistant", "content": response})
    return {"response": response}
