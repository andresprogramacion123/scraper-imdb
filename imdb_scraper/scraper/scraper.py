import requests
from bs4 import BeautifulSoup
import json
import re
import time
import csv
from urllib.parse import urljoin

IMDB_TOP_URL = "https://www.imdb.com/chart/top/"
PROXIES = {
     "http": "socks5h://tor:9050",
     "https": "socks5h://tor:9050"
 }
#PROXIES = None  # Desactivar proxy para pruebas
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def parse_duration(iso_duration):
    """Convierte duración ISO 8601 (PT#H#M) a minutos"""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration)
    if not match:
        return ""
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    return hours * 60 + minutes

############################## Funcion obtener peliculas #########################################################
def get_top_movies():
    print("🔍 Obteniendo lista de películas...")

    try:
        response = requests.get(IMDB_TOP_URL, headers=HEADERS, proxies=PROXIES, timeout=10)
        print(f"✅ Código de estado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al acceder a IMDb: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    movies = []

    # Método 1: Intentar extraer desde JSON-LD
    try:
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag and script_tag.string:
            data = json.loads(script_tag.string)
            if "itemListElement" in data:
                items = data.get("itemListElement", [])
                for entry in items[:50]:
                    item = entry.get("item", {})
                    if item:
                        movie = {
                            "title": item.get("name"),
                            "year": item.get("datePublished", ""),
                            "duration": parse_duration(item.get("duration", "")),
                            "rating": item.get("aggregateRating", {}).get("ratingValue", ""),
                            "ratingCount": item.get("aggregateRating", {}).get("ratingCount", ""),
                            "url": item.get("url"),
                            "genre": item.get("genre"),
                            "description": item.get("description"),
                            "image": item.get("image"),
                        }
                        movies.append(movie)
                print(f"✅ Encontradas {len(movies)} películas via JSON-LD")
                if movies:
                    return movies
    except Exception as e:
        print(f"⚠️ Error con JSON-LD: {e}")

    # Método 2: Extraer desde la tabla HTML
    try:
        movie_links = soup.select("h3.ipc-title__text a[href*='/title/']")
        if movie_links:
            for link in movie_links[:50]:
                href = link.get('href')
                if href and '/title/' in href:
                    if not href.startswith('http'):
                        href = 'https://www.imdb.com' + href
                    
                    # Extraer título del texto del enlace
                    title_text = link.get_text(strip=True)
                    # Remover numeración si existe (ej: "1. The Shawshank Redemption")
                    title = re.sub(r'^\d+\.\s*', '', title_text)
                    
                    movie = {
                        "title": title,
                        "year": "",
                        "duration": "",
                        "rating": "",
                        "ratingCount": "",
                        "url": href,
                        "genre": "",
                        "description": "",
                        "image": "",
                    }
                    movies.append(movie)
            print(f"✅ Encontradas {len(movies)} películas via HTML")
            if movies:
                return movies
    except Exception as e:
        print(f"⚠️ Error con HTML parsing: {e}")

    # Método 3: Buscar enlaces en cualquier parte de la página
    try:
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            href = link.get('href')
            if href and '/title/tt' in href and '/chart/top' not in href:
                if not href.startswith('http'):
                    href = 'https://www.imdb.com' + href
                
                # Evitar duplicados
                if not any(movie['url'] == href for movie in movies):
                    title_text = link.get_text(strip=True)
                    title = re.sub(r'^\d+\.\s*', '', title_text) if title_text else "Unknown"
                    
                    movie = {
                        "title": title,
                        "year": "",
                        "duration": "",
                        "rating": "",
                        "ratingCount": "",
                        "url": href,
                        "genre": "",
                        "description": "",
                        "image": "",
                    }
                    movies.append(movie)
                    if len(movies) >= 50:
                        break
        print(f"✅ Encontradas {len(movies)} películas via búsqueda general")
        if movies:
            return movies
    except Exception as e:
        print(f"⚠️ Error con búsqueda general: {e}")

    print("❌ No se pudieron extraer links de películas")
    return movies
############################## Funcion obtener peliculas #########################################################

############################## Funcion obtener detalles de peliculas #########################################################
def get_movie_details(movie_url):
    """Extrae detalles adicionales de una película específica"""
    if not movie_url.startswith('http'):
        movie_url = urljoin("https://www.imdb.com", movie_url)
    
    print(f"🎬 Obteniendo detalles de: {movie_url}")
    
    try:
        time.sleep(1)  # Rate limiting
        response = requests.get(movie_url, headers=HEADERS, proxies=PROXIES, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code} para {movie_url}")
            return {}
            
    except Exception as e:
        print(f"❌ Error al acceder a {movie_url}: {e}")
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    details = {}
    
    # Intentar extraer datos desde JSON-LD primero
    try:
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag and script_tag.string:
            data = json.loads(script_tag.string)
            
            # Título
            details['title'] = data.get("name", "")
            
            # Año
            details['precise_year'] = data.get("datePublished", "")
            
            # Rating
            details['rating'] = data.get("aggregateRating", {}).get("ratingValue", "")
            
            # Duración
            duration_iso = data.get("duration", "")
            if duration_iso:
                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_iso)
                if match:
                    horas = int(match.group(1)) if match.group(1) else 0
                    minutos = int(match.group(2)) if match.group(2) else 0
                    details['detailed_duration'] = horas * 60 + minutos
            
            # Actores
            actors = []
            actor_data = data.get("actor", [])
            if isinstance(actor_data, list):
                for actor in actor_data[:3]:
                    if isinstance(actor, dict) and 'name' in actor:
                        actors.append(actor['name'])
            details['actors'] = actors
            
            print(f"✅ Datos extraídos via JSON-LD: {details['title']}")
            
    except Exception as e:
        print(f"⚠️ Error extrayendo JSON-LD: {e}")
    
    # Fallback: extraer datos desde HTML si JSON-LD no funcionó
    if not details.get('title'):
        try:
            # Título
            titulo_tag = soup.select_one("h1[data-testid='hero-title-block__title']")
            if not titulo_tag:
                titulo_tag = soup.select_one("h1.sc-afe43def-0")
            details['title'] = titulo_tag.text.strip() if titulo_tag else ""
            
            # Año
            año_tag = soup.select_one("span[data-testid='hero-title-block__metadata'] li")
            if not año_tag:
                año_tag = soup.select_one("ul.ipc-inline-list li")
            details['precise_year'] = año_tag.text.strip() if año_tag else ""
            
            # Rating
            rating_tag = soup.select_one("span[data-testid='hero-rating-bar__aggregate-rating__score'] span")
            if not rating_tag:
                rating_tag = soup.select_one("span.sc-7ab21ed2-1")
            details['rating'] = rating_tag.text.strip() if rating_tag else ""
            
            # Duración
            duracion_tag = soup.select_one("li[data-testid='title-techspec-runtime']")
            if not duracion_tag:
                duracion_tag = soup.find('time')
            if duracion_tag:
                duration_text = duracion_tag.text.strip()
                match = re.search(r'(\d+)h\s*(\d+)m', duration_text)
                if match:
                    horas = int(match.group(1))
                    minutos = int(match.group(2))
                    details['detailed_duration'] = horas * 60 + minutos
                else:
                    match = re.search(r'(\d+)\s*min', duration_text)
                    if match:
                        details['detailed_duration'] = int(match.group(1))
            
            # Actores (primeros 3)
            actors = []
            actores_tags = soup.select("a[data-testid='title-cast-item__actor']")
            if not actores_tags:
                actores_tags = soup.select("div[data-testid='title-cast'] a[href*='/name/']")
            for tag in actores_tags[:3]:
                actor_name = tag.text.strip()
                if actor_name:
                    actors.append(actor_name)
            details['actors'] = actors
            
            print(f"✅ Datos extraídos via HTML fallback: {details.get('title', 'Unknown')}")
            
        except Exception as e:
            print(f"⚠️ Error extrayendo HTML: {e}")
    
    # Extraer metascore
    metascore_elem = soup.find('span', class_='metacritic-score-box')
    if not metascore_elem:
        metascore_elem = soup.find('div', {'data-testid': 'metacritic-score-box'})
    if not metascore_elem:
        metascore_elem = soup.find('span', class_='score-meta')
    
    details['metascore'] = metascore_elem.get_text(strip=True) if metascore_elem else ""
    
    # Asegurar valores por defecto
    details.setdefault('title', '')
    details.setdefault('precise_year', '')
    details.setdefault('rating', '')
    details.setdefault('detailed_duration', '')
    details.setdefault('actors', [])
    details.setdefault('metascore', '')
    
    actors_count = len(details['actors'])
    print(f"✅ Detalles finales: título={bool(details['title'])}, año={bool(details['precise_year'])}, rating={bool(details['rating'])}, duración={bool(details['detailed_duration'])}, actores={actors_count}, metascore={bool(details['metascore'])}")
    return details
