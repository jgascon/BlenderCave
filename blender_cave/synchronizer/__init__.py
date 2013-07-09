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

class Synchronizer(blender_cave.base.Base):
    CREATE_ITEM     = b'c'
    UPDATE_ITEM     = b'u'
    END_UPDATE_ITEM = b'e'
    DELETE_ITEM     = b'd'
    SET_ATTRIBUTE   = b'a'

    def __init__(self, parent):
        super(Synchronizer, self).__init__(parent)

        self._item_types = {}
        item_types = { 'module'             : 'item_root',
                       'KX_Scene'           : 'item_scene',
                       'KX_GameObject'      : 'item_object',
                       'KX_LightObject'     : 'item_light',
                       'KX_Camera'          : 'item_camera',
                       'KX_FontObject'      : 'item_font',
                       'BL_ArmatureObject'  : 'item_armature_object',
                       'BL_ArmatureChannel' : 'item_armature_channel',
                       'default'            : 'item_default'}
        for item_name, module_name in item_types.items():
            try:
                self._item_types[item_name] = __import__(module_name, globals(), locals(), [], -1)
            except ImportError:
                self.getLogger().debug('unimplemented blender item type : ' + item_name)

        self.getBlenderCave().addObjectToSynchronize(self, 'Blender objects synchronization system')
        self._alreadyStart    = False

    def _createSynchronizerItem(self, item):
        if isinstance(item, str):
            item_type = item
        else:
            item_type = item.__class__.__name__
        try:
            module = self._item_types[item_type]
        except KeyError:
            self.getLogger().warning('unrocognized type : ' + item_type)
            module = self._item_types['default']
        if self.getBlenderCave().isMaster():
            return module.Master(self, item)
        else:
            return module.Slave(self, item)
