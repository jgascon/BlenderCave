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

import xml.sax.handler
import xml.sax.xmlreader
import blender_cave.base
import blender_cave.exceptions
from . import Configure

try:
    import mathutils
except ImportError:
    pass

class Base(blender_cave.base.Base, xml.sax.handler.ContentHandler):

    def __init__(self, parent, attrs, name = ''):
        super(Base, self).__init__(parent)
        self._children         = {}
        if isinstance(self.getParent(), Configure):
            self._parser       = self.getParent()
            self._xml_name     = 'root'
            self._name         = 'root'
            self._xml_position = self.getParser()._file_name
        else:
            self._parser       = self.getParent().getParser()
            self._xml_name     = self.getParser()._current_tag
            self._xml_position = self.getParser().getXML_Position() 
            if name != '':
                self._name = name
            else:
                self._name = self.getNodeName(attrs)

    def getParser(self):
        return self._parser

    def raise_error(self, msg, addCurrentPosition = True):
        if addCurrentPosition:
            raise blender_cave.exceptions.Configure(msg +' (' + self.getParser().getXML_Position() + ')')
        else:
            raise blender_cave.exceptions.Configure(msg +' (' + self._xml_position + ')')

    def print_warning(self, msg, addCurrentPosition = True):
        if addCurrentPosition:
            self.getLogger().warning(msg +' (' + self.getParser().getXML_Position() + ')')
        else:
            self.getLogger().warning(msg +' (' + self._xml_position + ')')

    def print_display(self, indent, msg):
        for i in range(indent):
            msg = '  ' + msg
        self.getLogger().info(msg)


    def getNodeName(self, attrs):
        try:
            return attrs['name']
        except KeyError:
            self.raise_error('Cannot get ' + self._xml_name + ' name')

    def addChild(self, child):
        if child is None:
            return self
        name = child._name
        xml = child._xml_name
        try:
            if name in self._children[xml]:
                self.raise_error(xml + '::' + name + ' already defined here ' + self._children[xml][name]._xml_position)
        except KeyError:
            self._children[xml] = {name : child}
        else:
            self._children[xml][name] = child
        return child

    def startElement(self, name, attrs):
        return self

    def characters(self,characters):
        return

    def endElement (self, name):
        if (name == self._xml_name):
            return self.getParent()
        return self

    def display(self, indent):
        for child_type in self._children:
            for child_name in self._children[child_type]:
                self._children[child_type][child_name].display(indent + 1)

    def getMathVector(self, vector, option = 3):
        try:
            if isinstance(option, mathutils.Vector):
                return option
            elif isinstance(option, int):
                if option == 2:
                    return mathutils.Vector((vector[0], vector[1]))
                elif option == 3:
                    return mathutils.Vector((vector[0], vector[1], vector[2]))
                elif option == 4:
                    return mathutils.Vector((vector[0], vector[1], vector[2], vector[3]))
                else:
                    return
            else:
                return
        except NameError:
            return vector

    def getVector(self, vector, option = 3):
        if isinstance(vector, str):
            coordinates = []
            try:
                for coordinate in vector.split(','):
                    coordinates.append(float(coordinate))
                    if len(coordinates) == option:
                        return self.getMathVector(coordinates)
            except ValueError as error:
                self.raise_error('Invalid vector "' + vector + '": ' + str(error))
            self.raise_error('Invalid vector : "' + vector + '"')
        elif isinstance(vector, xml.sax.xmlreader.AttributesImpl):
            result = self.getMathVector((0.0, 0.0, 0.0, 0.0), option)
            if result is None:
                return
            if len(result) == 2:
                components = ['x', 'y']
            elif len(result) == 3:
                components = ['x', 'y', 'z']
            elif len(result) == 4:
                components = ['x', 'y', 'z', 'w']
            else:
                return
            for component in components:
                if component in vector:
                    setattr(result, component, float(vector[component]))
            return result
