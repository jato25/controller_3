#!/usr/bin/python3
import rospy
from pacman.msg import actions    """ se importan losmensajes que indican acciones que debe ejecutar el pacman """
from pacman.srv import mapServicen """ se importa el servicio para solicitar el mapa"""
from pacman.msg import pacmanPos """ se importan los mensajes que indican la posicion de pacman """
from pynput.keyboard import Key, Listener """ se importa la libreria para detectar las acciones del teclado """
import threading

pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)	""" publica las acciones de pacman"""

def iniciar():
	global mapa, matriz, actual, siguiente """ se crean las variables para guardar el mapa, la matriz que lo representa, la posicion actual y la posicion siguiente"""

	rospy.init_node('punto3', anonymous = True)  """ se incializa el nodo """
	mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService) """ Se solicita el mapa """
	mapa = mapaSolicitado("Harvey") """ se solicita el nombre """
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)] """ se crea la matriz usando las dimensiones del mapa """

	rospy.Subscriber("pacmanCoord0", pacmanPos, andar) """ se inicializa la accion en 4 para que pacman comience detenido"""
	actual = 4
	siguiente = 4


	for i in range(mapa.nObs):
		matriz[-mapa.obs[i].y - mapa.minY][mapa.obs[i].x - mapa.minX] = "%" """ se muestra en la terminal el mapa dependiendo de la posicion de los obstaculos """

	tasa = rospy.Rate(10)
	while not rospy.is_shutdown():
		tasa.sleep()

def keypress(key):
	global siguiente  """ se crea la variable siguiente para guardar la ultima accion ejecutada """
	if key == Key.esc: 
		rospy.signal_shutdown("Escape") """ si se presiona la tecla esc se sale del juego"""
		return False
	else:
		if key.char == 'a' or key.char == 'w' or key.char == 's' or key.char == 'd':   """ si se presionan las teclas indicadas se asigna la accion dada por la documentacion tecnica de pacman"""

			mensajes = {'a':3, 'w':0, 's':1, 'd':2}
			siguiente = int(mensajes[key.char])

def andar(data): """ se define el siguiente movimiento que debe hacer pacman de acuerdo al valor de la variable siguiente"""
	global mapa, matriz, actual, siguiente
	if (siguiente == actual):
		siguiente = 4
	else:
		if (siguiente == 0 and matriz[-data.pacmanPos.y - mapa.minY - 1][data.pacmanPos.x - mapa.minX] == " "): """ pacman se mueve hacia arriba cuando sea posible """
			actual = siguiente
		if (siguiente == 1 and matriz[-data.pacmanPos.y - mapa.minY + 1][data.pacmanPos.x - mapa.minX] == " "):  """ pacman se mueve hacia abajo cuando sea posible """
			actual = siguiente
		if (siguiente == 2 and matriz[-data.pacmanPos.y - mapa.minY][data.pacmanPos.x - mapa.minX + 1] == " "): """ pacman se mueve hacia la derecha cuando sea posible """
			actual = siguiente
		if (siguiente == 3 and matriz[-data.pacmanPos.y - mapa.minY][data.pacmanPos.x - mapa.minX - 1] == " "): """ pacman se mueve hacia la izquierda cuando sea posible """
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
