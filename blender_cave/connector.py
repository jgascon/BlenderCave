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
import struct
import select
import sys
from . import controller
from . import packer
from . import exceptions
from . import quit

class Connector:

    def __init__(self, master, port, address, nbNodes, master_computer, currentScreenID):
        self._protocol = {"NOP": -1,
                          "start simulation": 0,
                          "sending buffer synchronization": 1,
                          "end of simulation": 2}
        self._controlProtocol = {"received slice of buffer": 1,
                                 "received whole buffer": 2}

        self._bufferSendingSize = 1024
        self._master = master
        if self._master:
            self._sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._address = (address, port)
            self._sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1) # Stay in local network !
        else:
            self._listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listener.bind(('', int(port)))
            mreq = struct.pack("4sl", socket.inet_aton(address), socket.INADDR_ANY)
            self._listener.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self._controller = controller.Controller(master, port, address, nbNodes, master_computer, currentScreenID)

    def __del__(self):
        buffer = packer.command(self._protocol["end of simulation"])
        self._send(buffer)

    def _send(self, data):
        if self._master:
            self._sender.sendto(data, self._address)

    def _receive(self, size):
        if self._master == False:
            return self._listener.recv(self._bufferSendingSize)

    def receiveData(self):
        if self._master == False:
            buffer = self._receive(self._bufferSendingSize)
            command, buffer = packer.command(buffer)
            if command == self._protocol["start simulation"]:
                return false
            if command == self._protocol["end of simulation"]:
                quit("End of the simulation sended by the master !")
            if command == self._protocol["sending buffer synchronization"]:
                self._controller.sendToMaster(self._controlProtocol["received slice of buffer"])
                bufferSize, buffer = packer.integer(buffer)
                while (len(buffer) < bufferSize):
                    buffer = buffer + self._receive(self._bufferSendingSize)
                    self._controller.sendToMaster(self._controlProtocol["received slice of buffer"])
                return buffer
                

    def sendBuffer(self, buffer):
        if self._master:
            # Prepend the buffer size to the buffer. Thus, the slaves will know the size of the data they must wait for
            buffer = packer.command(self._protocol["sending buffer synchronization"]) + packer.integer(len(buffer)) + buffer
            # Send "self._bufferSendingSize" elements to the slaves
            while len(buffer) > 0:
                self._send(buffer[:self._bufferSendingSize])
                buffer = buffer[self._bufferSendingSize:]
                self._controller.waitForSlaves(self._controlProtocol["received slice of buffer"])

    def barrier(self):
        return
