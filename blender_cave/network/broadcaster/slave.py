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

import struct
import socket
import blender_cave.buffer
import blender_cave.exceptions
from . import Broadcaster

class Slave(Broadcaster):
    def __init__(self, parent, config):
        super(Slave, self).__init__(parent, config)

        control_buffer = blender_cave.buffer.Buffer()
        control_buffer.command(self.SEND_BUFFER)
        control_buffer.integer(0)
        self._size_controle_buffer = len(control_buffer)

    def createSocket(self, address, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', int(port)))
        mreq = struct.pack("4sl", socket.inet_aton(address), socket.INADDR_ANY)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.getParent()._getSelect().setClient(self._socket, self._rcvFromMaster)

    def _rcvFromMaster(self, master):
        if not hasattr(self, '_buffer'):
            self._buffer = blender_cave.buffer.Buffer()
        self._buffer._buffer += self._socket.recv(self.BUFFER_SIZE)
        self._getController().barrier()
        if not hasattr(self, '_command'):
            self._command = self._buffer.command()
            self._buffer_size = self._buffer.integer()
        if len(self._buffer) > self._buffer_size:
            raise blender_cave.exceptions.Broadcaster("Cannot append something to a buffer that is already full !")
        

    def run(self):
        while (not hasattr(self, '_buffer_size')) or (not hasattr(self, '_buffer')) or (len(self._buffer) < self._buffer_size):
            self.getParent()._getSelect().run(True)

        del(self._buffer_size)

        command = self._command
        del(self._command)

        buffer  = self._buffer
        del(self._buffer)

        if command == self.SEND_BUFFER:

            while not buffer.isEmpty():
                command = buffer.command()

                if command == self.NOP:
                    break;

                elif command == self.NEW_OBJECT:
                    new_objects_buffer = buffer.subBuffer()
                    while not new_objects_buffer.isEmpty():
                        objects_id   = new_objects_buffer.itemID()
                        objects_name = new_objects_buffer.string()
                        for i in range(len(self._synchronizedObjectsToAdd)):
                            if self._synchronizedObjectsToAdd[i]._synchronize_object_name == objects_name:
                                object = self._synchronizedObjectsToAdd.pop(i)
                                self._synchronizedObjects[objects_id] = object
                                break

                elif command == self.OBJECT:
                    objects_id   = buffer.itemID()
                    objectBuffer = buffer.subBuffer()
                    if objects_id in self._synchronizedObjects:
                        self._synchronizedObjects[objects_id].processSynchronizerBuffer(objectBuffer)


    def reloadFlush(self):
        return
