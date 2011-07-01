#!/usr/bin/python
# -*- coding: utf-8 -*-
import GameLogic

if GameLogic.im_master == True:
	f=open("../../home/jose/anchobanda.txt","a")
	ancho = ""
	for key in GameLogic.ancholista:
		ancho += str(key) + "\n"
	f.write(ancho)
	f.close()