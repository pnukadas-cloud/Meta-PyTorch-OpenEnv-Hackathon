FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md openenv.yaml /app/
COPY index.html /app/index.html
COPY admin-login.html /app/admin-login.html
COPY user-login.html /app/user-login.html
COPY crisis_commander_env /app/crisis_commander_env
COPY server /app/server
COPY static /app/static

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["python", "-m", "server.app"]
