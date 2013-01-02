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

import socket
import blender_cave.base

class Network(blender_cave.base.Base):
    
    def __init__(self, parent, config):
        super(Network, self).__init__(parent)

        self._is_master  = config['is_master']

        from . import select
        self._select  = select.Select(self)
        

        if self._is_master:

            from .controller import master
            self._controller  = master.Master(self, config)

            from .broadcaster import master
            self._broadcaster  = master.Master(self, config)

        else:

            from .controller import slave
            self._controller  = slave.Slave(self, config)

            from .broadcaster import slave
            self._broadcaster  = slave.Slave(self, config)

        self._firstRun = True

    def addObjectToSynchronize(self, object, name):
        self._broadcaster.addObjectToSynchronize(object, name)

    def isMaster(self):
        return self._is_master

    def isReady(self):
        return self._controller._status == self._controller.STATUS_READY

    def quit(self, reason):
        self._controller.quit(reason)

    def run(self):
        if self._firstRun:
            self._controller.firstRun()
            self._broadcaster.firstRun()
            self._firstRun = False
        self._select.run(False)
        self._controller.process()
        if self.isReady():
            self._broadcaster.run()

    def _quitByController(self, reason):
        self.getParent()._quitByNetwork(reason)

    def _startSimulation(self):
        self.getParent()._startSimulation()

    def addSocketToBuffer(self, buffer, sock):
        buffer.integer(sock.fileno())
        buffer.integer(sock.family)
        buffer.integer(sock.type)
        buffer.integer(sock.proto)

    def getSocketFromBuffer(self, buffer):
        fileno = buffer.integer()
        family = buffer.integer()
        type = buffer.integer()
        proto = buffer.integer()
        return socket.fromfd(fileno, family, type, proto)
    
    def _getController(self):
        return self._controller

    def _getBroadcaster(self):
        return self._broadcaster

    def _getSelect(self):
        return self._select
