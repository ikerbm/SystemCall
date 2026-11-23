import React, { useState, useEffect } from 'react';
import ParticleSphere from './components/ParticleSphere/ParticleSphere';
import Chat from './components/Chat/Chat';
import { ASSISTANT_STATES, apiService } from './services/apiService';
import { Eye, MessageSquare } from 'lucide-react';
import './App.css';

export default function App() {
  const [assistantState, setAssistantState] = useState(ASSISTANT_STATES.IDLE);
  const [activeMobileTab, setActiveMobileTab] = useState('both'); // 'sphere' | 'chat' | 'both'

  useEffect(() => {
    // Sincronizar el estado del asistente con el servicio central
    const unsubscribe = apiService.subscribeState((newState) => {
      setAssistantState(newState);
    });
    return () => unsubscribe();
  }, []);

  return (
    <div className="app-main-layout">
      {/* Botones de navegación para pantallas móviles */}
      <div className="mobile-nav-toggle">
        <button
          className={`mobile-tab-btn ${activeMobileTab === 'sphere' ? 'active' : ''}`}
          onClick={() => setActiveMobileTab('sphere')}
        >
          <Eye size={14} /> <span>Esfera 3D</span>
        </button>
        <button
          className={`mobile-tab-btn ${activeMobileTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveMobileTab('chat')}
        >
          <MessageSquare size={14} /> <span>Chat</span>
        </button>
      </div>

      {/* ZONA IZQUIERDA: 60% — VISUALIZACIÓN DE RAFAEL */}
      <section
        className={`zone-sphere-container ${
          activeMobileTab === 'chat' ? 'mobile-hidden' : ''
        }`}
      >
        <ParticleSphere assistantState={assistantState} />
      </section>

      {/* ZONA DERECHA: 40% — CHAT CONVERSACIONAL */}
      <section
        className={`zone-chat-container ${
          activeMobileTab === 'sphere' ? 'mobile-hidden' : ''
        }`}
      >
        <Chat assistantState={assistantState} />
      </section>
    </div>
  );
}
