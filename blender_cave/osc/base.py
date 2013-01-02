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

import blender_cave.base
import blender_cave.exceptions
import mathutils

class Base(blender_cave.base.Base):
    def __init__(self, parent, name, OSC_ID):
        super(Base, self).__init__(parent)
        self._name     = name
        self._OSC_ID   = OSC_ID
        self._commands = {
            'start':  { 'type': 'bool'},
            'volume': { 'type': 'vol' },
            'mute':   { 'type': 'bool'}
            }

    def run(self):
        for name, attribut in self._commands.items():
            if attribut['update']:
                cmd = '/' + self._name + ' '
                if self._OSC_ID is not None:
                    cmd += str(self._OSC_ID) + ' '
                cmd += attribut['cmd'] + ' '
                cmd += attribut['value']
                self.getParent().sendCommand(cmd)
                attribut['update'] = False

    def _command(self, attribut, value):
        new_value = getattr(self, attribut['method'])(value)
        if attribut['value'] != new_value:
            attribut['value'] = new_value
            attribut['update'] = True

    def _prepare_bool(self, value):
        if isinstance(value, bool):
            if value == True:
                return '1'
            return '0'
        raise blender_cave.exceptions.OSC_Invalid_Type(str(value) + ' is not a boolean')

    def _prepare_int(self, value):
        if isinstance(value, int):
            return str(value)
        raise blender_cave.exceptions.OSC_Invalid_Type(str(value) + ' is not an integer')

    def _prepare_matrix(self, value):
        if isinstance(value, mathutils.Matrix):
            result  = str(value[0][0]) + ' ' + str(value[1][0]) + ' ' + str(value[2][0]) + ' ' + str(value[3][0]) + ' '
            result += str(value[0][1]) + ' ' + str(value[1][1]) + ' ' + str(value[2][1]) + ' ' + str(value[3][1]) + ' '
            result += str(value[0][2]) + ' ' + str(value[1][2]) + ' ' + str(value[2][2]) + ' ' + str(value[3][2]) + ' '
            result += str(value[0][3]) + ' ' + str(value[1][3]) + ' ' + str(value[2][3]) + ' ' + str(value[3][3])
            return result
        raise blender_cave.exceptions.OSC_Invalid_Type(str(value) + ' is not a matrix')

    def _prepare_string(self, value):
        if isinstance(value, str):
            return value
        raise blender_cave.exceptions.OSC_Invalid_Type(str(value) + ' is not a string')

    def _prepare_vol(self, value):
        if isinstance(value, str):
            if value[0] == '%' or value[0] == '+' or value[0] == '-':
                try:
                    int(value[1])
                    value = value[0] + str(int(value[1:]))
                    return value
                except:
                    pass
        raise blender_cave.exceptions.OSC_Invalid_Type(str(value) + ' is not a valid volume (%32, +5, -17)')

    def define_commands(self):
        from types import MethodType
        for name, attribut in self._commands.items():
            if 'cmd' not in attribut:
                attribut['cmd'] = name
            attribut['update'] = False
            attribut['value']  = ''
            attribut['method'] = '_prepare_' + attribut['type']
            setattr(self, name, MethodType(getattr(self, '_command'), attribut))
