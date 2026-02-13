FROM python:3.11-slim AS base

WORKDIR /app

# Install build tools and CUPS development headers for pycups
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libcups2-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

FROM base AS test

COPY tests ./tests

CMD ["python", "-m", "unittest", "discover", "-s", "tests"]

FROM base AS runtime

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
