FROM python:3.10-slim as builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /app
WORKDIR /app
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root


FROM python:3.10-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl
WORKDIR /app
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv

# Necessary Files
COPY main.py app.py /app/

# Expose port
EXPOSE 8000

CMD ["uvicorn","main:app","--proxy-headers","--host","0.0.0.0","--port","8000","--workers","3"]