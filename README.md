# SystemCall — Rafael AI

**Rafael** es un asistente de IA conversacional con interfaz web 3D, bot de Telegram y síntesis de voz. Usa **Claude (Anthropic)** como LLM principal, búsqueda web con DuckDuckGo y control de Spotify.

---

## Capacidades

- 💬 **Chat web** — Interfaz React con esfera de partículas 3D que reacciona al estado del asistente
- 🤖 **Bot de Telegram** — Sesiones independientes por usuario con historial persistente
- 🔍 **Búsqueda web** — DuckDuckGo en tiempo real, sin API key
- 🎵 **Control de Spotify** — Reproduce música por comando de voz o texto
- 🧠 **Memoria persistente** — Historial de conversación por sesión en JSON local
- 🔒 **Seguridad** — Detección de prompt injection y filtrado de fugas de configuración interna

---

## Requisitos previos

- Python 3.11+
- Node.js 20+ y npm (solo para la UI web)
- Cuenta de [Anthropic](https://console.anthropic.com/) con API key
- App de [Spotify Developer](https://developer.spotify.com/) con OAuth configurado *(opcional)*
- Bot de Telegram creado con [@BotFather](https://t.me/botfather) *(opcional)*

---

## Instalación

### 1. Backend Python

```bash
# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Frontend (UI web)

```bash
cd UI
npm install
```

### 3. Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
ANTHROPIC_API_KEY=sk-ant-...
CLIENT_ID_SPOTIFY=...
CLIENT_SECRET_SPOTIFY=...
TELEGRAM_API_KEY=...
```

---

## Uso

```bash
# API backend (requerida para la UI web)
python api_server.py

# UI web en http://localhost:3000
iniciar_ui.bat          # Windows
# cd UI && npm run dev  # manual

# Bot de Telegram
iniciar_bot_telegram.bat
# python -m Services.Bots.telegram_rafael

#iniciar el api de Fastapi
uvicorn API.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Stack

| Capa | Tecnología |
|---|---|
| LLM | Claude (`claude-haiku-5-5`) vía `langchain-anthropic` |
| Backend API | Flask (`api_server.py`) en puerto 8000 |
| Frontend | React 18 + Vite + Three.js |
| Búsqueda web | DuckDuckGo (`langchain-community`) |
| Música | Spotipy (Spotify Web API) |
| Bot mensajería | pyTelegramBotAPI (`telebot`) |
| Memoria | `FileChatMessageHistory` (JSON local) |
| TTS (voz) | Coqui TTS — modelo `tts_models/es/css10/vits` |
| STT (escucha) | Faster-Whisper `base` + SpeechRecognition |

---

## Estructura

```
SystemCall/
├── Core/               # Rafael (asistente), Administrator (enrutador), Oyente (voz)
├── Services/           # Claude, LLMs locales, búsqueda, Spotify, bot Telegram
├── UI/                 # Frontend React (esfera 3D + chat)
├── Documentation/      # Docs detalladas por módulo
├── Memoria_Rafael/     # Historiales de sesión (JSON, gitignored)
├── api_server.py       # API REST Flask
└── .env                # Credenciales (no subir al repo)
```

> La documentación detallada de cada módulo está en [`Documentation/`](Documentation/).
