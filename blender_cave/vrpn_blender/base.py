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

import bge
from blender_cave import exceptions

if hasattr(bge.logic, 'vrpn_devices') == False:
    bge.logic.vrpn_devices = {}

def setDeviceInformation(name, info):
    bge.logic.vrpn_devices[name] = info


def getDeviceInformation(deviceName):
    if (hasattr(bge.logic, 'vrpn_devices') == False) or (deviceName not in bge.logic.vrpn_devices):
        return False
    return bge.logic.vrpn_devices[deviceName]

class Base:
    def __init__(self, node):
        try:
            super(Base, self).__init__(node)
        except TypeError:
            pass
        try:
            self._name = node.attributes['name'].value
            self._host = node.attributes['host'].value
        except KeyError:
            raise exceptions.VRPN('cannot get name and host for device') 

    def __str__(self):
        return self._name + "@" + self._host

    def _start(self):
        raise NotImplementedError

    def run(self):
        if not hasattr(self, '_connexion'):
            self._start()
        self._connexion.mainloop()

class Sender:
    def __init__(self, node):
        try:
            super(Sender, self).__init__(node)
        except TypeError:
            pass
        try:
            self._processor_method = node.attributes['processor_method'].value
        except KeyError:
            raise exceptions.VRPN('cannot get processor_method for ' + self.__class__.__name__ + ':' + self.__str__()) 
        try:
            self._data = node.attributes['data'].value
        except KeyError:
            self._data = ""

    def process(self, info):
        try:
            getattr(bge.logic.vrpn_processor, self._processor_method)(info, self._data)
        except AttributeError:
            pass

