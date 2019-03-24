#!/usr/bin/python3
import rospy
from pacman.msg import actions
from pacman.srv import mapService
from pacman.msg import pacmanPos

pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)	## Publicador que controla al  pacman con el algoritmo de la mano derecha

def iniciar():
	##Variables globaales que permiten el manejo del mapa (matriz), actual * almacenamiento del mapa. Itera es la variable que verifica cuantas veces se ha verificado la direccion de la derecha del pacman
	global matriz, actual, mapa, itera
	
	##Se inicializa el nodo
	rospy.init_node('punto4', anonymous = False)
	mapaSolicitado = rospy.ServiceProxy('pacman_world' , mapService)
	mapa = mapaSolicitado("Harvey")
	##Inicializacion de la matriz
	matriz = [[" "  for i in range(mapa.maxX - mapa.minX + 1)]for j in range(mapa.maxY - mapa.minY + 1)]
	actual = 2
	rospy.Subscriber("pacmanCoord0", pacmanPos, derecha)
	##Se guardan en la matriz los obstaculos
	for i in range(mapa.nObs):
		matriz[-mapa.obs[i].y - mapa.minY][mapa.obs[i].x - mapa.minX] = "%"
	itera = 0
	tasa = rospy.Rate(10)
	while not rospy.is_shutdown():
		tasa.sleep()

def derecha(data): ##Metodo que realiza el algoritmo de la derecha
	global mapa, actual, matriz, itera
	#Diccionario que retorna el numero correspondiente a la derecha de la direccion actual
	dirDerecha = {3:0,0:2,2:1,1:3}
	#Diccionario que retorna **
	coord = {3:[0,-1],0:[-1,0],2:[0,1],1:[1,0]}
	siguiente = dirDerecha[actual]
	posx =  data.pacmanPos.x - mapa.minX ##Posicion actual del pacman en las columnas de la matriz 
	posy = -data.pacmanPos.y - mapa.minY  ##Posicion actual del pacman en las filas de la matriz
	vec1 = coord[siguiente] ##Vector para verificar la direccion de movimiento a la derecha 
	vec2 = coord[actual]  ##Vector para verificar la direccion de movimeinto actual		
	if (matriz[posy + vec2[0]][posx + vec2[1]] == " " and matriz[posy + vec1[0]][posx + vec1[1]] == "%"):  ## Si la direccion actual esta disponible (no hay obstaculo) y en el espacio de la derecha hay un obstaculo se continua en la direccion actual
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
		derecha(data)

if __name__ == '__main__':
	try:
		iniciar()
	except rospy.ServiceException:
		pass
