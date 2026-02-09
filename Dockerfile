FROM python:3.12-slim-bookworm AS base

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM base AS development

COPY requirements_dev.txt .
RUN pip install --no-cache-dir -r requirements_dev.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]


FROM base AS production

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
