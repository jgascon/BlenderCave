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

import bge
import blender_cave.buffer
import blender_cave.exceptions

class ItemProperty():
    def __init__(self, synchronizer, parent_id, child_id, child_item_type_id, child_name):
        self._synchronizer = synchronizer
        self._parent_id = parent_id
        self._id = child_id

        if child_item_type_id >= len(self._synchronizer._itemsDefinitions):
            raise blender_cave.exceptions.Synchronizer("Error : undefined object (" + str(child_item_type_id) + ") !")

        self._itemDefinition = self._synchronizer._itemsDefinitions[child_item_type_id]

        if (self._id == self._parent_id) and (self._itemDefinition.name != 'KX_Scene'):
            raise blender_cave.exceptions.Synchronizer("An object must have a different master than it !")

        if (self._itemDefinition.name == 'KX_Scene') and (self._id != self._parent_id):
            raise blender_cave.exceptions.Synchronizer("A scene cannot be children of anything else !")

        if (self._itemDefinition.name == 'KX_Scene'):
            for scene in bge.logic.getSceneList():
                if self._isValidChoiceForName(scene, child_name):
                    self._item = scene
            if (hasattr(self, '_item')) == False:
                raise blender_cave.exceptions.Synchronizer("Error : undefined scene : " + child_name + " !")
            self._scene_id = self._id
        else:
            parentItemProperty = self._synchronizer.getItemPropertyFromSlave(self._parent_id)
            parent = parentItemProperty.getItem()

            sceneItemProperty = parentItemProperty
            while sceneItemProperty._itemDefinition.name != 'KX_Scene':
                sceneItemProperty = self._synchronizer.getItemPropertyFromSlave(sceneItemProperty._parent_id)

            self._scene_id = sceneItemProperty._id

            children = getattr(parent, self._itemDefinition.ancestors[parent.__class__.__name__])
            try:
                for child in children:
                    if self._isValidChoiceForName(child, child_name):
                        self._item = child
                    
            except TypeError:
                if self._isValidChoiceForName(children, child_name):
                    self._item = child

            if (hasattr(self, '_item')) == False: # Ici, il faut créer l'objet ...
                scene = self._synchronizer.getItemPropertyFromSlave(self._scene_id).getItem()
                if self._scene_id == self._parent_id:
                    other = child_name
                else:
                    other = self._synchronizer.getItemPropertyFromSlave(self._parent_id).getItem()
                self._item = scene.addObject(child_name, other)

        return

    def __del__(self):
        self._item.endObject()

    def _isValidChoiceForName(self, item, name):
        if (hasattr(item, 'name') == False):
            return False
        if item.name != name:
            return False
        return (self._synchronizer.alreadyRegistredLocalItemID(id(item)) == False)

    def updateAttributes(self, buffer):
        while True:
            attributes_id = buffer.unsigned_char()
            if attributes_id == self._synchronizer.END_ATTRIBUTE:
                break
            attribute = self._itemDefinition.attributes[attributes_id]
            value = getattr(buffer, attribute.packMethod)()
            setattr(self._item, attribute.name, value)

    def getItemDefinition(self):
        return self._itemDefinition

    def getItem(self):
        return self._item
