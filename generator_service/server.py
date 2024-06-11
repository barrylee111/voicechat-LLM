from fastapi import FastAPI
from generator_service.routes import router as chat_router

app = FastAPI()

# Include route
app.include_router(chat_router, prefix='/chat')
