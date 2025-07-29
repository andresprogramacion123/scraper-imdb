FROM python:3.11-slim

WORKDIR /app

# Crear directorio de salida para archivos generados
RUN mkdir -p /app/output

# Instala netcat (versión openbsd) y dependencias de Python
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    pip install --no-cache-dir requests beautifulsoup4 pysocks && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY scraper.py .
COPY wait-for-tor.sh .

RUN chmod +x wait-for-tor.sh
CMD ["./wait-for-tor.sh", "tor", "9050", "--", "python", "scraper.py"]



