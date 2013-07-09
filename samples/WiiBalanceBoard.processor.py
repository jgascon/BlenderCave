## Copyright © LIMSI-CNRS (2013)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer, 
## 
## This software is a computer program whose purpose is to distribute
## blender to render on CAVE(TM) device systems.
## 
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use, 
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info". 
## 
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability. 
## 
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or 
## data to be ensured and,  more generally, to use and operate it in the 
## same conditions as regards security. 
## 
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
## 

import blender_cave.processor

import blender_cave
import bge
import math
import sys

class Configure(blender_cave.processor.Configure):
    def __init__(self, parent, attrs):
        super(Configure, self).__init__(parent, attrs)

class Processor(blender_cave.processor.Processor):
    def __init__(self, parent, configuration):
        super(Processor, self).__init__(parent, configuration)

        if (self.getBlenderCave().getVersion() >= 3.0) and (self.getBlenderCave().isMaster()):
            self.getBlenderCave().getSceneSynchronizer().getItem(bge.logic).activate(True, True)

    def wiimote_a(self, info): # analog
        state = [round(elmt,2) for elmt in info['channel'][64:71]]
        # print (state[0],state[1],state[2],state[3])
        # print ('total weight',state[4])
        # print ('barycenter position',state[5],state[6],'\n')

        scaleCorner = 0.02
        scaleWeight = 0.02
        scalePos = 1
        scene = bge.logic.getCurrentScene()

        corner = scene.objects['Corner']
        corner.localScale = (state[0]*scaleCorner,state[0]*scaleCorner,state[0]*scaleCorner)
        corner1 = scene.objects['Corner.001']
        corner1.localScale = (state[1]*scaleCorner,state[1]*scaleCorner,state[1]*scaleCorner)
        corner2 = scene.objects['Corner.002']
        corner2.localScale = (state[2]*scaleCorner,state[2]*scaleCorner,state[2]*scaleCorner)
        corner3 = scene.objects['Corner.003']
        corner3.localScale = (state[3]*scaleCorner,state[3]*scaleCorner,state[3]*scaleCorner)

        weight = scene.objects['Weight']
        weight.localScale = (state[4]*scaleWeight,.2,.1)
        bary = scene.objects['Bary']
        if not math.isnan(state [5]) and (state[1]+state[2]+state[3]+state[0]) >= 1:
            bary.worldPosition = (scalePos*state[5],scalePos*state[6],0)
        else: bary.worldPosition = (0,0,0)

    def wiimote_b(self, info): # button
        # print('button A pressed',info['state'])
        scene = bge.logic.getCurrentScene()
        button = scene.objects['Button']
        if info['state']==1:
            button.worldPosition = (0,0,.01)
        else:button.worldPosition = (0,0,-1)

    def run(self):
        return
        print ('always launched')

    def console(self, info):
        return
        print("console informations: ", info)
