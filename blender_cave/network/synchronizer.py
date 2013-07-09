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

import socket
import blender_cave.buffer
import blender_cave.exceptions
import blender_cave.base

class Base(blender_cave.base.Base):

    NEW_OBJECT = b'c'
    OBJECT     = b'o'

    def __init__(self, parent):
        super(Base, self).__init__(parent)
        self._synchronizedObjectsToAdd = []
        self._synchronizedObjects = {}

    def addObjectToSynchronize(self, object, name):
        object._synchronize_object_name = name
        self._synchronizedObjectsToAdd.append(object)

    def run(self):
        pass

class Master(Base):

    def __init__(self, parent, config):
        super(Master, self).__init__(parent)


    def getBuffer(self):
        buffer = blender_cave.buffer.Buffer()

        # Create new objects affectations ...
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
            if (object_data_buffer is not None) and (not object_data_buffer.isEmpty()):
                buffer.command(self.OBJECT)
                buffer.itemID(objects_id)
                buffer.subBuffer(object_data_buffer)

        return buffer

class Slave(Base):

    def __init__(self, parent, config):
        super(Slave, self).__init__(parent)


    def process(self, buffer):
        while not buffer.isEmpty():
            command = buffer.command()

            if command == self.NEW_OBJECT:
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
