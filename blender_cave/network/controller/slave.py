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
import select
import blender_cave.buffer
import blender_cave.exceptions
from . import Controller

class Slave(Controller):

    def __init__(self, parent, config):
        super(Slave, self).__init__(parent)

        if not self.getBlenderCave().getReloadBackupper().isOriginal():
            self._socket, = self.getSocketFromReloader(__class__.__name__)
            self.getParent()._getSelect().setClient(self._socket, self._processMessageFromMaster)

        if self._socket is None:
            self._port                 = config['port']
            self._master               = config['master_node']
            self._slaveID              = config['screen_id']
            self.process               = self._connectToToMaster

        self._master_is_waiting_for_barrier = False

    def barrier(self):
        while not self._master_is_waiting_for_barrier:
            self.getParent()._getSelect().run(True)
        self._sendCommand(self.BARRIER)
        self._master_is_waiting_for_barrier = False

    def quit(self, reason):
        super(Slave, self).quit(reason)

    def _send(self, buffer):
        self._sendTo(self._socket, buffer)

    def _connectToToMaster(self, wait_for_packet = False):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((self._master, self._port))
        except socket.error as error:
            del(self._socket)
            self._socket = None
            return
        # Set TCP_NODELAY option to improve speed ...
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Adding the buffer to the backup reloader ...
        self.addSocketToReloader(__class__.__name__, self._socket, False, 'boolean')

        # ... and notify the server of who I am ..
        buffer = blender_cave.buffer.Buffer()
        buffer.integer(self._slaveID)
        self._sendTo(self._socket, buffer)

        # ... add the socket to the select
        self.getParent()._getSelect().setClient(self._socket, self._processMessageFromMaster)

        # ... then log
        self.getLogger().debug("Connected to master, waiting everybody connected !")

        self.process = super(Slave, self).process

    def _process(self):
        return

    def _processMessageFromMaster(self, peer):
        buffer = self._receiveFrom(peer)
        if buffer is None:
            self.quit("Lose connection from the master !")
            return
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.EVERYBODY_HERE:
                self._status = self.STATUS_READY
                self.addSocketToReloader(__class__.__name__, self._socket, True, 'boolean')
                self.getParent()._startSimulation()
            elif command == self.BARRIER:
                master_barrier_counter = buffer.integer()
                if self._barrier_counter != master_barrier_counter:
                    self._sendCommand(self.BARRIER_BUG)
                    raise blender_cave.exceptions.Controller("Not coherent barrier counter (" + str(self._barrier_counter) +"!=" + str(master_barrier_counter) + ") ...")
                self._barrier_counter += 1
                self._master_is_waiting_for_barrier = True
            elif command == self.QUIT:
                self._shutdown()
                self.quit(buffer.string())
            else:
                raise blender_cave.exceptions.Controller("Unattended command (" + str(command) + ") from " + str(peer))
        

################################################################
    def _runControlWaitForReload(self):
        self.sendCommand(self.RELOAD)
        self._master_is_ready = False
        self.processAllConnections(False)
        if self._master_is_ready:
            self.runControl  = self._runControlWaitForReload
            self.msgFromPeer = self._processReloadMessage
            self.isRead      = self._isReadyWaitForReload
            del(self._master_is_ready)

    def _processReloadMessage(self, peer):
        buffer = self._receiveFrom(peer)
        if buffer is None:
            self.quit("Lose connection from the master !")
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.RELOAD:
                self._master_is_ready = True
