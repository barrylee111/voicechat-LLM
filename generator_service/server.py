from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as chat_router

app = FastAPI()

# Include route
app.include_router(chat_router, prefix='/chat')

origins = [
    'http://localhost',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)