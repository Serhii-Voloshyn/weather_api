import json
from uuid import uuid4

import aioboto3
from io import BytesIO
from aiohttp import ClientError
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import time

from fastapi import HTTPException

from app.config import settings
from app.utils.parse_data import make_request_to_weather_api

load_dotenv()


class AWSDataProcessor:
    """Class for processing weather data from the OpenWeatherMap API and caching it in S3."""

    def __init__(self, city: str) -> None:
        self.city = city

    async def get_weather_data_with_s3_cache(self) -> dict:
        """
            Retrieves weather data from S3 cache if available, otherwise makes a request to the
            OpenWeatherMap API and caches the data in S3.

            Raises: HTTPException(status_code=404, detail=f"No cache found for city: {self.city}") if no cache is found.
                    HTTPException(status_code=500, detail=f"Error accessing S3: {e.response['Error']['Message']}") if there is an error accessing S3.

            Returns: A dictionary containing weather data.
        """

        timestamp = time.time()
        cache_key = f"{self.city}_{timestamp}.json"

        async with aioboto3.Session().client(
            's3',
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region_name
        ) as s3_client:
            try:
                response = await s3_client.list_objects(Bucket=settings.s3_bucket_name, Prefix=self.city)
                if 'Contents' in response:
                    last_modified = response['Contents'][-1]['LastModified']
                    current_time = datetime.now(timezone.utc)

                    if current_time - last_modified < timedelta(minutes=settings.cache_expiry_minutes):
                        s3_response = await s3_client.get_object(
                            Bucket=settings.s3_bucket_name,
                            Key=response['Contents'][0]['Key']
                        )

                        return json.loads((await s3_response['Body'].read()).decode('utf-8'))

            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise HTTPException(status_code=404, detail=f"No cache found for city: {self.city}")
                else:
                    raise HTTPException(status_code=500, detail=f"Error accessing S3: {e.response['Error']['Message']}")

        weather_data = await make_request_to_weather_api(self.city)

        await self.__safe_and_log_data(cache_key, weather_data)

        return weather_data

    async def __safe_and_log_data(self, cache_key: str, data: dict) -> None:
        """
            Safely logs and saves the provided data to S3.

            Raises: HTTPException(status_code=500, detail=f"Error caching data: {e}") if there is an error caching the data.
                    HTTPException(status_code=500, detail=f"Error logging event to DynamoDB: {e}") if there is an error logging the event to DynamoDB.

            Returns: None
        """

        await self.__save_json_to_s3(cache_key, data)
        await self.__log_event_to_dynamodb(f's3://{settings.s3_bucket_name}/{cache_key}')

    async def __log_event_to_dynamodb(self, s3_url: str) -> None:
        """
            Logs the event to DynamoDB.

            Raises: HTTPException(status_code=500, detail=f"Error logging event to DynamoDB: {e}") if there is an error logging the event to DynamoDB.

            Returns: None
        """

        async with aioboto3.Session().client(
            'dynamodb',
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region_name
        ) as dynamodb_client:
            table_name = settings.dynamodb_table_name
            timestamp = datetime.now().isoformat()

            await dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    'log_id': {'S': str(uuid4())},
                    'city': {'S': self.city},
                    'timestamp': {'S': timestamp},
                    's3_url': {'S': s3_url}
                }
            )

    async def __save_json_to_s3(self, cache_key: str, data: dict) -> None:
        """
            Saves the provided data as a JSON file to S3.

            Raises: HTTPException(status_code=500, detail=f"Error caching data: {e}") if there is an error caching the data.

            Returns: None
        """

        json_data = json.dumps(data)
        byte_data = BytesIO(json_data.encode('utf-8'))

        async with aioboto3.Session().client(
            's3',
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region_name
        ) as s3_client:
            await s3_client.upload_fileobj(byte_data, settings.s3_bucket_name, cache_key)
