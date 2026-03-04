import pygame
import sys
import threading
from Entidades import Jugador
from Imagenes import JugadorSprite, ThermalElementSprite
from Core import Rafael, Administrator, Oyente
from utils import cortar_sprites


WIDTH, HEIGHT = 1820, 960 # Dimensiones de la ventana
FPS = 60

comando_actual = None
escuchando = False
diccionario_tipos_magia = {"fuego": ThermalElementSprite} # Diccionario de tipos de magia y sus respectivas clases


def escuchar_comando_en_hilo(oyente):
    global comando_actual, escuchando
    comando_actual = input("Escuchando comando: ")  # Simulación de entrada de voz
    comando_actual = comando_actual.lower()
    escuchando = False

def mostrar_hechizos(jugador : JugadorSprite):
    listos_despliegues = []
    # Aquí puedes implementar la lógica para mostrar los hechizos del jugador
    # Por ejemplo, podrías imprimirlos en la consola o mostrarlos en la pantalla
    print("Hechizos disponibles:")
    for tipo, hechizo in jugador.jugador_logico.hechizos.items():
        if hechizo:
            if not hechizo.desplegado:
                constructor = diccionario_tipos_magia.get(tipo)
                listos_despliegues.append(constructor(jugador))
                hechizo.desplegado = True  # Marca el hechizo como desplegado
    return listos_despliegues


def main():
    global comando_actual, escuchando


    pygame.init()
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("System Call")

    reloj = pygame.time.Clock()    

    #Crear jugador
    jugador_logico = Jugador("Rain", 100, 100, 50, 100, 100)
    jugador_sprite = JugadorSprite(jugador_logico) #Instancia de la clase JugadorSprite

    #Crear un thermal para probar
    #prueba_thermal = ThermalElementSprite(matriz_thermal,jugador_sprite) #Instancia de la clase ThermalElementSprite

    rafael = Rafael(jugador_logico) # Inicializa la voz del mundo
    #rafael.Voz_del_mundo(f"System call en linea, esperando ordenes, {jugador_logico.nombre}")
    admin = Administrator(jugador_logico,rafael) # Inicializa el administrador
    oyente = Oyente() # Inicializa el oyente
    
    grupo_sprites = pygame.sprite.Group() #Grupo de sprites
    grupo_hechizos = pygame.sprite.Group() #Grupo de hechizos
    grupo_sprites.add(jugador_sprite) #Agrega el jugador al grupo de sprites
    #grupo_hechizos.add(prueba_thermal) #Agrega el thermal al grupo de sprites
    
    #bucle principal
    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        #iniciar hilo de escucha si no hay uno activo
        if not escuchando:
            escuchando = True
            threading.Thread(target=escuchar_comando_en_hilo, args=(oyente,), daemon=True).start()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ejecutando = False

        if comando_actual:
            print("Comando recibido:", comando_actual)
            # Procesar el comando recibido
            respuesta = admin.Identificar_comando(comando_actual)
            if "salir" in comando_actual:
                ejecutando = False
                print("Saliendo del programa...")
                rafael.Voz_del_mundo("System Call fuera de linea...")
            comando_actual = None # Reiniciar el comando actual
            
            if respuesta == "hechizo":
                lista_despliegue = mostrar_hechizos(jugador_sprite)
                for magia in lista_despliegue:
                    grupo_hechizos.add(magia)

        teclas = pygame.key.get_pressed()
        grupo_sprites.update(teclas) # Actualiza el jugador y otros sprites
        grupo_hechizos.update() # Actualiza los hechizos
        # Actualiza la pantalla
        pantalla.fill((30, 30, 30)) # Rellena la pantalla con un color gris oscuro
        grupo_sprites.draw(pantalla) # Dibuja los sprites en la pantalla
        grupo_hechizos.draw(pantalla)
        pygame.display.flip() #Actualiza la pantalla

    pygame.quit()
    sys.exit()
if __name__ == "__main__":

    main()
            
        