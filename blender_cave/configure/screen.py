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

from . import base

class Screen(base.Base):

    def __init__(self, parent, attrs):
        super(Screen, self).__init__(parent, attrs)
        self._screen_id    = self._parent.addScreenAndGetItsID(self)
        self._is_master    = (self._screen_id == 0)

        self._corners      = {}
        self._buffers      = {}
        self._set_corner   = False
        self._set_viewport = False

    def startElement(self, name, attrs):
        if name == 'graphic_buffer':
            buffer_name = self.getNodeName(attrs)
            buffer = {}
            try:
                buffer['user'] = attrs['user']
            except KeyError:
                self.raise_error('Graphic buffer must have a "user" attribut !')
            try:
                eye = attrs['eye']
            except KeyError:
                self.raise_error('Graphic buffer must have a "eye" attribut !')
            for key, value in {'left': -1.0, 'middle': 0.0, 'right': +1.0}.items():
                if eye == key:
                    buffer['eye'] =  value
            if not 'eye' in buffer:
                self.raise_error('Invalid eye position "' + eye + '" !')
            self._buffers[buffer_name] =  buffer
        if (self._set_corner != False) or (self._set_viewport != False):
            self.raise_error('Cannot include any tag inside corner, viewport or graphic_buffer')
        if name == 'corner':
            self._set_corner   = self.getNodeName(attrs)
        if name == 'viewport':
            self._set_viewport = True
        if name == 'player':
            self._player = {}
            if 'options' in attrs:
                self._player['options'] = attrs['options']
            if 'display' in attrs:
                self._player['display'] = attrs['display']
        return self

    def characters(self, string):
        if self._set_corner != False:
            self._corner = self.getVector(string)
        if self._set_viewport != False:
            self._viewport     = []
            try:
                for coordinate in string.split(','):
                    self._viewport.append(int(coordinate))
            except ValueError as error:
                self.raise_error('Invalid viewport "' + string + '" : ' + str(error))
            if len(self._viewport) != 4:
                self.raise_error('viewport ("' + string + '") must have 4 components')
        
    def endElement(self, name):
        if name == 'corner':
            self._corners[self._set_corner] = self._corner
            del(self._corner)
            self._set_corner = False
        if name == 'viewport':
            self._set_viewport = False
        return super(Screen, self).endElement(name)

    def display(self, indent):
        if (self._is_master):
            master = '[master]'
        else:
            master = ''
        if hasattr(self, '_viewport'):
            viewport = 'viewport : ' + str(self._viewport)
        else:
            viewport = 'no viewport'
        self.print_display(indent, 'Screen ' + master + ': ' + self._name + ' - ' + str(viewport) + ' - corner :')
        for corner in self._corners:
            self.print_display(indent + 1, '[' + corner + ']' + str(self._corners[corner]))
        for buffer in self._buffers:
            self.print_display(indent + 1, '[' + buffer + ']' + str(self._buffers[buffer]))
        super(Screen, self).display(indent)

    def getConfiguration(self):
        configuration = { 'focus' : self._focus }
        try:
            configuration['player'] = self._player
        except AttributeError:
            pass
        configuration['master'] = self._is_master
        try:
            configuration['viewport'] = self._viewport
        except AttributeError:
            pass
        configuration['corners'] = {}
        not_found = []
        for cornerName in ['topRightCorner', 'topLeftCorner', 'bottomRightCorner']:
            try:
                configuration['corners'][cornerName] = self._corners[cornerName]
            except KeyError:
                not_found.append(cornerName)
        if len(not_found) > 0:
            self.raise_error('Cannot find corners : ' + str(not_found), False)

        configuration['buffers'] = {}
        for bufferName in ['left', 'alone', 'right']:
            try:
                configuration['buffers'][bufferName] = self._buffers[bufferName]
            except KeyError:
                pass
        if (len(configuration['buffers']) == 0):
            self.raise_error('No graphic buffer available for the current configuration', False)

        configuration['id'] = self._screen_id

        return configuration
