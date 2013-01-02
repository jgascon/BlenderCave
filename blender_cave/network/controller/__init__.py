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
import time
import sys
import bge
import blender_cave.buffer
import blender_cave.base
import blender_cave.exceptions

class Controller(blender_cave.base.Base):
    BUFFER_SIZE = 4096

    # Controller status
    STATUS_WAIT_FOR_CONNECTION = 0
    STATUS_WAIT_FOR_RELOAD     = 1
    STATUS_READY               = 2

    # Protocol from master to slaves
    EVERYBODY_HERE = b'c'
    QUIT           = b'q'

    # Protocol from slave to master
    BARRIER = b'b'
    RELOAD  = b'r'

    #Protocol both sides
    BARRIER_BUG = b'B'

    def __init__(self, parent):
        super(Controller, self).__init__(parent)
        self._barrier_counter = 0
        self._socket  = None

        if self.getBlenderCave().getReloadBackupper().isOriginal():
            self._status  = self.STATUS_WAIT_FOR_CONNECTION
        else:
            self._socket, self.boolean = self.getSocketFromReloader(__class__.__name__, 'boolean')
            self._status  = self.STATUS_WAIT_FOR_RELOAD

    def firstRun(self):
        if self._status == self.STATUS_READY:
            self.getParent()._startSimulation()

    def quit(self, reason):
        self.getParent()._quitByController(reason)

    def _sendCommand(self, command):
        buffer = blender_cave.buffer.Buffer()
        buffer.command(command)
        self._send(buffer)

    def _sendTo(self, peer, buffer):
        try:
            peer.send(buffer._buffer)
        except socket.error:
            return None

    def _receiveFrom(self, client):
        try:
            data = client.recv(self.BUFFER_SIZE)
        except socket.error:
            return None
        if not data:
            return None
        buffer = blender_cave.buffer.Buffer()
        buffer._buffer = data
        return buffer

    def _shutdown(self):
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except:
                pass                
            try:
                self.getParent()._getSelect().setClient(self._socket, None)
            except:
                pass
            self._socket.close()
            self._socket = None

    def addSocketToReloader(self, name, socket, complement, complement_method_name):
        buffer = blender_cave.buffer.Buffer()
        if self._socket is not None:
            self.getParent().addSocketToBuffer(buffer, self._socket)
            getattr(buffer, complement_method_name)(complement)
        self.getBlenderCave().getReloadBackupper().addBuffer(name, buffer)

    def getSocketFromReloader(self, name, complement_method_name):
        buffer = self.getBlenderCave().getReloadBackupper().getBuffer(name)
        if buffer is None:
            raise blender_cave.exceptions.Controller('Invalid result readden from Reload Backupper !')
        if not buffer.isEmpty():
            socket  = self.getParent().getSocketFromBuffer(buffer)
            complement = getattr(buffer, complement_method_name)()
            return [socket, complement]
        return [None, None]
        
    def process(self):
        return
