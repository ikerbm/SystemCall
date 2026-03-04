# Estructura del Proyecto y Sugerencias de Arquitectura

Este documento explica en detalle cómo está organizado actualmente tu proyecto `System Call`, qué nuevas carpetas podrías agregar para mejorar la escalabilidad, y –muy importante– **cómo y dónde integrar un modelo de lenguaje (LLM)** en el Core de la aplicación.

---

## 🏗️ 1. Estructura Actual del Proyecto

Actualmente, el proyecto sigue un patrón muy parecido a modelo-vista-controlador (MVC) adaptado para videojuegos.

*   `Core/`: **El cerebro de control.** Aquí reside la lógica principal y los "sistemas nerviosos" del proyecto: el que escucha (`Oyente`), el que habla (`Rafael`), y el que toma decisiones (`Administrator`).
*   `Entidades/`: **Los datos (Modelos).** Clases abstractas puras, como `Jugador`, que tienen atributos (salud, maná, inventario) pero no saben cómo dibujarse. Hacer esto así es una excelente práctica.
*   `Imagenes/`: **La Vista.** Contiene todas las clases que heredan de `pygame.sprite.Sprite`. Agarra la lógica de Entidades/Magias y le pone imágenes y animaciones.
*   `Magias/`: **La lógica de negocio de hechizos.** Centraliza el complejo sistema mágico, separado del `Jugador`. `Hecate` funciona como fábrica.
*   `utils/`: Funciones de apoyo, como recortar imágenes, que no pertenecen a ninguna de las lógicas de negocio pero son súper útiles.

---

## 📁 2. Nuevas Carpetas Sugeridas y sus Objetivos

Para mantener el proyecto organizado conforme crezca o si decides hacerlo mucho más masivo, podrías agregar:

1.  **`Services/` (Servicios Externos / APIs)**
    *   **Objetivo:** Manejar todas las comunicaciones que salen de tu programa hacia internet. En esta carpeta irían tus integraciones con APIs de terceros, bases de datos en la nube (si planeas guardar jugadores online), u otros servicios desconectados de Pygame. Ya tienes una carpeta vacía que se llama `Services`, es el lugar perfecto.
2.  **`UI/` (Interfaz de Usuario)**
    *   **Objetivo:** Ya tienes otra carpeta vacía llamada UI. Su propósito debe ser manejar menús, botones, barra de vida, barra de maná, inventarios visuales emergentes y cuadros de diálogo. Separa esto de `Imagenes/` para no mezclar sprites de personajes con partes estáticas de la pantalla.
3.  **`Config/` o `Settings/`**
    *   **Objetivo:** Archivos que guarden variables globales estáticas, como diccionarios de configuraciones de teclas, colores de Pygame en formato RGB, tamaños de ventana (`WIDTH, HEIGHT`), y lo más importante: **Prompts y API Keys** para el LLM. (Ej: `config/llm_prompts.json` o `.env` para claves secretas).
4.  **`Audio/` o `Sonidos/`**
    *   **Objetivo:** Para organizar no solo tu base de efectos de sonido (si decides añadir sonidos de hechizos) o música de fondo (`BGM`), sino tal vez para guardar temporalmente audios para mandarlos a modelos de *Text-To-Speech* especializados si dejas de usar `pyttsx3`.

---

## 🤖 3. Implementación de un LLM en el "Core"

Si planeas integrar inteligencia artificial conversacional (LLM) como OpenAI (ChatGPT), Anthropic (Claude), o uno local (Llama3) para darle capacidades reales al `Administrator` o a `Rafael`, la arquitectura de tu proyecto actual lo hace **muy fácil**. 

### ¿Dónde debería ir el código del LLM?

**El lugar ideal es la carpeta `Services/`.**

Deberías crear un archivo, por ejemplo `Services/LlmService.py`, que contenga la lógica de conectarse al modelo, enviarle el prompt del sistema y obtener la respuesta. No debes ensuciar `Administrator.py` con tokens o librerías del LLM directamente; el administrador simplemente debe consumir ese *servicio*.

### Flujo de Trabajo Propuesto con LLM

Así es como se vería el ciclo en tu proyecto adaptado:

1.  **El Micrófono recibe audio**: `Core/Oyente.py` escucha y transcribe la voz a texto (Sigue funcionando igual o puedes reemplazarlo por Whisper de OpenAI y ponerlo dentro de `Services`).
2.  **Envío al Cerebro (Administrator)**: El `Administrator` recibe la transcripción (Ej: `"Rafael, veo un orco, ¡destrúyelo con una enorme ráfaga de fuego!"`).
3.  **El Administrador utiliza el Servicio LLM**:
    En lugar de tu código actual de buscar palabras en listas (`Opciones_Generate`, etc.), el `Administrator` llama al `LlmService`.
    *Modificación en Administrator.py:*
    ```python
    # Administrator.py
    from Services.LlmService import InteligenciaArtificial

    # ... dentro de Identificar_comando(self, texto):
    llm = InteligenciaArtificial()
    # Le pides al LLM que analice y extraiga la "intención" del jugador en un formato como JSON.
    resultado_json = llm.analizar_intencion(texto_del_jugador) 
    ```
4.  **El LLM responde estructurado**:
    Gracias a un `System Prompt` que definas en tu `LlmService`, el LLM interpretará que el jugador de arriba quería lanzar magia de fuego, y el `LlmService` devolverá un diccionario en Python:
    ```json
    {
        "intent": "lanzar_hechizo",
        "element": "fuego",
        "target": "orco",
        "rafael_response": "Entendido. Desplegando ráfaga de fuego de alta potencia."
    }
    ```
5.  **Ejecución de Lógica Interna**:
    El `Administrator` ahora lee ese Diccionario/JSON en lugar de estar descifrando frases, y como dice "lanzar_hechizo", invoca a `Hecate(elemento="fuego")`.
6.  **Rafael HABLA**:
    El LLM **ya te generó** de forma dinámica una respuesta personalizada (`"Entendido. Desplegando ráfaga de fuego..."`). El `Administrator` se la pasa a `Core/Rafael.py`, y Rafael la dice con voz robótica, dando la sensación real de tener un asistente de sistema mágico inteligente.

### Resumen del Refactor

*   `Core/Oyente.py`: Transcribe -> Pasa texto crudo. (Sigue en Core)
*   `Services/LlmService.py`: *(¡NUEVO!)* Agarra texto crudo -> Devuelve JSON de acción y Diálogo de Rafael.
*   `Core/Administrator.py`: Agarra JSON -> Dirige a código de Python correspondiente (Crea la magia).
*   `Core/Rafael.py`: Recibe el Diálogo del JSON -> Habla. (Sigue en Core)

Tener el LLM en `Services/` te permitirá mañana cambiar de OpenAI a Llama3 o a Gemini sin tocar ni una sola línea de lógica del `Administrator` o de tus mecánicas de juego.
