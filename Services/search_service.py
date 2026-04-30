from langchain_community.tools import DuckDuckGoSearchRun


# Instancia única del motor de búsqueda
_search_engine = DuckDuckGoSearchRun()


def buscar(query: str) -> str:
    """
    Realiza una búsqueda en internet usando DuckDuckGo y devuelve los resultados como texto.
    Esta función es llamada manualmente por Rafael cuando detecta una palabra clave de búsqueda.
    """
    if not query or not query.strip():
        return "No se proporcionó un término de búsqueda."

    try:
        return _search_engine.run(query.strip())
    except Exception as e:
        return f"No se pudo completar la búsqueda: {str(e)}"
