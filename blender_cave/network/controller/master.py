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
import blender_cave.buffer
import blender_cave.exceptions
from . import Controller

class Master(Controller):

    def __init__(self, parent, config):
        super(Master, self).__init__(parent)

        self._number_slaves = config['number_screens'] - 1
        self._clients       = {}

        if self.getBlenderCave().getReloadBackupper().isOriginal():
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind(('', config['port']))
            self._socket.listen(self._number_slaves)
            self.addSocketToReloader(__class__.__name__, self._socket, True, 'boolean')
        else:
            self._socket, = self.getSocketFromReloader(__class__.__name__)
            for client_id in range(1, self._number_slaves + 1): # 0 = master = this !
                client_socket, client_address = self._socket, = self.getSocketFromReloader(__class__.__name__ + " client " + str(client_id))
                if client_socket is not None:
                    self._addClient(client_id, client_socket, client_address, buffer, False)

        if self._socket is not None:
            self.getParent()._getSelect().setClient(self._socket, self._processConnexions)

        self._check_everybody_connected()

        self._number_clients_at_barrier = 0

    def _processConnexions(self, server):
        if server == self._socket:
            client_socket, address = self._socket.accept()
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            buffer = self._receiveFrom(client_socket)
            if buffer is None:
                raise blender_cave.exceptions.Controller("Protocol error : client don't send correct connection message !")
            client_id = buffer.integer()
            self._addClient(client_id, client_socket, str(address), buffer, True)
            self.getLogger().info("Main Connection of a client [" + str(client_id) + "] : " + str(address))
            if self._check_everybody_connected():
                self.getParent()._startSimulation()

    def _processMessageFromClient(self, peer):
        buffer = self._receiveFrom(peer)
        if buffer is None:
            self._delClient(peer)
            return
        while not buffer.isEmpty():
            command = buffer.command()
            if command == self.BARRIER:
                self._number_clients_at_barrier += 1
            elif command == self.BARRIER_BUG:
                raise blender_cave.exceptions.Controller("Not coherent barrier counter from client : " + str(self._clients[peer]['address']))
            elif command == self.QUIT:
                reason = buffer.string()
                self.quit(reason)
            else:
                raise blender_cave.exceptions.Controller("Unattended command (" + str(command) + ") from " + self._clients[peer]['address'])

    def barrier(self):
        buffer = blender_cave.buffer.Buffer()
        buffer.command(self.BARRIER)
        buffer.integer(self._barrier_counter)
        self._send(buffer)
        while self._number_clients_at_barrier < len(self._clients):
            self.getParent()._getSelect().run(True)
        self._number_clients_at_barrier = 0
        self._barrier_counter += 1

    def quit(self, reason):
        if not hasattr(self,'_is_quitting'): 
            self._is_quitting = True
            buffer = blender_cave.buffer.Buffer()
            buffer.command(self.QUIT)
            buffer.string(reason)
            self._send(buffer)
            while len(self._clients) > 0:
                self.getParent()._getSelect().run(True)
            super(Master, self).quit(reason)

    def _send(self, buffer):
        for client_socket in self._clients:
            self._sendTo(client_socket, buffer)

    def _check_everybody_connected(self):
        if (self._socket is not None) and (len(self._clients) == self._number_slaves):
            self._shutdown()
            self._sendCommand(self.EVERYBODY_HERE)
            self._status        = self.STATUS_READY
            return True
        return False

    def _addClient(self, client_id, client_socket, address, buffer, add_to_backup):
        for index, client in self._clients.items():
            if client['id'] == client_id:
                raise blender_cave.exceptions.Controller("Protocol error : client already defined !")
        self._clients[client_socket] = {'id'      : client_id,
                                        'socket'  : client_socket,
                                        'address' : address}
        self.getParent()._getSelect().setClient(client_socket, self._processMessageFromClient)
        if add_to_backup:
            self.addSocketToReloader(__class__.__name__+ " client " + str(client_id), self._socket, str(address), 'string')

    def _delClient(self, client_socket):
        if client_socket in self._clients:
            msg = "Lose connection to client \"" + self._clients[client_socket]['address'] + "\""
            del(self._clients[client_socket])
            self.getParent()._getSelect().setClient(client_socket, None)
        else:
            msg = "Lose connection to an unknown client"
        self.quit(msg)
