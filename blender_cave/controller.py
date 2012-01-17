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
import time
import struct
import sys
from . import exceptions

class Controller:

    def __init__(self, master, port, address, nbNodes, master_computer, currentScreenID):
        self._master = master
        self._nbNodes = nbNodes
        self._currentScreenID = currentScreenID

        if self._master:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('', port))
            server.listen(nbNodes)
            self._clients = {}
            self._selectEntries=[server]
            while (len(self._clients) + 1) < self._nbNodes:
                inputready,outputready,exceptready = select.select(self._selectEntries, [], [])
                for peer in inputready:
                    if peer == server:
                        client, address = peer.accept()
                        self._selectEntries.append(client)
                        data = client.recv(1024)
                        clientID, = struct.unpack_from('>i', data)
                        self._clients[client] = {'id':clientID, 'socket': client, 'address' : address}
                        print("Connection of a client [", clientID, "] : ",address)
                    else:
                        data = peer.recv(1024)
                        if data:
                            print("Data from client : ", data)
                        else:
                            if peer in self._clients:
                                print("Removing : ", self._clients[peer]['address'])
                                del(self._clients[peer])
                            else:
                                print("Closing connection !")
                            self._selectEntries.remove(peer)
                            peer.close()
            self._selectEntries.remove(server)
            server.close()
        else:
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connected = False
            lastWaitingWarning = 0.0
            while connected == False:
                try:
                    self._client.connect((master_computer, port))
                    connected = True
                except socket.error as error:
                    print("waiting for master node !")
                    time.sleep(1)
            print("Connected !")
            data = struct.pack('>i', self._currentScreenID)
            self._client.send(data)

    def __del__(self):
        if self._master == False:
            self._client.close()

    def waitForSlaves(self, command):
        if self._master:
            nbAnswers = 0
            while nbAnswers < len(self._clients):
                inputready,outputready,exceptready = select.select(self._selectEntries, [], [])
                for peer in inputready:
                    client_address = self._clients[peer]['address']
                    data = peer.recv(1024)
                    if data:
                        receivedCommand, = struct.unpack_from('>i', data)
                        if command != receivedCommand:
                            raise exceptions.Controller("Unwanted command (" + str(command) + ") from " + str(client_address))
                        nbAnswers = nbAnswers + 1
                    else:
                        if peer in self._clients:
                            client_address = self._clients[peer]['address']
                            del(self._clients[peer])
                        self._selectEntries.remove(peer)
                        peer.close()
                        raise exceptions.Controller("Lost connection from " + client_address)

    def sendToMaster(self, command):
        if self._master == False:
            data = struct.pack('>i', command)
            self._client.send(data)

    def checkCommand(self, command):
        if self._master:
            self.waitForSlaves(command)
        else:
            self.sendToMaster(command)
            

                
