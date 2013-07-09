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
import blender_cave.vrpn.head_controlled_navigation as hc_nav
import blender_cave
import bge
import mathutils
import math
import sys
import copy
import bgl
from math import radians

class Configure(blender_cave.processor.Configure):
    def __init__(self, parent, attrs):
        super(Configure, self).__init__(parent, attrs)

class Processor(blender_cave.processor.Processor):
    def __init__(self, parent, configuration):
        super(Processor, self).__init__(parent, configuration)
        self._navigator = hc_nav.HCNav(parent)
        self._navigator.setPositionFactors(1, 20.0, 1.0)

        controller = bge.logic.getCurrentController()
        self._ray_sensor   = controller.sensors['ray']
        self._laser_object = controller.owner
        self._laser_ray    = {'origin' : mathutils.Vector(),
                              'destin' : mathutils.Vector(),
                              'color'  : [1.0, 1.0, 1.0] }

        scene                               = bge.logic.getCurrentScene()
        scene.pre_draw.append(self.display_laser)

        camera                              = scene.active_camera
        self._laser_object.worldPosition    = camera.worldPosition
        self._laser_object.worldOrientation = camera.worldOrientation
        self._laser_object.setParent(camera)

        if (self.getBlenderCave().getVersion() >= 3.0) and (self.getBlenderCave().isMaster()):
            self.getBlenderCave().getSceneSynchronizer().getItem(bge.logic).activate(True, True)

            self._OSC = self.getBlenderCave().getOSC()
            self._OSC.getGlobal().start(True)


            user     = self.getBlenderCave().getUserByName('user C')
            osc_user = self._OSC.getUser(user)

            osc_objects = [{'name'  : 'Cone',
                            'sound' : 'TF_kick.wav',
                            'mute'  : False},
                           {'name'  : 'Cylinder',
                            'sound' : 'TF_ride.wav',
                            'mute'  : False},
                           {'name'  : 'Barre',
                            'sound' : 'TF_snare.wav',
                            'mute'  : False},
                           {'name'  : 'Sphere',
                            'sound' : 'TF_piano.wav',
                            'mute'  : False},
                           {'name'  : 'Suzanne',
                            'sound' : 'TF_saxophone.wav',
                            'mute'  : False}]

            self._objects = {}

            for osc_object_def in osc_objects:
                blender_object = scene.objects[osc_object_def['name']]
                osc_object     = self._OSC.getObject(blender_object)
                osc_object.sound(osc_object_def['sound'])
                osc_object.loop(True)

                self._objects[id(blender_object)] = {'object' : osc_object,
                                                     'volume' : 50,
                                                     'mute'   :  False}

                osc_user_objet = self._OSC.getObjectUser(osc_object, osc_user)

            self.reset_sound()
            self.reset_volume()

    def user_position(self, info):
        super(Processor, self).user_position(info)
        for user in info['users']:
            self._navigator.setHeadLocation(user, info)

    def reset(self, users = None):
        if not users is None:
            for user in users:
                self._navigator.update(self._navigator.RESET, user)
                user.resetVehiclePosition()

    def send_volume(self):
        for id, obj in self._objects.items():
            if obj['mute']:
                obj['object'].volume('%0')
            else:
                obj['object'].volume('%'+str(obj['volume']))

    def reset_volume(self):
        for id, obj in self._objects.items():
            obj['volume'] = 10
        self.send_volume()

    def reset_sound(self):
        for id, obj in self._objects.items():
            obj['object'].start(False)
        for id, obj in self._objects.items():
            obj['object'].start(True)

    def buttons(self, info):
        if info['button'] == 0:
            if info['state'] == 1:
                if (not hasattr(self, '_object')) and (self._ray_sensor.hitObject is not None):
                    self._object = self._ray_sensor.hitObject
                    self._object.setParent(self._laser_object)
            elif hasattr(self, '_object'):
                    self._object.removeParent()
                    del(self._object)
        if (info['button'] == 1) and (info['state'] == 1):
            if hasattr(self, '_object'):
                obj = self._object
            elif self._ray_sensor.hitObject is not None:
                obj = self._ray_sensor.hitObject
            else:
                return
            obj = self._objects[id(obj)]
            obj['mute'] = (obj['mute'] == False)
            self.send_volume()

    def movements(self, info):
        if info['channel'][1] != 0:
            if hasattr(self, '_object'):
                obj = self._object
            elif self._ray_sensor.hitObject is not None:
                obj = self._ray_sensor.hitObject
            else:
                return
            obj = self._objects[id(obj)]
            if info['channel'][1] > 0:
                obj['volume'] = obj['volume'] - 1
            else:
                obj['volume'] = obj['volume'] + 1
            if obj['volume'] > 100:
                obj['volume'] = 100
            if obj['volume'] < 0:
                obj['volume'] = 0
            self.send_volume()

    def texts(self, info):
        cmd = None
        if info['message'] == 'COMPUTER CALIBRATION':
            cmd = self._navigator.CALIBRATE
        elif info['message'] == 'COMPUTER NAVIGATION':
            cmd = self._navigator.TOGGLE
        elif info['message'] == 'COMPUTER HOME':
            self.reset(info['users'])
        elif info['message'] == 'COMPUTER QUIT':
            self.getBlenderCave().quit("because user asked !")

        if cmd is not None:
            for user in info['users']:
                self._navigator.update(cmd, user)

    def tracker_1(self, info):
        self._laser_object.localPosition    = info['matrix'].to_translation()
        self._laser_object.localOrientation = info['matrix'].to_3x3() * mathutils.Matrix.Rotation(radians(-90.0), 3, 'X')

    def run(self):
        ray_vec = mathutils.Vector(self._ray_sensor.rayDirection)
        ray_vec.magnitude = self._ray_sensor.range

        self._laser_ray['origin'] = mathutils.Vector(self._laser_object.worldPosition)

        if self._ray_sensor.positive:
            hit_vec = mathutils.Vector(self._ray_sensor.hitPosition)
            ray_vec = hit_vec - self._laser_ray['origin']

        self._laser_ray['destin'] = self._laser_ray['origin'] + ray_vec

    def console(self, information):
        try:
            if information['key'] == 113:
                self.getBlenderCave().quit("pressed 'q' key")
            if information['key'] == 114:
                self.reset_sound()
            if information['key'] == 115:
                self.reset_volume()
        except KeyError:
            pass


    def display_laser(self):
        bgl.glColor3f(self._laser_ray['color'][0], self._laser_ray['color'][1], self._laser_ray['color'][2])
        bgl.glLineWidth(1.0)

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(self._laser_ray['origin'].x, self._laser_ray['origin'].y, self._laser_ray['origin'].z)
        bgl.glVertex3f(self._laser_ray['destin'].x, self._laser_ray['destin'].y, self._laser_ray['destin'].z)
        bgl.glEnd()
