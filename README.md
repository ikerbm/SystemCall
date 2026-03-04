# System Call

System Call es un prototipo de juego 2D en Python desarrollado con **Pygame**, que se distingue por su innovador sistema de comandos por voz. Los jugadores pueden lanzar hechizos, administrar entidades y recibir respuestas a través de un sistema de reconocimiento y síntesis de voz, aportando una experiencia inmersiva.

## 🚀 Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

1. **Crear un entorno virtual** dentro de la carpeta del proyecto:
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**:
   - En Windows: `venv\Scripts\activate`
   - En macOS/Linux: `source venv/bin/activate`

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el juego principal**:
   ```bash
   python main.py
   ```

---

## 🏗️ Arquitectura y Módulos del Proyecto

El proyecto está diseñado de forma modular, separando la lógica del juego, la representación gráfica, el sistema de magias y la interacción por voz. A continuación, se detalla qué hace cada parte y cómo se relacionan entre sí:

### 1. `main.py` (El Bucle Principal)
Es el núcleo del proyecto. Inicializa la ventana de Pygame y el bucle del juego (`while ejecutando`). 
- **Relación**: Interconecta todos los módulos. Instancia al `Jugador` (lógica) y `JugadorSprite` (gráficos), inicia un hilo asíncrono para el `Oyente` (reconocimiento de voz), e inicializa al `Administrator` y `Rafael` (síntesis de voz). También maneja los eventos del teclado para el movimiento.

### 2. Módulo `Core/` (El Cerebro del Sistema)
Contiene la lógica de los comandos de voz y la respuesta del sistema.
- **`Oyente.py`**: Utiliza `SpeechRecognition` para registrar el audio del micrófono del usuario y transcribirlo a texto.
  - *Relación*: Se ejecuta constantemente de fondo desde `main.py` para no detener visualmente el juego.
- **`Administrator.py`**: Interpreta el texto capturado por el Oyente (ej. "hechizo fuego" o "cambiar nombre").
  - *Relación*: Actúa como un *router*. Según el comando, manda ejecutar lógica en `Jugador` o solicita hechizos al módulo `Magias`.
- **`Rafael.py` ("La Voz del Mundo")**: Utiliza `pyttsx3` para hablar con el jugador.
  - *Relación*: El Administrator recurre a Rafael para confirmar acciones (ej. "Lanzando hechizo" o presentándose).

### 3. Módulo `Entidades/` (Lógica de Entidades)
- **`Jugador.py`**: Contiene únicamente la información lógica (estadísticas, salud, maná, nivel, inventario y hechizos disponibles) del personaje, de forma completamente agnóstica a los gráficos.
  - *Relación*: El Administrator o el módulo de Magias pueden afectar estas variables sin necesidad de modificar los gráficos.

### 4. Módulo `Imagenes/` (Representación Visual - Sprites)
Encargada de dibujar todo en pantalla a través de las clases nativas estándar de Pygame (`pygame.sprite.Sprite`).
- **`JugadorSprite.py`**: Gestiona el movimiento (con WASD o flechas), animación y renderizado de la entidad `Jugador`.
- **`ThermalElementSprite.py`**: Se encarga de mostrar y animar visualmente un hechizo en la pantalla.
  - *Relación*: Necesitan la información de los objetos lógicos (`Entidades` y `Magias`) para saber dónde y cómo dibujarse.

### 5. Módulo `Magias/` (Fábrica de Hechizos)
- **`Hecate.py` ("La Hechicera")**: Es una fábrica (`Factory Pattern`) de magias. Cuando el `Administrator` recibe el comando de crear un hechizo, Hecate analiza si es fuego, agua, tierra o aire, e instancia el hechizo correcto.
- **`Thermal.py`**: Reglas y comportamientos específicos de la magia de fuego.
  - *Relación*: El `Administrator` interactúa con Hecate, y Hecate se encarga de crear el objeto `Thermal` y asignarlo al `Jugador`.

### Extras
- **`requirements.txt`**: Define las librerías necesarias como `PyAudio`, `SpeechRecognition`, etc.
- **`utils/`**: Scripts de ayuda, como el encargado de recortar los *spritesheets* (`cortar_sprites`).
