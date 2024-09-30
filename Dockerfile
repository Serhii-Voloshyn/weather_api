FROM python:3.12


RUN mkdir "backend"

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml

RUN python -m pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY ./app ./app
COPY ./commands ./commands

RUN chmod +x commands/*.sh

CMD ["bash", "commands/start_server.sh"]