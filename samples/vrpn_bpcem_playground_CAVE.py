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

class bpcem_playground(processor.Processor):
    def __init__(self):
        super(bpcem_playground, self).__init__()
        self._scene = bge.logic.getCurrentScene()
        self._gun = self._scene.objects['Gun']
        self._gun.setParent(self._scene.active_camera)

    def tracker_1(self, info, data):
        matrix = info['matrix']
        self._gun.localPosition = matrix.to_translation()
        # The gun is not oriented itself as expected ...
        gun_local_orientation = mathutils.Matrix(((-1.0, 0.0, 0.0),
                                                  ( 0.0, 0.0, 1.0),
                                                  ( 0.0, 1.0, 0.0)))
        self._gun.localOrientation = gun_local_orientation * matrix.to_3x3()

    def movements(self, info, data):
        channels = info['channel']
        self._scene.active_camera.localOrientation *= mathutils.Matrix.Rotation(math.radians(-channels[0]), 3, 'Y')
        self._scene.active_camera.localOrientation *= mathutils.Matrix.Rotation(math.radians(-channels[1]), 3, 'X')

    def _fire(self):
        new_ball = self._scene.addObject("ball", self._gun, 100)
        # We translate the origin of the balls such that they appear leaving from the extremity of the gun
        new_ball.worldPosition = self._gun.worldPosition + self._gun.worldOrientation * mathutils.Vector((0.0, -1.0, 0.0))
        new_ball.worldOrientation = self._gun.worldOrientation
        new_ball.localLinearVelocity = mathutils.Vector((0.0, -15.0, 0.0))

    def buttons(self, info, data):
        if (info['button'] == 0) and (info['state'] == 1):
            self._fire()
        if (info['button'] == 1) and (info['state'] == 1):
            for i in range(10):
                self._fire()

bge.logic.vrpn_processor = bpcem_playground()
