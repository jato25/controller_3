#!/usr/bin/python3
import rospy
from pacman.msg import actions """se importan los mensajes que indican acciones que debe ejecutar el pacman"""
from pacman.msg import pacmanPos """se importan los mensajes que indican acciones que debe ejecutar el pacman"""
from pacman.srv import mapService """se importa el servicio que permite solicitar el mapa"""
from pynput.keyboard import Key, Listener """se importa la libreria para detectar las acciones del teclado"""
import threading

pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)	

def solicitarMapa():
	rospy.init_node('punto1', anonymous = True) """se inicializa el nodo"""
	try:
		mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService) """se solicita el mapa"""
		mapa = mapaSolicitado("Harvey")
		tasa = rospy.Rate(10)
		while not rospy.is_shutdown():
			tasa.sleep()

	except rospy.ServiceException as e:
		pass


def keypress(key):
	if key == Key.esc: 
		rospy.signal_shutdown("Escape") """si se presiona la tecla esc se cancela la ejecucion de pacman y se sale del juego"""
		return False
	else:
		if key.char == 'a' or key.char == 'w' or key.char == 's' or key.char == 'd': """si se presionan las teclas indicadas se asigna el movimiento dado por la documentacion tecnica de pacman"""
			mensajes = {'a':3, 'w':0, 's':1, 'd':2}
			pub.publish(action = int(mensajes[key.char]))
		else:
			pub.publish(action = 4)    """si se presiona otra tecla pacman se quedara quieto"""

def keydown(key):
	pub.publish(action = 4)   """si se deja de oprimir las teclas indicadas pacman se quedara quieto"""

def ThreadInputs():
	with Listener(on_press = keypress, on_release = keydown) as listener:
		listener.join()

if __name__ == '__main__':
	try:
		print("Presione una tecla (Esc para salir):")
		threading.Thread(target=ThreadInputs).start()
		solicitarMapa()
	except rospy.ServiceException:
		pass


