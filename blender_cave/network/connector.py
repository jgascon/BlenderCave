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

import struct
import socket
import blender_cave.buffer
import blender_cave.exceptions
import blender_cave.base

class Base(blender_cave.base.Base):

    BUFFER_SIZE = 4096
    SIZE_FORMAT = '>i'
    # Beware: we limit to 256 nodes
    ID_FORMAT   = 'B'

    # Controller status
    STATUS_WAIT_FOR_CONNECTION = 0
    STATUS_READY               = 1

    # Protocol from master to slaves
    SYNCHRONIZER   = b'S'
    EVERYBODY_HERE = b'c'
    QUIT           = b'q'

    def __init__(self, parent, synchronizer):
        super(Base, self).__init__(parent)
        self._status = self.STATUS_WAIT_FOR_CONNECTION

        self._synchronizer = synchronizer

        from . import select
        self._select = select.Select(self)

    def _receiveFrom(self, client):
        try:
            whole_size = client.recv(struct.calcsize(self.SIZE_FORMAT))
            if len(whole_size) < struct.calcsize(self.SIZE_FORMAT):
                return
            whole_size = struct.unpack_from(self.SIZE_FORMAT, whole_size)
            whole_size = whole_size[0]
            buffer = blender_cave.buffer.Buffer()
            rcv_size = min(self.BUFFER_SIZE, whole_size - len(buffer))
            while rcv_size > 0:
                data = client.recv(rcv_size)
                if not data:
                    return
                buffer._buffer += data
                rcv_size = min(self.BUFFER_SIZE, whole_size - len(buffer))
            return buffer
        except socket.error:
            return

    def _send(self, buffer):
        buffer = buffer._buffer
        size = len(buffer)
        self._sendPartialBinary(struct.pack(self.SIZE_FORMAT, size))
        size = min(self.BUFFER_SIZE, len(buffer))
        while size > 0:
            self._sendPartialBinary(buffer[:size])
            buffer = buffer[size:]
            size = min(self.BUFFER_SIZE, len(buffer))
        
    def _sendBinaryTo(self, peer, buffer):
        try:
            peer.send(buffer)
        except socket.error:
            return

    def _sendCommand(self, command):
        buffer = blender_cave.buffer.Buffer()
        buffer.command(command)
        self._send(buffer)

    def _shutdown(self):
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except:
                pass                
            try:
                self._select.setClient(self._socket, None)
            except:
                pass
            self._socket.close()
            self._socket = None

    def _switchToReady(self):
        self._status = self.STATUS_READY
        self.getParent()._startSimulation()

    def start(self):
        pass

    def quit(self, reason):
        self.getParent()._quitByConnector(reason)

    def isReady(self):
        return self._status == self.STATUS_READY

class Master(Base):

    def __init__(self, parent, config, synchronizer):
        super(Master, self).__init__(parent, synchronizer)

        self._number_slaves = config['number_screens'] - 1
        self._clients       = {}

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('', config['port']))
        self._socket.listen(self._number_slaves)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # improve speed ...

        self._select.setClient(self._socket, self._connectClient)

    def run(self):
        if self.isReady():
            buffer = blender_cave.buffer.Buffer()
            buffer.command(self.SYNCHRONIZER)
            buffer.subBuffer(self._synchronizer.getBuffer())
            self._send(buffer)
        self._select.run(False)

    def _connectClient(self, server):
        if server == self._socket:
            client_socket, address = self._socket.accept()
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                client_id = struct.unpack_from(self.ID_FORMAT, client_socket.recv(struct.calcsize(self.ID_FORMAT)))
                client_id = client_id[0]
            except socket.error:
                raise blender_cave.exceptions.Controller("Protocol error : client don't send correct connection message !")
            self.getLogger().info("Main Connection of a client [" + str(client_id) + "] : " + str(address))
            self._addClient(client_id, client_socket, str(address))
            self._check_everybody_connected()

    def _addClient(self, client_id, client_socket, address):
        for index, client in self._clients.items():
            if client['id'] == client_id:
                raise blender_cave.exceptions.Controller("Protocol error : client already defined !")
        self._clients[client_socket] = {'id'      : client_id,
                                        'socket'  : client_socket,
                                        'address' : address}
        self._select.setClient(client_socket, self._processMessageFromClient)

    def _delClient(self, client_socket):
        if client_socket in self._clients:
            msg = "Lose connection to client \"" + self._clients[client_socket]['address'] + "\""
            del(self._clients[client_socket])
            self._select.setClient(client_socket, None)
        else:
            msg = "Lose connection to an unknown client"
        self.quit(msg)

    def _processMessageFromClient(self, peer): 
        buffer = self._receiveFrom(peer)
        if buffer is None:
            self._delClient(peer)
            return
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.QUIT:
                reason = buffer.string()
                self.quit(reason)
            else:
                raise blender_cave.exceptions.Controller("Unattended command (" + str(command) + ") from " + self._clients[peer]['address'])

    def _check_everybody_connected(self):
        if (self._socket is not None) and (len(self._clients) == self._number_slaves):
            self._shutdown()
            self._sendCommand(self.EVERYBODY_HERE)
            self._switchToReady()

    def _sendPartialBinary(self, buffer):
        for client_socket in self._clients:
            self._sendBinaryTo(client_socket, buffer)

    def start(self):
        self._check_everybody_connected()

    def quit(self, reason):
        if not hasattr(self,'_is_quitting'): 
            self._is_quitting = True
            buffer = blender_cave.buffer.Buffer()
            buffer.command(self.QUIT)
            buffer.string(reason)
            self._send(buffer)
            while len(self._clients) > 0:
                self._select.run(True)
            super(Master, self).quit(reason)

class Slave(Base):

    def __init__(self, parent, config, synchronizer):
        super(Slave, self).__init__(parent, synchronizer)

        self._port    = config['port']
        self._master  = config['master_node']
        self._slaveID = config['screen_id']

        self.run = self._connectToMaster

    def _connectToMaster(self):
        self._select.run(False)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._socket.connect((self._master, self._port))
        except socket.error as error:
            del(self._socket)
            self._socket = None
            return
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # improve speed ...

        # ... and notify the server of who I am ..
        try:
            self._socket.send((struct.pack(self.ID_FORMAT, self._slaveID)))
        except socket.error:
            pass

        # ... add the socket to the select
        self._select.setClient(self._socket, self._processMessageFromMaster)

        self.run = self._run

        self.getLogger().info('Connected to master, waiting everybody connected !')

    def _processMessageFromMaster(self, peer):
        buffer = self._receiveFrom(peer)
        if buffer is None:
            self.quit("Lose connection from the master !")
            return
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.EVERYBODY_HERE:
                self._switchToReady()
            elif command == self.QUIT:
                self._shutdown()
                self.quit(buffer.string())
            elif command == self.SYNCHRONIZER:
                self._synchronizer.process(buffer.subBuffer())
            else:
                raise blender_cave.exceptions.Controller("Unattended command (" + str(command) + ") from " + str(peer))

    def _run(self):
        self._select.run(False)

    def _sendPartialBinary(self, buffer):
        self._sendBinaryTo(self._socket, buffer)



