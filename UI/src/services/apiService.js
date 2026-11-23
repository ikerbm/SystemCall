/**
 * Servicio de comunicación con el backend de Rafael.
 * Gestiona el ciclo de vida de los estados del asistente y la conexión HTTP.
 * El frontend no genera respuestas simuladas: si no hay conexión con el backend,
 * reporta error para que la UI informe al usuario.
 */

export const ASSISTANT_STATES = {
  IDLE: 'IDLE',
  LISTENING: 'LISTENING',
  THINKING: 'THINKING',
  RESPONDING: 'RESPONDING',
  ERROR: 'ERROR',
};

const DEFAULT_API_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.apiUrl = localStorage.getItem('rafael_api_url') || DEFAULT_API_URL;
    this.currentState = ASSISTANT_STATES.IDLE;
    this.listeners = new Set();
    this.isBackendAvailable = false;
    this.checkHealth();
  }

  subscribeState(callback) {
    this.listeners.add(callback);
    callback(this.currentState);
    return () => this.listeners.delete(callback);
  }

  setState(newState) {
    this.currentState = newState;
    this.listeners.forEach((callback) => {
      try {
        callback(newState);
      } catch (err) {
        console.error('Error notificando cambio de estado:', err);
      }
    });
  }

  getState() {
    return this.currentState;
  }

  getApiUrl() {
    return this.apiUrl;
  }

  setApiUrl(newUrl) {
    this.apiUrl = newUrl.replace(/\/+$/, '');
    localStorage.setItem('rafael_api_url', this.apiUrl);
    return this.checkHealth();
  }

  async checkHealth() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.apiUrl}/api/status`, {
        method: 'GET',
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      this.isBackendAvailable = res.ok;
    } catch {
      this.isBackendAvailable = false;
    }
    return this.isBackendAvailable;
  }

  /**
   * Envía un mensaje a Rafael en el backend.
   * Si no hay respuesta o falla la conexión, activa el estado ERROR y propaga el fallo.
   */
  async sendMessage(text, sessionId = 'web_user') {
    // 1. Estado LISTENING (recepción)
    this.setState(ASSISTANT_STATES.LISTENING);
    await new Promise((resolve) => setTimeout(resolve, 300));

    // 2. Estado THINKING (procesando en backend)
    this.setState(ASSISTANT_STATES.THINKING);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s para peticiones con búsqueda/LLM

      const response = await fetch(`${this.apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const aiResponse = data.response || data.mensaje;

      if (!aiResponse) {
        throw new Error('Respuesta vacía recibida del backend');
      }

      this.isBackendAvailable = true;

      // 3. Estado RESPONDING
      this.setState(ASSISTANT_STATES.RESPONDING);

      const animDuration = Math.min(Math.max(aiResponse.length * 20, 1800), 4500);
      setTimeout(() => {
        this.setState(ASSISTANT_STATES.IDLE);
      }, animDuration);

      return {
        text: aiResponse,
        tool: data.tool || null,
      };
    } catch (error) {
      console.warn('[ApiService] Error al conectar con el backend:', error.message);
      this.isBackendAvailable = false;

      // 4. Estado ERROR
      this.setState(ASSISTANT_STATES.ERROR);
      setTimeout(() => {
        this.setState(ASSISTANT_STATES.IDLE);
      }, 3000);

      throw error;
    }
  }

  triggerStateManual(stateName) {
    if (ASSISTANT_STATES[stateName]) {
      this.setState(ASSISTANT_STATES[stateName]);
    }
  }
}

export const apiService = new ApiService();
