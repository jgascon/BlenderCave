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
from . import Broadcaster

class Master(Broadcaster):
    def __init__(self, parent, config):
        super(Master, self).__init__(parent, config)

    def createSocket(self, address, port):
        self._address = (address, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1) # Stay in local network !
        

    def run(self):
        buffer = blender_cave.buffer.Buffer()

        # Creat new objects affectations ...
        newObjects = blender_cave.buffer.Buffer()
        while len(self._synchronizedObjectsToAdd) > 0:
            object = self._synchronizedObjectsToAdd.pop()
            objects_id = id(object)
            self._synchronizedObjects[objects_id] = object
            newObjects.itemID(objects_id)
            newObjects.string(object._synchronize_object_name)
        if not newObjects.isEmpty():
            buffer.command(self.NEW_OBJECT)
            buffer.subBuffer(newObjects)

        # Then update objects attributs
        for objects_id, object in self._synchronizedObjects.items():
            object_data_buffer = object.getSynchronizerBuffer()
            if not object_data_buffer.isEmpty():
                buffer.command(self.OBJECT)
                buffer.itemID(objects_id)
                buffer.subBuffer(object_data_buffer)
        if not buffer.isEmpty():
            buffer.command(self.NOP)

        control_buffer = blender_cave.buffer.Buffer()
        control_buffer.command(self.SEND_BUFFER)
        control_buffer.integer(len(buffer))
        buffer = control_buffer._buffer + buffer._buffer
        while len(buffer) > 0:
            self._socket.sendto(buffer[:self.BUFFER_SIZE], self._address)
            buffer = buffer[self.BUFFER_SIZE:]
            self._getController().barrier()
