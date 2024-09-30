# FastAPI Project with Docker, Poetry, and DynamoDB Integration

This project is a FastAPI application containerized with Docker. It uses Poetry for dependency management, and supports caching weather data in S3 with logging to DynamoDB.

## Project Structure

```
.
├── app
│   ├── config.py
│   ├── __init__.py
│   ├── main.py
│   ├── routers
│   │   └── wheather_router.py
│   └── utils
│       ├── data_processing.py
│       └── parse_data.py
├── commands
│   └── start_server.sh
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
└── pyproject.toml
```

## Prerequisites

Make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Poetry](https://python-poetry.org/docs/#installation)
- A `.env` file containing the required environment variables (explained below).

## Environment Variables

Create a `.env` file in the project root directory and set the following environment variables:

```
aws_access_key=<your-aws-access-key>
aws_secret_key=<your-aws-secret-key>
s3_bucket_name=<your-s3-bucket-name>
cache_expiry_minutes=<cache-expiry-in-minutes>
weather_api_key=<your-weather-api-key>
dynamodb_table_name=weather_logs
```

These variables are used to interact with the S3 bucket for caching, DynamoDB for logging, and the weather API for fetching data.

## Installation and Setup

### 1. Build and Run with Docker

Ensure that Docker is running on your machine, then use the following commands:

```bash
docker-compose up --build
```

This command will:
- Build the Docker image based on the provided `Dockerfile`.
- Run the FastAPI app in the container, exposing it on port 8000.

Once the container is running, you can access the FastAPI server at `http://localhost:8000`.

### 2. Poetry Setup

If you prefer to run the app locally (without Docker):

1. Install dependencies using Poetry:

```bash
poetry install
```

2. Run the FastAPI application:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Example Request

After running the app, you can fetch weather data for a specific city by accessing the following endpoint:

```http
GET http://localhost:8000/weather/?city={city}
```

Replace `{city}` with the name of the city for which you want to retrieve weather information.

## Adding Environment Variables to Docker

The `.env` file is automatically passed to Docker Compose via the `docker-compose.yml` file:

```yaml
services:
  fastapi:
    ...
    env_file:
      - .env
```

Ensure you have the `.env` file in the root of the project directory before running the Docker container.