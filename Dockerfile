
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock* ./

# Install dependencies (frozen if lock exists, otherwise resolve)
RUN uv sync --no-dev

# Copy the rest of the project
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
