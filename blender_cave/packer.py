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

import struct
import mathutils

def _extractFromBuffer(buffer, format):
    values = struct.unpack_from(format, buffer)
    buffer = buffer[struct.calcsize(format):]
    return [values, buffer]

def command(data):
    if isinstance(data, bytes):
        command, data = _extractFromBuffer(data, '>i')
        return command[0], data
    return struct.pack('>i', data)

def itemID(data):
    if isinstance(data, bytes):
        command, data = _extractFromBuffer(data, '>Q')
        return command[0], data
    return struct.pack('>Q', data)

def integer(data):
    if isinstance(data, bytes):
        integer, data = _extractFromBuffer(data, '>i')
        return integer[0], data
    return struct.pack('>i', data)

def float(data):
    if isinstance(data, bytes):
        float, data = _extractFromBuffer(data, '>f')
        return float[0], data
    return struct.pack('>f', data)

def string(data):
    if isinstance(data, bytes):
        length,data = _extractFromBuffer(data, ">i")
        length = length[0]
        string = data[:length]
        data = data[length:]
        return string.decode('UTF-8'), data
    string = bytes(data, 'UTF-8')
    return struct.pack(">i", len(string)) + string

def vector3(data): 
    if isinstance(data, bytes):
        newVector, data = _extractFromBuffer(data, ">3f")
        vector = mathutils.Vector(newVector)
        return vector, data
    return struct.pack(">3f", data[0], data[1], data[2])

def vector4(data):
    if isinstance(data, bytes):
        newVector, data = _extractFromBuffer(data, ">4f")
        vector = mathutils.Vector(newVector)
        return vector, data
    return struct.pack(">4f", data[0], data[1], data[2], data[3])

def matrix3x3(data):
    if isinstance(data, bytes):
        newMatrix, data = _extractFromBuffer(data, ">9f")
        matrix = mathutils.Matrix.Scale(1.0, 3)
        matrix[0][:] = newMatrix[0:3]
        matrix[1][:] = newMatrix[3:6]
        matrix[2][:] = newMatrix[6:9]
        return matrix, data
    return struct.pack(">9f", data[0][0], data[0][1], data[0][2],
                              data[1][0], data[1][1], data[1][2],
                              data[2][0], data[2][1], data[2][2])

def matrix4x4(data):
    if isinstance(data, bytes):
        newMatrix, data = _extractFromBuffer(data, ">16f")
        matrix = mathutils.Matrix.Scale(1.0, 4)
        matrix[0][:] = newMatrix[ 0: 4]
        matrix[1][:] = newMatrix[ 4: 8]
        matrix[2][:] = newMatrix[ 8:12]
        matrix[3][:] = newMatrix[12:16]
        return matrix, data
    return struct.pack(">16f", data[0][0], data[0][1], data[0][2], data[0][3],
                               data[1][0], data[1][1], data[1][2], data[1][3],
                               data[2][0], data[2][1], data[2][2], data[2][3],
                               data[3][0], data[3][1], data[3][2], data[3][3])
