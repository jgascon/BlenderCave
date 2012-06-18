## Copyright © LIMSI-CNRS (2011)
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

import blender_cave.vrpn_blender.processor as processor
import bge
import mathutils
import math
import sys
from blender_cave import parser

class bpcem_playground(processor.Processor):
    def __init__(self, node):
        super(bpcem_playground, self).__init__()
        self._scene = bge.logic.getCurrentScene()
        self._cube = self._scene.objects['Cube']
        #It is VERY important that the objects are defined as son of the camera, because the camera is the bridge between the real world and the virtual word (ie.: the vehicle)
        self._cube.setParent(self._scene.active_camera, False, False)
        self._scale = self._cube.localScale.x

    def tracker_1(self, info, data):
        object_matrix = info['matrix']
        self._cube.localPosition = object_matrix.to_translation()
        self._cube.localOrientation = object_matrix.to_3x3()

    def buttons(self, info, data):
        if (info['button'] == 0) and (info['state'] == 1):
            self._scale *= 1.2
        if (info['button'] == 1) and (info['state'] == 1):
            self._scale /= 1.2
        self._cube.localScale = (self._scale, self._scale, self._scale)

def load_vrpn_processor(node):
    return bpcem_playground(node)

