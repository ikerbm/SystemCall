from Entidades import Jugador


class Thermal:
    def __init__(self,jugador_activo: Jugador):
        self.daño = 10
        self.efecto = "quemadura"
        self.duracion = 5
        self.tipo = "fuego"
        self.efecto_secundario = "reducción de velocidad"
        self.mana = jugador_activo.mana
        self.energia = jugador_activo.energia
        self.poder_sagrado = jugador_activo.poder_sagrado
        self.poder_sagrado_minimo = 1
        self.autorizacion = self.__verificar_recursos()
        
        self.desplegado = False #verifica si el hechizo ya fue desplegado o no en pantalla

    def __verificar_recursos(self): #se puede agregar un titulo o algo para dar buffos al jugador
        if self.poder_sagrado >= self.poder_sagrado_minimo: #verificar nivel de artes sagradas
            if self.mana > 10: #verificar cantidad necesaria de mana
                return True
            else:
                return False
        else:
            return False

    def __nivelar_hechizo(self):
        self.daño = self.daño * (0.5 * self.poder_sagrado)
        self.duracion += 1 * (self.poder_sagrado / 10)
        

    def generar_hechizo(self):
        if self.autorizacion:
            self.__nivelar_hechizo()
        else:
            raise ValueError("El jugador no cumple con los requisitos para usar magia de fuego.")

        


        