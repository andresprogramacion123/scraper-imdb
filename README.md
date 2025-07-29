# 🎬 IMDB Top Movies Scraper

Un scraper robusto para extraer información de las mejores películas de IMDB con soporte para proxies y evasión de bloqueos.

## ⚠️ Consideraciones de Red IMPORTANTES

### 🏢 Redes Corporativas y Restricciones
**ADVERTENCIA**: Este proyecto requiere conexión a internet sin restricciones corporativas.

- **Redes empresariales**: Las redes corporativas suelen bloquear:
  - Instalación de paquetes Python (`pip install`)
  - Conexiones SOCKS/proxies
  - Tráfico TOR
  - Puertos no estándar (9050 para TOR)
  
- **Solución implementada**: 
  - ✅ Usar datos móviles compartidos desde celular al PC
  - ✅ Conexión sin restricciones firewall
  - ✅ Acceso completo para instalación de dependencias

### 📱 Configuración de Red Recomendada
1. **Compartir datos móviles** desde celular al PC
2. **Desconectar** de red corporativa/empresarial
3. **Verificar** acceso a puertos 9050 (TOR) y 80/443 (HTTP/HTTPS)

## 🚀 Características Implementadas

### ✅ Funcionalidades Completadas
- **Extracción de 50+ películas** desde IMDB Top 250
- **Datos completos por película**:
  - Título, año de estreno, calificación IMDB
  - Duración en minutos (desde página de detalle)
  - Metascore (cuando disponible)
  - Mínimo 3 actores principales
- **Múltiples métodos de extracción**:
  - JSON-LD estructurado (método principal)
  - Fallback HTML parsing
  - Búsqueda general de enlaces
- **Manejo robusto de errores** con try-except
- **Exportación dual**: CSV y JSON
- **Rate limiting** (1 segundo entre requests)
- **Headers personalizados** para evadir detección

### 🔄 Infraestructura de Proxies
- **Docker Compose** con servicio TOR
- **Contenedor TOR** dedicado (puerto 9050)
- **Red privada** entre contenedores
- **Configuración SOCKS5** preparada

## 📋 Requisitos del Sistema

### Dependencias
```bash
# Python packages
requests
beautifulsoup4
pysocks

# Sistema
docker
docker-compose
```

### Estructura del Proyecto
```
imdb_scraper/
├── docker-compose.yml      # Orquestación de contenedores
├── scraper/
│   ├── Dockerfile         # Imagen del scraper
│   ├── scraper.py         # Script principal
│   └── wait-for-tor.sh    # Script de espera para TOR
├── tor/
│   ├── Dockerfile         # Imagen de TOR
│   └── torrc             # Configuración TOR
└── output/               # Archivos generados
    ├── movies_detailed.csv
    └── movies_detailed.json
```

## 🛠️ Instalación y Uso

### 1. Verificar Conectividad de Red
```bash
# Verificar acceso a IMDB
curl -I https://www.imdb.com/chart/top/

# Verificar que no hay restricciones de proxy
curl --socks5 127.0.0.1:9050 https://httpbin.org/ip
```

### 2. Ejecutar con Docker
```bash
# Construir e iniciar servicios
docker-compose up --build

# Ejecutar scraper en contenedor separado
docker exec -it scraper python scraper.py
```

### 3. Ejecutar Localmente (Sin Proxies)
```bash
# Instalar dependencias
pip install requests beautifulsoup4

# Ejecutar directamente
cd imdb_scraper/scraper
python scraper.py
```

## 📊 Datos Extraídos

### Campos por Película
| Campo | Descripción | Fuente |
|-------|-------------|---------|
| Título | Nombre de la película | JSON-LD/HTML |
| Año | Año de estreno | Página de detalle |
| Calificación | Rating IMDB (1-10) | JSON-LD/HTML |
| Duración (min) | Duración en minutos | Página de detalle |
| Metascore | Puntuación Metacritic | Página de detalle |
| Actores | Primeros 3 actores principales | Página de detalle |

### Formato de Salida

**CSV**: `movies_detailed.csv`
```csv
Título,Año,Calificación,Duración (min),Metascore,Actor 1,Actor 2,Actor 3
The Shawshank Redemption,1994,9.3,142,80,Tim Robbins,Morgan Freeman,Bob Gunton
```

**JSON**: `movies_detailed.json`
```json
[
  {
    "Título": "The Shawshank Redemption",
    "Año": "1994",
    "Calificación": "9.3",
    "Duración (min)": 142,
    "Metascore": "80",
    "Actores": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"]
  }
]
```

## 🔐 Configuración de Proxies

### Estado Actual
- **TOR**: Configurado pero desactivado (`PROXIES = None` en línea 14)
- **Docker**: Infraestructura lista para activar proxies
- **SOCKS5**: Puerto 9050 expuesto para TOR

### Activar Proxies TOR
```python
# En scraper.py, cambiar línea 14:
PROXIES = {
    "http": "socks5h://tor:9050",
    "https": "socks5h://tor:9050"
}
```

## 📈 Análisis de Cumplimiento

### ✅ Requisitos Cumplidos (Punto 1 - 80%)
- ✅ Extracción desde IMDB Top 250
- ✅ 50+ películas procesadas
- ✅ Todos los datos requeridos
- ✅ BeautifulSoup + Requests
- ✅ Headers personalizados
- ✅ Manejo de errores básico
- ✅ Exportación CSV/JSON
- ✅ Estructura modular

### ⚠️ Mejoras Pendientes (Punto 1 - 20%)
- ❌ **Patrón Factory**: No implementado
- ❌ **Logging estructurado**: Solo prints básicos
- ❌ **Reintentos con backoff**: No automatizado
- ❌ **Cookies personalizados**: No implementados

### 🔄 Proxies y Red (Punto 3 - 30%)
- ✅ Infraestructura TOR con Docker
- ✅ Configuración SOCKS5 preparada
- ❌ **Proxies activos**: Desactivados por defecto
- ❌ **Rotación automática**: No implementada
- ❌ **Logging de IPs**: No implementado
- ❌ **Healthcheck**: No configurado

## 🚨 Limitaciones Conocidas

1. **Dependencia de red**: Requiere conexión sin restricciones
2. **Rate limiting manual**: Solo 1 segundo entre requests
3. **Sin persistencia BD**: Falta implementación SQL (Punto 2)
4. **Proxies desactivados**: Por estabilidad en pruebas
5. **Sin patrón Factory**: Arquitectura pendiente

## 🔧 Próximos Pasos

1. **Implementar patrón Factory** para creación de scrapers
2. **Activar sistema de proxies** con rotación automática
3. **Añadir logging estructurado** con niveles apropiados
4. **Implementar reintentos** con backoff exponencial
5. **Crear base de datos** SQL con modelo relacional

## 📞 Troubleshooting

### Error: "No se pudieron extraer links"
- Verificar conectividad: `curl https://www.imdb.com/chart/top/`
- Revisar restricciones de red corporativa
- Cambiar a datos móviles

### Error: "Connection refused (TOR)"
- Verificar que docker-compose esté ejecutándose
- Comprobar puerto 9050: `netstat -an | grep 9050`
- Reiniciar servicios: `docker-compose restart`

### Archivos de salida vacíos
- Verificar permisos en directorio `output/`
- Revisar logs del contenedor: `docker logs scraper`
- Ejecutar en modo debug local

---

⚡ **Recomendación**: Para uso en producción, activar proxies TOR y implementar las mejoras pendientes antes del despliegue.