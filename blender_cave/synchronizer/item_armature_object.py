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

from . import item_object
import blender_cave.exceptions

class ArmatureObject:

    OBJECT =   b'o'
    FRAME  =   b'f'

    def __init__(self, parent, item):
        super(ArmatureObject, self).__init__(parent, item)
        self._channels = []
        return
        for channel in self._item.channels:
            self._channels.append(self.getParent().getItem(channel))

    def _getSubItems(self):
        return list(self._item.channels)

class Master(ArmatureObject, item_object.Master):
    def __init__(self, parent, item):
        super(Master, self).__init__(parent, item)
        self._curentActionFrame = self._item.getActionFrame()

    def getSynchronizerBuffer(self):
        buffer = blender_cave.buffer.Buffer()

        object_buffer = super(Master, self).getSynchronizerBuffer()
        if len(object_buffer) > 0:
            buffer.command(self.OBJECT)
            buffer.subBuffer(object_buffer)

        if (self._curentActionFrame != self._item.getActionFrame()) and False:
            self._curentActionFrame = self._item.getActionFrame()
            buffer.command(self.FRAME)
            buffer.float(self._curentActionFrame)
        return buffer

class Slave(ArmatureObject, item_object.Slave):
    def __init__(self, parent, item):
        super(Slave, self).__init__(parent, item)

    def processSynchronizerBuffer(self, buffer):

        while len(buffer) > 0:
            command = buffer.command()

            if command == self.OBJECT:
                object_buffer = buffer.subBuffer()
                super(Slave, self).processSynchronizerBuffer(object_buffer)

            if command == self.FRAME:
                actionFrame = buffer.float()
                self._item.setActionFrame(actionFrame)
                self._item.update()
