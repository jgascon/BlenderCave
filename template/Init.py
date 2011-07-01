#!/usr/bin/python
# -*- coding: utf-8 -*-
import GameLogic
import cPickle
from GameKeys import *
from socket import *

MCAST_ADDR = "224.168.2.9"
MCAST_PORT = 1600
def get_local_ip():
   s = socket(AF_INET,SOCK_DGRAM)
   s.connect(('192.168.1.1', 0))
   ip = s.getsockname()[0]
   s.close()
   return ip

c = GameLogic.getCurrentController()
o = c.owner
o['ipcamara'] = get_local_ip()
print "Local IP: ",o['ipcamara']
GameLogic.im_master = False
dormido = True
allksens = []
teclasens = []
GameLogic.tiempo=0.0
GameLogic.veces=0
GameLogic.ancholista = []
GameLogic.senskeyboard = {}
GameLogic.total_bytes=0
#fich=open("anchobanda.txt","w")
#fich.close()
datos=cPickle.dumps(dormido)
act = c.actuators['setcamara']

if o['ipcamara'] == '192.168.1.1':
   act.camera = 'OBCamera_Left'
   GameLogic.cam = "Left"
else:
  if o['ipcamara'] == '192.168.1.2':
    #if o['ipcamara'] == '192.168.1.2':
    act.camera = 'OBCamera_Front'
    GameLogic.im_master = True
    GameLogic.cam = "Front"
  else:
    if o['ipcamara'] == '192.168.1.3':
      act.camera = 'OBCamera_Right'
      GameLogic.cam = "Right"
    else:
      if o['ipcamara'] == '192.168.1.4':
        act.camera = 'OBCamera_Bottom'
        GameLogic.cam = "Bottom"
      else:
        print "ERROR: No camera."

c.activate(act)



if GameLogic.im_master == True:
	#print "Master: Creating Local socket:"
	GameLogic.cliente = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	GameLogic.cliente.setsockopt(SOL_SOCKET,SO_REUSEADDR,2)
	GameLogic.cliente.bind(('0.0.0.0', 11111))
	#Indicamos al kernel que queremos enviar mensajes multicast.
	GameLogic.cliente.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 255)
	GameLogic.cliente.sendto(datos, (MCAST_ADDR,MCAST_PORT) );
	#print "Master: Ok, my ip is ",get_local_ip()
	#print "Changing status."
	c.activate(c.actuators['masterchangestate'])	
else:
	#print "Slave: Creating Local socket:"
	GameLogic.server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	#Indicamos al kernel que vamos a conectar varios sockets al mismo puerto.
	GameLogic.server.setsockopt(SOL_SOCKET,SO_REUSEADDR,2)
	#Este es el socket que recibira mensajes multicast.
	GameLogic.server.bind(('0.0.0.0',MCAST_PORT))
	#Este socket tambien podra enviar mensajes multicast.
	GameLogic.server.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 255)
	#Nos apuntamos al grupo multicast.
	status = GameLogic.server.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton(MCAST_ADDR) + inet_aton('0.0.0.0'));
	GameLogic.server.setblocking(1)
	nombres_obj = GameLogic.getCurrentScene().objects
	for objeto in nombres_obj:
			sensores = objeto.sensors
			for sensor in sensores:
				if sensor.isA('SCA_KeyboardSensor') and objeto.name<> 'OBProtagonista':
					allkeys = sensor.useAllKeys
					if allkeys == True:
						if 'Allkeys' in GameLogic.senskeyboard:
							allksens = GameLogic.senskeyboard['Allkeys']
							allksens.append(sensor)
							GameLogic.senskeyboard['Allkeys'] = allksens
						else:
							allksens = []
							allksens.append(sensor)
							GameLogic.senskeyboard['Allkeys'] = allksens
					else:
						tec = sensor.key
						if tec in GameLogic.senskeyboard:
							aux = GameLogic.senskeyboard[tec]
							aux.append(sensor)
							GameLogic.senskeyboard[tec] = aux
						else:
							teclasens = []
							teclasens.append(sensor)
							GameLogic.senskeyboard[tec] = teclasens
			
	#GameLogic.server.settimeout(0.0002)
	c.activate(c.actuators['slavesleepstate'])	

