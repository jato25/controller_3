#!/usr/bin/python
import rospy
from pacman.msg import actions
from pacman.srv import mapService
from pacman.msg import pacmanPos
from pynput.keyboard import Key, Listener
import threading

pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)	  ##Se crea el publicador a cargo de mostrar las acciones que debe realizar el pacman 

def iniciar(): ## Se inicia el nodo y se crea la matriz con los obstaculos correspondientes al mapa cargado 
	global mapa, matriz, actual, siguiente
	rospy.init_node('punto5a', anonymous = False)		 ##Se inicia el nodo 
	mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService) 
	mapa = mapaSolicitado("Harvey") 					## Se realiza el protocolo de solicitud del mapa 
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)]
	rospy.Subscriber("pacmanCoord0", pacmanPos, andar)   			## Se suscribe al topico que retorna la posicion del pacman 
	actual = 4
	siguiente = 4			##Variable que guarda el ultimo moviemiento presionado por el usuario


	for i in range(mapa.nObs):
		matriz[-mapa.obs[i].y - mapa.minY][mapa.obs[i].x - mapa.minX] = "%"	##Se carga el mapa con los obtaculos representados por %

	tasa = rospy.Rate(10)
	while not rospy.is_shutdown():
		tasa.sleep()

def keypress(key): 		 ## Al presionar cualquier tecla del teclado este metodo es llamado
	global siguiente
	if key == Key.esc: 
		rospy.signal_shutdown("Escape")
		return False 		    ##En caso de presionar la tecla Esc se termina el nodo 
	else:
		if key.char == 'a' or key.char == 'w' or key.char == 's' or key.char == 'd':
			mensajes = {'a':3, 'w':0, 's':1, 'd':2}
			siguiente = int(mensajes[key.char])    	 ##Se actualiza el valor del movimiento siguiente

def andar(data): 		### Metodo que maneja la recepcion de archivos de pamcan
	global mapa, matriz, actual, siguiente
	coord = {3:[0,-1],0:[-1,0],2:[0,1],1:[1,0],4:[0,0]}  ## Se crea un diccionario con las posiciones que deben ser verificadas para realizar cada movimiento
	posx =  data.pacmanPos.x - mapa.minX  ## Posicion del pacman en las columnas de la matriz de Strings
	posy = -data.pacmanPos.y - mapa.minY  ## Posicion del pacman en las filas de la matriz de Strings
	vec1 = coord[siguiente]			## Vector con las posiciones contiguas al pacman que deben ser verificadas 
	if (siguiente == actual):  		## En caso de que ya se haya ejecutado el movimiento se descarta el movimiento siguiente
		siguiente = 4
	elif (matriz[posy + vec1[0]][posx + vec1[1]] == " " and siguiente != 4):   ## Si no hay obstaculo en la posicion que desea mover se cambia el valor de la variable actual y se publica
		actual = siguiente
	pub.publish(action = actual)
		

def ThreadInputs():
	with Listener(on_press = keypress) as listener:
		listener.join()

if __name__ == '__main__':
	try:
		threading.Thread(target=ThreadInputs).start()
		iniciar()
	except rospy.ServiceException:
		pass
