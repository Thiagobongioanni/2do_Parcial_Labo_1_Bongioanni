import pygame
from clase_naves import Naves
from biblioteca_parcial import crear_sql_jugadores
from biblioteca_parcial import limpiar_datos_sql
from biblioteca_parcial import actualizar_pantalla
from biblioteca_parcial import controlar_estado_juego_principal
from biblioteca_parcial import imprimir_score
from biblioteca_parcial import movimiento_nave_player
from biblioteca_parcial import controlar_rect_disparo_enemigo

from colores import RED1
from colores import WHITE
from colores import GREEN1
from colores import BLACK

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
RADIO = 80
TIEMPO_DISPARO_ENEMIGO= 2500
CANTIDAD_INICIAL_NAVES = 5

pygame.init()
pygame.mixer.init()

naves = Naves()

#TIMER
timer_segundos = pygame.USEREVENT # evento de usuario (propio)
pygame.time.set_timer(timer_segundos,100) #1000 es un segundo

posicion_nave_player = [360,540]

#game over
font = pygame.font.Font(None, 48)
game_over_surface = font.render("Game Over", True, RED1)
game_over_rect = game_over_surface.get_rect()
game_over_rect.center = (ANCHO_VENTANA // 2, ALTO_VENTANA // 2)
tiempo_game_over = 0
tiempo_limite = 2000

#imagen
imagen_nave_player = pygame.image.load("nave_player.png")
imagen_nave_player= pygame.transform.scale(imagen_nave_player,(50,50))
rect_player = pygame.Rect(0,0,50,50)

fondo_inicio = pygame.image.load("fondo_inicio.png")
fondo_inicio = pygame.transform.scale(fondo_inicio, (ANCHO_VENTANA, ALTO_VENTANA))
fondo = pygame.image.load("galaxy.png")
fondo = pygame.transform.scale(fondo, (ANCHO_VENTANA, ALTO_VENTANA))
pantalla = pygame.display.set_mode((ANCHO_VENTANA,ALTO_VENTANA))
pygame.display.set_caption("Galaxy")

imagen_jugar = pygame.image.load("play_boton.png")
imagen_jugar = pygame.transform.scale(imagen_jugar,(130,130))
rect_boton = imagen_jugar.get_rect()
rect_boton.y = 160
rect_boton.x = 310

imagen_puntaje = pygame.image.load("score_boton.png")
imagen_puntaje = pygame.transform.scale(imagen_puntaje,(110,50))
rect_boton_puntos = imagen_puntaje.get_rect()
rect_boton_puntos.y = 260
rect_boton_puntos.x = 320

#nombre jugador
nombre_jugador = ""
input_rect = pygame.Rect(320, 330, 140, 32)
input_active = False

# Fuente para mostrar las vidas
font_vidas = pygame.font.Font(None, 36)  
cont_vidas = 3


#musica juego
pygame.mixer.music.load("musica_juego.mp3")
pygame.mixer.music.play(-1) 

#disparo sonido
sonido_disparo_jugador = pygame.mixer.Sound("sonido_disparo.mp3")

flag_correr = True

cantidad = CANTIDAD_INICIAL_NAVES
list_naves_enemigas = naves.crear_lista_naves(cantidad)
disparo_activo_player = False
puede_disparar_player = True
lista_disparos_player = []
lista_disparos_enemigos = []
tiempo_transcurrido_disparo_enemigo = 0
puntos = 0
estado_juego = 0
jugadores_datos=[]
jugadores = []

jugadores = crear_sql_jugadores(nombre_jugador,puntos)

while flag_correr:
    
    lista_eventos = pygame.event.get()

    if estado_juego == 0:
       
       pantalla.blit(fondo_inicio, (0, 0)) 
       pantalla.blit(imagen_jugar, rect_boton)
       pantalla.blit(imagen_puntaje, rect_boton_puntos)

       pygame.draw.rect(pantalla, WHITE, input_rect)
       font_input = pygame.font.Font(None, 28)
       texto_input = font_input.render(nombre_jugador, True,BLACK)
       pantalla.blit(texto_input, (input_rect.x + 5, input_rect.y + 5))
   

       pygame.display.flip()

       for evento in lista_eventos:
           if evento.type == pygame.QUIT:
              flag_correr = False
              limpiar_datos_sql()
              pygame.mixer.music.stop()
              pygame.mixer.quit()
      
           if evento.type == pygame.MOUSEBUTTONDOWN:
                
              lista_click = list(evento.pos)
              estado_juego = controlar_estado_juego_principal(lista_click,rect_boton,rect_boton_puntos)

              if lista_click[0] > input_rect.x and lista_click[0] < input_rect.x + input_rect.width:
                 if lista_click[1] > input_rect.y and lista_click[1] < input_rect.y + input_rect.height:
                    input_active = not input_active
                 else:
                      input_active = False

           if evento.type == pygame.KEYDOWN:  # Verificar si se ha presionado una tecla
              if input_active:
                 if evento.key == pygame.K_RETURN:
                    for jugador in jugadores:
                        jugadores_datos.append(jugador.copy())
                        
                    input_active = False
                 elif evento.key == pygame.K_BACKSPACE:
                      nombre_jugador = nombre_jugador[:-1]
                 else:
                      nombre_jugador += evento.unicode
      
    elif estado_juego == 1:
      
      for evento in lista_eventos:
           pantalla.blit(fondo, (0, 0)) 
           
           if evento.type == pygame.QUIT:
              flag_correr = False
              limpiar_datos_sql()
              pygame.mixer.music.stop()
              pygame.mixer.quit()

           if evento.type == pygame.KEYDOWN:
              if evento.key == pygame.K_ESCAPE:
                 estado_juego = 0

           imprimir_score(jugadores_datos,pantalla)
              
    elif estado_juego == 2:
       pantalla.blit(fondo, (0, 0)) 

       for evento in lista_eventos:
           
           if evento.type == pygame.QUIT:
              flag_correr = False
              limpiar_datos_sql()
              pygame.mixer.music.stop()
              pygame.mixer.quit()

           if evento.type == timer_segundos:
              i = 0
              # Movimiento naves enemigas
              for nave in list_naves_enemigas:
                  if nave["visible"]:
                     nave["posicion"][1] += nave["velocidad"]  # Mover la nave enemiga usando su velocidad individual
                     if nave["posicion"][1] >= ALTO_VENTANA:
                        nave["posicion"][1] = -RADIO * 2 
                  else:
                      i += 1
                  if i == cantidad:
                     cantidad += 1
                     list_naves_enemigas = naves.crear_lista_naves(cantidad)
                     if nave["posicion"][1] >= ALTO_VENTANA:
                        nave["posicion"][1] = -RADIO * 2 
                     i = 0
              
              tiempo_transcurrido_disparo_enemigo += 100

       #movimiento nave player
       lista_teclas = pygame.key.get_pressed()
       
       posicion_nave_player = movimiento_nave_player(lista_teclas,posicion_nave_player,rect_player,ANCHO_VENTANA,ALTO_VENTANA)
      
       if lista_teclas[pygame.K_SPACE] and puede_disparar_player: 
          lista_disparos_player.append([posicion_nave_player[0]+25, posicion_nave_player[1]])
          puede_disparar_player = False
          disparo_activo_player = True
          sonido_disparo_jugador.play()
       if not lista_teclas[pygame.K_SPACE]:
          puede_disparar_player = True
       
       rect_player[0] = posicion_nave_player[0]
       rect_player[1] = posicion_nave_player[1]

       controlar_rect_disparo_enemigo(list_naves_enemigas,lista_disparos_enemigos)

       if disparo_activo_player:
          disparos_colisionados = []
          for disparo in lista_disparos_player:
              disparo[1] -= 7  # Velocidad del disparo hacia arriba
              pygame.draw.circle(pantalla, RED1, (disparo[0], disparo[1]), 5) 
              rect_disparo = pygame.Rect(disparo[0]-5, disparo[1]-6, 10, 10) 

              for nave in list_naves_enemigas:
                  if rect_disparo.colliderect(nave["rect"]) and nave["visible"]:
                     nave["visible"] = False
                     puntos += 100
                     jugadores[0]["puntos"] = puntos
                     jugadores[0]["nombre"] = nombre_jugador
                     disparos_colisionados.append(disparo)
                     break

          for disparo in disparos_colisionados:
              lista_disparos_player.remove(disparo)
 
       font = pygame.font.SysFont("Arial",20)
       texto = font.render("SCORE: {0}".format(jugadores[0]["puntos"]),True,WHITE)
       pantalla.blit(texto,(10,10))

       if tiempo_transcurrido_disparo_enemigo >= TIEMPO_DISPARO_ENEMIGO:
          for nave in list_naves_enemigas:
              if nave["visible"]:
                 nave["puede_disparar"] = True
                 sonido_disparo_jugador.play()
          tiempo_transcurrido_disparo_enemigo = 0

       for disparo_enemigo in lista_disparos_enemigos:
           disparo_enemigo[1] += 5
           pygame.draw.circle(pantalla, GREEN1, (disparo_enemigo[0], disparo_enemigo[1]), 5)
           rect_disparo_enemigo = pygame.Rect(disparo_enemigo[0] - 5, disparo_enemigo[1] - 6, 10, 10)
           if rect_disparo_enemigo.colliderect(rect_player):
              if cont_vidas == 0:
                 if tiempo_game_over == 0:
                    tiempo_game_over = pygame.time.get_ticks()
              else:
                  cont_vidas -= 1
                  lista_disparos_enemigos.remove(disparo_enemigo)
       
       pantalla.blit(imagen_nave_player,(posicion_nave_player))
       actualizar_pantalla(list_naves_enemigas,pantalla)

       vidas_surface = font_vidas.render(f"Vidas: {cont_vidas}", True, WHITE)
       pantalla.blit(vidas_surface, (0, 575))

       if tiempo_game_over != 0:
          tiempo_actual = pygame.time.get_ticks()
          pantalla.blit(game_over_surface, game_over_rect)
          #reiniciar valores a su estado original luego de perder
          nombre_jugador = ""
          puntos = 0
          cont_vidas = 3
          list_naves_enemigas = naves.crear_lista_naves(CANTIDAD_INICIAL_NAVES)
          cantidad = CANTIDAD_INICIAL_NAVES
          lista_disparos_enemigos = []
          for nave in list_naves_enemigas:
              nave["puede_disparar"] = True
              nave["visible"] = True
          if tiempo_actual - tiempo_game_over >= tiempo_limite:
             tiempo_game_over = 0
             estado_juego = 0

    pygame.display.flip()

pygame.mixer.quit()
pygame.quit()