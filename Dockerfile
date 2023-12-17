FROM python:3.11

RUN addgroup --gid 1000 dockeruser
RUN adduser --disabled-login --uid 1000 --gid 1000 dockeruser
RUN mkdir -p /app/
RUN chown -R dockeruser:dockeruser /app/

RUN pip install poetry
COPY pyproject.toml poetry.lock ./app/

USER dockeruser
RUN poetry install

COPY . /app
WORKDIR /app


CMD ["poetry", "run", "gunicorn", "hackathon-23-ai-assistant.main:application", "--bind", "0.0.0.0:8081", "--worker-class", "aiohttp.GunicornWebWorker", "--reload"]
