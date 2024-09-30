from fastapi import FastAPI
from .config import settings

from .routers.wheather_router import router as weather_router

app = FastAPI()

app.include_router(weather_router, prefix="/weather")
