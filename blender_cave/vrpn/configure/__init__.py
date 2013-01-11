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

import mathutils
import bge
import os
import imp
import blender_cave.configure.base
import blender_cave.vrpn

class VRPN(blender_cave.configure.base.Base):

    def __init__(self, parent, attrs):
        super(VRPN, self).__init__(parent, attrs, 'vrpn')
        self._available = False

        if blender_cave.vrpn._VRPN_NOT_AVAILABLE:
            self.getLogger().warning('No VRPN Available !')
            return
        self._available = True

    def startElement(self, name, attrs):
        if not self._available:
            return self
        child = None
        if name == 'floor':
            try:
                self._floor = self.getVector(attrs)
            except KeyError:
                self.raise_error('Floor must have a value !')
        if name == 'tracker':
            from . import tracker
            child = tracker.Tracker(self, attrs)
        if name == 'button':
            from . import button
            child = button.Button(self, attrs)
        if name == 'analog':
            from . import analog
            child = analog.Analog(self, attrs)
        if name == 'text':
            from . import text
            child = text.Text(self, attrs)
        return self.addChild(child)

    def getConfiguration(self):
        if not self._available:
            return {}
        localConfiguration = {'tracker' : [], 'button' : [], 'analog' : [], 'text' : [], 'local_devices' : []}
        for deviceType in localConfiguration:
            try:
                for deviceName in self._children[deviceType]:
                    localConfiguration[deviceType].append(self._children[deviceType][deviceName].getLocalConfiguration())
            except KeyError:
                pass

        try:
            localConfiguration['floor'] = self._floor
        except AttributeError:
            pass

        return localConfiguration
