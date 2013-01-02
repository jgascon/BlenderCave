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
import struct
import select
import sys
import blender_cave.buffer
import blender_cave.base

class Broadcaster(blender_cave.base.Base):

    NOP        = b'n'
    NEW_OBJECT = b'c'
    OBJECT     = b'o'

    # Sending constants
    BUFFER_SIZE        = 1024
    BUFFER_SIZE_FORMAT = '>i'

    # Multicast protocol
    SEND_BUFFER = b's'

    # Unicast protocol
    PROTOCL_ACK = 0

    def __init__(self, parent, config):
        super(Broadcaster, self).__init__(parent)

        if self.getBlenderCave().getReloadBackupper().isOriginal():
            self.createSocket(config['address'], config['port'])
            buffer = blender_cave.buffer.Buffer()
            self.getParent().addSocketToBuffer(buffer, self._socket)
            self.getBlenderCave().getReloadBackupper().addBuffer(__class__.__name__, buffer)
        else:
            buffer = self.getBlenderCave().getReloadBackupper().getBuffer(__class__.__name__)
            self._socket = self.getParent().getSocketFromBuffer(buffer)

        self._synchronizedObjectsToAdd = []
        self._synchronizedObjects = {}

    def addObjectToSynchronize(self, object, name):
        object._synchronize_object_name = name
        self._synchronizedObjectsToAdd.append(object)

    def _getController(self):
        return self.getParent()._getController()
    
    def firstRun(self):
        return
