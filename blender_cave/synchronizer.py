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
import select
import time
import sys
import bge
import pprint
from . import connector
from . import exceptions
from . import packer
from . import master
from . import slave

class Attribut:
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
        self.attributs = []

    def appendAttribut(self, attribut):
        self.attributs.append(attribut)

    def appendAttributsFrom(self, itemDefinition):
        self.attributs += itemDefinition.attributs

class Synchronizer:

    def __init__(self, master, port, address, nbNodes, master_computer, currentScreenID):
        self._master = master
        self._nbNodes = nbNodes
        self._currentScreenID = currentScreenID
        self._connector = connector.Connector(self._master, port, address, nbNodes, master_computer, currentScreenID)
        self._started = False

        self._metaCommands = {'begin attributs' : -1,
                              'end attributs'   : -2,
                              'other object'    : -3,
                              'new item'        : -4,
                              'delete item'     : -5,
                              'NOP'             : -6}

        self._itemsDefinitions = []
        Scene = ItemDefinition('KX_Scene', {}, ['objects'])
        GameObject = ItemDefinition('KX_GameObject', {'KX_Scene' : 'objects'}, [])
        LightObject = ItemDefinition('KX_LightObject', {'KX_Scene' : 'objects'}, [])
        Camera = ItemDefinition('KX_Camera', {'KX_Scene' : 'objects'}, [])
        #ArmatureObject = ItemDefinition('BL_ArmatureObject', {'KX_Scene' : 'objects'}, [], True)
        ArmatureObject = ItemDefinition('BL_ArmatureObject', {'KX_Scene' : 'objects'}, ['channels'], True)
        ArmatureChannel = ItemDefinition('BL_ArmatureChannel', {'BL_ArmatureObject' : 'channels'}, [])

        GameObject.appendAttribut(Attribut('localPosition', 'vector3'))
        GameObject.appendAttribut(Attribut('localOrientation', 'matrix3x3'))
        GameObject.appendAttribut(Attribut('localScale', 'vector3'))

        ArmatureChannel.appendAttribut(Attribut('location', 'vector3'))
        ArmatureChannel.appendAttribut(Attribut('scale', 'vector3'))
        ArmatureChannel.appendAttribut(Attribut('rotation_mode', 'integer'))
        ArmatureChannel.appendAttribut(Attribut('rotation_quaternion', 'vector4'))
        ArmatureChannel.appendAttribut(Attribut('rotation_euler', 'vector3'))
        ArmatureChannel.appendAttribut(Attribut('joint_rotation', 'vector3')) 

        LightObject.appendAttributsFrom(GameObject)

        Camera.appendAttributsFrom(GameObject)

        self._itemsDefinitions.append(Scene)
        self._itemsDefinitions.append(GameObject)
        self._itemsDefinitions.append(LightObject)
        self._itemsDefinitions.append(Camera)
        self._itemsDefinitions.append(ArmatureObject)
        self._itemsDefinitions.append(ArmatureChannel)

        self._itemsIDs = {}
        for itemID in range(len(self._itemsDefinitions)):
            self._itemsIDs[self._itemsDefinitions[itemID].name] = itemID

        if hasattr(bge.logic, 'objectsToSynchronize') == False:
            bge.logic.objectsToSynchronize = []

    def appendItemFromMaster(self, parent_id, child_id, child_item_type_id, child_name):
        self._hierarchyBuffer += packer.command(self._metaCommands['new item'])
        self._hierarchyBuffer += packer.itemID(parent_id) + packer.itemID(child_id)
        self._hierarchyBuffer += packer.command(child_item_type_id) + packer.string(child_name)

    def removeItemFromMaster(self, item_id):
        self._hierarchyBuffer += packer.command(self._metaCommands['delete item'])
        self._hierarchyBuffer += packer.itemID(item_id)

    def appendAttributsFromMaster(self, item_id, buffer):
        if len(buffer) > 0:
            self._attributsBuffer += packer.command(self._metaCommands['begin attributs'])
            self._attributsBuffer += packer.itemID(item_id) + buffer
            self._attributsBuffer += packer.command(self._metaCommands['end attributs'])

    def _createBufferFromItem(self, item, parent):
        item_id = id(item)
        if (item_id in self._master_items_definitions) == False:
            self._master_items_definitions[item_id] = master.ItemProperty(item, self, parent)
        self._master_items_definitions[item_id].packAttributs()
        self._master_items_definitions[item_id].packChildrens()

    def getItemPropertyFromSlave(self, item_id):
        if item_id in self._masterItemsIDs:
            return self._masterItemsIDs[item_id]
        sys.exit()
        raise exceptions.Synchronizer("Error : cannot find item " + str(item_id) + " !")

    def _updateSceneFromBuffer(self):
        if hasattr(self, '_masterItemsIDs') == False:
            self._masterItemsIDs = {}
        while len(self._receivedBuffer) > 0:
            item_state, self._receivedBuffer = packer.command(self._receivedBuffer)

            # First, check the state ...
            if item_state == self._metaCommands['NOP']:
                break # NOP means empty buffer in case of no update ...

            if item_state == self._metaCommands['new item']:
                parent_id, self._receivedBuffer = packer.itemID(self._receivedBuffer)
                child_id, self._receivedBuffer = packer.itemID(self._receivedBuffer)
                child_item_type_id, self._receivedBuffer = packer.command(self._receivedBuffer)
                child_name, self._receivedBuffer = packer.string(self._receivedBuffer)
                self._masterItemsIDs[child_id] = slave.ItemProperty(self, parent_id, child_id, child_item_type_id, child_name)
                continue

            if item_state == self._metaCommands['delete item']:
                item_id, self._receivedBuffer = packer.itemID(self._receivedBuffer)
                del(self._masterItemsIDs[item_id])
                continue

            if item_state == self._metaCommands['begin attributs']:
                item_id, self._receivedBuffer = packer.itemID(self._receivedBuffer)
                self.getItemPropertyFromSlave(item_id).updateAttributs()
                continue

            if item_state == self._metaCommands['other object']:
                objectToSynchronizeID, self._receivedBuffer = packer.integer(self._receivedBuffer)
                objectBufferSize, self._receivedBuffer = packer.integer(self._receivedBuffer)
                objectBufffer = self._receivedBuffer[0:objectBufferSize]
                self._receivedBuffer = self._receivedBuffer[objectBufferSize:]
                if objectToSynchronizeID < len(bge.logic.objectsToSynchronize):
                        bge.logic.objectsToSynchronize[objectToSynchronizeID].synchronizerUnpack(objectBufffer)
                continue

            raise exceptions.Synchronizer("buffer from master reading error: not start of item !")
        return

    def alreadyRegistredLocalItemID(self, local_item_id):
        for item_id in self._masterItemsIDs:
            itemProperty = self._masterItemsIDs[item_id]
            if (hasattr(itemProperty, '_item')) == False:
                continue
            if id(itemProperty.getItem()) == local_item_id:
                return True
        return False


    def run(self):
        if self._started == False:
            if self._master == False:
                print("Waiting for Start !")
            self._started = True

        if self._master:
            self._hierarchyBuffer = b''
            self._attributsBuffer = b''
            if (hasattr(self, '_master_items_definitions') == False):
                self._master_items_definitions = {}
            itemBuffer = self._createBufferFromItem(bge.logic.getCurrentScene(), bge.logic.getCurrentScene())
            buffer = self._hierarchyBuffer + self._attributsBuffer
            for objectToSynchronizeID in range(len(bge.logic.objectsToSynchronize)):
                objectToSynchronize = bge.logic.objectsToSynchronize[objectToSynchronizeID]
                object_buffer = objectToSynchronize.synchronizerPack()
                if len(object_buffer) > 0:
                    buffer += packer.command(self._metaCommands['other object']) + packer.integer(objectToSynchronizeID)
                    buffer += packer.integer(len(object_buffer)) + object_buffer
            del (self._hierarchyBuffer)
            del (self._attributsBuffer)
            # In case of buffer is empty (ie : no update), we send NOP to don't break the frame rate ...
            if (len(buffer) == 0):
                buffer = packer.command(self._metaCommands['NOP'])
            self._connector.sendBuffer(buffer)
        else:
            self._receivedBuffer = self._connector.receiveData()
            self._updateSceneFromBuffer()
            del(self._receivedBuffer)

        buffer = self._connector.barrier()

def addObjectToSynchronize(objectToSynchronize):
    if hasattr(bge.logic, 'objectsToSynchronize') == False:
        bge.logic.objectsToSynchronize = []
    bge.logic.objectsToSynchronize.append(objectToSynchronize)
