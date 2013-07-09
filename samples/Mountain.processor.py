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

class Configure(blender_cave.processor.Configure):
    def __init__(self, parent, attrs):
        super(Configure, self).__init__(parent, attrs)

class Processor(blender_cave.processor.Processor):
    def __init__(self, parent, configuration):
        super(Processor, self).__init__(parent, configuration)
        #self._navigator = hc_nav.HCNav(parent, self.process_hcnav)
        self._navigator = hc_nav.HCNav(parent)
        self._navigator.setPositionFactors(1, 20.0, 1.0)

        if (self.getBlenderCave().getVersion() >= 3.0) and (self.getBlenderCave().isMaster()):
            self.getBlenderCave().getSceneSynchronizer().getItem(bge.logic).activate(True, True)

            OSC = self.getBlenderCave().getOSC()

            # Sample of how to add sound to the "Plane.011" object
            plane = bge.logic.getCurrentScene().objects['Plane.011']
            user = self.getBlenderCave().getUserByName('user A')

            osc_plane = OSC.getObject(plane)
            osc_plane.sound('trumpet.wav')
            osc_plane.mute(OSC.stateToggle)
            osc_plane.volume('%50')

            osc_plane = OSC.getObject(plane)

            osc_user = OSC.getUser(user)

            osc_user_objet = OSC.getObjectUser(osc_plane, osc_user)
            osc_user_objet.mute(True)


    def process_hcnav(self, matrix):
        print(matrix)

    def user_position(self, info):
        super(Processor, self).user_position(info)
        for user in info['users']:
            self._navigator.setHeadLocation(user, info)

    def reset(self, users = None):
        if not users is None:
            for user in users:
                self._navigator.update(self._navigator.RESET, user)
                user.resetVehiclePosition()

    def buttons(self, info):
        if (info['button'] == 0) and (info['state'] == 1):
            self._navigator.update(self._navigator.CALIBRATE)
        if (info['button'] == 1) and (info['state'] == 1):
            self._navigator.update(self._navigator.TOGGLE)
        if (info['button'] == 2) and (info['state'] == 1):
            self.reset(info['users'])
        if (info['button'] == 3) and (info['state'] == 1):
            self.getBlenderCave().quit("because user asked !")

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

    def console(self, info):
        return
        print("console informations: ", info)
