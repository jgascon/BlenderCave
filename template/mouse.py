#!/usr/bin/python
# -*- coding: utf-8 -*-

xsensitivity = -0.10
ysensitivity = 0.10


import GameLogic
import Rasterizer
import cPickle
import time
from math import sin, cos
from GameKeys import *
from socket import *

MCAST_ADDR = "224.168.2.9"
MCAST_PORT = 1600
midx = Rasterizer.getWindowWidth()/2
midy = Rasterizer.getWindowHeight()/2
c = GameLogic.getCurrentController()
m_move = c.sensors["m_move"]
#m_button = c.getSensor("m_button")
o = c.owner

CamaraFront = c.actuators["camara"].owner
# the second object???!!!

# move the cursor back to the center
Rasterizer.setMousePosition(midx, midy)

c = GameLogic.getCurrentController()
mouse = c.sensors[0] # change to specify name of sensor if you connect multiple sensors to this script

# initilization
if o["ago"] < 0.0:
    Rasterizer.showMouse(0) # hide the cursor
    Rasterizer.setMousePosition(Rasterizer.getWindowWidth()/2, Rasterizer.getWindowHeight()/2)
    deltax = 0
    deltay = 0
else:
    deltax = midx - mouse.position[0]
    deltay = midy - mouse.position[1]

# based on the cursor's movement, and the constraints, rotate this object
# (and how much time passed)

dt = o['now'] - o['ago'] # dt = time passed to this frame
o['ago'] = o['now']

# create copies of the values, then calculate the new ones
## z axis rotation (no constraints)
osz = o['sz']
ocz = o['cz']
zrot = (3.141592654 * xsensitivity) * dt* deltax
szrot = sin(zrot)
czrot = cos(zrot)
o['cz'] = -osz*szrot + ocz*czrot
o['sz'] =  osz*czrot + ocz*szrot

# x axis rotation (there are constraints)
osx = o['sx']
ocx = o['cx']
xrot = (3.141592654 * ysensitivity) * dt* deltay
sxrot = sin(xrot)
cxrot = cos(xrot)
o['cx'] = -osx*sxrot + ocx*cxrot
o['sx'] =  osx*cxrot + ocx*sxrot

if o['cx'] < 0.0: # prevent looking past top or bottom
    o['cx'] = ocx
    o['sx'] = osx


#o.setOrientation([ \
#   [  o['cz'], o['sz']*o['cx'], o['sz']*o['sx'] ], \
#   [ -o['sz'], o['cz']*o['cx'], o['cz']*o['sx'] ], \
#   [    0,     -o['sx'],    o['cx']   ] ] )

# only horizontal rotation, around z axis
o.orientation = [ \
    [ o['cz'], o['sz'], 0], \
    [ -o['sz'], o['cz'], 0], \
    [  0, 0, 1] ]

# only vertical rotation [around x axis]
# this is for an empty: [+y axis is forward]
#CamaraFront.setOrientation([ \
#   [1, 0, 0], \
#   [0, o['cx'], o['sx']], \
#   [0, -o['sx'], o['cx']] ] )
# this is for a camera [-z axis forward]
CamaraFront.orientation = [ \
    [1, 0, 0], \
    [0, -o['sx'], -o['cx']], \
    [0, o['cx'], -o['sx']] ]


c = GameLogic.getCurrentController()
sen = c.sensors["keyboard"]
list = GameLogic.getCurrentScene().objects
text_selected = None
offset = [0.0, 0.0, 0.0]
STEP = 0.02

camera = list["OBCamera_Front"]

teclas = []
rotacion = []
for keys in sen.events:
	if keys[1] == GameLogic.KX_INPUT_JUST_ACTIVATED or keys[1] == GameLogic.KX_INPUT_JUST_RELEASED:
		key	= keys[0]
		if key == 144:
			offset[1] = -STEP
		if key == 146:
			offset[1] = +STEP
		if key == 143:
			offset[0] = -STEP
		if key == 145:
			offset[0] = +STEP
		teclas.extend([key])
		if key == 116:
			SceneDic= {"Tiempo": True}
			datos=cPickle.dumps(SceneDic)
			t1 = time.time()
			GameLogic.cliente.sendto(datos,("192.168.1.4",11111))
			data, addr= GameLogic.cliente.recvfrom(2048)
			t2 = time.time()
			GameLogic.tiempo += (t2 - t1)*0.5
			GameLogic.veces += 1

			t1 = time.time()
			GameLogic.cliente.sendto(datos,("192.168.1.1",11111))
			data, addr= GameLogic.cliente.recvfrom(2048)
			t2 = time.time()
			GameLogic.tiempo += (t2 - t1)*0.5
			GameLogic.veces += 1
			
			t1 = time.time()
			GameLogic.cliente.sendto(datos,("192.168.1.3",11111))
			data, addr= GameLogic.cliente.recvfrom(2048)
			t2 = time.time()
			GameLogic.tiempo += (t2 - t1)*0.5
			GameLogic.veces += 1
		

rotacion = rotacion + [o['cx']] + [o['cz']] + [o['sx']] + [o['sz']]
loc = o.localPosition
loc[0] += offset[0]
loc[1] += offset[1]
loc[2] += offset[2]
o.localPosition

	
SceneDic = { 'Rotacion': rotacion }
SceneDic['Posicion'] =  o.localPosition

if teclas != []: 
	SceneDic['Teclas'] = teclas
	
datos = cPickle.dumps(SceneDic)
GameLogic.total_bytes += len(datos)
GameLogic.cliente.sendto(datos, (MCAST_ADDR,MCAST_PORT) );

if GameLogic.veces >= 20:
	print "Latencia media ",GameLogic.tiempo/GameLogic.veces
	GameLogic.tiempo = 0
	GameLogic.veces = 0