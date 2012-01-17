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

import copy
from . import exceptions
from . import packer

class ItemProperty():
    def __init__(self, item, synchronizer, parent):
        self._item = item
        self._synchronizer = synchronizer

        self._id = id(self._item)

        item_type = self._item.__class__.__name__
        if (item_type in self._synchronizer._itemsIDs) == False:
            raise exceptions.Synchronizer("Error : undefined object (" + item_type + ") !")
        self._item_type_id = self._synchronizer._itemsIDs[item_type]
        item_definition = self._synchronizer._itemsDefinitions[self._item_type_id]
        self.attributs = item_definition.attributs
        self.children = item_definition.children

        self._previousValues = {}

        for attribut in self.attributs:
            self._previousValues[attribut.name] = attribut.default

        self._listOfKnownChildren = {}
        self._currentRenderingIndex = 0

        self._synchronizer.appendItemFromMaster(id(parent), self._id, self._item_type_id, self._item.name)

    def _packChild(self, child):
        child_id = id(child)
        self._listOfKnownChildren[child_id] = self._currentRenderingIndex
        self._synchronizer._createBufferFromItem(child, self._item)

    def packAttributs(self):
        buffer = b''

        for attributID in range(len(self.attributs)):
            attribut = self.attributs[attributID]
            attribut.name = attribut.name
            value = getattr(self._item, attribut.name)
            if (self._previousValues[attribut.name] != value):
                buffer += packer.command(attributID) + getattr(packer, attribut.packMethod)(value)
                self._previousValues[attribut.name] = copy.copy(value)

        self._synchronizer.appendAttributsFromMaster(self._id, buffer)

    def packChildrens(self):
        hierarchyBuffer = b''
        attributsBuffer = b''
        for children_name in self.children:
            children = getattr(self._item, children_name)
            try:
                for child in children:
                    self._packChild(child)
            except TypeError:
                self._packChild(children)

        deletedItems = []
        for itemID, renderingIndex in self._listOfKnownChildren.items():
            if renderingIndex != self._currentRenderingIndex:
                deletedItems.append(itemID)

        for i in range(len(deletedItems)):
            itemID = deletedItems[i]
            del(self._listOfKnownChildren[itemID])
            self._synchronizer.removeItemFromMaster(itemID)

        self._currentRenderingIndex += 1
