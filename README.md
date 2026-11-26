# SystemCall — Rafael AI

**Rafael** es un asistente de IA conversacional con interfaz web 3D, bot de Telegram y síntesis de voz. Usa **Claude (Anthropic)** como LLM principal, búsqueda web con DuckDuckGo y control de Spotify.

---

## Capacidades

- 💬 **Chat web** — Interfaz React con esfera de partículas 3D que reacciona al estado del asistente
- 🔐 **Autenticación y persistencia en Supabase** — API REST con FastAPI, Supabase Auth y Row Level Security (RLS)
- 🤖 **Bot de Telegram** — Sesiones independientes por usuario con historial persistente
- 🔍 **Búsqueda web** — DuckDuckGo en tiempo real, sin API key
- 🎵 **Control de Spotify** — Reproduce música por comando de voz o texto
- 🧠 **Memoria persistente** — Historial en Supabase Cloud y respaldo en JSON local
- 🔒 **Seguridad** — Detección de prompt injection, validación estricta de JWT y filtrado de fugas internas

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
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
CLIENT_ID_SPOTIFY=...
CLIENT_SECRET_SPOTIFY=...
TELEGRAM_API_KEY=...
```

---

## Uso

```bash
# API REST FastAPI + Supabase (Recomendada para la UI web y clientes móviles)
uvicorn API.main:app --reload --host 127.0.0.1 --port 8000

# UI web en http://localhost:5173 (o 3000)
iniciar_ui.bat          # Windows
# cd UI && npm run dev  # manual

# Bot de Telegram
iniciar_bot_telegram.bat
# python -m Services.Bots.telegram_rafael

# Servidor Flask legado (opcional / uso local)
# python api_server.py
```

---

## Stack

| Capa | Tecnología |
|---|---|
| LLM | Claude (`claude-haiku-5-5`) vía `langchain-anthropic` |
| REST API Principal | FastAPI + Pydantic v2 + Uvicorn |
| Base de Datos & Auth | Supabase (PostgreSQL con RLS + Supabase Auth) |
| Servidor Local Legado | Flask (`api_server.py`) |
| Frontend | React 18 + Vite + Three.js |
| Búsqueda web | DuckDuckGo (`langchain-community`) |
| Música | Spotipy (Spotify Web API) |
| Bot mensajería | pyTelegramBotAPI (`telebot`) |
| Memoria | Supabase Cloud (`conversations` / `messages`) y `FileChatMessageHistory` local |
| TTS (voz) | Coqui TTS — modelo `tts_models/es/css10/vits` |
| STT (escucha) | Faster-Whisper `base` + SpeechRecognition |

---

## Estructura

```
SystemCall/
├── API/                # API REST con FastAPI, Supabase Auth y RLS
├── Core/               # Rafael (asistente), Administrator (enrutador), Oyente (voz)
├── Services/           # Claude, LLMs locales, búsqueda, Spotify, bot Telegram
├── UI/                 # Frontend React (esfera 3D + chat con bloqueo de sesión)
├── Documentation/      # Documentación técnica detallada por módulo
│   ├── API.md          # Documentación técnica completa de la API REST y Supabase
│   ├── Core.md         # Documentación del núcleo de IA
│   ├── Services.md     # Documentación de integraciones y servicios
│   └── UI.md           # Documentación de la interfaz web 3D
├── Memoria_Rafael/     # Historiales de sesión locales (JSON, gitignored)
├── api_server.py       # API REST Flask de uso local legado
└── .env                # Credenciales y claves de API (gitignored)
```

> La documentación detallada de cada módulo está en [`Documentation/`](Documentation/).
