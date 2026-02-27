FROM python:3.11-slim AS base

WORKDIR /app

# Build tools, CUPS for pycups, and WeasyPrint system deps (libpango, cairo, gdk-pixbuf)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		libcups2-dev \
		libpango-1.0-0 \
		libpangoft2-1.0-0 \
		libgdk-pixbuf-2.0-0 \
		libffi-dev \
		shared-mime-info \
		libcairo2 \
		libpangocairo-1.0-0 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar estructura DDD
COPY domain ./domain
COPY application ./application
COPY infrastructure ./infrastructure
COPY alembic.ini ./

FROM base AS test

COPY tests ./tests

RUN mkdir -p /app/.data && touch /app/.data/rine_test.db

CMD ["pytest", "tests/", "-v", "--tb=short"]

FROM base AS runtime

CMD ["uvicorn", "infrastructure.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
