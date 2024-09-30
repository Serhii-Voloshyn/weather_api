from fastapi import APIRouter

from app.utils.data_processing import AWSDataProcessor

router = APIRouter()


@router.get(path="/")
async def get_weather(city: str) -> dict:
    forecast = await AWSDataProcessor(city).get_weather_data_with_s3_cache()

    return forecast
