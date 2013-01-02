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

import sys
import xml.sax.handler
import optparse
import os.path
import blender_cave.base
import blender_cave.exceptions

class Configure(blender_cave.base.Base, xml.sax.handler.ContentHandler, xml.sax.handler.EntityResolver):

    def __init__(self, parent, environ, onlyScreens = False):
        super(Configure, self).__init__(parent)

        self._only_screens = onlyScreens
        self._environ      = environ
        self._file_name    = self._environ.getEnvironment('config_file')
        self._screen_name  = self._environ.getEnvironment('screen')

        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.setEntityResolver(self)

        from . import root
        self._currentObject = root.Root(self)
        parser.parse(self._file_name)

    def getOnlyScreens(self):
        return self._only_screens

    def getScreen(self):
        return self._screen_name

    def getConfiguration(self):
        return self._currentObject.getConfiguration()

    def resolveEntity(self,publicID,systemID):
        filename = self._environ.checkConfigurationFile(systemID, False)
        if filename is None:
            raise blender_cave.exceptions.Configure('Cannot load ' + systemID + ' configuration file')
        return filename

    def startElement(self, name, attrs):
        try:
            self._current_tag = name
            self._currentObject = self._currentObject.startElement(name, attrs)
        except:
            self.log_traceback(False)
            raise blender_cave.exceptions.Configure('See previous exception (' + self.getXML_Position() + ')')

    def characters(self, string):
        try:
            self._currentObject.characters(string)
        except:
            self.log_traceback(False)
            raise blender_cave.exceptions.Configure('See previous exception (' + self.getXML_Position() + ')')

    def endElement(self, name):
        try:
            self._currentObject = self._currentObject.endElement(name)
        except:
            self.log_traceback(False)
            raise blender_cave.exceptions.Configure('See previous exception (' + self.getXML_Position() + ')')

    def getXML_LineNumber(self):
        return self._locator.getLineNumber()

    def getXML_FileName(self):
        return self._locator.getSystemId()

    def getXML_Position(self):
        return 'line ' + str(self.getXML_LineNumber()) + ' of ' + self.getXML_FileName()

