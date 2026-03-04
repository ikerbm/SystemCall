

class Jugador():
    def __init__(self, nombre, nivel,salud,mana,energia,poder_sagrado):
        #atributos del jugador
        self.nombre = nombre
        self.titulo ="El Novato"
        self.nivel = nivel
        self.experiencia = 0
        self.siguient_nivel = 100
        self.salud = salud
        self.salud_max = salud
        self.mana = mana
        self.mana_max = mana
        self.energia = energia
        self.poder_sagrado = poder_sagrado
        # objetos, hechizos y estadisticas del jugador
        self.equipamiento ={
            "arma": None,
            "armadura": None,
            "accesorio": None
        }
        self.hechizos = {
            "fuego": None,
            "agua": None,
            "tierra": None,
            "aire": None,
            "sagrado": None,    
            "sombra": None,
        }
        self.estadisticas = {
            "fuerza": 0,
            "destreza": 0,
            "inteligencia": 0,
            "sabiduria": 0,
            "agilidad": 0,
            "resistencia": 0,
            "suerte": 0
        }
        

    def nivelUp(self):

        if self.experiencia >= self.siguient_nivelnivel:
            self.nivel += 1
            self.experiencia = self.experiencia - self.siguient_nivel
            self.siguient_nivel += 100
            
            print(f"{self.nombre} ha subido de nivel a {self.nivel}")
        else:
            print(f"{self.nombre} no tiene suficiente experiencia para subir de nivel")





