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

        self.stateToggle = None

        self._global = base.Base(self, 'global', None) 

        self._global._commands['configuration'] = { 'type'  : 'string' }
        self._global._commands['reset']         = { 'type'  : 'none' }

        if 'configuration' in configuration:
            self._global._commands['configuration']['value'] = configuration['configuration']

        self._global._commands_order = ['reset', 'configuration', 'volume', 'start', 'mute']

        self._global.define_commands()

        if 'room' in configuration:
            for attribut in global_attributs:
                if attribut in configuration['room']:
                    getattr(self._global, attribut)(configuration['room'][attribut])

        self._objects = {}

        self._users = []
        for _user in self.getBlenderCave().getAllUsers():
            try:
                self._users.append(user.User(self, _user, len(self._users) + 1))
            except:
                self.log_traceback(False)

        if ('host' in configuration) or ('port' in configuration):
            self._client = client.Client(self, configuration['host'], configuration['port'])

    def __del__(self):
        self._close()

    def _close(self):
        del(self._client)


    def isAvailable(self):
        return hasattr(self, '_client')

    def reset(self):
        if hasattr(self, '_client'):
            cmd = msg.MSG(self, '/global')
            cmd.append('reset')
            self.sendCommand(cmd)        

    def addObject(self, obj, configuration):
        try:
            obj = object.Object(self, obj, configuration)
            self._objects[obj.getName()] = obj
        except:
            self.log_traceback(False)
                 
    def start(self):
        pass


    def reset(self):
        self._global.reset();
        self._global.runAttribut(self._global.getAttribut('reset'))

    def run(self):
        if hasattr(self, '_client'):
            try:
                self._global.run()
                for name, object in self._objects.items():
                    object.run()
                for user in self._users:
                    user.run()
            except socket.error:
                self.getBlenderCave().log_traceback(False)
                self.getLogger().warning('Cannot send command to OSC host => stop OSC !')
                self._close()

    def sendCommand(self, cmd):
        if hasattr(self, '_client'):
            self._client.send(cmd)

    def getGlobal(self):
        return self._global
