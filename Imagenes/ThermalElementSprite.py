import os
import pygame
import math
from utils import cortar_sprites


ruta_img = os.path.join(os.path.dirname(__file__), "ThermalElement.png")

class ThermalElementSprite(pygame.sprite.Sprite):
    def __init__(self, jugador_activo):
        super().__init__()
        sabana_thermal = pygame.image.load(ruta_img).convert_alpha()
        matriz_thermal = cortar_sprites(sabana_thermal, 16, 16, 1, 5) #Corta la sabana de thermal

        self.spritesheet = matriz_thermal #sabana ya cortada
        self.jugador_activo = jugador_activo

        self.cargar_animaciones()
        self.image = self.sprites["estatico"][0]
        self.rect = self.image.get_rect(topleft=(16, 16))
        self.angulo = 0 # Inicializa el ángulo a 0
        self.radio = 50 # Radio del círculo
        self.velocidad = 2 # Velocidad de rotación

        self.frame_index = 0
        self.contador_frames = 0
        self.frame_rate = 4  # Cambia este valor para ajustar la velocidad de la animación
        #self.sonido_paso = pygame.mixer.Sound("Sonidos/paso.wav") se puede pensar

    def cargar_animaciones(self):
        # Cambia las filas según cómo esté organizada tu hoja
        self.sprites = {
            "estatico": self.spritesheet[0],
        }

    def update(self):
        self.mover()
        self.animar()

    def mover(self):
        self.angulo += self.velocidad  # Aumenta el ángulo para la rotación
        if self.angulo >= 360:
            self.angulo = 0
        
        rad = math.radians(self.angulo)
        # centro del jugador
        jugador_centro = (self.jugador_activo.rect.center)

        # calcular la nueva posición circular
        new_X = jugador_centro[0] + self.radio * math.cos(rad)
        new_Y = jugador_centro[1] + self.radio * math.sin(rad)
        
        self.rect.center = (new_X, new_Y)  # Actualiza la posición del sprite
        #self.sonido_paso.play() # Reproduce el sonido de paso al mover el sprite


    def animar(self):
        animacion = self.sprites["estatico"]

        self.contador_frames += 1

        if self.contador_frames >= self.frame_rate:
            self.frame_index += 1
            if self.frame_index >= len(animacion):
                self.frame_index = 1  # saltar el 0
            self.contador_frames = 0


        self.image = animacion[self.frame_index]

