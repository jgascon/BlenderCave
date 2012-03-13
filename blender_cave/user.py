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

import mathutils
from . import parser
from . import synchronizer
from . import packer
from . import exceptions

class User:

    def __init__(self, node):
        if (node.hasAttributes() == False) or (('ID' in node.attributes) == False):
            raise exceptions.User("User don't have a valid ID !");
        self._id = int(node.attributes['ID'].value)
        if 'name' in node.attributes:
            self._name = node.attributes['name'].value
        else:
            self._name = 'User '+str(self._id)
        if 'eye_separation' in node.attributes:
            self._eye_separation = float(node.attributes['eye_separation'].value)
        else:
            self._eye_separation = 0.06
        child = node.firstChild
        while child:
            if child.nodeName == 'default_position':
                self._default_position = mathutils.Matrix.Translation((parser.getVectorFromNode(child)))
            child = child.nextSibling

        if hasattr(self, '_default_position') == False:
            raise exceptions.user("No default position for the user !");

        synchronizer.addObjectToSynchronize(self)
        return

    def getID(self):
        return self._id
        
    def getName(self):
        return self._name
        
    def getPosition(self):
        if hasattr(self, '_position'):
            return self. _position
        return self._default_position

    def getEyeSeparation(self):
        return self._eye_separation

    def setPosition(self, position):
        self._position = position

    # Both methods are use for the synchronization mechanism ...
    def synchronizerPack(self):
        currentPosition = self.getPosition()
        if (hasattr(self, '_previousSynchronizedPosition') == False) or (self._previousSynchronizedPosition != currentPosition):
            self._previousSynchronizedPosition = currentPosition
            return packer.matrix4x4(currentPosition)
        return b''

    def synchronizerUnpack(self, buffer):
        matrix, buffer = packer.matrix4x4(buffer)
        self.setPosition(matrix)