############################## Funcion obtener detalles de peliculas #########################################################

############################## FUNCION PRINCIPAL #########################################################
if __name__ == "__main__":
    movies = get_top_movies()
    print(f"\n📦 Películas extraídas: {len(movies)}\n")
    
    # Procesar solo las primeras 50 películas para pruebas (puedes cambiar este número)
    movies_to_process = movies[:50]
    enhanced_movies = []
    
    for idx, movie in enumerate(movies_to_process, start=1):
        print(f"\n--- Procesando película {idx}/{len(movies_to_process)} ---")
        print(f"🎬 {movie['title']}")
        
        # Obtener detalles adicionales
        details = get_movie_details(movie['url'])
        
        # Combinar datos básicos con detalles adicionales
        enhanced_movie = {
            'Título': details.get('title') or movie['title'],
            'Año': details.get('precise_year') or movie['year'],
            'Calificación': details.get('rating') or movie['rating'],
            'Duración (min)': details.get('detailed_duration') or movie['duration'],
            'Metascore': details.get('metascore', 'N/A'),
            'Actores': details.get('actors', []),
            'url': movie['url'],
            'genre': movie['genre'],
            'description': movie['description']
        }
        
        enhanced_movies.append(enhanced_movie)
        
        # Mostrar resumen de la película procesada
        actors_str = ', '.join(enhanced_movie['Actores']) if enhanced_movie['Actores'] else 'No disponible'
        print(f"✅ {enhanced_movie['Título']} - Año: {enhanced_movie['Año']} - Duración: {enhanced_movie['Duración (min)']} min - Rating: {enhanced_movie['Calificación']} - Metascore: {enhanced_movie['Metascore']} - Actores: {actors_str}")
    
    print(f"\n🎉 Procesamiento completado. {len(enhanced_movies)} películas con detalles completos.")
    
    # Guardar resultados en archivo JSON (en directorio de salida)
    json_path = '/app/output/movies_detailed.json'
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_movies, f, ensure_ascii=False, indent=2)
        print(f"💾 Resultados guardados en '{json_path}'")
    except Exception as e:
        print(f"❌ Error al guardar archivo JSON: {e}")
    
    # Guardar resultados en archivo CSV (en directorio de salida)
    csv_path = '/app/output/movies_detailed.csv'
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            if enhanced_movies:
                fieldnames = ['Título', 'Año', 'Calificación', 'Duración (min)', 'Metascore', 'Actor 1', 'Actor 2', 'Actor 3']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for movie in enhanced_movies:
                    # Extraer solo el año de la fecha completa
                    año_solo = movie['Año']
                    if año_solo and '-' in str(año_solo):
                        año_solo = str(año_solo).split('-')[0]
                    
                    # Preparar datos para CSV
                    csv_row = {
                        'Título': movie['Título'],
                        'Año': año_solo,
                        'Calificación': movie['Calificación'],
                        'Duración (min)': movie['Duración (min)'],
                        'Metascore': movie['Metascore'] if movie['Metascore'] else 'N/A',
                        'Actor 1': movie['Actores'][0] if len(movie['Actores']) > 0 else '',
                        'Actor 2': movie['Actores'][1] if len(movie['Actores']) > 1 else '',
                        'Actor 3': movie['Actores'][2] if len(movie['Actores']) > 2 else ''
                    }
                    writer.writerow(csv_row)
        print(f"💾 Resultados guardados en '{csv_path}'")
    except Exception as e:
        print(f"❌ Error al guardar archivo CSV: {e}")
    
    # Mostrar resumen final
    print(f"\n📊 Resumen final:")
    for idx, movie in enumerate(enhanced_movies, start=1):
        actors_display = ', '.join(movie['Actores'][:3]) if movie['Actores'] else 'No disponible'
        metascore_display = movie['Metascore'] if movie['Metascore'] != 'N/A' else 'N/A'
        print(f"{idx}. {movie['Título']} ({movie['Año']}) - {movie['Duración (min)']} min - IMDb: {movie['Calificación']} - Metascore: {metascore_display}")
        print(f"   Actores: {actors_display}")
        print()
############################## FUNCION PRINCIPAL #########################################################









