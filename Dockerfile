FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

COPY run_pipeline.sh /usr/local/bin/run_pipeline.sh
RUN chmod +x /usr/local/bin/run_pipeline.sh

ENTRYPOINT ["/usr/local/bin/run_pipeline.sh"]