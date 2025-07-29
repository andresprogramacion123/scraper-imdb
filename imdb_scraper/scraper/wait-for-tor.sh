#!/bin/sh

echo "Esperando a que el proxy Tor esté disponible en $1:$2..."

while ! nc -z "$1" "$2"; do
  sleep 1
done

echo "Tor está disponible. Ejecutando scraper..."
exec "$@"
