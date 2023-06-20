import pygame
import colores
import sqlite3

def actualizar_pantalla(lista_naves_enemigas: list, pantalla):
    for e_nave in lista_naves_enemigas:
        if e_nave["visible"]:
            pantalla.blit(e_nave["surface"], e_nave["rect"])

def crear_sql_jugadores(nombre,puntos):

    with sqlite3.connect("bd_btf.db") as conexion:
        try:
            sentencia = '''CREATE TABLE IF NOT EXISTS jugadores
                           (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           nombre TEXT,
                           puntos REAL
                           )
                        '''
            conexion.execute(sentencia)
            print("Se creó la tabla jugadores")                       
        except sqlite3.OperationalError:
            print("La tabla jugadores ya existe")
        try:
            conexion.execute("INSERT INTO jugadores(nombre, puntos) VALUES (?,?)", (nombre,puntos))
            conexion.commit()  # Actualiza los datos realmente en la tabla
        
        except sqlite3.Error as error:
            print("Error al insertar las puntuaciones:", error)

        jugadores = []
        cursor = conexion.execute("SELECT * FROM jugadores ORDER BY puntos DESC LIMIT 3")
        for fila in cursor:
            jugadores.append({
                "nombre": fila[1],
                "puntos": fila[2]
            })
        

    return jugadores

def limpiar_datos_sql():
   with sqlite3.connect("bd_btf.db") as conexion:
        try:
            conexion.execute("DELETE FROM jugadores")
            print("Se borraron todas las puntuaciones.")
        except sqlite3.Error as error:
             print("Error al borrar las puntuaciones:", error)

def controlar_estado_juego_principal(lista_click,rect_boton,rect_boton_puntos):
    estado_juego = 0

    if lista_click[0] > rect_boton[0] and lista_click[0] < (rect_boton[0] + rect_boton[2]):
       if lista_click[1] > rect_boton[1] and lista_click[1] < (rect_boton[1] + rect_boton[3]):
          estado_juego = 2

    if lista_click[0] > rect_boton_puntos[0] and lista_click[0]< (rect_boton_puntos[0]+rect_boton_puntos[2]):
       if lista_click[1]> rect_boton_puntos[1] and lista_click[1]< (rect_boton_puntos[1]+rect_boton_puntos[3]):
          estado_juego = 1
    return estado_juego

def imprimir_score(jugadores_datos,pantalla):
    for i in range(len(jugadores_datos)):
        jugadores_datos = sorted(jugadores_datos, key=lambda x: x["puntos"], reverse=True)
        # Mostrar nombre del jugador
        font_nombre = pygame.font.SysFont("Arial", 24)
        texto_nombre = font_nombre.render(jugadores_datos[i]["nombre"], True, colores.WHITE)
        pantalla.blit(texto_nombre, (120, 80 + (i * 25)))

        # Mostrar puntaje del jugador
        font_puntos = pygame.font.SysFont("Arial", 24)
        texto_puntos = font_puntos.render(str(jugadores_datos[i]["puntos"]), True, colores.WHITE)
        pantalla.blit(texto_puntos, (300 * 2.5, 80 + (i * 25)))
        i += 1

def movimiento_nave_player(lista_teclas,posicion_nave_player,rect_player,ANCHO_VENTANA,ALTO_VENTANA):
    if True in lista_teclas:
        if lista_teclas[pygame.K_RIGHT]:
          if posicion_nave_player[0] + rect_player.width < ANCHO_VENTANA:
             posicion_nave_player[0] += 3
        if lista_teclas[pygame.K_LEFT]:
           if posicion_nave_player[0] > 0: 
              posicion_nave_player[0] -= 3
        if lista_teclas[pygame.K_UP]:
           if posicion_nave_player[1] > ALTO_VENTANA // 2:
              posicion_nave_player[1] -= 3
        if lista_teclas[pygame.K_DOWN]:
           if posicion_nave_player[1] < ALTO_VENTANA - rect_player.height:
              posicion_nave_player[1] += 3    
    return posicion_nave_player

def controlar_rect_disparo_enemigo(list_naves_enemigas,lista_disparos_enemigos):
    desplazamiento = 60  # Separación horizontal entre las naves enemigas

    for i, nave in enumerate(list_naves_enemigas):
        if nave["visible"]:
           nave["rect"].x = i * desplazamiento + nave["posicion"][0]
           nave["rect"].y = nave["posicion"][1]
           i += 1
        if nave["puede_disparar"]:
           lista_disparos_enemigos.append([nave["rect"].x + nave["rect"].width // 2, nave["rect"].y + nave["rect"].height])
           nave["puede_disparar"] = False
    