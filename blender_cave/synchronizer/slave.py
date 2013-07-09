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

class Slave(Synchronizer):
    def __init__(self, parent):
        super(Slave, self).__init__(parent) 

        self._items            = {}

        self._not_object_items = {}

        self._items[0] = self._createSynchronizerItem(bge.logic)

    def processSynchronizerBuffer(self, buffer):

        while len(buffer) > 0:
            
            command = buffer.command()

            if command == self.DELETE_ITEM:
                item_id   = buffer.itemID()
                try:
                    del(self._items[item_id])
                except KeyError:
                    pass
                continue

            if command == self.CREATE_ITEM:
                parent_id   = buffer.itemID()
                item_id     = buffer.itemID()
                item_name   = buffer.string()
                parent_name = buffer.string()
                try:
                    parent_item = self._items[parent_id]
                except KeyError:
                    continue
                item = parent_item.getItemByName(item_name, parent_name)
                self._items[item_id] = self._createSynchronizerItem(item)
                continue

            if command == self.SET_ATTRIBUTE:
                item_id     = buffer.itemID()
                item_buffer = buffer.subBuffer()
                try:
                    item = self._items[item_id]
                    item.processSynchronizerBuffer(item_buffer)
                except KeyError:
                    pass
                except:
                    self.getBlenderCave().log_traceback(False)
                continue

            raise blender_cave.exceptions.Synchronizer("buffer from master reading error: not start of item !")
        return
