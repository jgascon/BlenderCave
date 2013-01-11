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
from . import base

class User(base.Base):

    def __init__(self, parent, attrs):
        super(User, self).__init__(parent, attrs)
        try:
            self._eye_separation = float(attrs['eye_separation'])
        except KeyError as error:
            self._eye_separation = 0.06
        except ValueError as error:
            self.print_warning('Invalid float value (' + attrs['eye_separation'] + ')')
            self._eye_separation = 0.06

        self._default_position = mathutils.Vector()
        self._set_default_position = False

    def startElement(self, name, attrs):
        if name == 'default_position':
            self._set_default_position = True
        return self

    def characters(self, string):
        if self._set_default_position:
            self._default_position = self.getVector(string)
        
    def endElement(self, name):
        if name == 'default_position':
            self._set_default_position = False
        return super(User, self).endElement(name)

    def display(self, indent):
        self.print_display(indent, 'User : ' + self._name + ' - eye separation : ' + str(self._eye_separation) + ' - default : ' + str(self._default_position))
        super(User, self).display(indent)
        
    def getConfiguration(self):
        return {'name'             : self._name,
                'eye_separation'   : self._eye_separation,
                'default_position' : self._default_position}
