from datetime import datetime
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


# Configuración del motor de búsqueda
_search_wrapper = DuckDuckGoSearchAPIWrapper(
    max_results=10
)

_search_engine = DuckDuckGoSearchRun(
    api_wrapper=_search_wrapper
)


def _generar_consultas(query: str) -> list[str]:
    """
    Genera variantes de la consulta para ampliar la cobertura
    de la búsqueda y evitar depender de una sola respuesta.
    """
    año_actual = datetime.now().year

    return [
        query,
        f"{query} explicación",
        f"{query} documentación",
        f"{query} ejemplos",
        f"{query} {año_actual}",
    ]


def _agregar_si_es_nuevo(resultado: str, resultados: list[str]) -> None:
    """
    Evita agregar resultados idénticos o vacíos.
    """
    if not resultado:
        return

    texto_normalizado = resultado.strip().lower()

    if not texto_normalizado:
        return

    for existente in resultados:
        if texto_normalizado == existente.strip().lower():
            return

    resultados.append(resultado.strip())


def buscar(query: str) -> str:
    """
    Realiza varias búsquedas relacionadas usando DuckDuckGo
    y combina los resultados para obtener una respuesta
    más completa y menos dependiente de una sola fuente.
    """

    if not query or not query.strip():
        return "No se proporcionó un término de búsqueda."

    query = query.strip()

    try:
        resultados = []

        for consulta in _generar_consultas(query):
            try:
                respuesta = _search_engine.run(consulta)
                _agregar_si_es_nuevo(respuesta, resultados)

            except Exception:
                # Ignora errores individuales para que una
                # consulta fallida no arruine toda la búsqueda.
                continue

        if not resultados:
            return "No se encontraron resultados relevantes."

        return "\n\n" + ("\n\n" + ("-" * 80) + "\n\n").join(resultados)

    except Exception as e:
        return f"No se pudo completar la búsqueda: {str(e)}"