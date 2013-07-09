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

import copy
import bge
import blender_cave.base
import blender_cave.exceptions
from . import Synchronizer
from . import item_base

class Master(Synchronizer):
    def __init__(self, parent):
        super(Master, self).__init__(parent)
        self._items            = {}
        self._active           = []
        self._mainItem         = self.getItem(bge.logic)
        self._firstCreation     = True

    def _activateItem(self, synchronizerItem, activate):
        if synchronizerItem.isSynchronizable():
            if activate:
                self._active.append(synchronizerItem.getItemID())
            else:
                try:
                    self._active.remove(synchronizerItem.getItemID())
                except ValueError:
                    pass

    def getItem(self, item):
        item_id = id(item)
        if item_id not in self._items:
            synchronizerItem = self._createSynchronizerItem(item)
            self._items[item_id] = synchronizerItem
        return self._items[item_id]

    def getSynchronizerBuffer(self):

        buffer = blender_cave.buffer.Buffer()

        items_to_delete = []
        for item_id in self._items:
            item = self._items[item_id]
            try:
                str(item.getItem())
            except SystemError:
                items_to_delete.append(item_id)
        for item_id in items_to_delete:
            buffer.command(self.DELETE_ITEM)
            buffer.itemID(item_id)
            del(self._items[item_id])

        buffer += self._mainItem.getCreationBuffer(0)

        for item_id in self._active:
            try:
                item = self._items[item_id]
                item_buffer = item.getSynchronizerBuffer()
                if len(item_buffer) > 0:
                    buffer.command(self.SET_ATTRIBUTE)
                    buffer.itemID(item_id)
                    buffer.subBuffer(item_buffer)
            except KeyError:
                pass

        self._firstCreation = False

        return buffer
