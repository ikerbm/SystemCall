import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { ASSISTANT_STATES, apiService } from '../../services/apiService';
import './ParticleSphere.css';

/**
 * Crea una textura de partícula suave con gradiente radial y glow
 * sin necesidad de cargar imágenes externas.
 */
function createParticleTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
  gradient.addColorStop(0.2, 'rgba(180, 255, 210, 0.9)');
  gradient.addColorStop(0.5, 'rgba(0, 255, 136, 0.4)');
  gradient.addColorStop(0.8, 'rgba(5, 150, 105, 0.15)');
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 64, 64);

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

export default function ParticleSphere({ assistantState }) {
  const containerRef = useRef(null);
  const stateRef = useRef(assistantState);

  // Mantener referencia al estado actual para el loop de animación
  useEffect(() => {
    stateRef.current = assistantState;
  }, [assistantState]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // 1. Escena, Cámara y Renderer
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020617, 0.0018);

    const camera = new THREE.PerspectiveCamera(
      55,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 120; // Para acercar reducir el numero

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x020617, 1);
    container.appendChild(renderer.domElement);

    const particleTexture = createParticleTexture();

    // 2. Parámetros de Partículas
    const TOTAL_PARTICLES = 1000;

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(TOTAL_PARTICLES * 3);
    const colors = new Float32Array(TOTAL_PARTICLES * 3);
    const sizes = new Float32Array(TOTAL_PARTICLES);

    // Arrays auxiliares para la física y simulación orgánica
    const originalRadii = new Float32Array(TOTAL_PARTICLES);
    const phiAngles = new Float32Array(TOTAL_PARTICLES);
    const thetaAngles = new Float32Array(TOTAL_PARTICLES);
    const speeds = new Float32Array(TOTAL_PARTICLES);
    const isDetached = new Uint8Array(TOTAL_PARTICLES);
    const detachPhase = new Float32Array(TOTAL_PARTICLES);
    const detachMaxDist = new Float32Array(TOTAL_PARTICLES);

    // Paleta de colores solicitada: Verde Neón, Verde Esmeralda y Amarillo eléctrico
    const colorNeonGreen = new THREE.Color(0x00ff88);
    const colorEmerald = new THREE.Color(0x059669);
    const colorYellow = new THREE.Color(0xfacc15);
    const colorLime = new THREE.Color(0xccff00);
    const colorError = new THREE.Color(0xf97316);

    for (let i = 0; i < TOTAL_PARTICLES; i++) {
      const i3 = i * 3;

      // Destellos coronales contenidos (pequeña aura pegada a la esfera, sin rezagados)
      const willDetach = Math.random() < 0.10;
      isDetached[i] = willDetach ? 1 : 0;
      detachPhase[i] = Math.random() * Math.PI * 2;
      detachMaxDist[i] = 1.0 + Math.random() * 2.0;

      // Distribución de esfera pensante sólida y definida:
      // - 65% en la corteza esférica (silueta nítida y pura)
      // - 20% en la red sináptica intermedia
      // - 15% en el núcleo hiperdenso de pensamiento
      const u = Math.random();
      let baseRadius;
      if (u < 0.15) {
        // Núcleo central
        baseRadius = 4 + Math.random() * 6;
      } else if (u < 0.35) {
        // Manto neural intermedio
        baseRadius = 11 + Math.random() * 9;
      } else {
        // Corteza exterior: radio compacto bien definido (22 a 25)
        baseRadius = 22 + Math.random() * 3.2;
      }

      originalRadii[i] = baseRadius;
      phiAngles[i] = Math.acos(2 * Math.random() - 1);
      thetaAngles[i] = Math.random() * Math.PI * 2;
      speeds[i] = (0.2 + Math.random() * 0.8) * (Math.random() > 0.4 ? 1 : -1);

      // Posición inicial en 3D
      positions[i3] = baseRadius * Math.sin(phiAngles[i]) * Math.cos(thetaAngles[i]);
      positions[i3 + 1] = baseRadius * Math.sin(phiAngles[i]) * Math.sin(thetaAngles[i]);
      positions[i3 + 2] = baseRadius * Math.cos(phiAngles[i]);

      // Color coherente: Núcleo amarillo brillante, manto verde neón, corteza esmeralda viva
      const tempColor = new THREE.Color();
      if (baseRadius <= 10) {
        tempColor.copy(Math.random() > 0.35 ? colorYellow : colorLime);
      } else if (baseRadius <= 20) {
        tempColor.copy(Math.random() > 0.3 ? colorNeonGreen : colorLime);
      } else {
        tempColor.copy(Math.random() > 0.4 ? colorEmerald : colorNeonGreen);
      }

      colors[i3] = tempColor.r;
      colors[i3 + 1] = tempColor.g;
      colors[i3 + 2] = tempColor.b;

      // Tamaños nítidos: partículas elegantes y consistentes
      sizes[i] = 1.4 + Math.random() * 2.0;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    // Guardamos una copia exacta de los colores originales para restaurarlos tras cualquier estado de alerta/error
    const originalColors = new Float32Array(colors);

    // Material con brillo de energía equilibrado
    const material = new THREE.PointsMaterial({
      size: 3.0,
      map: particleTexture,
      vertexColors: true,
      transparent: true,
      opacity: 0.92,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });

    const particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);

    // 3. Parallax con el cursor del mouse
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const onMouseMove = (event) => {
      const rect = container.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      mouseX = (x / rect.width - 0.5) * 2;
      mouseY = (y / rect.height - 0.5) * 2;
    };
    window.addEventListener('mousemove', onMouseMove);

    // 4. Variables de animación interpoladas
    let clock = new THREE.Clock();
    let currentOrbitSpeed = 0.5;
    let currentPulseScale = 1.0;
    let currentConcentration = 1.0; // En THINKING se concentra hacia el centro
    let waveOffset = 0;
    let errorBlend = 0.0; // Factor de interpolación hacia el color de alerta (0 = original, 1 = error)

    let animationFrameId;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const delta = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // Parallax suave
      targetX += (mouseX * 0.4 - targetX) * 0.05;
      targetY += (mouseY * 0.4 - targetY) * 0.05;
      particleSystem.rotation.y = targetX * 0.6;
      particleSystem.rotation.x = -targetY * 0.4;

      // Modulación de parámetros según el ESTADO DEL ASISTENTE
      const state = stateRef.current;
      let targetOrbitSpeed = 0.5;
      let targetConcentration = 1.0;
      let pulseFreq = 1.8;
      let pulseAmplitude = 0.06;

      switch (state) {
        case ASSISTANT_STATES.LISTENING:
          targetOrbitSpeed = 0.9;
          targetConcentration = 1.08; // Se expande con curiosidad
          pulseFreq = 3.5;
          pulseAmplitude = 0.09;
          waveOffset += delta * 4.0;
          break;

        case ASSISTANT_STATES.THINKING:
          targetOrbitSpeed = 2.4; // Aceleración orbital
          targetConcentration = 0.72; // Se concentra en el núcleo
          pulseFreq = 6.0;
          pulseAmplitude = 0.15;
          break;

        case ASSISTANT_STATES.RESPONDING:
          targetOrbitSpeed = 1.2;
          targetConcentration = 1.15;
          pulseFreq = 4.2;
          pulseAmplitude = 0.22; // Ondas de expansión desde el núcleo
          waveOffset += delta * 7.0;
          break;

        case ASSISTANT_STATES.ERROR:
          targetOrbitSpeed = 0.0;
          targetConcentration = 1.0;
          pulseFreq = 8.0;
          pulseAmplitude = 0.08;
          break;

        case ASSISTANT_STATES.IDLE:
        default:
          targetOrbitSpeed = 0.0; // CERO rotación: las partículas quedan fijas en su órbita
          targetConcentration = 1.0;
          pulseFreq = 1.35; // Ritmo de respiración pausado y profundo (~4.6s por ciclo)
          pulseAmplitude = 0.15; // Inhalación y exhalación orgánica pronunciada
          waveOffset += delta * 2.8; // Ondas continuas de respiro que viajan desde el núcleo (estilo responding)
          break;
      }

      // Interpolación suave (lerp)
      currentOrbitSpeed += (targetOrbitSpeed - currentOrbitSpeed) * 0.06;
      currentConcentration += (targetConcentration - currentConcentration) * 0.06;

      // Pulsación senoidal orgánica de respiración
      currentPulseScale =
        currentConcentration * (1.0 + Math.sin(elapsed * pulseFreq) * pulseAmplitude);

      // Respiración de brillo lumínico en reposo
      material.opacity = 0.82 + Math.sin(elapsed * pulseFreq) * 0.12;

      // Actualizar posiciones de cada partícula
      const posAttr = geometry.attributes.position;
      const colAttr = geometry.attributes.color;
      const pArr = posAttr.array;
      const cArr = colAttr.array;

      // Transición suave de color hacia ERROR y RETORNO AUTOMÁTICO a los colores originales
      const targetErrorBlend = state === ASSISTANT_STATES.ERROR ? 1.0 : 0.0;
      if (Math.abs(errorBlend - targetErrorBlend) > 0.001 || targetErrorBlend > 0) {
        errorBlend += (targetErrorBlend - errorBlend) * 0.12;
        if (targetErrorBlend === 0.0 && errorBlend < 0.002) {
          errorBlend = 0.0;
        }

        for (let i = 0; i < TOTAL_PARTICLES; i++) {
          const i3 = i * 3;
          cArr[i3] = THREE.MathUtils.lerp(originalColors[i3], colorError.r, errorBlend);
          cArr[i3 + 1] = THREE.MathUtils.lerp(originalColors[i3 + 1], colorError.g * 0.6, errorBlend);
          cArr[i3 + 2] = THREE.MathUtils.lerp(originalColors[i3 + 2], colorError.b * 0.2, errorBlend);
        }
        colAttr.needsUpdate = true;
      }

      for (let i = 0; i < TOTAL_PARTICLES; i++) {
        const i3 = i * 3;

        // Giro orbital continuo diferencial (0 en reposo)
        thetaAngles[i] += speeds[i] * delta * currentOrbitSpeed;

        let r = originalRadii[i] * currentPulseScale;

        // Comportamiento de partículas desprendibles: se alejan y regresan
        if (isDetached[i]) {
          detachPhase[i] += delta * (0.8 + speeds[i] * 0.3);
          // Ciclo suave de desprendimiento y retorno
          const drift = Math.sin(detachPhase[i]);
          if (drift > 0) {
            r += drift * detachMaxDist[i];
          }
        }

        // Ondas radiales de expansión: activo en RESPONDING y en IDLE como respiración viva
        if (state === ASSISTANT_STATES.RESPONDING) {
          const wave = Math.sin(r * 0.35 - waveOffset);
          r += wave * 4.0;
        } else if (state === ASSISTANT_STATES.IDLE) {
          // Ondas armónicas que viajan del núcleo hacia la periferia como ondas de respiración
          const breathWave = Math.sin(r * 0.3 - waveOffset);
          r += breathWave * 2.6;
        }

        // En estado ERROR, agregamos vibración de glitch sutil
        if (state === ASSISTANT_STATES.ERROR) {
          r += (Math.random() - 0.5) * 1.8;
        }

        pArr[i3] = r * Math.sin(phiAngles[i]) * Math.cos(thetaAngles[i]);
        pArr[i3 + 1] = r * Math.sin(phiAngles[i]) * Math.sin(thetaAngles[i]);
        pArr[i3 + 2] = r * Math.cos(phiAngles[i]);
      }

      posAttr.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    // 5. Manejo de Redimensionamiento
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
      particleTexture.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Formato y color del badge según el estado
  const getStateBadge = () => {
    switch (assistantState) {
      case ASSISTANT_STATES.LISTENING:
        return { label: 'ESCUCHANDO', class: 'badge-listening' };
      case ASSISTANT_STATES.THINKING:
        return { label: 'PROCESANDO...', class: 'badge-thinking' };
      case ASSISTANT_STATES.RESPONDING:
        return { label: 'RESPONDIENDO', class: 'badge-responding' };
      case ASSISTANT_STATES.ERROR:
        return { label: 'ALERTA / ERROR', class: 'badge-error' };
      case ASSISTANT_STATES.IDLE:
      default:
        return { label: 'EN REPOSO', class: 'badge-idle' };
    }
  };

  const badge = getStateBadge();

  return (
    <div className="particle-sphere-wrapper" ref={containerRef}>
      {/* HUD Superior: Título y Estado */}
      <div className="sphere-hud-header">
        <div className="hud-title-box">
          <span className="hud-label">NÚCLEO NEURONAL</span>
          <h1 className="hud-name">RAFAEL</h1>
        </div>
        <div className={`state-pill ${badge.class}`}>
          <span className="state-pulse-dot" />
          <span className="state-text">{badge.label}</span>
        </div>
      </div>

      {/* HUD Inferior: Controles Rápidos de Prueba */}
      <div className="sphere-hud-footer">
        {/* Botonera de simulación para probar visualmente los 5 estados */}
        <div className="state-test-controls">
          <span className="test-label">PROBAR ESTADOS:</span>
          {Object.keys(ASSISTANT_STATES).map((st) => (
            <button
              key={st}
              className={`btn-test-state ${assistantState === st ? 'active' : ''}`}
              onClick={() => apiService.triggerStateManual(st)}
              title={`Activar estado ${st}`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
