import os
import pygame
from utils import cortar_sprites


ruta_img = os.path.join(os.path.dirname(__file__), "Rain.png")


class JugadorSprite(pygame.sprite.Sprite):
    def __init__(self,jugador_logico):
        super().__init__()
        spritesheet = pygame.image.load(ruta_img).convert_alpha()
        matriz_sprites = cortar_sprites(spritesheet, 64, 64, 25, 7)
        self.jugador_logico = jugador_logico #Jugador logico
        self.spritesheet = matriz_sprites #sabana ya cortada

        self.cargar_animaciones()
        self.image = self.sprites["estatico_abajo"][0]
        self.rect = self.image.get_rect(topleft=(64, 64))

        self.direccion = "abajo"
        self.movimiento = False
        self.velocidad = 4
        self.frame_index = 0
        self.contador_frames = 0
        self.frame_rate = 4  # Cambia este valor para ajustar la velocidad de la animación
        #self.sonido_paso = pygame.mixer.Sound("Sonidos/paso.wav") se puede pensar

    def cargar_animaciones(self):
        # Cambia las filas según cómo esté organizada tu hoja
        self.sprites = {
            "estatico_abajo": self.spritesheet[0],
            "estatico_arriba": self.spritesheet[1],
            "estatico_izquierda": self.spritesheet[2],
            "estatico_derecha": self.spritesheet[3],
            "correr_abajo": self.spritesheet[8],
            "correr_arriba": self.spritesheet[9],
            "correr_izquierda": self.spritesheet[10],
            "correr_derecha": self.spritesheet[11],
            "caminar_abajo": self.spritesheet[16],
            "caminar_arriba": self.spritesheet[17],
            "caminar_izquierda": self.spritesheet[18],
            "caminar_derecha": self.spritesheet[19],
        }

    def update(self, teclas):
        self.mover(teclas)
        self.animar()

    def mover(self, teclas):
        self.movimiento = False  # reset para detectar si no se mueve

        if teclas[pygame.K_w]:
            self.direccion = "arriba"
            self.rect.y -= self.velocidad
            self.movimiento = True
        if teclas[pygame.K_s]:
            self.direccion = "abajo"
            self.rect.y += self.velocidad
            self.movimiento = True
        if teclas[pygame.K_a]:
            self.direccion = "izquierda"
            self.rect.x -= self.velocidad
            self.movimiento = True
        if teclas[pygame.K_d]:
            self.direccion = "derecha"
            self.rect.x += self.velocidad
            self.movimiento = True


    def animar(self):
        if self.movimiento:
            animacion = self.sprites["caminar_" + self.direccion]
        else:
            animacion = self.sprites["estatico_" + self.direccion]

        self.contador_frames += 1

        if self.contador_frames >= self.frame_rate:
            self.frame_index += 1
            if self.frame_index >= len(animacion):
                self.frame_index = 1  # saltar el 0
            self.contador_frames = 0


        self.image = animacion[self.frame_index]

