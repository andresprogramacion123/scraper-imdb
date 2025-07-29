import requests
from bs4 import BeautifulSoup
import time

IMDB_TOP_URL = "https://www.imdb.com/chart/top/"
PROXIES = {
    "http": "socks5h://tor:9050",
    "https": "socks5h://tor:9050"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def get_top_movie_links():
    print("🔍 Obteniendo lista de películas...")
    try:
        response = requests.get(IMDB_TOP_URL, headers=HEADERS, proxies=PROXIES, timeout=10)
        print(f"✅ Código de estado: {response.status_code}")
        print("📄 Mostrando los primeros 5000 caracteres del HTML recibido:\n")
        print(response.text[:5000])
    except Exception as e:
        print(f"❌ Error al acceder a IMDb: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("tbody", class_="lister-list")
    if not table:
        print("❌ No se encontró la tabla con las películas.")
        return []

    rows = table.find_all("tr")
    links = []
    for row in rows[:50]:  # Solo primeras 50
        link_tag = row.find("td", class_="titleColumn").find("a")
        if link_tag:
            relative_url = link_tag.get("href")
            full_url = f"https://www.imdb.com{relative_url.split('?')[0]}"
            links.append(full_url)
    print(f"✅ Se encontraron {len(links)} enlaces a películas.")
    return links


def get_movie_details(url):
    print(f"\n🔗 Accediendo a {url}")
    try:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=10)
        print("📄 HTML recibido (primeros 2000 caracteres):\n")
        print(response.text[:2000])
    except Exception as e:
        print(f"❌ Error al acceder a {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    rating_tag = soup.find("span", class_="sc-bde20123-1 iZlgcd")
    rating = rating_tag.text if rating_tag else "N/A"

    return {
        "title": title,
        "rating": rating,
        "url": url
    }


def main():
    movie_urls = get_top_movie_links()
    print("\n⏳ Extrayendo información detallada de películas...\n")
    movies = []
    for i, url in enumerate(movie_urls, start=1):
        details = get_movie_details(url)
        if details:
            print(f"✅ {i}. {details['title']} - ⭐ {details['rating']}")
            movies.append(details)
        time.sleep(3)  # Esperar entre requests para evitar bloqueo

    print(f"\n📦 Películas extraídas: {len(movies)}")


if __name__ == "__main__":
    main()









