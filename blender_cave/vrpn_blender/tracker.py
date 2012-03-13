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

import vrpn
from . import base
import blender_cave
import mathutils
from blender_cave import exceptions

def _getMatrixFromVRPN_info(info, position_name = 'position', quaternion_name = 'quaternion'):
    quaternion = mathutils.Quaternion((info[quaternion_name][0], info[quaternion_name][1], info[quaternion_name][2]), info[quaternion_name][3])
    orientation = quaternion.to_matrix()
    orientation.resize_4x4()
    position = mathutils.Matrix.Translation((info[position_name][0], info[position_name][1], info[position_name][2]))

    return position * orientation

def _addMatrixToObject(object, matrix_name, matrix):
    setattr(object, matrix_name, matrix * getattr(object, matrix_name))

def _extractMatrixInformation(node, object):
    if node.nodeName == 'transformation':
        attributName = '_' + node.nodeName
        transformation = node.firstChild
        while transformation:
            if transformation.nodeName == 'translate' and transformation.hasAttributes():
                translation = mathutils.Vector()
                if 'x' in transformation.attributes:
                    translation.x = float(transformation.attributes['x'].value)
                if 'y' in transformation.attributes:
                    translation.y = float(transformation.attributes['y'].value)
                if 'z' in transformation.attributes:
                    translation.z = float(transformation.attributes['z'].value)
                _addMatrixToObject(object, attributName, mathutils.Matrix.Translation(translation))
            if transformation.nodeName == 'scale' and transformation.hasAttributes() and 'factor' in transformation.attributes:
                axis = mathutils.Vector()
                orientate = False
                if 'x' in transformation.attributes:
                    orientate = True
                    axis.x = float(transformation.attributes['x'].value)
                if 'y' in transformation.attributes:
                    orientate = True
                    axis.y = float(transformation.attributes['y'].value)
                if 'z' in transformation.attributes:
                    orientate = True
                    axis.z = float(transformation.attributes['z'].value)
                if orientate:
                    _addMatrixToObject(object, attributName, mathutils.Matrix.Scale(float(transformation.attributes['factor'].value), 4, axis))
                else:
                    _addMatrixToObject(object, attributName, mathutils.Matrix.Scale(float(transformation.attributes['factor'].value), 4))
            if transformation.nodeName == 'rotate' and transformation.hasAttributes() and 'angle' in transformation.attributes:
                axis = mathutils.Vector()
                axed = False
                if 'x' in transformation.attributes:
                    axed = True
                    axis.x = float(transformation.attributes['x'].value)
                if 'y' in transformation.attributes:
                    axed = True
                    axis.y = float(transformation.attributes['y'].value)
                if 'z' in transformation.attributes:
                    axed = True
                    axis.z = float(transformation.attributes['z'].value)
                if axed:
                    _addMatrixToObject(object, attributName, mathutils.Matrix.Rotation(float(transformation.attributes['angle'].value), 4, axis))
            transformation = transformation.nextSibling

def _position_handler(object, info):
    object._position(info)

class _Sensor(base.Sender):
    def __init__(self, tracker, node):
        self._tracker = tracker
        self._id = int(node.attributes['id'].value)
        super(_Sensor, self).__init__(node)
        self._transformation = mathutils.Matrix()
        configuration = node.firstChild
        while configuration:
            try:
                _extractMatrixInformation(configuration, self)
            except AttributeError:
                pass
            configuration = configuration.nextSibling

    def run(self, info):
        info['matrix'] = self._tracker._transformation * info['matrix'] * self._transformation
        self.process(info)

    def __str__(self):
        return self._tracker.__str__() + '[' + str(self._id) + ']'

class Tracker(base.Base):
    def __init__(self, node):
        super(Tracker, self).__init__(node)
        self._transformation = mathutils.Matrix()
        self._sensors = {}
        sensor = node.firstChild
        while sensor:
            if sensor.nodeName == 'sensor':
                try:
                    self._sensors[int(sensor.attributes['id'].value)] = _Sensor(self, sensor)
                except KeyError:
                    continue
            try:
                _extractMatrixInformation(sensor, self)
            except AttributeError:
                pass
            sensor = sensor.nextSibling

    def _start(self):
        self._connexion = vrpn.receiver.Tracker(self._name + "@" + self._host)
        self._connexion.register_change_handler(self, _position_handler, "position")

    def _position(self, info):
        sensor = info['sensor']
        if sensor in self._sensors:
            new_information = {'matrix' : _getMatrixFromVRPN_info(info), 'time' : info['time']}
            self._sensors[sensor].run(new_information)
