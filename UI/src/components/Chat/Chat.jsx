import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, RefreshCw, Settings, Search, Music, AlertTriangle } from 'lucide-react';
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

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll automático suave hacia el último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, assistantState]);

  // Verificar conexión con el backend
  useEffect(() => {
    const checkConnection = async () => {
      const online = await apiService.checkHealth();
      setIsBackendOnline(online);
    };
    checkConnection();
    const interval = setInterval(checkConnection, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = async (textToSend) => {
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
      const res = await apiService.sendMessage(query);
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
        text: 'no se ha podido comunicar con el servidor',
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
  };

  const handleSaveApiUrl = async () => {
    setSettingsStatus('Probando conexión...');
    const ok = await apiService.setApiUrl(customApiUrl);
    setIsBackendOnline(ok);
    if (ok) {
      setSettingsStatus('¡Conectado exitosamente con Rafael backend!');
      setTimeout(() => {
        setShowSettings(false);
        setSettingsStatus(null);
      }, 1200);
    } else {
      setSettingsStatus('No se pudo conectar con el servidor.');
    }
  };

  return (
    <div className="chat-panel-container">
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
                {isBackendOnline ? 'Conectado al servidor' : 'Sin conexión al servidor'}
              </span>
            </div>
          </div>
        </div>

        <div className="chat-header-actions">
          <button
            className="chat-action-btn"
            onClick={clearChat}
            title="Limpiar conversación"
          >
            <RefreshCw size={15} />
          </button>
          <button
            className="chat-action-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Configurar servidor backend"
          >
            <Settings size={15} />
          </button>
        </div>
      </div>

      {/* Modal / Desplegable de Configuración de API */}
      {showSettings && (
        <div className="settings-drawer glass-panel-glow">
          <div className="settings-drawer-title">Configuración de Backend</div>
          <p className="settings-desc">
            Ingresa la URL del servidor Python de Rafael (api_server.py) para procesar las consultas:
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

      {/* Lista de Mensajes */}
      <div className="chat-messages-area">
        {messages.length === 0 && (
          <div className="empty-chat-placeholder">
            <Bot size={32} className="placeholder-icon" />
            <p className="placeholder-title">Rafael está listo</p>
            <p className="placeholder-sub">
              Escribe un mensaje para comenzar.
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
      </div>

      {/* Área de Entrada de Texto */}
      <div className="chat-input-area glass-panel">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un mensaje para Rafael... (Enter para enviar)"
          rows={1}
          className="chat-textarea"
          disabled={isSending}
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || isSending}
          className="chat-send-btn"
          title="Enviar mensaje"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
