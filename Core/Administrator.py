from . import Rafael
from Entidades import Jugador
from Magias import Hecate


Opciones_Generate= ["hechizo"]
Opciones_Fabricate = ["fabricar"]
Opciones_Discharge= ["disparar"]
Opciones_presentacion= ["presentar","preséntate","presentación"]


class Administrator:
    def __init__(self,personaje_activo : Jugador,voz_del_mundo : Rafael): # agregar confirmaciones de contenido
        self.personaje_activo = personaje_activo
        self.comando = {}
        self.titulo = "El Administrador"
        self.respuesta = None
        self.voz_del_mundo = voz_del_mundo

    def Identificar_comando(self,comando):
        self.comando.update({
            "comando" : comando.lower().split(), # Dividimos el comando en palabras para facilitar la identificación
            "estado" : "analizando"
        })

        # identificamos el comando como una orden al sistema de hechizos
        # generar - fabricar - curar - invocar
        if any(palabra in Opciones_Generate for palabra in self.comando["comando"]):
            self.Iniciar_lanzamiento_hechizo()

        #identificamos el comando como una orden en base a hechizos ya existentes
        if any(palabra in Opciones_Discharge for palabra in self.comando["comando"]):
            self.Iniciar_disparo()
            #ejecutar la secuencia de comandos para discharge
        
        #identificamos comandos de control maestro, 
        if self.voz_del_mundo.nombre.lower() in self.comando["comando"]:
            print("Comando de control maestro detectado")
            self.Iniciar_comando_maestro()
        
        return self.respuesta

    def Iniciar_lanzamiento_hechizo(self):
        self.comando.update({"estado" : "ejecutando"})
        magia = Hecate(self.comando, self.personaje_activo, self.voz_del_mundo).generate()
        if magia:
            self.personaje_activo.hechizos.update({
                f"{magia.tipo}": magia
            })
            self.respuesta = "hechizo"

    def Iniciar_fabricacion(self):
        self.comando.update({"estado" : "ejecutando"})
        self.respuesta = self.voz_del_mundo.Voz_del_mundo("Iniciando fabricacion de " + self.comando["comando"][-1])
        # Aquí puedes agregar la lógica para el comando "fabricate"

    def Iniciar_disparo(self):
        self.comando.update({"estado" : "ejecutando"})
        self.respuesta = self.voz_del_mundo.Voz_del_mundo("Lanzando hechizo")  
        # Aquí puedes agregar la lógica para el comando "discharge"  

    def Iniciar_comando_maestro(self):
        #Cambiar nombre de la voz del mundo
        if "cambiar" in self.comando["comando"] and "nombre" in self.comando["comando"]:
            self.comando.update({"estado" : "ejecutando"})
            nuevo_nombre = self.comando["comando"][-1]
            self.voz_del_mundo.Cambiar_nombre(nuevo_nombre)

        #presentacion de la voz del mundo
        if any(palabra in Opciones_presentacion for palabra in self.comando["comando"]):
            print("Comando de presentacion detectado")
            self.comando.update({"estado" : "ejecutando"})
            self.voz_del_mundo.Presentacion()
        # Aquí puedes agregar la lógica para el comando "master command"

        