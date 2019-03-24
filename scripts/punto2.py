#!/usr/bin/python3
import rospy
from pacman.msg import actions """se importan los mensajes que indican acciones que debe ejecutar el pacman"""
from pacman.msg import pacmanPos """se importan los mensajes que indican acciones que debe ejecutar el pacman"""
from pacman.msg import bonusPos """se importan los mensajes que indican la posicion de los bonus"""
from pacman.msg import cookiesPos """se importan los mensajes que indican la posicion de las galletas"""
from pacman.msg import ghostsPos """se importan los mensajes que indican la posicion de los fantasmas"""
from pacman.msg import pacmanPos """se importan los mensajes que indican la posicion de pacman"""
from pacman.srv import mapService """ se importa el servicio que permite solicitar el mapa"""


def iniciar():  """se inicializa el nodo "punto 2" y los topicos a los que se suscribe el nodo"""
	global mapa  """ se crean las variables del mapa y la matriz que lo representa"""
	global matriz
	rospy.init_node('punto2', anonymous = True) """ se inicializa el nodo"""
	rospy.Subscriber("ghostsCoord", ghostsPos, plotGhost) """se suscribe el nodo al topico que envia la posicion de los fantasmas"""
	rospy.Subscriber("bonusCoord", bonusPos, plotBonus) """se suscribe el nodo al topico que envia la posicion de los bonus"""
	rospy.Subscriber("cookiesCoord", cookiesPos, plotCookies) """se suscribe el nodo al topico que envia la posicion de las galletas"""
	rospy.Subscriber("pacmanCoord0", pacmanPos, plotPacman) """ se suscribe el nodo al topico que envia la posicion de pacman"""
	mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService) """ se solicita el mapa  """
	mapa = mapaSolicitado("Harvey")
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)] """se define el mapa como una matriz con las dimensiones del mapa"""
	tasa = rospy.Rate(10)
	while not rospy.is_shutdown():
		plot()
		tasa.sleep()

def plotCookies(data): """Se muestra en la terminal la posicion de las galletas"""
	global matriz
	global mapa
	for i in range(data.nCookies):
		matriz[-data.cookiesPos[i].y - mapa.minY][data.cookiesPos[i].x - mapa.minX] = "."

def plotPacman(data): """Se muestra en la terminal la posicion de pacman"""
	global matriz
	global mapa
	if (data.nPacman > 1):
		for i in range(data.nPacman):
			matriz[-data.pacmanPos[i].y - mapa.minY][data.pacmanPos[i].x - mapa.minX] = "P"
	else:
		matriz[-data.pacmanPos.y - mapa.minY][data.pacmanPos.x - mapa.minX] = "P"
	
def plotBonus(data):   """ Se muestra en la terminal la posicion de los bonus  """
	global matriz
	global mapa
	for i in range(data.nBonus):
		matriz[-data.bonusPos[i].y - mapa.minY][data.bonusPos[i].x - mapa.minX] = "o"
	
def plotGhost(data): """ Se muestra en la terminal la posicion de los fantasmas """
	global mapa
	global matriz
	for i in range(mapa.nObs):
		matriz[-mapa.obs[i].y - mapa.minY][mapa.obs[i].x - mapa.minX] = "%"

	for i in range(data.nGhosts):
		matriz[-data.ghostsPos[i].y - mapa.minY][data.ghostsPos[i].x - mapa.minX] = "G"

def plot():   """ Se muestra en la terminal la posicion de los obstaculos que forman el mapa  """
	global mapa
	global matriz
	for i in range(mapa.maxY - mapa.minY + 1):
		for j in range (mapa.maxY - mapa.minY + 1):
			print(matriz[i][j],end="")
		print(matriz[i][mapa.maxY - mapa.minY + 1])
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)]

if __name__ == '__main__':
	try:
		iniciar()
	except rospy.ServiceException:
		pass
