FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev
RUN poetry run pip install --no-cache-dir torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu


FROM python:3.10-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
ENV PORT=8000 \
    HOST=0.0.0.0

RUN apt update && \
    apt install --no-install-recommends -y build-essential curl&& \
    apt clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# Necessary Files
COPY models/ /app/models/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY main.py /app/

# Expose port
EXPOSE $PORT

CMD python -m uvicorn main:app --proxy-headers --host $HOST --port $PORT --workers 1 --forwarded-allow-ips '*'