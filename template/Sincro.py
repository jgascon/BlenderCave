import GameLogic
import cPickle
from socket import *

nombres_obj = GameLogic.getCurrentScene().objects
SceneDic = {}
objanimado={}

for objeto in nombres_obj:
	if "animated" in objeto.getPropertyNames():
		if objeto.name <> 'OBProtagonista' and objeto.name<> 'OBCamera_Front':
			objanimado = {'Posicion' : objeto.localPosition, 'Rotacion' : objeto.localOrientation}
			SceneDic[objeto.name] = objanimado
datos = cPickle.dumps(SceneDic)
GameLogic.cliente.sendto(datos, ("192.168.1.1", 11111))
GameLogic.cliente.sendto(datos, ("192.168.1.3", 11111))
GameLogic.cliente.sendto(datos, ("192.168.1.4", 11111))