#!/usr/bin/python
# -*- coding: utf-8 -*-
import GameLogic
import cPickle
from GameKeys import *
from socket import *
c = GameLogic.getCurrentController()

try:
	#print "Me quedo dormido"
	dormido, addr= GameLogic.server.recvfrom(2048)
	#print "Me despierto"
except error, e:
	pass
GameLogic.server.setblocking(0)
c.activate(c.actuators['slaveawakestate'])