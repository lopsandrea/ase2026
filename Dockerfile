FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates fonts-liberation libnss3 libxss1 libgbm1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libdrm2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY doc2test ./doc2test
RUN pip install --upgrade pip && pip install .

COPY baselines ./baselines
COPY mutation_tool ./mutation_tool
COPY evaluation ./evaluation
COPY uats ./uats
COPY scripts ./scripts

ENV DOC2TEST_CACHE_DIR=/cache
RUN mkdir -p /cache

ENTRYPOINT ["doc2test"]
CMD ["--help"]
