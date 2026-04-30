import os
import json
from langchain_core.messages import SystemMessage, HumanMessage

from Services.llm_service import load_llm
from Services.search_service import buscar

admin_prompt = """Eres el Administrador del sistema. Tu función es analizar el mensaje del usuario y decidir qué acción debe tomar el asistente (Rafael) antes de responder.

Herramientas disponibles:
- "search": Útil cuando el usuario necesita información actualizada, noticias, clima, datos precisos de internet o cuando pide explícitamente buscar algo.
- "none": Para conversación general, saludos, preguntas teóricas, matemáticas, o cuando no se necesite información externa para responder correctamente.

Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura, sin texto adicional:
{
    "tool": "search" o "none",
    "query": "Si elegiste 'search', escribe aquí la mejor consulta de búsqueda para Google. Si elegiste 'none', déjalo vacío."
}
"""

class Administrator:

    def __init__(self):
        self.nombre = "Administrator"
        # Usamos el mismo servicio de LLM que usa Rafael
        self.llm = load_llm()

    def procesar_mensaje(self, user_input: str) -> dict:
        """
        Analiza el mensaje del usuario utilizando el LLM para decidir qué herramienta usar.
        Si se elige una herramienta, la ejecuta y devuelve el contexto.
        
        Retorna un diccionario con el formato:
        {
            "tool": str,
            "query": str,
            "contexto_herramienta": str o None
        }
        """
        print(f"[Administrator] Analizando intención del mensaje: '{user_input}'")
        
        messages = [
            SystemMessage(content=admin_prompt),
            HumanMessage(content=user_input)
        ]

        response = self.llm.invoke(messages)
        
        # Extraer y parsear la respuesta del LLM a JSON
        try:
            content = response.content.strip()
            # Limpiar posibles bloques de formato Markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                decision = json.loads(json_str)
            else:
                decision = {"tool": "none", "query": ""}
                
        except Exception as e:
            print(f"[Administrator] Error parseando la decisión del LLM: {e}")
            decision = {"tool": "none", "query": ""}

        tool = decision.get("tool", "none").lower()
        query = decision.get("query", "")

        resultado_herramienta = None

        # Ejecutar la herramienta si el Administrador lo decidió
        if tool == "search" and query:
            print(f"[Administrator] Acción decidida: Búsqueda requerida. Ejecutando query: '{query}'")
            try:
                resultado_herramienta = buscar(query)
            except Exception as e:
                print(f"[Administrator] Error al ejecutar la búsqueda en internet: {e}")
                resultado_herramienta = "Hubo un error al intentar buscar en internet."
        else:
            print(f"[Administrator] Acción decidida: Conversación normal (ninguna herramienta extra).")

        return {
            "tool": tool,
            "query": query,
            "contexto_herramienta": resultado_herramienta
        }
