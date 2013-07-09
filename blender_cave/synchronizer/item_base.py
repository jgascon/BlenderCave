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

import blender_cave.base
import blender_cave.exceptions
import blender_cave.buffer
import bge

class Base(blender_cave.base.Base):
    def __init__(self, parent, item):
        super(Base, self).__init__(parent)
        self._item = item
        self._name = str(self._item)

    def __del__(self):
        try:
            self._item.endObject()
        except:
            pass
        del(self._item)
        self._item = None

    def getItem(self):
        return self._item

    def getItemID(self):
        return id(self._item)

    def __str__(self):
        return self._name

    def getItemName(self):
        return self._name

    def default(self):
        return

    def isSynchronizable(self):
        return True

    def _getSubItems(self):
        return []

class Master(Base):
    def __init__(self, parent, item):
        super(Master, self).__init__(parent, item)
        self._created   = False

    def __del__(self):
        super(Master, self).__del__()
        self.activate(False)

    def getCreationBuffer(self, parent_id):

        buffer = blender_cave.buffer.Buffer()
        item_id = self.getItemID()

        if not self._created:
            buffer.command(self.getParent().CREATE_ITEM)
            buffer.itemID(parent_id)
            buffer.itemID(item_id)
            item_name = self.getItemName()
            buffer.string(item_name)
            try:
                if self._item.parent is not None:
                    parent_name = str(self._item.parent)
                else:
                    parent_name = item_name
            except AttributeError:
                parent_name = item_name
            buffer.string(parent_name)
            self._created = True
            if not self.getParent()._firstCreation:
                self.activate(True, True)

        for item in self._getSubItems():
            item = self.getParent().getItem(item)
            buffer += item.getCreationBuffer(item_id)
        return buffer

    def getSynchronizerBuffer(self):
        return blender_cave.buffer.Buffer()

    def activate(self, enable, recursive = False):
        self.getParent()._activateItem(self, enable)
        if recursive:
            for item in self._getSubItems():
                item = self.getParent().getItem(item)
                item.activate(enable, True)
            

class Slave(Base):
    def __init__(self, parent, item):
        super(Slave, self).__init__(parent, item)

    def getItemByName(self, name, parent_name):
        for subItem in self._getSubItems():
            if str(subItem) == name:
                return subItem
        return None

    def processSynchronizerBuffer(self, buffer):
        return
