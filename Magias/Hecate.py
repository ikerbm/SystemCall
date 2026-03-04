from Core.Rafael import Rafael
from Entidades import Jugador
from .Thermal import Thermal

Opciones_Elementales = ["fuego", "agua", "tierra", "aire"]
class Hecate: #Hécate, diosa de la magia y la brujería
    def __init__(self, comando,jugador_activo: Jugador, voz_del_mundo: Rafael):
        self.comando = comando["comando"]
        self.jugador_activo = jugador_activo
        self.voz_del_mundo = voz_del_mundo
        self.titulo = "La Hechicera"
        self.name = "Hecate"
    
    def __seleccionar_elemento(self, elemento):
        try:
            if elemento == "fuego":
                print("elemento fuego seleccionado")
                magia = Thermal(self.jugador_activo)
                magia.generar_hechizo()
                return magia
            elif elemento == "agua":
                return "Agua"
            elif elemento == "tierra":
                return "Tierra"
            elif elemento == "aire":
                return "Aire"
            else:
                raise ValueError("Elemento no válido. Debe ser fuego, agua, tierra o aire.")
        except ValueError as e:
            print(f"Error: {e}")
            Rafael().Voz_del_mundo(str(e))
            return None 
    
    def generate(self):
        if self.comando[-1] in Opciones_Elementales:
            elemento = self.comando[-1]
            magia = self.__seleccionar_elemento(elemento)
            return magia

        else: 
            print("Elemento no válido. Por favor, elige entre fuego, agua, tierra o aire.")
            return None

    def fabricate(self):
        pass
        # Aquí puedes agregar la lógica para el comando "fabricate"
        # Por ejemplo, crear un nuevo objeto o recurso basado en el comando
        # y aplicarlo al jugador activo o al mundo del juego.

    def discharge(self):
        pass