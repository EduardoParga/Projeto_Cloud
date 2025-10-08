FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# dependências do sistema para psycopg2 e build de wheels se necessário
RUN apt-get update && apt-get install -y gcc libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# copiar código
COPY . /app

# instalar deps: usa requirements.txt se existir, senão instala libs mínimas
RUN pip install --upgrade pip setuptools wheel
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install azure-storage-blob lxml psycopg2-binary; fi

# manter o container rodando para executar comandos via docker-compose exec
CMD ["tail", "-f", "/dev/null"]