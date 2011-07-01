#!/usr/bin/python
# -*- coding: utf-8 -*-
import GameLogic
import cPickle
from GameKeys import *
from socket import *
import select
c = GameLogic.getCurrentController()
list = GameLogic.getCurrentScene().objects
text_selected = None
offset = [0.0, 0.0, 0.0]
STEP = 0.02
allk = []

ready_read, ready_write, broken = select.select([GameLogic.server],[],[],0)
if (GameLogic.server in ready_read):
	data, addr= GameLogic.server.recvfrom(2048)
	if len(data):
		SceneDic = cPickle.loads(data)
		if SceneDic != True:
			for key in SceneDic.keys():
				if key == 'Tiempo':
					SceneDic= {"Tiempo": True}
					datos=cPickle.dumps(SceneDic)
					GameLogic.server.sendto(datos,("192.168.1.2",11111))
				else:
					if key == 'Teclas':
						for teclas in SceneDic['Teclas']:
							if 'Allkeys' in GameLogic.senskeyboard:
								for sensor in GameLogic.senskeyboard['Allkeys']:
									if sensor.invert == False:
										sensor.invert = True
										sensor.reset()
									else:
										sensor.invert = False
										sensor.reset()
							if teclas in GameLogic.senskeyboard:
								for sensor in GameLogic.senskeyboard[teclas]:
									if sensor.invert == False:
										sensor.invert = True
										sensor.reset()
									else:
										sensor.invert = False
										sensor.reset()
						
					#Getting the selected camera
					#camara = c.actuators["camara"]
					else:
							if key == 'Posicion':
								protagonista = c.actuators["prota"].owner
								protagonista.setPosition(SceneDic['Posicion'])
							else:
								if key == 'Rotacion':
									protagonista.setOrientation([ \
									[ SceneDic['Rotacion'][1],SceneDic['Rotacion'][3], 0], \
									[ -SceneDic['Rotacion'][3],SceneDic['Rotacion'][1], 0], \
									[  0, 0, 1] ] )
								
									camera = c.actuators['camara'].owner
									camera.setOrientation([ \
									[1, 0, 0], \
									[0, -SceneDic['Rotacion'][2], -SceneDic['Rotacion'][0]], \
									[0, SceneDic['Rotacion'][0], -SceneDic['Rotacion'][2]] ] )
								else:
									objeto = GameLogic.getCurrentScene().objects[key]
									for key2 in SceneDic[key].keys():
										if key2 == 'Posicion':
											objeto.localPosition = SceneDic[key][key2]
										else:
											if key2 == 'Rotacion':
												objeto.orientation = SceneDic[key][key2]

	


