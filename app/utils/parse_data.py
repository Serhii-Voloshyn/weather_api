import aiohttp

from aiohttp import ClientResponse
from dotenv import load_dotenv
from fastapi import HTTPException

from app.config import settings

load_dotenv()


async def make_request_to_weather_api(city: str) -> ClientResponse:
    """
    Makes a request to the weather API to get the current weather data for a given city.

    Args:
        city (str): The name of the city for which to get the weather data.

    Returns:
        ClientResponse: The response object returned by the aiohttp client.

    Raises:
        HTTPException: If the response status code is not 200.
    """

    headers = {
        'User-Agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }

    api_key = settings.weather_api_key

    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=yes'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                error_data = await resp.json()
                print(error_data)
                raise HTTPException(
                    status_code=resp.status,
                    detail=f"Error fetching weather data: {error_data['error']['message']}"
                )

            data = await resp.json()

    return data
