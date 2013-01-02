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

import blender_cave.base
import blender_cave.exceptions
import bge
import socket
from . import base
from . import object
from . import user
from . import client

class OSC(blender_cave.base.Base):
    def __init__(self, parent,  configuration):
        super(OSC, self).__init__(parent)

        self._valid = False

        if ('server' not in configuration) or ('port' not in configuration):
            return

        self._global = base.Base(self, 'global', None)

        global_attributs = ['warmth', 'brightness', 'presence',
                            'reverb_volume', 'running_reverb',
                            'late_reverb', 'envelop', 'heavyness',
                            'livelyness']

        for attribut in global_attributs:
            self._global._commands[attribut] = { 'type': 'int'}
        self._global.define_commands()

        if 'room' in configuration:
            for attribut in global_attributs:
                if attribut in configuration['room']:
                    getattr(self._global, attribut)(configuration['room'][attribut])

        specific_processor, file_name, module_name, specific_name = blender_cave.blender_file_script.getBlenderFileModule(bge.logic.getCurrentBlendName(), True)
        if not hasattr(specific_processor, 'OSC_Objects'):
            self._available = False
            return
        self._objects   = {}
        for name, attributs in specific_processor.OSC_Objects.items():
            try:
                self._objects[name] = object.Object(self, name, attributs, len(self._objects))
            except:
                self.log_traceback(False)

        self._users = []
        for _user in self.getBlenderCave().getAllUsers():
            try:
                self._users.append(user.User(self, _user, len(self._users)))
            except:
                self.log_traceback(False)

        self.getLogger().info('Connection to OSC server : ' + configuration['server'] + ':' + str(configuration['port']))
        self._client = client.Client(self, configuration['server'], configuration['port'])
        self._valid = True

    def start(self):
        pass

    def run(self):
        if self._valid:
            try:
                self._global.run()
                for name, object in self._objects.items():
                    object.run()
                for user in self._users:
                    user.run()
            except socket.error:
                self.getBlenderCave().log_traceback(False)
                self.getLogger().warning('Cannot send command to OSC server => stop OSC !')
                self._valid = False

    def sendCommand(self, cmd):
        if self._valid:
            self._client.send(cmd)

    def getGlobal(self):
        return self._global
