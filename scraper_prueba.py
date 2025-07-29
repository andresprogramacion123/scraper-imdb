import requests
from bs4 import BeautifulSoup
import json
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
        "DNT": "1"
    }

def get_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(get_random_headers())
    return session

def extraer_links_top_250():
    url = "https://www.imdb.com/chart/top/"
    session = get_session()
    
    # Pequeña pausa inicial
    time.sleep(1)
    
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        print(f"Status code: {resp.status_code}")
        print("📄 Mostrando los primeros 1000 caracteres del HTML recibido:\n")
        print(resp.text[:1000])
        
        if len(resp.text) < 100:
            print("⚠️ Respuesta muy corta, posible bloqueo")
            return []
            
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

    links = []

    # Método 1: Intentar extraer desde JSON-LD
    try:
        json_ld = soup.find("script", type="application/ld+json")
        if json_ld and json_ld.string:
            data = json.loads(json_ld.string)
            if "itemListElement" in data:
                links = [item["item"]["url"] for item in data["itemListElement"][:50]]
                print(f"✅ Encontrados {len(links)} links via JSON-LD")
                print("hola")
                return links
    except Exception as e:
        print(f"⚠️ Error con JSON-LD: {e}")

    # Método 2: Extraer desde la tabla HTML
    try:
        # Buscar enlaces en la tabla de películas
        movie_links = soup.select("h3.ipc-title__text a[href*='/title/']")
        if movie_links:
            links = []
            for link in movie_links[:50]:
                href = link.get('href')
                if href and '/title/' in href:
                    if not href.startswith('http'):
                        href = 'https://www.imdb.com' + href
                    links.append(href)
            print(f"✅ Encontrados {len(links)} links via HTML")
            return links
    except Exception as e:
        print(f"⚠️ Error con HTML parsing: {e}")

    # Método 3: Buscar enlaces en cualquier parte de la página
    try:
        all_links = soup.find_all("a", href=True)
        movie_links = []
        for link in all_links:
            href = link.get('href')
            if href and '/title/tt' in href and '/chart/top' not in href:
                if not href.startswith('http'):
                    href = 'https://www.imdb.com' + href
                if href not in movie_links:
                    movie_links.append(href)
                    if len(movie_links) >= 50:
                        break
        print(f"✅ Encontrados {len(movie_links)} links via búsqueda general")
        return movie_links
    except Exception as e:
        print(f"⚠️ Error con búsqueda general: {e}")

    print("❌ No se pudieron extraer links de películas")
    return []


def extraer_datos_pelicula(url):
    session = get_session()
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"❌ Error accediendo a {url}: {e}")
        return {
            "Título": "Error de conexión",
            "Año": "N/A",
            "Calificación": "N/A",
            "Duración (min)": 0,
            "Metascore": "N/A",
            "Actores": []
        }

    # Intentar extraer datos desde JSON-LD
    try:
        json_ld = soup.find("script", type="application/ld+json")
        if json_ld and json_ld.string:
            data = json.loads(json_ld.string)

            titulo = data.get("name")
            año = data.get("datePublished")
            rating = data.get("aggregateRating", {}).get("ratingValue")
            duracion_iso = data.get("duration")

            # Convertir duración a minutos
            duracion_minutos = 0
            if duracion_iso:
                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duracion_iso)
                if match:
                    horas = int(match.group(1)) if match.group(1) else 0
                    minutos = int(match.group(2)) if match.group(2) else 0
                    duracion_minutos = horas * 60 + minutos

            actores = [a['name'] for a in data.get("actor", [])][:3]

            return {
                "Título": titulo,
                "Año": año,
                "Calificación": rating,
                "Duración (min)": duracion_minutos,
                "Metascore": "N/A",  # Se extraerá por separado
                "Actores": actores
            }
    except Exception as e:
        print(f"⚠️ Error extrayendo JSON-LD de {url}: {e}")

    # Fallback: extraer datos desde HTML
    try:
        # Título
        titulo_tag = soup.select_one("h1[data-testid='hero-title-block__title']")
        titulo = titulo_tag.text.strip() if titulo_tag else "N/A"

        # Año
        año_tag = soup.select_one("span[data-testid='hero-title-block__metadata'] li")
        año = año_tag.text.strip() if año_tag else "N/A"

        # Rating
        rating_tag = soup.select_one("span[data-testid='hero-rating-bar__aggregate-rating__score'] span")
        rating = rating_tag.text.strip() if rating_tag else "N/A"

        # Duración
        duracion_tag = soup.select_one("li[data-testid='title-techspec-runtime']")
        duracion_text = duracion_tag.text.strip() if duracion_tag else ""
        duracion_minutos = 0
        if duracion_text:
            match = re.search(r'(\d+)h\s*(\d+)m', duracion_text)
            if match:
                horas = int(match.group(1))
                minutos = int(match.group(2))
                duracion_minutos = horas * 60 + minutos

        # Actores (primeros 3)
        actores_tags = soup.select("a[data-testid='title-cast-item__actor']")[:3]
        actores = [tag.text.strip() for tag in actores_tags]

        return {
            "Título": titulo,
            "Año": año,
            "Calificación": rating,
            "Duración (min)": duracion_minutos,
            "Metascore": "N/A",
            "Actores": actores
        }
    except Exception as e:
        print(f"⚠️ Error extrayendo HTML de {url}: {e}")
        return {
            "Título": "Error",
            "Año": "N/A",
            "Calificación": "N/A",
            "Duración (min)": 0,
            "Metascore": "N/A",
            "Actores": []
        }


# 🔁 Scrapeo en lote
def scrapear_top_50():
    links = extraer_links_top_250()

    if not links:
        print("❌ No se pudieron obtener links de películas")
        return []

    resultados = []

    print(f"🔎 Obteniendo datos de {len(links)} películas...\n")

    for idx, link in enumerate(links, 1):
        print(f"{idx:02d}. {link}")
        try:
            datos = extraer_datos_pelicula(link)
            resultados.append(datos)
            print(f"   ✅ {datos['Título']}")
            print("Tenemos una peli")
        except Exception as e:
            print(f"   ⚠️ Error en {link}: {e}")
        time.sleep(2)  # Mayor tiempo entre peticiones

    return resultados


# 🔧 Ejecutar todo
if __name__ == "__main__":
    peliculas = scrapear_top_50()

    # Mostrar resultados
    print(f"\n🎬 Resultados obtenidos: {len(peliculas)} películas\n")
    for peli in peliculas:
        print("🎬", peli["Título"])
        for k, v in peli.items():
            if k != "Título":
                print(f"   {k}: {v}")
        print()
