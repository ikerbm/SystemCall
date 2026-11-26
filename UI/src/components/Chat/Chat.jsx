import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  RefreshCw,
  Settings,
  Search,
  Music,
  AlertTriangle,
  Lock,
  LogIn,
  LogOut,
  Mail,
  Key,
  ShieldCheck,
} from 'lucide-react';
import { ASSISTANT_STATES, apiService } from '../../services/apiService';
import './Chat.css';

export default function Chat({ assistantState }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [customApiUrl, setCustomApiUrl] = useState(apiService.getApiUrl());
  const [settingsStatus, setSettingsStatus] = useState(null);
  const [conversationId, setConversationId] = useState(null);

  // Estados de Autenticación
  const [isAuthenticated, setIsAuthenticated] = useState(apiService.isAuthenticated());
  const [currentUser, setCurrentUser] = useState(apiService.getUser());
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll automático suave hacia el último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, assistantState]);

  // Sincronizar estado de autenticación con el servicio
  useEffect(() => {
    const unsubscribeAuth = apiService.subscribeAuth((auth) => {
      setIsAuthenticated(auth.isAuthenticated);
      setCurrentUser(auth.user);
    });
    return () => unsubscribeAuth();
  }, []);

  // Verificar conexión con el backend periódicamente
  useEffect(() => {
    const checkConnection = async () => {
      const online = await apiService.checkHealth();
      setIsBackendOnline(online);
    };
    checkConnection();
    const interval = setInterval(checkConnection, 8000);
    return () => clearInterval(interval);
  }, []);

  // Manejo de Inicio de Sesión
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError(null);

    if (!authEmail.trim() || !authPassword.trim()) {
      setAuthError('Por favor completa el correo y la contraseña.');
      return;
    }

    setAuthLoading(true);
    try {
      await apiService.login(authEmail, authPassword);
      setAuthPassword('');
    } catch (err) {
      setAuthError(err.message || 'Error al iniciar sesión.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
    setMessages([]);
    setConversationId(null);
  };

  const handleSend = async (textToSend) => {
    if (!isAuthenticated) return;

    const query = (textToSend || input).trim();
    if (!query || isSending) return;

    setInput('');
    setIsSending(true);

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      time: now,
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await apiService.sendMessage(query, conversationId);
      if (res.conversationId) {
        setConversationId(res.conversationId);
      }

      const botMsg = {
        id: Date.now() + 1,
        sender: 'rafael',
        text: res.text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tool: res.tool,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'rafael',
        text: err.message || 'No se ha podido comunicar con Rafael.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId(null);
  };

  const handleSaveApiUrl = async () => {
    setSettingsStatus('Probando conexión...');
    const ok = await apiService.setApiUrl(customApiUrl);
    setIsBackendOnline(ok);
    if (ok) {
      setSettingsStatus('¡Conectado exitosamente con Rafael API!');
      setTimeout(() => {
        setShowSettings(false);
        setSettingsStatus(null);
      }, 1200);
    } else {
      setSettingsStatus('No se pudo conectar con el servidor.');
    }
  };

  return (
    <div className={`chat-panel-container ${!isAuthenticated ? 'chat-panel-locked' : ''}`}>
      {/* Cabecera del Chat */}
      <div className="chat-header glass-panel">
        <div className="chat-header-info">
          <div className="avatar-core">
            <Bot size={18} className="text-neon" />
          </div>
          <div>
            <div className="chat-title-row">
              <span className="chat-agent-name">Rafael</span>
              <span className="chat-agent-badge">AI ASSISTANT</span>
            </div>
            <div className="chat-status-sub">
              <span className={`status-dot ${isBackendOnline ? 'online' : 'offline'}`} />
              <span className="status-label">
                {isBackendOnline ? 'Servidor Conectado' : 'Sin conexión al servidor'}
              </span>
            </div>
          </div>
        </div>

        <div className="chat-header-actions">
          {isAuthenticated && (
            <div className="user-profile-badge" title={currentUser?.email || 'Usuario'}>
              <ShieldCheck size={13} className="text-neon" />
              <span className="user-email-text">{currentUser?.email || 'Autenticado'}</span>
              <button
                className="chat-action-btn logout-btn"
                onClick={handleLogout}
                title="Cerrar sesión"
              >
                <LogOut size={13} />
              </button>
            </div>
          )}

          <button
            className="chat-action-btn"
            onClick={clearChat}
            disabled={!isAuthenticated}
            title="Limpiar conversación"
          >
            <RefreshCw size={15} />
          </button>
          <button
            className="chat-action-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Configurar servidor API"
          >
            <Settings size={15} />
          </button>
        </div>
      </div>

      {/* Modal / Desplegable de Configuración de API */}
      {showSettings && (
        <div className="settings-drawer glass-panel-glow">
          <div className="settings-drawer-title">Configuración de API</div>
          <p className="settings-desc">
            URL de la API REST de Rafael (FastAPI / Supabase):
          </p>
          <div className="settings-input-group">
            <input
              type="text"
              value={customApiUrl}
              onChange={(e) => setCustomApiUrl(e.target.value)}
              placeholder="http://localhost:8000"
              className="settings-input"
            />
            <button className="settings-save-btn" onClick={handleSaveApiUrl}>
              Conectar
            </button>
          </div>
          {settingsStatus && <div className="settings-feedback">{settingsStatus}</div>}
        </div>
      )}

      {/* ZONA DE MENSAJES / BLOQUEO SI NO ESTÁ AUTENTICADO */}
      <div className="chat-messages-area">
        {!isAuthenticated ? (
          /* OVERLAY HUD BLOQUEADO CUANDO NO HAY SESIÓN */
          <div className="chat-locked-overlay">
            <div className="locked-card glass-panel-glow">
              <div className="locked-icon-wrapper">
                <Lock size={32} className="lock-icon" />
              </div>

              <div className="locked-badge-hud">
                <span className="locked-badge-dot" />
                ACCESO RESTRINGIDO
              </div>

              <h3 className="locked-title">Sesión requerida</h3>
              <p className="locked-desc">
                Rafael solo procesa consultas de usuarios autenticados.
                Inicia sesión con tu cuenta de Supabase para desbloquear el canal de comunicación.
              </p>

              {/* Formulario de Inicio de Sesión */}
              <form className="auth-form" onSubmit={handleAuthSubmit}>
                {authError && (
                  <div className="auth-alert alert-error">
                    <AlertTriangle size={14} />
                    <span>{authError}</span>
                  </div>
                )}

                <div className="auth-field">
                  <label className="auth-label">Correo Electrónico</label>
                  <div className="auth-input-wrapper">
                    <Mail size={15} className="auth-input-icon" />
                    <input
                      type="email"
                      required
                      value={authEmail}
                      onChange={(e) => setAuthEmail(e.target.value)}
                      placeholder="usuario@ejemplo.com"
                      className="auth-input"
                    />
                  </div>
                </div>

                <div className="auth-field">
                  <label className="auth-label">Contraseña</label>
                  <div className="auth-input-wrapper">
                    <Key size={15} className="auth-input-icon" />
                    <input
                      type="password"
                      required
                      minLength={6}
                      value={authPassword}
                      onChange={(e) => setAuthPassword(e.target.value)}
                      placeholder="••••••••"
                      className="auth-input"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="auth-submit-btn"
                >
                  {authLoading ? (
                    <span className="auth-btn-content">
                      <span className="auth-spinner" /> Conectando con Supabase...
                    </span>
                  ) : (
                    <span className="auth-btn-content">
                      <LogIn size={15} /> Iniciar Sesión
                    </span>
                  )}
                </button>
              </form>
            </div>
          </div>
        ) : (
          /* CONVERSACIÓN NORMAL SI ESTÁ AUTENTICADO */
          <>
            {messages.length === 0 && (
              <div className="empty-chat-placeholder">
                <Bot size={32} className="placeholder-icon" />
                <p className="placeholder-title">Rafael está listo</p>
                <p className="placeholder-sub">
                  Escribe un mensaje para comenzar la sesión.
                </p>
              </div>
            )}

            {messages.map((msg) => {
              const isBot = msg.sender === 'rafael';
              return (
                <div
                  key={msg.id}
                  className={`message-row ${isBot ? 'row-rafael' : 'row-user'}`}
                >
                  <div className={`message-avatar ${msg.isError ? 'avatar-error' : ''}`}>
                    {msg.isError ? (
                      <AlertTriangle size={16} />
                    ) : isBot ? (
                      <Bot size={16} />
                    ) : (
                      <User size={16} />
                    )}
                  </div>

                  <div className="message-bubble-wrapper">
                    <div className="message-meta">
                      <span className="message-sender-name">
                        {isBot ? 'Rafael' : 'Tú'}
                      </span>
                      <span className="message-timestamp">{msg.time}</span>
                      {msg.tool === 'search' && (
                        <span className="tool-badge search-badge">
                          <Search size={11} /> Búsqueda Web
                        </span>
                      )}
                      {msg.tool === 'spotify' && (
                        <span className="tool-badge spotify-badge">
                          <Music size={11} /> Spotify
                        </span>
                      )}
                    </div>

                    <div
                      className={`message-bubble ${isBot ? 'bubble-rafael' : 'bubble-user'} ${
                        msg.isError ? 'bubble-error' : ''
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Indicador de escritura dinámico */}
            {assistantState === ASSISTANT_STATES.THINKING && (
              <div className="message-row row-rafael typing-indicator-row">
                <div className="message-avatar">
                  <Bot size={16} />
                </div>
                <div className="typing-bubble glass-panel">
                  <span className="typing-dot dot-1" />
                  <span className="typing-dot dot-2" />
                  <span className="typing-dot dot-3" />
                  <span className="typing-text">Rafael está procesando...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Área de Entrada de Texto (Bloqueada si no está autenticado) */}
      <div className={`chat-input-area glass-panel ${!isAuthenticated ? 'input-area-disabled' : ''}`}>
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            !isAuthenticated
              ? '🔒 Inicia sesión con Supabase para desbloquear el chat...'
              : 'Escribe un mensaje para Rafael... (Enter para enviar)'
          }
          rows={1}
          className="chat-textarea"
          disabled={!isAuthenticated || isSending}
        />
        <button
          onClick={() => handleSend()}
          disabled={!isAuthenticated || !input.trim() || isSending}
          className="chat-send-btn"
          title={!isAuthenticated ? 'Chat bloqueado: inicia sesión' : 'Enviar mensaje'}
        >
          {isAuthenticated ? <Send size={16} /> : <Lock size={15} />}
        </button>
      </div>
    </div>
  );
}
