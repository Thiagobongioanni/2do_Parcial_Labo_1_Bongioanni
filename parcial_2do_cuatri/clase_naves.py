import pygame
import random

class Naves:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((800, 600))
        self.lista_naves_enemigas = self.crear_lista_naves(5)  # Ejemplo: crear 5 naves enemigas

    def crear_nave(self, imagen, x, y, alto, ancho):
        imagen_nave = pygame.image.load(imagen)
        imagen_nave = pygame.transform.scale(imagen_nave, (alto, ancho))
        rect_nave = pygame.Rect(x, y, alto, ancho)

        dict_nave = {}
        dict_nave["surface"] = imagen_nave
        dict_nave["rect"] = rect_nave
        dict_nave["visible"] = True
        dict_nave["posicion"] = [random.randint(0,400),-100]
        dict_nave["puede_disparar"] = True
        dict_nave["velocidad"] = random.randint(2, 10)

        return dict_nave

    def crear_lista_naves(self, cantidad):
        list_naves_enemigas = []
        ancho_nave = 50
        alto_nave = 50

        while len(list_naves_enemigas) < cantidad:
            list_naves_enemigas.append(self.crear_nave("nave_enemiga.png", 50, 50, ancho_nave, alto_nave))

        return list_naves_enemigas

