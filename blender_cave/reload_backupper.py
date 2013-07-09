# -*- coding: iso-8859-1 -*-
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

import os
import tempfile
import blender_cave.base
import blender_cave.buffer

class ReloadBackupper(blender_cave.base.Base):

    def __init__(self, parent, environ):
        super(ReloadBackupper, self).__init__(parent)
        self._backup_filename = environ.getEnvironment('rb_file')
        if self._backup_filename is None:
            self._backup_filename = os.path.join(tempfile.gettempdir(), 'blender_cave.!PID!.dat')
        self._backup_filename = self._backup_filename.replace('!PID!', str(os.getpid()))
        try:
            buffer = blender_cave.buffer.Buffer()
            file = open(self._backup_filename, "rb")
            buffer._buffer = file.read()
            file.close()
            self._buffers = {}
            while not buffer.isEmpty():
                buffer_name = buffer.string()
                obj_buffer  = buffer.subBuffer()
                self._buffers[buffer_name] = obj_buffer
            self._original = False
                
        except IOError:
            self._original = True
            file = open(self._backup_filename, "wb")
            file.close()

    def __del__(self):
        os.remove(self._backup_filename)

    def isOriginal(self):
        return self._original

    def addBuffer(self, buffer_name, obj_buffer):
        if self._original:
            buffer = blender_cave.buffer.Buffer()
            buffer.string(buffer_name)
            buffer.subBuffer(obj_buffer)
            file = open(self._backup_filename, "ab")
            file.write(buffer._buffer)
            file.close()

    def getBuffer(self, buffer_name):
        if (not self._original) and (buffer_name in self._buffers):
            return self._buffers[buffer_name]
        return None

