from urllib.parse import urlsplit, urlunsplit
import logging

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


logger = logging.getLogger(__name__)

# Configuración del motor de búsqueda
_search_wrapper = DuckDuckGoSearchAPIWrapper(
    max_results=5,
    region="co-es",
    safesearch="moderate",
    time=None,
)



def _generar_consultas(query: str) -> list[str]:
    """
    Genera variantes de la consulta para ampliar la cobertura
    de la búsqueda y evitar depender de una sola respuesta.
    """

    return [
        query,
        f"{query} explicación",
        f"{query} documentación oficial",
    ]

def _normalizar_url(url: str) -> str:
    """
    Normaliza URLs para evitar resultados duplicados.
    """
    try:
        parsed = urlsplit(url.strip())
        # Reconstruye la URL sin query ni fragmento
        return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, '')).lower()
    except Exception:
        return url.strip().lower()

def buscar(query: str) -> str:
    """
    Realiza varias búsquedas relacionadas usando DuckDuckGo
    y combina los resultados para obtener una respuesta
    más completa y menos dependiente de una sola fuente.
    """

    if not query or not query.strip():
        return "No se proporcionó un término de búsqueda."

    query = query.strip()
    resultados = []
    urls_encontrados = set()

    try:
        respuesta = _search_wrapper.results(query,max_results =5)
        for resultado in respuesta:         
            titulo = resultado.get("title", "")
            url = resultado.get("link", "")
            snippet = resultado.get("snippet", "")

            if not url or not snippet:
                continue
            
            url_normalizada = _normalizar_url(url)
            if url_normalizada in urls_encontrados:
                continue
            
            urls_encontrados.add(url_normalizada)
            resultados.append({
                "titulo": titulo,
                "url": url,
                "contenido": snippet                
            })

        if not resultados:
            return "No se encontraron resultados relevantes."

        salida = []
        for i, res in enumerate(resultados[:5], 1):
            salida.append(
                f"RESULTADO {i}\n"
                f"título: {res['titulo']}\n"
                f"URL: {res['url']}\n"
                f"Informacion: {res['contenido']}"
            )
        return "\n\n" + "\n\n".join(salida)

    except Exception as e:
        logger.error("Error durante la búsqueda: %s", str(e))
        return f"No se pudo completar la búsqueda: {str(e)}"