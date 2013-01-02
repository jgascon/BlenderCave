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
import blender_cave.base
import blender_cave.exceptions
from . import master
from . import slave

class Attribute:
    def __init__(self, name, packMethod, default = False):
        self.name = name
        self.packMethod = packMethod
        self.default = default

class ItemDefinition:
    def __init__(self, name, ancestors, children, update = False):
        self.name = name
        self.ancestors = ancestors
        self.children = children
        self.update = update
        self.attributes = []

    def appendAttribute(self, attribute):
        self.attributes.append(attribute)

    def appendAttributesFrom(self, itemDefinition):
        self.attributes += itemDefinition.attributes

class Synchronizer(blender_cave.base.Base):
    ADD_ITEM        = b'n'
    REMOVE_ITEM     = b'r'
    BEGIN_ATTRIBUTE = b'b'

    # Managed as an integer ...
    END_ATTRIBUTE   = 255

    def __init__(self, parent):
        super(Synchronizer, self).__init__(parent)

        self._started = False

        self._itemsDefinitions = []
        Scene = ItemDefinition('KX_Scene', {}, ['objects'])
        GameObject = ItemDefinition('KX_GameObject', {'KX_Scene' : 'objects'}, [])
        LightObject = ItemDefinition('KX_LightObject', {'KX_Scene' : 'objects'}, [])
        Camera = ItemDefinition('KX_Camera', {'KX_Scene' : 'objects'}, [])
        #ArmatureObject = ItemDefinition('BL_ArmatureObject', {'KX_Scene' : 'objects'}, [], True)
        ArmatureObject = ItemDefinition('BL_ArmatureObject', {'KX_Scene' : 'objects'}, ['channels'], True)
        ArmatureChannel = ItemDefinition('BL_ArmatureChannel', {'BL_ArmatureObject' : 'channels'}, [])

        GameObject.appendAttribute(Attribute('localPosition', 'vector_3'))
        GameObject.appendAttribute(Attribute('localOrientation', 'matrix_3x3'))
        GameObject.appendAttribute(Attribute('localScale', 'vector_3'))

        ArmatureChannel.appendAttribute(Attribute('location', 'vector_3'))
        ArmatureChannel.appendAttribute(Attribute('scale', 'vector_3'))
        ArmatureChannel.appendAttribute(Attribute('rotation_mode', 'integer'))
        ArmatureChannel.appendAttribute(Attribute('rotation_quaternion', 'vector_4'))
        ArmatureChannel.appendAttribute(Attribute('rotation_euler', 'vector_3'))
        ArmatureChannel.appendAttribute(Attribute('joint_rotation', 'vector_3')) 

        LightObject.appendAttributesFrom(GameObject)

        Camera.appendAttributesFrom(GameObject)

        self._itemsDefinitions.append(Scene)
        self._itemsDefinitions.append(GameObject)
        self._itemsDefinitions.append(LightObject)
        self._itemsDefinitions.append(Camera)
        self._itemsDefinitions.append(ArmatureObject)
        self._itemsDefinitions.append(ArmatureChannel)

        self._itemsIDs = {}
        for itemID in range(len(self._itemsDefinitions)):
            self._itemsIDs[self._itemsDefinitions[itemID].name] = itemID

        self.getBlenderCave().addObjectToSynchronize(self, 'Blender objects synchronization system')

    def appendItemFromMaster(self, parent_id, child_id, child_item_type_id, child_name):
        self._hierarchyBuffer.command(self.ADD_ITEM)
        self._hierarchyBuffer.itemID(parent_id)
        self._hierarchyBuffer.itemID(child_id)
        self._hierarchyBuffer.integer(child_item_type_id)
        self._hierarchyBuffer.string(child_name)

    def removeItemFromMaster(self, item_id):
        self._hierarchyBuffer.command(self.REMOVE_ITEM)
        self._hierarchyBuffer.itemID(item_id)

    def appendAttributesFromMaster(self, item_id, buffer):
        if len(buffer) > 0:
            self._attributesBuffer.command(self.BEGIN_ATTRIBUTE)
            self._attributesBuffer.itemID(item_id)
            self._attributesBuffer += buffer
            self._attributesBuffer.unsigned_char(self.END_ATTRIBUTE)

    def _createBufferFromItem(self, item, parent):
        item_id = id(item)
        if (item_id in self._master_items_definitions) == False:
            self._master_items_definitions[item_id] = master.ItemProperty(item, self, parent)
        self._master_items_definitions[item_id].packAttributes()
        self._master_items_definitions[item_id].packChildrens()

    def getItemPropertyFromSlave(self, item_id):
        if item_id in self._masterItemsIDs:
            return self._masterItemsIDs[item_id]
        raise blender_cave.exceptions.Synchronizer("Error : cannot find item " + str(item_id) + " !")

    def _updateSceneFromBuffer(self, buffer):
        if hasattr(self, '_masterItemsIDs') == False:
            self._masterItemsIDs = {}
        while len(buffer) > 0:
            command = buffer.command()

            # First, check the state ...
            if command == self.ADD_ITEM:
                parent_id = buffer.itemID()
                child_id = buffer.itemID()
                child_item_type_id = buffer.integer()
                child_name = buffer.string()
                self._masterItemsIDs[child_id] = slave.ItemProperty(self, parent_id, child_id, child_item_type_id, child_name)
                continue

            if command == self.REMOVE_ITEM:
                item_id = buffer.itemID()
                del(self._masterItemsIDs[item_id])
                continue

            if command == self.BEGIN_ATTRIBUTE:
                item_id = buffer.itemID()
                self.getItemPropertyFromSlave(item_id).updateAttributes(buffer)
                continue

            raise blender_cave.exceptions.Synchronizer("buffer from master reading error: not start of item !")
        return

    def alreadyRegistredLocalItemID(self, local_item_id):
        for item_id in self._masterItemsIDs:
            itemProperty = self._masterItemsIDs[item_id]
            if (hasattr(itemProperty, '_item')) == False:
                continue
            if id(itemProperty.getItem()) == local_item_id:
                return True
        return False

    def getSynchronizerBuffer(self):
        self._hierarchyBuffer = blender_cave.buffer.Buffer()
        self._attributesBuffer = blender_cave.buffer.Buffer()

        if not hasattr(self, '_master_items_definitions'):
            self._master_items_definitions = {}

        self._createBufferFromItem(bge.logic.getCurrentScene(), bge.logic.getCurrentScene())

        buffer = self._hierarchyBuffer + self._attributesBuffer

        del(self._hierarchyBuffer)
        del(self._attributesBuffer)

        return buffer

    def processSynchronizerBuffer(self, buffer):
        self._updateSceneFromBuffer(buffer)
