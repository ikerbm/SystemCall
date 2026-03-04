import pygame


def cortar_sprites(sheet, ancho, alto, filas, columnas):
    matriz = []
    for y in range(filas):
        fila = []
        for x in range(columnas):
            sprite = sheet.subsurface(pygame.Rect(x * ancho, y * alto, ancho, alto))
            fila.append(sprite)
        matriz.append(fila)
    return matriz
