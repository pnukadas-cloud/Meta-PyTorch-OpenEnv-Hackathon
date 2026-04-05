FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md openenv.yaml /app/
COPY crisis_commander_env /app/crisis_commander_env
COPY server /app/server

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["python", "-m", "server.app"]

