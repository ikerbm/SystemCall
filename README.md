# System Call (Rafael - La Voz del Mundo)

System Call es un asistente de Inteligencia Artificial llamado **Rafael**, diseñado para interactuar de forma natural mediante voz y a través de Telegram. Utiliza modelos de lenguaje locales (Llama 3.1 a través de Ollama) y síntesis de voz avanzada (TTS) para ofrecer una experiencia conversacional fluida.

## 🚀 Instalación y Configuración

1. **Crear un entorno virtual**:
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**:
   - En Windows: `venv\Scripts\activate`
   - En macOS/Linux: `source venv/bin/activate`

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar y configurar Ollama**:
   Asegúrate de tener [Ollama](https://ollama.com/) instalado y funcionando con el modelo `llama3.1:8b` (o ajusta el modelo en `Services/llm_service.py`):
   ```bash
   ollama run llama3.1:8b
   ```

5. **Configurar el entorno (.env)**:
   Crea un archivo `.env` en la raíz del proyecto y añade tu token de Telegram y de Porcupine (opcional para Wake Word):
   ```env
   TELEGRAM_API_KEY=tu_token_aqui
   ```

## 🎮 Uso

El proyecto tiene dos modos de operación principales:

### 1. Asistente por Voz (`test_rafael.py`)
Puedes hablarle por micrófono diciendo la palabra clave "Rafael" (configurado en `Core/Oyente.py`). El asistente te escuchará, procesará tu entrada usando `faster-whisper` y responderá en voz alta con TTS.
```bash
python test_rafael.py
```

### 2. Bot de Telegram
Puedes interactuar con Rafael a través de un chat de Telegram. Esto ejecuta un proceso que mantiene una memoria independiente para cada chat (basada en el ID de usuario o grupo).
```bash
# Ejecutar el bot de Telegram
python -m Services.Bots.telegram_rafael

# O usar el script de Windows incluido
iniciar_bot_telegram.bat
```

## 🏗️ Arquitectura y Estructura del Proyecto

* **`Core/`**: Contiene el cerebro y los sentidos del sistema.
  * `Rafael.py`: La clase principal que maneja la memoria persistente, la conexión con LangChain/Ollama y la generación de voz mediante TTS.
  * `Oyente.py`: Sistema de reconocimiento de voz usando `faster-whisper` y `speech_recognition` para la transcripción de comandos y detección de "wake word".
* **`Services/`**: Servicios externos e integraciones.
  * `llm_service.py`: Configura y provee la conexión con el modelo de lenguaje local (Ollama).
  * `wake_word.py`: Detección de palabra clave de activación utilizando `pvporcupine`.
  * `Bots/telegram_rafael.py`: Integración con la API de Telegram usando `telebot`.
* **`Memoria_Rafael/`**: Almacenamiento local persistente donde se guardan los historiales de chat en formato JSON, manteniendo el contexto de cada sesión o chat de Telegram.
