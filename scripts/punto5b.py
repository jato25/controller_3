#!/usr/bin/python
import rospy
from pacman.msg import actions
from pacman.srv import mapService
from pacman.msg import pacmanPos
from pynput.keyboard import Key, Listener
import threading

pub = rospy.Publisher('pacmanActions1', actions, queue_size=10)	 ## Publicador que controla al segundo pacman

def iniciar():
	global mapa, matriz, actual, siguiente, control, itera 
	itera = 0   				 	##Variable que verifica cuantas veces se ha verificado la direccion de la derecha del pacman
	control = False   				## Variable que determina cuando el humano tiene el control del pacman
	rospy.init_node('punto5b', anonymous = False)   ## Se inicia el nodo 
	mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService)
	mapa = mapaSolicitado("Harvey 2.0")
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)] 		 ##Se solicita el mapa y se guarda en una variable global
	rospy.Subscriber("pacmanCoord1", pacmanPos, andar)  				##Se suscribe a los topicos que muestran la posicion de ambos pacman para poder determinar cuando se encuentran
	rospy.Subscriber("pacmanCoord0", pacmanPos, recibir)
	actual = 2      	##Varaible que representa la direccion actual de movimiento 
	siguiente = 4		##Variavle que representa la ultima direccion seleccionada por el usuario


	for i in range(mapa.nObs):
		matriz[-mapa.obs[i].y - mapa.minY][mapa.obs[i].x - mapa.minX] = "%"

	tasa = rospy.Rate(10)
	while not rospy.is_shutdown():
		tasa.sleep()

def keypress(key): ##Metodo que permite controlar el pacman con las acciones del teclado 
	global control 
	if control:
		global siguiente
		if key == Key.esc: 
			rospy.signal_shutdown("Escape")
			return False
		else:
			if key.char == 'a' or key.char == 'w' or key.char == 's' or key.char == 'd':  ##Se guarda la accion siguiente 
				mensajes = {'a':3, 'w':0, 's':1, 'd':2}
				siguiente = int(mensajes[key.char])

def andar(data):
	global mapa, matriz, actual, siguiente, itera, info, control 
	if control:  ## Cuando el usuario tiene el control del pacman se verifica la direccion del movimiento y si es valida se mueve
		coord = {3:[0,-1],0:[-1,0],2:[0,1],1:[1,0],4:[0,0]}
		posx =  data.pacmanPos.x - mapa.minX  ##Posicion actual del pacman en las columnas de la matriz 
		posy = -data.pacmanPos.y - mapa.minY  ##Posicion actual del pacman en las filas de la matriz
		vec1 = coord[siguiente]
		if (siguiente == actual):
			siguiente = 4
		elif (matriz[posy + vec1[0]][posx + vec1[1]] == " " and siguiente != 4):
			actual = siguiente
		pub.publish(action = actual)
	else: ##Mientras el usuario no tiene el control, se ejecuta el algoritmo de la mano derecha 
		dirDerecha = {3:0,0:2,2:1,1:3}
		coord = {3:[0,-1],0:[-1,0],2:[0,1],1:[1,0]}
		siguiente = dirDerecha[actual]
		posx =  data.pacmanPos.x - mapa.minX  ##Posicion actual del pacman en las columnas de la matriz
		posy = -data.pacmanPos.y - mapa.minY  ##Posicion actual del pacman en las flias de la matriz
		vec1 = coord[siguiente]      ##Vector para verificar la direccion de movimiento a la derecha 
		vec2 = coord[actual]	     ##Vector para verificar la direccion de movimeinto actual		
		if ((info.pacmanPos.x == data.pacmanPos.x  or info.pacmanPos.x == data.pacmanPos.x + 1 or info.pacmanPos.x == data.pacmanPos.x - 1) and (info.pacmanPos.y == data.pacmanPos.y  or info.pacmanPos.y == data.pacmanPos.y + 1 or info.pacmanPos.y == data.pacmanPos.y - 1)):
			control = True				##En caso de que el pacman controlado por el humano este en una vecindad de uno se otorga el control a este 
		if (matriz[posy + vec2[0]][posx + vec2[1]] == " " and matriz[posy + vec1[0]][posx + vec1[1]] == "%"):   ## Si la direccion actual esta disponible (no hay obstaculo) y en el espacio de la derecha hay un obstaculo se continua en la direccion actual  
			itera = 0
			pub.publish(action = actual)
			return
		elif (matriz[posy + vec1[0]][posx + vec1[1]] == " " and itera != 1):  ##Si la direccion de la derecha esta libre y se han verificado todas las direcciones disponibles, se gira a la derecha. 
##En el condicional del if se evalua "itera != 1" ya que en este caso el algoritmo esta evaluando la direccion opuesta a la que pacman se dirige actualmente y se devolveria sin evaluar la izquierda
			actual = siguiente
			pub.publish(action = actual)
			itera = 0
			return
		else: ##Si la direccion de la derecha no esta disponible se aumenta el iterador y se reinicia el metodo hasta encontrar una direccion que este disponible (maximo 6 iteraciones)
			actual = siguiente
			itera = itera + 1
			andar(data)

def recibir(data):
	global  info
	info = data  ##Cada vez que llega la informacion del pacman controlado por el usuario es actualizada la variable global info, para evaluar la cercania y determinar si el usuario toma el control
			

def ThreadInputs():
	with Listener(on_press = keypress) as listener:
		listener.join()

if __name__ == '__main__':
	try:
		threading.Thread(target=ThreadInputs).start()
		iniciar()
	except rospy.ServiceException:
		pass
