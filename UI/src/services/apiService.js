/**
 * Servicio de comunicación con el backend de Rafael y Supabase Auth.
 * Gestiona la autenticación, los estados del asistente y el envío de consultas con JWT.
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
    this.authListeners = new Set();
    this.isBackendAvailable = false;

    // Cargar sesión guardada de localStorage
    this.token = localStorage.getItem('rafael_token') || null;
    try {
      this.user = JSON.parse(localStorage.getItem('rafael_user') || 'null');
    } catch {
      this.user = null;
    }

    this.checkHealth();
  }

  // ==========================================
  // GESTIÓN DE ESTADOS DEL ASISTENTE
  // ==========================================

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

  // ==========================================
  // CONFIGURACIÓN DE URL DEL BACKEND
  // ==========================================

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
      const timeoutId = setTimeout(() => controller.abort(), 2500);

      // Probar primero el endpoint de FastAPI /health
      let res = await fetch(`${this.apiUrl}/health`, {
        method: 'GET',
        signal: controller.signal,
      }).catch(() => null);

      // Si falla, probar /api/status por compatibilidad
      if (!res || !res.ok) {
        res = await fetch(`${this.apiUrl}/api/status`, {
          method: 'GET',
          signal: controller.signal,
        }).catch(() => null);
      }

      clearTimeout(timeoutId);
      this.isBackendAvailable = Boolean(res && res.ok);
    } catch {
      this.isBackendAvailable = false;
    }
    return this.isBackendAvailable;
  }

  // ==========================================
  // AUTENTICACIÓN (SUPABASE AUTH)
  // ==========================================

  subscribeAuth(callback) {
    this.authListeners.add(callback);
    callback({
      isAuthenticated: this.isAuthenticated(),
      user: this.user,
      token: this.token,
    });
    return () => this.authListeners.delete(callback);
  }

  notifyAuthChange() {
    const authState = {
      isAuthenticated: this.isAuthenticated(),
      user: this.user,
      token: this.token,
    };
    this.authListeners.forEach((callback) => {
      try {
        callback(authState);
      } catch (err) {
        console.error('Error notificando cambio de auth:', err);
      }
    });
  }

  isAuthenticated() {
    return Boolean(this.token);
  }

  getUser() {
    return this.user;
  }

  getToken() {
    return this.token;
  }

  /**
   * Inicia sesión con email y contraseña contra /auth/login
   */
  async login(email, password) {
    try {
      const response = await fetch(`${this.apiUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al iniciar sesión.');
      }

      this.token = data.access_token;
      this.user = data.user;

      localStorage.setItem('rafael_token', this.token);
      localStorage.setItem('rafael_user', JSON.stringify(this.user));

      if (data.refresh_token) {
        localStorage.setItem('rafael_refresh_token', data.refresh_token);
      }

      this.notifyAuthChange();
      return { user: this.user, token: this.token };
    } catch (err) {
      throw err;
    }
  }

  /**
   * Registra un nuevo usuario en Supabase Auth contra /auth/signup
   */
  async signup(email, password, userMetadata = {}) {
    try {
      const response = await fetch(`${this.apiUrl}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          password,
          user_metadata: userMetadata,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al registrar usuario.');
      }

      // Si la confirmación de email está deshabilitada en Supabase, retorna sesión directa
      if (data.session && data.session.access_token) {
        this.token = data.session.access_token;
        this.user = data.user || data.session.user;

        localStorage.setItem('rafael_token', this.token);
        localStorage.setItem('rafael_user', JSON.stringify(this.user));
        this.notifyAuthChange();
      }

      return data;
    } catch (err) {
      throw err;
    }
  }

  /**
   * Cierra la sesión activa localmente y en el servidor
   */
  async logout() {
    try {
      if (this.token) {
        await fetch(`${this.apiUrl}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
          },
        }).catch(() => null);
      }
    } finally {
      this.token = null;
      this.user = null;
      localStorage.removeItem('rafael_token');
      localStorage.removeItem('rafael_user');
      localStorage.removeItem('rafael_refresh_token');
      this.notifyAuthChange();
    }
  }

  // ==========================================
  // MENSAJES Y CONSULTAS CON IA (RAFAEL)
  // ==========================================

  /**
   * Envía un mensaje a Rafael en el backend usando el token JWT del usuario.
   */
  async sendMessage(text, sessionId = null) {
    if (!this.isAuthenticated()) {
      throw new Error('Debes iniciar sesión para comunicarte con Rafael.');
    }

    // 1. Estado LISTENING
    this.setState(ASSISTANT_STATES.LISTENING);
    await new Promise((resolve) => setTimeout(resolve, 200));

    // 2. Estado THINKING
    this.setState(ASSISTANT_STATES.THINKING);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s para inferencia LLM y herramientas

      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      };

      const payload = {
        message: text,
      };
      if (sessionId) {
        payload.conversation_id = sessionId;
      }

      // Probar primero el endpoint /chat de FastAPI
      let response = await fetch(`${this.apiUrl}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      // Si el endpoint no existe (404), intentar ruta alternativa /api/chat
      if (response.status === 404) {
        response = await fetch(`${this.apiUrl}/api/chat`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ message: text, session_id: sessionId || 'web_user' }),
          signal: controller.signal,
        });
      }

      clearTimeout(timeoutId);

      if (response.status === 401) {
        // Token expirado o revocado
        this.logout();
        throw new Error('Tu sesión ha expirado. Por favor, inicia sesión de nuevo.');
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const aiResponse = data.response || data.assistant_message?.content || data.mensaje;

      if (!aiResponse) {
        throw new Error('Respuesta vacía recibida de Rafael');
      }

      this.isBackendAvailable = true;

      // 3. Estado RESPONDING
      this.setState(ASSISTANT_STATES.RESPONDING);

      const animDuration = Math.min(Math.max(aiResponse.length * 15, 1500), 4000);
      setTimeout(() => {
        this.setState(ASSISTANT_STATES.IDLE);
      }, animDuration);

      return {
        text: aiResponse,
        tool: data.tool || data.assistant_message?.tool_used || null,
        conversationId: data.conversation_id || null,
      };
    } catch (error) {
      console.warn('[ApiService] Error al consultar a Rafael:', error.message);

      // Estado ERROR
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
