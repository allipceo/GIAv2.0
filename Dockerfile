FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV APP_VERSION=0.0.1

CMD ["/bin/sh", "-c", "GIT_SHA=${GIT_SHA:-dev} ./start.sh"]


